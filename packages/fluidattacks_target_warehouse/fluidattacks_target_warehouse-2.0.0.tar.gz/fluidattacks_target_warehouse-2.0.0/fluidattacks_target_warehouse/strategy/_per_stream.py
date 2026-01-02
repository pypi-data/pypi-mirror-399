import inspect
from dataclasses import (
    dataclass,
)

from fa_purity import (
    Cmd,
    PureIterFactory,
    PureIterTransform,
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

from fluidattacks_target_warehouse._utils import (
    chain_cmd_result,
)

from ._core import (
    LoadingStrategy,
    LoadProcedure,
    StagingProcedure,
    StagingSchemas,
)
from ._move_data import (
    move_data,
)


@dataclass(frozen=True)
class RecreatePerStream:
    _staging: StagingProcedure
    _client: CommonSchemaClient
    _client_2: CommonTableClient
    _persistent_tables: frozenset[str]

    def _backup(self, schemas: StagingSchemas) -> Cmd[ResultE[None]]:
        """Migrate non-persistent tables, target -> backup."""

        def _migrate(table: DbTableId) -> Cmd[None]:
            if table.table.name.to_str() in self._persistent_tables:
                return Cmd.wrap_value(None)
            return self._client_2.migrate(table, DbTableId(schemas.backup, table.table)).map(
                lambda r: Bug.assume_success(
                    "RecreatePerStream._backup._migrate",
                    inspect.currentframe(),
                    (str(table), str(schemas.backup)),
                    r,
                ),
            )

        create_schema = self._client.recreate_cascade(schemas.backup)
        return chain_cmd_result(
            create_schema,
            lambda _: chain_cmd_result(
                self._client.table_ids(schemas.target),
                lambda tables: PureIterTransform.consume(
                    PureIterFactory.pure_map(_migrate, tuple(tables)),
                ).map(lambda x: Result.success(x)),
            ),
        )

    def _main(self, procedure: LoadProcedure) -> Cmd[None]:
        return self._staging.main(
            procedure,
            lambda s: chain_cmd_result(
                self._client.create_if_not_exist(s.target),
                lambda _: chain_cmd_result(
                    self._backup(s),
                    lambda _: move_data(
                        self._client,
                        self._client_2,
                        self._persistent_tables,
                        s,
                    ),
                ),
            ).map(
                lambda r: Bug.assume_success(
                    "per_stream_post_upload",
                    inspect.currentframe(),
                    (),
                    r,
                ),
            ),
        )

    @property
    def strategy(self) -> LoadingStrategy:
        return LoadingStrategy(self._main)
