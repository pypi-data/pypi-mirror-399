from dataclasses import (
    dataclass,
)

from fa_purity import (
    Cmd,
    Maybe,
)
from fluidattacks_connection_manager import (
    CommonTableClient,
)
from fluidattacks_etl_utils.parallel import (
    ThreadPool,
)

from fluidattacks_target_warehouse._s3 import (
    S3URI,
)
from fluidattacks_target_warehouse.data_schema.duplicates import (
    SingerToColumnMap,
)

from ._core import (
    SingerLoader,
)
from ._handlers import (
    CommonSingerHandler,
    MutableMap,
    MutableTableMap,
    SingerHandlerOptions,
)


@dataclass(frozen=True)
class Loaders:
    @staticmethod
    def common_loader(
        thread_pool: ThreadPool,
        client: CommonTableClient,
        options: SingerHandlerOptions,
        s3_state: Maybe[S3URI],
        column_map: SingerToColumnMap,
    ) -> Cmd[SingerLoader]:
        """
        Create a common data loader.

        - upload singer records into the warehouse
        - transforms singer schemas into the warehouse tables
        - saves singer states into a s3 file
        """
        state: Cmd[MutableTableMap] = MutableMap.new()
        return state.map(
            lambda m: SingerLoader(
                lambda s, p: CommonSingerHandler(
                    s,
                    client,
                    options,
                    s3_state,
                    thread_pool,
                    column_map,
                ).handle(m, p),
            ),
        )
