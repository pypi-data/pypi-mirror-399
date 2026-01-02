from __future__ import (
    annotations,
)

import inspect
import logging
from collections.abc import (
    Callable,
)
from dataclasses import (
    dataclass,
)

from fa_purity import (
    Cmd,
    Maybe,
    Result,
    ResultE,
    cast_exception,
)
from fluidattacks_connection_manager import (
    ClientAdapter,
    CommonTableClient,
    ConnectionConf,
    ConnectionManager,
    ConnectionManagerFactory,
    Databases,
    DbClients,
    Roles,
    Warehouses,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)
from fluidattacks_etl_utils.parallel import (
    ThreadPool,
)
from redshift_client.core.id_objs import (
    SchemaId,
)
from snowflake_client import (
    SnowflakeCursor,
)

from fluidattacks_target_warehouse._s3 import (
    S3URI,
)
from fluidattacks_target_warehouse.data_schema.duplicates import (
    SingerToColumnMap,
)
from fluidattacks_target_warehouse.loader import (
    Loaders,
    SingerHandlerOptions,
)
from fluidattacks_target_warehouse.strategy import (
    LoadingStrategy,
    Strategies,
    StrategiesFactory,
)

from ._input import (
    InputEmitter,
)
from ._output import (
    OutputEmitter,
)

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class GenericExecutor:
    target: SchemaId
    options: SingerHandlerOptions
    s3_state: Maybe[S3URI]
    ignore_failed: bool
    strategy: Callable[
        [Strategies, SchemaId],
        Cmd[LoadingStrategy],
    ]
    thread_pool: ThreadPool
    column_map: SingerToColumnMap

    def _upload(
        self,
        cursor: SnowflakeCursor,
        table_client: CommonTableClient,
        s3_state: Maybe[S3URI],
    ) -> Cmd[None]:
        _input = InputEmitter(self.ignore_failed).input_stream
        loader = Loaders.common_loader(
            self.thread_pool,
            table_client,
            self.options,
            s3_state,
            self.column_map,
        )
        return loader.bind(
            lambda _loader: self.strategy(
                StrategiesFactory.from_snowflake(cursor),
                self.target,
            ).bind(
                lambda s: OutputEmitter(
                    _input,
                    _loader,
                    s,
                ).main(),
            ),
        )

    def _main(
        self,
        new_cursor: Cmd[SnowflakeCursor],
        new_table_client: Cmd[CommonTableClient],
    ) -> Cmd[None]:
        return new_cursor.bind(
            lambda sql: new_table_client.bind(
                lambda table: self._upload(sql, table, self.s3_state),
            ),
        )

    def _execute_with_manager(self, manager: ConnectionManager) -> Cmd[None]:
        def _with_clients(clients: DbClients) -> Cmd[ResultE[None]]:
            return self._main(
                clients.connection.cursor(LOG),
                clients.connection.cursor(LOG)
                .map(clients.new_table_client)
                .map(ClientAdapter.snowflake_table_client_adapter),
            ).map(lambda x: Result.success(x))

        conf = ConnectionConf(
            Warehouses.GENERIC_COMPUTE,
            Roles.ETL_UPLOADER,
            Databases.OBSERVES,
        )
        action = manager.execute_with_snowflake(
            _with_clients,
            conf,
        ).map(
            lambda r: r.alt(
                lambda e: e.map(
                    lambda x: x,
                    cast_exception,
                ),
            ),
        )
        return action.map(
            lambda r: Bug.assume_success("generic executor", inspect.currentframe(), (), r),
        )

    def execute(self) -> Cmd[None]:
        return (
            ConnectionManagerFactory.observes_manager()
            .map(
                lambda r: Bug.assume_success(
                    "fluidattacks_connection_manager",
                    inspect.currentframe(),
                    (),
                    r,
                ),
            )
            .bind(self._execute_with_manager)
        )
