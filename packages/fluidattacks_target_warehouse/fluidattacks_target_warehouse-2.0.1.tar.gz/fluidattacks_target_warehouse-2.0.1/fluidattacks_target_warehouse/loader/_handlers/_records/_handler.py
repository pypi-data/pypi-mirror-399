from __future__ import (
    annotations,
)

import inspect
import logging
from dataclasses import (
    dataclass,
    field,
)

from fa_purity import (
    Cmd,
    FrozenDict,
    Maybe,
    PureIter,
    PureIterFactory,
    Result,
    ResultE,
    ResultTransform,
    cast_exception,
)
from fa_purity.json import (
    JsonPrimitive,
    JsonValue,
    Unfolder,
)
from fa_singer_io.singer import (
    SingerRecord,
)
from fluidattacks_connection_manager import (
    CommonTableClient,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)
from fluidattacks_etl_utils.parallel import (
    ThreadPool,
)
from redshift_client.core.column import (
    Column,
)
from redshift_client.core.data_type.core import (
    PrecisionTypes,
    StaticTypes,
)
from redshift_client.core.id_objs import (
    ColumnId,
    DbTableId,
    Identifier,
)
from redshift_client.core.table import (
    Table,
)
from redshift_client.sql_client import (
    DbPrimitive,
    Limit,
    RowData,
)

from fluidattacks_target_warehouse.data_schema.duplicates import (
    SingerToColumnMap,
)
from fluidattacks_target_warehouse.loader import (
    _truncate,
)

from ._stream_records import (
    StreamRecords,
)

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class _Private:
    pass


@dataclass(frozen=True)
class StdSingerRecord:
    _private: _Private = field(repr=False, hash=False, compare=False)
    singer: SingerRecord
    std_record: FrozenDict[ColumnId, JsonValue]

    @staticmethod
    def new(record: SingerRecord, column_map: SingerToColumnMap) -> StdSingerRecord:
        def _to_column(raw: str) -> ColumnId:
            return Maybe.from_optional(column_map.value.get(raw)).or_else_call(
                lambda: ColumnId(Identifier.new(raw)),
            )

        _records = PureIterFactory.pure_map(
            lambda t: (_to_column(t[0]), t[1]),
            tuple(record.record.items()),
        ).transform(lambda p: FrozenDict(dict(p)))
        return StdSingerRecord(_Private(), record, _records)


@dataclass(frozen=True)
class SingerHandlerOptions:
    truncate_str: bool
    records_per_query: int


StreamTables = FrozenDict[str, tuple[DbTableId, Table]]


def _is_str_represented(column: Column) -> bool:
    return column.data_type.map(
        lambda s: s
        in [
            StaticTypes.TIMESTAMP,
            StaticTypes.TIMESTAMPTZ,
            StaticTypes.TIME,
            StaticTypes.TIMETZ,
        ],
        lambda p: p.data_type is PrecisionTypes.VARCHAR,
        lambda _: False,
    )


def _adjust_nullable_values(column: Column, data: JsonPrimitive) -> JsonPrimitive:
    if _is_str_represented(column) and data == JsonPrimitive.from_str("") and column.nullable:
        return JsonPrimitive.empty()
    return data


def _get_column_value(
    values_map: FrozenDict[ColumnId, JsonValue],
    column_id: ColumnId,
    column: Column,
) -> ResultE[JsonPrimitive]:
    value = (
        Maybe.from_optional(values_map.get(column_id))
        .to_result()
        .lash(
            lambda _: Result.success(JsonValue.from_primitive(JsonPrimitive.empty()), Exception)
            if column.nullable
            else Result.failure(
                Bug.new(
                    "set_nullable",
                    inspect.currentframe(),
                    KeyError(
                        "Value not found and column `"
                        + column_id.name.to_str()
                        + "` is NOT nullable",
                    ),
                    (str(column_id), str(column)),
                ),
                JsonValue,
            ).alt(cast_exception),
        )
        .bind(
            lambda j: Unfolder.to_primitive(j).alt(
                lambda e: Bug.new(
                    "value_to_primitive",
                    inspect.currentframe(),
                    e,
                    (str(column_id), str(column)),
                ),
            ),
        )
    )
    return value.map(lambda v: _adjust_nullable_values(column, v))


def _to_row(table: Table, record: StdSingerRecord) -> ResultE[RowData]:
    return PureIterFactory.pure_map(
        lambda cid: Maybe.from_optional(table.columns.get(cid))
        .to_result()
        .alt(lambda _: KeyError("Column " + cid.name.to_str() + " not found"))
        .alt(cast_exception)
        .bind(lambda c: _get_column_value(record.std_record, cid, c)),
        table.order,
    ).transform(
        lambda x: ResultTransform.all_ok(tuple(x)).map(
            lambda d: RowData(PureIterFactory.pure_map(DbPrimitive.inl, d).to_list()),
        ),
    )


def _upload_records(
    client: CommonTableClient,
    pool: ThreadPool,
    options: SingerHandlerOptions,
    table_id: DbTableId,
    table: Table,
    group: StreamRecords,
    column_map: SingerToColumnMap,
) -> Cmd[None]:
    chunks = (
        group.records.map(
            lambda r: _to_row(table, StdSingerRecord.new(r, column_map)).bind(
                lambda d: _truncate.truncate_row(table, d)
                if options.truncate_str
                else Result.success(d),
            ),
        )
        .map(lambda r: Bug.assume_success("_to_row", inspect.currentframe(), (), r))
        .chunked(options.records_per_query)
    )
    commands = chunks.map(
        lambda p: client.insert(
            table_id,
            table,
            PureIterFactory.from_list(p),
            Limit(1000),
        ).map(lambda r: Bug.assume_success("insert_records", inspect.currentframe(), (), r))
        + Cmd.wrap_impure(lambda: LOG.debug("insert done!")),
    )
    return pool.in_threads_none(commands)


def record_handler(
    client: CommonTableClient,
    pool: ThreadPool,
    options: SingerHandlerOptions,
    table_map: StreamTables,
    records: PureIter[SingerRecord],
    column_map: SingerToColumnMap,
) -> Cmd[None]:
    tables = frozenset(records.map(lambda r: r.stream))
    grouped = PureIterFactory.from_list(tuple(tables)).map(
        lambda t: Maybe.from_optional(table_map.get(t))
        .to_result()
        .map(
            lambda u: _upload_records(
                client,
                pool,
                options,
                u[0],
                u[1],
                StreamRecords.filter(records, t),
                column_map,
            ),
        )
        .alt(lambda _: KeyError(f"{t} not found on table_map")),
    )
    return grouped.map(
        lambda r: Bug.assume_success(
            "record_handler",
            inspect.currentframe(),
            (str(table_map),),
            r,
        ),
    ).transform(lambda x: pool.in_threads_none(x))
