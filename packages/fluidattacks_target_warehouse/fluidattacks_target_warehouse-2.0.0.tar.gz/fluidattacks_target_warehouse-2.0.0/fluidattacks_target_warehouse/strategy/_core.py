from collections.abc import (
    Callable,
)
from dataclasses import (
    dataclass,
)

from fa_purity import (
    Cmd,
)
from redshift_client.core.id_objs import (
    SchemaId,
)

LoadProcedure = Callable[[SchemaId], Cmd[None]]


@dataclass(frozen=True)
class LoadingStrategy:
    """Procedure that adds pre and post upload operations for the supplied `LoadProcedure`."""

    _main: Callable[[LoadProcedure], Cmd[None]]

    def main(self, procedure: LoadProcedure) -> Cmd[None]:
        return self._main(procedure)


@dataclass(frozen=True)
class StagingSchemas:
    backup: SchemaId
    loading: SchemaId
    target: SchemaId


@dataclass(frozen=True)
class StagingProcedure:
    """Pre upload operations for the supplied `LoadProcedure`."""

    _main: Callable[[LoadProcedure, Callable[[StagingSchemas], Cmd[None]]], Cmd[None]]

    def main(
        self,
        procedure: LoadProcedure,
        post_upload: Callable[[StagingSchemas], Cmd[None]],
    ) -> Cmd[None]:
        return self._main(procedure, post_upload)
