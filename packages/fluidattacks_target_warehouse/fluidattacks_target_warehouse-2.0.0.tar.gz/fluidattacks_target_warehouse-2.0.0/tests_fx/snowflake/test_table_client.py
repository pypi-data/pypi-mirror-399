import logging
from collections.abc import (
    Callable,
)
from datetime import (
    UTC,
    datetime,
)

import pytest
from fa_purity import (
    Cmd,
    FrozenDict,
    PureIterFactory,
    Unsafe,
)
from redshift_client.client import (
    GroupedRows,
    TableRow,
)
from redshift_client.core.column import (
    Column,
)
from redshift_client.core.data_type.core import (
    DataType,
    StaticTypes,
)
from redshift_client.core.id_objs import (
    ColumnId,
    DbTableId,
    Identifier,
    SchemaId,
    TableId,
)
from redshift_client.core.table import (
    Table,
)
from redshift_client.sql_client import (
    DbPrimitiveFactory,
    Limit,
    RowData,
)
from snowflake_client import (
    ClientFactory,
    TableClient,
)

from ._utils import (
    common_cursor,
    connection_setup,
)

LOG = logging.getLogger(__name__)


def _common_test(test: Callable[[Cmd[TableClient]], Cmd[None]]) -> None:
    cmd: Cmd[None] = connection_setup().bind(
        lambda c: test(common_cursor(c, LOG).map(ClientFactory.new_table_client)),
    )
    with pytest.raises(SystemExit):
        cmd.compute()


common_table_id = DbTableId(
    SchemaId(Identifier.new("test")),
    TableId(Identifier.new("foo")),
)


def common_table() -> Table:
    column_1 = ColumnId(Identifier.new("col_1"))
    column_2 = ColumnId(Identifier.new("col_2"))
    columns: FrozenDict[ColumnId, Column] = FrozenDict(
        {
            column_1: Column(
                DataType(StaticTypes.INTEGER),
                False,
                DbPrimitiveFactory.from_raw(None),
            ),
            column_2: Column(
                DataType(StaticTypes.TIMESTAMPTZ),
                False,
                DbPrimitiveFactory.from_raw(None),
            ),
        },
    )
    return (
        Table.new((column_1, column_2), columns, frozenset([column_1]))
        .alt(Unsafe.raise_exception)
        .to_union()
    )


def test_new_table() -> None:
    def _test(client: TableClient) -> Cmd[None]:
        return client.new(
            common_table_id,
            common_table(),
        ).map(lambda r: r.alt(Unsafe.raise_exception).to_union())

    _common_test(lambda new: new.bind(_test))


def test_get_table() -> None:
    def assert_table(table: Table) -> None:
        assert table == common_table()

    def _test(client: TableClient) -> Cmd[None]:
        return client.get(
            common_table_id,
        ).map(lambda r: r.map(assert_table).alt(Unsafe.raise_exception).to_union())

    _common_test(lambda new: new.bind(_test))


def test_insert() -> None:
    def _test(client: TableClient) -> Cmd[None]:
        data = PureIterFactory.from_list(
            [
                (
                    DbPrimitiveFactory.from_raw(44299244),
                    DbPrimitiveFactory.from_raw(
                        datetime(2000, 1, 2, 3, 4, 5, 6, tzinfo=UTC),
                    ),
                ),
                (
                    DbPrimitiveFactory.from_raw(44299245),
                    DbPrimitiveFactory.from_raw(
                        datetime(2001, 1, 2, 3, 4, 5, 6, tzinfo=UTC),
                    ),
                ),
                (
                    DbPrimitiveFactory.from_raw(44299246),
                    DbPrimitiveFactory.from_raw(
                        datetime(2002, 1, 2, 3, 4, 5, 6, tzinfo=UTC),
                    ),
                ),
            ],
        ).map(RowData)
        return client.insert(common_table_id, common_table(), data, Limit(100)).map(
            lambda r: r.alt(Unsafe.raise_exception).to_union(),
        )

    _common_test(lambda new: new.bind(_test))


def test_named_insert() -> None:
    def _test(client: TableClient) -> Cmd[None]:
        data = PureIterFactory.from_list(
            [
                TableRow.new(
                    common_table(),
                    FrozenDict(
                        {
                            ColumnId(Identifier.new("col_1")): DbPrimitiveFactory.from_raw(5299244),
                            ColumnId(Identifier.new("col_2")): DbPrimitiveFactory.from_raw(
                                datetime(2010, 1, 2, 3, 4, 5, 6, tzinfo=UTC),
                            ),
                        },
                    ),
                )
                .alt(Unsafe.raise_exception)
                .to_union(),
                TableRow.new(
                    common_table(),
                    FrozenDict(
                        {
                            ColumnId(Identifier.new("col_1")): DbPrimitiveFactory.from_raw(
                                54299245,
                            ),
                            ColumnId(Identifier.new("col_2")): DbPrimitiveFactory.from_raw(
                                datetime(2020, 1, 2, 3, 4, 5, 6, tzinfo=UTC),
                            ),
                        },
                    ),
                )
                .alt(Unsafe.raise_exception)
                .to_union(),
                TableRow.new(
                    common_table(),
                    FrozenDict(
                        {
                            ColumnId(Identifier.new("col_1")): DbPrimitiveFactory.from_raw(
                                54299246,
                            ),
                            ColumnId(Identifier.new("col_2")): DbPrimitiveFactory.from_raw(
                                datetime(2030, 1, 2, 3, 4, 5, 6, tzinfo=UTC),
                            ),
                        },
                    ),
                )
                .alt(Unsafe.raise_exception)
                .to_union(),
            ],
        )
        grouped_data = (
            GroupedRows.new(common_table(), data.to_list()).alt(Unsafe.raise_exception).to_union()
        )
        return client.named_insert(
            common_table_id,
            grouped_data,
        ).map(lambda r: r.alt(Unsafe.raise_exception).to_union())

    _common_test(lambda new: new.bind(_test))
