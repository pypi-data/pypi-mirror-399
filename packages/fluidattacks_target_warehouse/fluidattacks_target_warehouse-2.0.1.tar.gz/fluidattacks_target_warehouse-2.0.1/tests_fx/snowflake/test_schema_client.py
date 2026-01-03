import logging
from collections.abc import (
    Callable,
)

import pytest
from fa_purity import (
    Cmd,
    PureIterFactory,
    Unsafe,
)
from redshift_client.core.id_objs import (
    DbTableId,
    Identifier,
    SchemaId,
    TableId,
)
from snowflake_client import (
    ClientFactory,
    SchemaClient,
)

from ._utils import (
    assert_false,
    assert_true,
    common_cursor,
    connection_setup,
)

LOG = logging.getLogger(__name__)


def _common_test(test: Callable[[Cmd[SchemaClient]], Cmd[None]]) -> None:
    cmd: Cmd[None] = connection_setup().bind(
        lambda c: test(common_cursor(c, LOG).map(ClientFactory.new_schema_client)),
    )
    with pytest.raises(SystemExit):
        cmd.compute()


def test_get_all_schemas() -> None:
    def assert_schemas(schemas: frozenset[SchemaId]) -> None:
        assert schemas == PureIterFactory.from_list(["information_schema", "test"]).map(
            lambda r: SchemaId(Identifier.new(r)),
        ).transform(frozenset)

    def _test(client: SchemaClient) -> Cmd[None]:
        return client.all_schemas.map(
            lambda r: r.map(assert_schemas).alt(Unsafe.raise_exception).to_union(),
        )

    _common_test(lambda new: new.bind(_test))


def test_table_ids() -> None:
    test_schema = SchemaId(Identifier.new("test"))

    def assert_tables(tables: frozenset[DbTableId]) -> None:
        assert tables == PureIterFactory.from_list(["foo"]).map(
            lambda r: DbTableId(test_schema, TableId(Identifier.new(r))),
        ).transform(frozenset)

    def _test(client: SchemaClient) -> Cmd[None]:
        return client.table_ids(test_schema).map(
            lambda r: r.map(assert_tables).alt(Unsafe.raise_exception).to_union(),
        )

    _common_test(lambda new: new.bind(_test))


def test_create_and_exist() -> None:
    def _test(client: SchemaClient) -> Cmd[None]:
        test_schema = SchemaId(Identifier.new("test"))
        return client.create(test_schema).map(
            lambda r: r.alt(Unsafe.raise_exception).to_union(),
        ) + client.exist(test_schema).map(
            lambda r: r.map(assert_true).alt(Unsafe.raise_exception).to_union(),
        )

    _common_test(lambda new: new.bind(_test))


def test_create_if_not_exist() -> None:
    def _test(client: SchemaClient) -> Cmd[None]:
        test_schema = SchemaId(Identifier.new("test"))

        _create: Cmd[None] = client.create_if_not_exist(test_schema).map(
            lambda r: r.alt(Unsafe.raise_exception).to_union(),
        )
        return (
            _create
            + _create
            + client.exist(test_schema).map(
                lambda r: r.map(assert_true).alt(Unsafe.raise_exception).to_union(),
            )
        )

    _common_test(lambda new: new.bind(_test))


def test_delete() -> None:
    def _test(client: SchemaClient) -> Cmd[None]:
        test_schema = SchemaId(Identifier.new("test"))

        _create: Cmd[None] = client.create_if_not_exist(test_schema).map(
            lambda r: r.alt(Unsafe.raise_exception).to_union(),
        )
        _delete: Cmd[None] = client.delete(test_schema).map(
            lambda r: r.alt(Unsafe.raise_exception).to_union(),
        )
        return (
            _create
            + _delete
            + client.exist(test_schema).map(
                lambda r: r.map(assert_false).alt(Unsafe.raise_exception).to_union(),
            )
        )

    _common_test(lambda new: new.bind(_test))


def test_rename() -> None:
    def _test(client: SchemaClient) -> Cmd[None]:
        test_schema = SchemaId(Identifier.new("test"))
        new_test_schema = SchemaId(Identifier.new("test_99"))

        _rename: Cmd[None] = client.rename(test_schema, new_test_schema).map(
            lambda r: r.alt(Unsafe.raise_exception).to_union(),
        )
        return (
            _rename
            + client.exist(test_schema).map(
                lambda r: r.map(assert_false).alt(Unsafe.raise_exception).to_union(),
            )
            + client.exist(new_test_schema).map(
                lambda r: r.map(assert_true).alt(Unsafe.raise_exception).to_union(),
            )
        )

    _common_test(lambda new: new.bind(_test))


def test_recreate() -> None:
    def _test(client: SchemaClient) -> Cmd[None]:
        test_schema = SchemaId(Identifier.new("test"))

        _recreate: Cmd[None] = client.recreate(test_schema).map(
            lambda r: r.alt(Unsafe.raise_exception).to_union(),
        )
        return _recreate + client.exist(test_schema).map(
            lambda r: r.map(assert_true).alt(Unsafe.raise_exception).to_union(),
        )

    _common_test(lambda new: new.bind(_test))
