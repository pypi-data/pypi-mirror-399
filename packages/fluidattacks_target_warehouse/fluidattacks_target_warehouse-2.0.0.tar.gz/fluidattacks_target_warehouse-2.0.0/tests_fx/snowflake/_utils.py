from logging import (
    Logger,
)

from fa_purity import (
    Cmd,
    Unsafe,
)
from fluidattacks_etl_utils.secrets import (
    ObservesSecretsFactory,
)
from snowflake_client import (
    ConnectionFactory,
    SnowflakeCredentials,
    SnowflakeDatabase,
    SnowflakeWarehouse,
)
from snowflake_client._core import (
    SnowflakeConnection,
    SnowflakeCursor,
    SnowflakeQuery,
)


def connection_setup() -> Cmd[SnowflakeConnection]:
    creds = (
        ObservesSecretsFactory.new()
        .map(lambda r: r.alt(Unsafe.raise_exception).to_union())
        .bind(lambda s: s.snowflake_etl_access)
    )
    return creds.bind(
        lambda creds: ConnectionFactory.snowflake_connection(
            SnowflakeDatabase("OBSERVES"),
            SnowflakeWarehouse("GENERIC_COMPUTE"),
            SnowflakeCredentials(
                user=creds.user,
                private_key=creds.private_key,
                account=creds.account,
            ),
        ),
    )


def common_cursor(connection: SnowflakeConnection, log: Logger) -> Cmd[SnowflakeCursor]:
    return connection.cursor(log).bind(
        lambda c: c.execute(SnowflakeQuery.new_query("USE ROLE etl_uploader"), None).map(
            lambda r: r.alt(Unsafe.raise_exception).to_union(),
        )
        + c.execute(SnowflakeQuery.new_query("USE DATABASE observes"), None).map(
            lambda r: r.alt(Unsafe.raise_exception).to_union(),
        )
        + c.execute(SnowflakeQuery.new_query("USE WAREHOUSE GENERIC_COMPUTE"), None).map(
            lambda r: r.alt(Unsafe.raise_exception).to_union(),
        )
        + Cmd.wrap_value(c),
    )


def assert_true(value: bool) -> None:
    assert value


def assert_false(value: bool) -> None:
    assert not value
