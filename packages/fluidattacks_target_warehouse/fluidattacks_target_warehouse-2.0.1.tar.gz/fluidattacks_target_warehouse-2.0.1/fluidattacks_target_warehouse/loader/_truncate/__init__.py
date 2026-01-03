from fa_purity import (
    PureIterFactory,
    Result,
    ResultE,
    ResultTransform,
    cast_exception,
)
from redshift_client.core.column import (
    Column,
)
from redshift_client.core.data_type.core import (
    PrecisionType,
    PrecisionTypes,
)
from redshift_client.core.table import (
    Table,
)
from redshift_client.sql_client import (
    DbPrimitive,
    DbPrimitiveFactory,
    RowData,
)

from .utf8_truncation import (
    utf8_byte_truncate,
)


def _truncate_str(column: Column, item: DbPrimitive) -> ResultE[DbPrimitive]:
    def _precision_type(value: PrecisionType) -> ResultE[DbPrimitive]:
        if value.data_type in (
            PrecisionTypes.CHAR,
            PrecisionTypes.VARCHAR,
        ):

            def _error(var_type: str) -> ResultE[DbPrimitive]:
                return Result.failure(
                    ValueError(
                        f"`CHAR` or `VARCHAR` item must be an str instance but got {var_type}",
                    ),
                ).alt(cast_exception)

            return item.map(
                lambda p: p.map(
                    lambda s: utf8_byte_truncate(s, value.precision).map(
                        DbPrimitiveFactory.from_raw,
                    ),
                    lambda _: _error("int"),
                    lambda _: _error("float"),
                    lambda _: _error("Decimal"),
                    lambda _: _error("bool"),
                    lambda: Result.success(DbPrimitiveFactory.from_raw(None))
                    if column.nullable
                    else _error("None"),
                ),
                lambda _: _error("datetime"),
            )
        return Result.success(item)

    return column.data_type.map(
        lambda _: Result.success(item),
        _precision_type,
        lambda _: Result.success(item),
    )


def truncate_row(table: Table, row: RowData) -> ResultE[RowData]:
    columns = PureIterFactory.pure_map(
        lambda c: (c[0], table.columns[c[1]]),
        tuple(enumerate(table.order)),
    )
    trucated = columns.map(lambda c: _truncate_str(c[1], row.data[c[0]]))
    return ResultTransform.all_ok(trucated.to_list()).map(RowData)
