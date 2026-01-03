import inspect

from fa_purity import (
    Cmd,
    Result,
    ResultE,
)
from fa_singer_io.singer import (
    SingerSchema,
)
from fluidattacks_connection_manager import (
    CommonTableClient,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)
from redshift_client.core.id_objs import (
    DbTableId,
    Identifier,
    SchemaId,
    TableId,
)
from redshift_client.core.table import (
    Table,
)

from fluidattacks_target_warehouse import (
    _utils,
)
from fluidattacks_target_warehouse._utils import (
    chain_cmd_result,
)
from fluidattacks_target_warehouse.data_schema import (
    extract_table,
)
from fluidattacks_target_warehouse.data_schema.duplicates import (
    SingerToColumnMap,
)


def _handle_new_columns(
    client: CommonTableClient,
    singer_table: Table,
    current_table: DbTableId,
) -> Cmd[ResultE[None]]:
    nothing: Cmd[ResultE[None]] = Cmd.wrap_value(Result.success(None))
    return chain_cmd_result(
        client.get(current_table),
        lambda t: _utils.add_missing_columns(
            client.add_columns,
            singer_table,
            (current_table, t),
        ).map(lambda n: Result.success(n))
        if singer_table != t
        else nothing,
    )


def _create_table(
    client: CommonTableClient,
    table_id: DbTableId,
    schema: SingerSchema,
    column_map: SingerToColumnMap,
) -> Cmd[ResultE[None]]:
    singer_table = Bug.assume_success(
        "extract_table",
        inspect.currentframe(),
        (str(schema), str(column_map)),
        extract_table(schema, column_map),
    )
    return chain_cmd_result(
        client.exist(table_id),
        lambda exist: _handle_new_columns(client, singer_table, table_id)
        if exist
        else client.new(table_id, singer_table),
    )


def schema_handler(
    client: CommonTableClient,
    schema: SchemaId,
    data_schema: SingerSchema,
    column_map: SingerToColumnMap,
) -> Cmd[None]:
    table_id = DbTableId(schema, TableId(Identifier.new(data_schema.stream)))
    return _create_table(client, table_id, data_schema, column_map).map(
        lambda r: Bug.assume_success(
            "schema_handler",
            inspect.currentframe(),
            (str(table_id), str(data_schema), str(column_map)),
            r,
        ),
    )
