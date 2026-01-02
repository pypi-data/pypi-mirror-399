from dataclasses import (
    dataclass,
)

from fa_purity import (
    Cmd,
    Stream,
    StreamTransform,
)
from fa_singer_io.singer import (
    SingerMessage,
)
from redshift_client.core.id_objs import (
    SchemaId,
)

from fluidattacks_target_warehouse.grouper import (
    Grouper,
)
from fluidattacks_target_warehouse.loader import (
    SingerLoader,
)
from fluidattacks_target_warehouse.strategy import (
    LoadingStrategy,
)


@dataclass(frozen=True)
class OutputEmitter:
    _data: Stream[SingerMessage]
    loader: SingerLoader
    strategy: LoadingStrategy

    def load_procedure(self, schema: SchemaId) -> Cmd[None]:
        grouper = Grouper.new(13 * 10**6)  # limit of 13MB
        return grouper.bind(
            lambda g: g.group_records(self._data)
            .map(lambda p: self.loader.handle(schema, p))
            .transform(StreamTransform.consume),
        )

    def main(self) -> Cmd[None]:
        return self.strategy.main(self.load_procedure)
