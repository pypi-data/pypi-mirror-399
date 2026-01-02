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

from fluidattacks_target_warehouse.grouper import (
    PackagedSinger,
)


@dataclass(frozen=True)
class SingerLoader:
    """Procedure to process a `PackagedSinger` over an `SchemaId`."""

    _procedure: Callable[[SchemaId, PackagedSinger], Cmd[None]]

    def handle(self, schema: SchemaId, msg: PackagedSinger) -> Cmd[None]:
        return self._procedure(schema, msg)
