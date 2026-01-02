from __future__ import (
    annotations,
)

import inspect
from dataclasses import (
    dataclass,
)

from fa_purity import (
    Cmd,
    Result,
    ResultE,
)
from fluidattacks_connection_manager import (
    CommonSchemaClient,
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
    StagingSchemas,
)


@dataclass(frozen=True)
class RecreateAll:
    _staging: StagingProcedure
    _client: CommonSchemaClient

    def _post_upload(self, schemas: StagingSchemas) -> Cmd[ResultE[None]]:
        _do_nothing: Cmd[ResultE[None]] = Cmd.wrap_value(Result.success(None))
        drop_backup = chain_cmd_result(
            self._client.exist(schemas.backup),
            lambda b: self._client.delete_cascade(schemas.backup) if b else _do_nothing,
        )
        rename_old = chain_cmd_result(
            self._client.exist(schemas.target),
            lambda b: self._client.rename(schemas.target, schemas.backup) if b else _do_nothing,
        )
        rename_loading = chain_cmd_result(
            self._client.exist(schemas.loading),
            lambda b: self._client.rename(schemas.loading, schemas.target) if b else _do_nothing,
        )
        return chain_cmd_result(
            drop_backup,
            lambda _: chain_cmd_result(rename_old, lambda _: rename_loading),
        )

    def _main(self, procedure: LoadProcedure) -> Cmd[None]:
        return self._staging.main(
            procedure,
            lambda s: self._post_upload(s).map(
                lambda r: Bug.assume_success("_post_upload", inspect.currentframe(), (str(s),), r),
            ),
        )

    @property
    def strategy(self) -> LoadingStrategy:
        return LoadingStrategy(self._main)
