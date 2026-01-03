from __future__ import (
    annotations,
)

from collections.abc import (
    Callable,
)
from dataclasses import (
    dataclass,
    field,
)

from fa_purity import (
    Cmd,
    FrozenList,
    PureIter,
    PureIterFactory,
    ResultE,
    ResultFactory,
)
from fa_singer_io.singer import (
    SingerRecord,
)


@dataclass(frozen=True)
class _Private:
    pass


@dataclass(frozen=True)
class MutableStreamRecords:
    """Grouped mutable list of `SingerRecord` that share the same stream attribute."""

    _private: _Private = field(repr=False, hash=False, compare=False)
    _records: list[SingerRecord]
    stream: str

    @staticmethod
    def init(stream: str) -> Cmd[MutableStreamRecords]:
        return Cmd.wrap_impure(lambda: MutableStreamRecords(_Private(), [], stream))

    def append(self, record: SingerRecord) -> ResultE[Cmd[None]]:
        factory: ResultFactory[Cmd[None], Exception] = ResultFactory()
        if record.stream == self.stream:
            return factory.success(Cmd.wrap_impure(lambda: self._records.append(record)))
        err = ValueError(f"The record does not belong to the `{self.stream}` stream i.e. {record}")
        return factory.failure(err)

    def get_records(self) -> Cmd[FrozenList[SingerRecord]]:
        return Cmd.wrap_impure(lambda: tuple(self._records))


@dataclass(frozen=True)
class StreamRecords:
    """Grouped list of `SingerRecord` that share the same stream attribute."""

    _private: _Private = field(repr=False, hash=False, compare=False)
    stream: str
    records: PureIter[SingerRecord]

    @staticmethod
    def assert_list(stream: str, records: FrozenList[SingerRecord]) -> ResultE[StreamRecords]:
        invalid = (
            PureIterFactory.from_list(records)
            .map(lambda r: (r, r.stream == stream))
            .find_first(lambda t: t[1] is False)
        )
        factory: ResultFactory[StreamRecords, Exception] = ResultFactory()
        return invalid.map(
            lambda t: factory.failure(
                ValueError(f"A record does not belong to the `{stream}` stream i.e. {t[0]}"),
            ),
        ).or_else_call(
            lambda: factory.success(
                StreamRecords(_Private(), stream, PureIterFactory.from_list(records)),
            ),
        )

    @staticmethod
    def from_mutable(mutable: MutableStreamRecords) -> Cmd[StreamRecords]:
        return mutable.get_records().map(
            lambda s: StreamRecords(_Private(), mutable.stream, PureIterFactory.from_list(s)),
        )

    @staticmethod
    def filter(records: PureIter[SingerRecord], stream: str) -> StreamRecords:
        return StreamRecords(_Private(), stream, records.filter(lambda r: r.stream == stream))

    def _new_record(self, record: SingerRecord) -> SingerRecord:
        return SingerRecord(self.stream, record.record, record.time_extracted)

    def map(self, function: Callable[[SingerRecord], SingerRecord]) -> StreamRecords:
        """
        Transform records that `StreamRecords` holds.

        [WARNING] changing the stream of a record is ignored
        """
        return StreamRecords(
            _Private(),
            self.stream,
            self.records.map(lambda r: self._new_record(function(r))),
        )
