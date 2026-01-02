import inspect
from typing import (
    Literal,
)

from fa_purity import (
    Cmd,
    PureIterFactory,
    Result,
    ResultE,
)
from fluidattacks_connection_manager import (
    CommonSchemaClient,
    CommonTableClient,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)
from redshift_client.core.id_objs import (
    DbTableId,
)

from fluidattacks_target_warehouse import (
    _utils,
)
from fluidattacks_target_warehouse._utils import (
    chain_cmd_result,
    consume_results,
)

from ._core import (
    StagingSchemas,
)


def _add_missing_columns(
    client: CommonTableClient,
    source: DbTableId,
    target: DbTableId,
) -> Cmd[ResultE[None]]:
    nothing: Cmd[ResultE[None]] = Cmd.wrap_value(Result.success(None))
    _add_columns: Cmd[ResultE[None]] = chain_cmd_result(
        client.get(source).map(
            lambda r: r.alt(
                lambda e: Bug.new(
                    "get_source_table",
                    inspect.currentframe(),
                    e,
                    (str(source),),
                ),
            ),
        ),
        lambda s: chain_cmd_result(
            client.get(target).map(
                lambda r: r.alt(
                    lambda e: Bug.new(
                        "target_table",
                        inspect.currentframe(),
                        e,
                        (str(target),),
                    ),
                ),
            ),
            lambda t: _utils.add_missing_columns(client.add_columns, s, (target, t)).map(
                lambda x: Result.success(x),
            )
            if s != t
            else nothing,
        ),
    )
    return chain_cmd_result(client.exist(target), lambda b: _add_columns if b else nothing)


def move_data(
    sh_client: CommonSchemaClient,
    tb_client: CommonTableClient,
    persistent_tables: frozenset[str] | Literal["ALL"],
    schemas: StagingSchemas,
) -> Cmd[ResultE[None]]:
    """
    Move data from schemas.

    loading -> target
    - migrate non-persistent tables
    - move persistent tables
    """

    def _to_target(table: DbTableId) -> Cmd[ResultE[None]]:
        target = DbTableId(schemas.target, table.table)
        if persistent_tables == "ALL" or table.table.name.to_str() in persistent_tables:
            return chain_cmd_result(
                _add_missing_columns(tb_client, table, target),
                lambda _: tb_client.move(table, target).map(
                    lambda r: r.alt(
                        lambda e: Bug.new(
                            "move_target_table",
                            inspect.currentframe(),
                            e,
                            (
                                str(table),
                                str(target),
                            ),
                        ),
                    ),
                ),
            )
        return tb_client.migrate(table, target).map(
            lambda r: r.alt(
                lambda e: Bug.new(
                    "migrate_target_table",
                    inspect.currentframe(),
                    e,
                    (
                        str(table),
                        str(target),
                    ),
                ),
            ),
        )

    return chain_cmd_result(
        sh_client.table_ids(schemas.loading).map(
            lambda r: r.alt(
                lambda e: Bug.new(
                    "table_ids",
                    inspect.currentframe(),
                    e,
                    (str(schemas.loading),),
                ),
            ),
        ),
        lambda tables: PureIterFactory.from_list(tuple(tables))
        .map(_to_target)
        .transform(consume_results),
    )
