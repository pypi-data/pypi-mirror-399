import inspect
import logging
from dataclasses import (
    dataclass,
)

from fa_purity import (
    Cmd,
    FrozenDict,
    Maybe,
    PureIter,
)
from fa_singer_io.singer import (
    SingerRecord,
    SingerSchema,
    SingerState,
)
from fluidattacks_connection_manager import (
    CommonTableClient,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)
from fluidattacks_etl_utils.parallel import (
    ThreadPool,
)
from redshift_client.core.id_objs import (
    DbTableId,
    Identifier,
    SchemaId,
    TableId,
)
from redshift_client.core.table import (
    Table,
)

from fluidattacks_target_warehouse._s3 import (
    S3URI,
)
from fluidattacks_target_warehouse._utils import (
    MutableMap,
)
from fluidattacks_target_warehouse.data_schema import (
    extract_table,
)
from fluidattacks_target_warehouse.data_schema.duplicates import (
    SingerToColumnMap,
)
from fluidattacks_target_warehouse.grouper import (
    PackagedSinger,
)

from . import (
    _records,
    _schema,
    _state,
)
from ._records import (
    SingerHandlerOptions,
    StreamTables,
)

LOG = logging.getLogger(__name__)


MutableTableMap = MutableMap[str, tuple[DbTableId, Table]]


@dataclass(frozen=True)
class CommonSingerHandler:
    schema: SchemaId
    client: CommonTableClient
    options: SingerHandlerOptions
    s3_state: Maybe[S3URI]
    thread_pool: ThreadPool
    columns_map: SingerToColumnMap

    def update_stream_tables(self, table_map: StreamTables, schema: SingerSchema) -> StreamTables:
        table_id = DbTableId(self.schema, TableId(Identifier.new(schema.stream)))
        table = Bug.assume_success(
            "extract_table",
            inspect.currentframe(),
            (str(schema), str(self.columns_map)),
            extract_table(schema, self.columns_map),
        )
        return (
            FrozenDict(dict(table_map) | {schema.stream: (table_id, table)})
            if schema.stream not in table_map
            else table_map
        )

    @staticmethod
    def state_handler(s3_state: Maybe[S3URI], state: SingerState) -> Cmd[None]:
        nothing = Cmd.wrap_value(None)
        return s3_state.map(lambda f: _state.save_to_s3(f, state)).value_or(nothing)

    @staticmethod
    def schema_handler(
        schema_id: SchemaId,
        client: CommonTableClient,
        schema: SingerSchema,
        columns_map: SingerToColumnMap,
    ) -> Cmd[None]:
        return _schema.schema_handler(client, schema_id, schema, columns_map)

    def records_handler(
        self,
        table_map: StreamTables,
        records: PureIter[SingerRecord],
    ) -> Cmd[None]:
        return _records.record_handler(
            self.client,
            self.thread_pool,
            self.options,
            table_map,
            records,
            self.columns_map,
        )

    def handle(self, state: MutableTableMap, item: PackagedSinger) -> Cmd[None]:
        return item.map(
            lambda records: state.freeze().bind(lambda t: self.records_handler(t, records)),
            lambda schema: state.freeze().bind(
                lambda t: self.schema_handler(self.schema, self.client, schema, self.columns_map)
                + state.update(self.update_stream_tables(t, schema)),
            ),
            lambda s: self.state_handler(self.s3_state, s),
        )


__all__ = [
    "MutableMap",
    "MutableTableMap",
    "SingerHandlerOptions",
]
