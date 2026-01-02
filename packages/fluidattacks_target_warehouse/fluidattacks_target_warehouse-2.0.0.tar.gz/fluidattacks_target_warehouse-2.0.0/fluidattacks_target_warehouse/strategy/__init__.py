import inspect
from collections.abc import (
    Callable,
)
from dataclasses import (
    dataclass,
)

from fa_purity import (
    Cmd,
    PureIterFactory,
)
from fluidattacks_connection_manager import (
    ClientAdapter,
    CommonSchemaClient,
    CommonTableClient,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)
from redshift_client.core.id_objs import (
    Identifier,
    SchemaId,
)
from snowflake_client import (
    ClientFactory as SnowflakeClientFactory,
)
from snowflake_client._core import (
    SnowflakeCursor,
)

from ._core import (
    LoadingStrategy,
)
from ._only_append import (
    OnlyAppend,
)
from ._per_stream import (
    RecreatePerStream,
)
from ._recreate_all import (
    RecreateAll,
)
from ._staging import (
    common_pre_upload,
)

PersistentTables = frozenset[str]
Pristine = bool


@dataclass(frozen=True)
class Strategies:
    """Data loading strategies."""

    recreate_all_schema: Callable[[SchemaId], LoadingStrategy]
    recreate_per_stream: Callable[[SchemaId, PersistentTables], LoadingStrategy]
    only_append: Callable[[SchemaId, Pristine], Cmd[LoadingStrategy]]


@dataclass(frozen=True)
class _StrategiesFactory1:
    _table_client: CommonTableClient
    _schema_client: CommonSchemaClient

    def recreate_all_schema(self, target: SchemaId) -> LoadingStrategy:
        """
        Recreates data to a target schema.

        - executes loading procedure on a pristine (empty) staging schema
        - saves `target` as backup
        - sets staging schema as the new `target`
        """
        _staging = common_pre_upload(
            target,
            self._schema_client,
            self._table_client,
            frozenset(),
            True,
        )
        return RecreateAll(_staging, self._schema_client).strategy

    def recreate_per_stream(
        self,
        target: SchemaId,
        persistent_tables: frozenset[str],
    ) -> LoadingStrategy:
        """
        Recreates data to a target schema.

        - executes loading procedure on a pristine (empty) staging schema
        - migrates (overrides) all NON `persistent_tables` on staging over the `target`
        - appends/moves data of `persistent_tables` on staging over the `target`
        """
        _persistent_tables = frozenset(Identifier.new(i) for i in persistent_tables)
        _staging = common_pre_upload(
            target,
            self._schema_client,
            self._table_client,
            _persistent_tables,
            True,
        )
        return RecreatePerStream(
            _staging,
            self._schema_client,
            self._table_client,
            persistent_tables,
        ).strategy

    def only_append(self, target: SchemaId, pristine: bool) -> Cmd[LoadingStrategy]:
        """
        Append data to a target schema.

        - executes loading procedure on a pristine (if enabled) staging schema
        - appends/moves data of staging over the `target`
        """
        _target_tables = (
            self._schema_client.table_ids(target)
            .map(
                lambda r: r.map(
                    lambda s: PureIterFactory.from_list(tuple(s)).map(lambda t: t.table.name),
                ).alt(
                    lambda e: Bug.new(
                        "_target_tables",
                        inspect.currentframe(),
                        e,
                        (str(target),),
                    ),
                ),
            )
            .map(
                lambda r: Bug.assume_success(
                    "only_append_loading_stategy",
                    inspect.currentframe(),
                    (),
                    r,
                ),
            )
        )
        _staging = _target_tables.map(
            lambda persistent: common_pre_upload(
                target,
                self._schema_client,
                self._table_client,
                frozenset(persistent),
                pristine,
            ),
        )
        return _staging.map(
            lambda s: OnlyAppend(s, self._schema_client, self._table_client).strategy,
        )


@dataclass(frozen=True)
class StrategiesFactory:
    @staticmethod
    def from_snowflake(cursor: SnowflakeCursor) -> Strategies:
        obj = _StrategiesFactory1(
            ClientAdapter.snowflake_table_client_adapter(
                SnowflakeClientFactory.new_table_client(cursor),
            ),
            ClientAdapter.snowflake_schema_client_adapter(
                SnowflakeClientFactory.new_schema_client(cursor),
            ),
        )
        return Strategies(
            obj.recreate_all_schema,
            obj.recreate_per_stream,
            obj.only_append,
        )


__all__ = [
    "LoadingStrategy",
    "StrategiesFactory",
]
