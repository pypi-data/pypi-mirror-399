from __future__ import (
    annotations,
)

import inspect
import logging
from collections.abc import (
    Callable,
    Iterable,
)
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    TypeVar,
)

from fa_purity import (
    Cmd,
    Coproduct,
    CoproductFactory,
    FrozenList,
    Maybe,
    PureIter,
    PureIterFactory,
    Result,
    ResultE,
    Stream,
    StreamTransform,
    Unsafe,
    cast_exception,
)
from fa_purity.json import (
    JsonUnfolder,
)
from fa_singer_io.singer import (
    SingerMessage,
    SingerRecord,
    SingerSchema,
    SingerState,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)

from fluidattacks_target_warehouse import (
    _utils,
)

LOG = logging.getLogger(__name__)
_T = TypeVar("_T")


@dataclass(frozen=True)
class PackagedSinger:
    """Wrapper for type `PureIter[SingerRecord] | SingerSchema | SingerState`."""

    _inner: Coproduct[PureIter[SingerRecord], Coproduct[SingerSchema, SingerState]]

    @staticmethod
    def new(
        item: PureIter[SingerRecord] | SingerSchema | SingerState,
    ) -> PackagedSinger:
        factory: CoproductFactory[SingerSchema, SingerState] = CoproductFactory()
        factory_2: CoproductFactory[
            PureIter[SingerRecord],
            Coproduct[SingerSchema, SingerState],
        ] = CoproductFactory()
        if isinstance(item, SingerSchema):
            return PackagedSinger(factory_2.inr(factory.inl(item)))
        if isinstance(item, SingerState):
            return PackagedSinger(factory_2.inr(factory.inr(item)))
        return PackagedSinger(factory_2.inl(item))

    def map(
        self,
        iter_case: Callable[[PureIter[SingerRecord]], _T],
        schema_case: Callable[[SingerSchema], _T],
        state_case: Callable[[SingerState], _T],
    ) -> _T:
        return self._inner.map(iter_case, lambda c: c.map(schema_case, state_case))


@dataclass(frozen=True)
class GroupedRecords:
    """Records that belongs to the same schema."""

    @dataclass(frozen=True)
    class _Private:
        pass

    _private: GroupedRecords._Private = field(repr=False, hash=False, compare=False)
    stream: str
    records: FrozenList[SingerRecord]

    def append(self, record: SingerRecord) -> ResultE[GroupedRecords]:
        if record.stream == self.stream:
            group = GroupedRecords(
                GroupedRecords._Private(),
                self.stream,
                (
                    *self.records,
                    record,
                ),
            )
            return Result.success(group)
        return Result.failure(
            ValueError("Singer record does not belong to the group schema"),
            GroupedRecords,
        ).alt(cast_exception)

    @staticmethod
    def from_raw(stream: str, records: FrozenList[SingerRecord]) -> ResultE[GroupedRecords]:
        if all(PureIterFactory.from_list(records).map(lambda r: r.stream == stream)):
            group = GroupedRecords(GroupedRecords._Private(), stream, records)
            return Result.success(group)
        return Result.failure(
            ValueError("Some singer records does not belong to the same singer schema"),
            GroupedRecords,
        ).alt(cast_exception)


@dataclass(frozen=True)
class Grouper:
    @dataclass(frozen=True)
    class _Private:
        pass

    _private: Grouper._Private = field(repr=False, hash=False, compare=False)
    _items: dict[str, list[SingerRecord]]
    _bytes_size: dict[str, int]
    _size_threshold: int

    @staticmethod
    def new(size_threshold: int) -> Cmd[Grouper]:
        return Cmd.wrap_impure(lambda: Grouper(Grouper._Private(), {}, {}, size_threshold))

    @staticmethod
    def _record_size(record: SingerRecord) -> int:
        return len(JsonUnfolder.dumps(record.record).encode("utf-8"))

    def _schema_handler(self, schema: SingerSchema) -> Cmd[PackagedSinger]:
        """Register an schema to keep track of its records and the size of them."""

        def _action() -> None:
            if schema.stream not in self._items:
                self._items[schema.stream] = []
                self._bytes_size[schema.stream] = 0
            else:
                LOG.warning("Schema `%s` already handled by the grouper", schema.stream)

        return Cmd.wrap_impure(_action).map(lambda _: PackagedSinger.new(schema))

    def _record_handler(self, record: SingerRecord) -> Cmd[Maybe[PackagedSinger]]:
        """
        Accumulate records of the same stream until optimal size is reached.

        When threshold is reached return the accumulated records as `GroupedRecords`
        and accumulate the supplied record.
        """
        record_size = self._record_size(record)

        def _action() -> Maybe[GroupedRecords]:
            new_size = self._bytes_size[record.stream] + record_size
            if new_size > self._size_threshold:
                items = tuple(self._items[record.stream])
                group = Bug.assume_success(
                    "grouped_records",
                    inspect.currentframe(),
                    (record.stream, str(items)),
                    GroupedRecords.from_raw(record.stream, items),
                )
                self._items[record.stream] = [record]
                self._bytes_size[record.stream] = record_size
                return Maybe.some(group)
            self._items[record.stream].append(record)
            self._bytes_size[record.stream] += record_size
            return Maybe.empty()

        return Cmd.wrap_impure(_action).map(
            lambda m: m.map(lambda g: PackagedSinger.new(PureIterFactory.from_list(g.records))),
        )

    @property
    def _flush(self) -> Stream[Maybe[PackagedSinger]]:
        def _action() -> Iterable[Maybe[PackagedSinger]]:
            for r in self._items.values():
                if len(r) > 0:
                    yield Maybe.some(PackagedSinger.new(PureIterFactory.from_list(r)))

        new_iter = Cmd.wrap_impure(_action)
        return Unsafe.stream_from_cmd(new_iter)

    def group_records(
        self,
        data: Stream[SingerMessage],
    ) -> Stream[PackagedSinger]:
        return (
            data.map(
                lambda m: m.map(
                    lambda r: self._record_handler(r),
                    lambda s: self._schema_handler(s).map(lambda v: Maybe.some(v)),
                    lambda s: Cmd.wrap_value(Maybe.some(PackagedSinger.new(s))),
                ),
            )
            .transform(lambda s: StreamTransform.squash(s))
            .transform(lambda s: _utils.join_stream(s, self._flush))
            .transform(lambda s: StreamTransform.filter_maybe(s))
        )
