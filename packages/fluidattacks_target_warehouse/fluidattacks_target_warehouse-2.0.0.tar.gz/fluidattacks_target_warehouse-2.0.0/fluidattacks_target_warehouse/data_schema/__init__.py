import inspect
from collections.abc import (
    Callable,
)

from fa_purity import (
    FrozenDict,
    FrozenList,
    PureIterFactory,
    ResultE,
    ResultTransform,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitiveUnfolder,
    JsonUnfolder,
    Unfolder,
)
from fa_singer_io.singer import (
    SingerSchema,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)
from redshift_client.core.column import (
    Column,
    ColumnId,
)
from redshift_client.core.id_objs import (
    Identifier,
)
from redshift_client.core.table import (
    Table,
)
from redshift_client.sql_client import (
    DbPrimitiveFactory,
)

from fluidattacks_target_warehouse.data_schema.duplicates import (
    SingerToColumnMap,
)

from . import (
    duplicates,
)
from ._data_types import (
    jschema_type_handler,
)


def _to_column_id(raw: str, columns_map: SingerToColumnMap) -> ColumnId:
    if raw in columns_map.value:
        return columns_map.value[raw]
    return ColumnId(Identifier.new(raw))


def _to_columns(
    properties: JsonObj,
    to_id: Callable[[str], ColumnId],
) -> ResultE[FrozenList[tuple[ColumnId, Column]]]:
    return (
        PureIterFactory.from_list(tuple(properties.items()))
        .map(
            lambda t: Unfolder.to_json(t[1])
            .bind(jschema_type_handler)
            .map(lambda c: (to_id(t[0]), c)),
        )
        .transform(lambda p: ResultTransform.all_ok(p.to_list()))
    )


def _set_nullable(
    column: tuple[ColumnId, Column],
    required: frozenset[ColumnId],
) -> tuple[ColumnId, Column]:
    if column[0] not in required:
        return (
            column[0],
            Column(column[1].data_type, True, DbPrimitiveFactory.from_raw(None)),
        )
    return column


def extract_table(schema: SingerSchema, columns_map: SingerToColumnMap) -> ResultE[Table]:
    encoded = schema.schema.encode()
    _properties = JsonUnfolder.require(encoded, "properties", Unfolder.to_json)
    _required: ResultE[frozenset[ColumnId]] = JsonUnfolder.optional(
        encoded,
        "required",
        lambda v: Unfolder.to_list_of(
            v,
            lambda i: Unfolder.to_primitive(i).bind(JsonPrimitiveUnfolder.to_str),
        ),
    ).map(
        lambda m: m.map(
            lambda i: frozenset(
                PureIterFactory.from_list(i).map(lambda v: ColumnId(Identifier.new(v))),
            ),
        ).value_or(frozenset()),
    )
    return _properties.bind(
        lambda props: _required.bind(
            lambda req: _to_columns(props, lambda r: _to_column_id(r, columns_map)).map(
                lambda i: PureIterFactory.from_list(i).map(lambda g: _set_nullable(g, req)),
            ),
        ).bind(
            lambda columns: Table.new(
                columns.map(lambda c: c[0]).to_list(),
                FrozenDict(dict(columns)),
                PureIterFactory.from_list(tuple(schema.key_properties))
                .map(lambda pk: ColumnId(Identifier.new(pk)))
                .transform(frozenset),
            ).alt(
                lambda e: Bug.new(
                    "Possible duplicated_columns. Suggeseted map: "
                    + duplicates.columns_map(
                        PureIterFactory.from_list(tuple(props.keys())),
                    ).encode(),
                    inspect.currentframe(),
                    e,
                    (str(props.keys()),),
                ),
            ),
        ),
    )
