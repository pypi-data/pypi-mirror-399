import inspect
from dataclasses import (
    dataclass,
)

from fa_purity import (
    Cmd,
)
from fluidattacks_connection_manager import (
    CommonSchemaClient,
    CommonTableClient,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)

from fluidattacks_target_warehouse._utils import (
    chain_cmd_result,
)

from ._core import (
    LoadingStrategy,
    LoadProcedure,
    StagingProcedure,
)
from ._move_data import (
    move_data,
)


@dataclass(frozen=True)
class OnlyAppend:
    _staging: StagingProcedure
    _client: CommonSchemaClient
    _client_2: CommonTableClient

    def _main(self, procedure: LoadProcedure) -> Cmd[None]:
        return self._staging.main(
            procedure,
            lambda s: chain_cmd_result(
                self._client.create_if_not_exist(s.target),
                lambda _: move_data(self._client, self._client_2, "ALL", s),
            ).map(
                lambda r: Bug.assume_success(
                    "only_append_post_upload",
                    inspect.currentframe(),
                    (),
                    r,
                ),
            ),
        )

    @property
    def strategy(self) -> LoadingStrategy:
        return LoadingStrategy(self._main)
