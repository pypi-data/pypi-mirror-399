from __future__ import (
    annotations,
)

import inspect
from collections.abc import (
    Callable,
)

from fa_purity import (
    Cmd,
    PureIterFactory,
    PureIterTransform,
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
    Identifier,
    SchemaId,
    TableId,
)

from ._core import (
    LoadProcedure,
    StagingProcedure,
    StagingSchemas,
)


def common_pre_upload(
    target: SchemaId,
    client: CommonSchemaClient,
    client_2: CommonTableClient,
    persistent_tables: frozenset[Identifier],
    pristine_loading: bool,
) -> StagingProcedure:
    _schemas = StagingSchemas(
        SchemaId(Identifier.new(target.name.to_str() + "_backup")),
        SchemaId(Identifier.new(target.name.to_str() + "_loading")),
        target,
    )

    def _mirror_table(table: Identifier) -> Cmd[None]:
        blueprint = DbTableId(_schemas.target, TableId(table))
        mirror = client_2.create_like(blueprint, DbTableId(_schemas.loading, TableId(table))).map(
            lambda r: Bug.assume_success(
                "common_pre_upload._mirror_table/mirror",
                inspect.currentframe(),
                (str(blueprint),),
                r,
            ),
        )
        nothing = Cmd.wrap_value(None)
        return (
            client_2.exist(blueprint)
            .map(
                lambda r: Bug.assume_success(
                    "common_pre_upload._mirror_table/blueprint_exists",
                    inspect.currentframe(),
                    (str(blueprint),),
                    r,
                ),
            )
            .bind(lambda b: mirror if b else nothing)
        )

    _mirror_persistent = PureIterTransform.consume(
        PureIterFactory.from_list(tuple(persistent_tables)).map(_mirror_table),
    )

    def _main(
        procedure: LoadProcedure,
        post_upload: Callable[[StagingSchemas], Cmd[None]],
    ) -> Cmd[None]:
        recreate = (
            client.recreate_cascade(_schemas.loading).map(
                lambda r: Bug.assume_success(
                    "recreate_cascade_loading_schema",
                    inspect.currentframe(),
                    (str(_schemas.loading),),
                    r,
                ),
            )
            if pristine_loading
            else Cmd.wrap_value(None)
        )
        upload = procedure(_schemas.loading)
        return recreate + _mirror_persistent + upload + post_upload(_schemas)

    return StagingProcedure(_main)
