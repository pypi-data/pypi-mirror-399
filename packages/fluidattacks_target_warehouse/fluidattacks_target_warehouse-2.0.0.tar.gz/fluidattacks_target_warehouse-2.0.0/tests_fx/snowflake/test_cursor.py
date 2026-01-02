import logging

import pytest
from fa_purity import (
    Cmd,
    Unsafe,
)
from snowflake_client._core import (
    SnowflakeQuery,
)

from ._utils import (
    common_cursor,
    connection_setup,
)

LOG = logging.getLogger(__name__)


def test_cursor() -> None:
    cmd: Cmd[None] = (
        connection_setup()
        .bind(lambda c: common_cursor(c, LOG))
        .bind(
            lambda c: c.execute(SnowflakeQuery.new_query("CREATE SCHEMA test"), None).map(
                lambda r: r.alt(Unsafe.raise_exception).to_union(),
            ),
        )
    )
    with pytest.raises(SystemExit):
        cmd.compute()
