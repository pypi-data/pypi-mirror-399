import inspect
from typing import (
    IO,
    NoReturn,
)

import click
from fa_purity import (
    Cmd,
    Maybe,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)
from fluidattacks_etl_utils.parallel import (
    ThreadPool,
)
from redshift_client.core.id_objs import (
    Identifier,
    SchemaId,
)

from fluidattacks_target_warehouse._s3 import (
    S3URI,
)
from fluidattacks_target_warehouse.executor import (
    GenericExecutor,
)
from fluidattacks_target_warehouse.loader import (
    SingerHandlerOptions,
)

from ._decode import (
    decode_columns_map,
)


@click.command()
@click.option(
    "-s",
    "--schema-name",
    type=str,
    required=True,
    help="Schema name in your warehouse",
)
# -- Optional --
@click.option(
    "--records-per-query",
    type=int,
    required=False,
    default=1000,
    help="Max # of records per sql query",
)
@click.option(
    "--s3-state",
    type=str,
    required=False,
    default=None,
    help="S3 file obj URI to upload the state; e.g. s3://mybucket/folder/state.json",
)
@click.option(
    "--threads",
    type=int,
    required=False,
    default=1000,
    help="max number of threads",
)
# -- Flags --
@click.option(
    "--ignore-failed",
    type=bool,
    is_flag=True,
    help="ignore json items that does not decode to a singer message",
)
@click.option(
    "--truncate",
    type=bool,
    is_flag=True,
    help="Truncate records that exceed column size?",
)
@click.option(
    "--columns-map",
    type=click.File("r"),
    help="Custom map from singer properties into ColumnId",
)
@click.option(
    "--use-snowflake",
    type=bool,
    is_flag=True,
    help="Use snowflake implementation",
)
def only_append(
    schema_name: str,
    records_per_query: int,
    s3_state: str | None,
    threads: int,
    ignore_failed: bool,
    truncate: bool,
    columns_map: IO[str] | None,
    use_snowflake: bool,  # noqa: ARG001
    # for legacy cli calls
) -> NoReturn:
    target = SchemaId(Identifier.new(schema_name))
    options = SingerHandlerOptions(
        truncate,
        records_per_query,
    )
    state = (
        Maybe.from_optional(s3_state)
        .map(S3URI.from_raw)
        .map(lambda r: Bug.assume_success("S3URI", inspect.currentframe(), (str(s3_state),), r))
    )
    pool = ThreadPool.new(threads)
    _columns_map = Bug.assume_success(
        "decode_columns_map",
        inspect.currentframe(),
        (),
        decode_columns_map(columns_map),
    )
    executor = pool.map(
        lambda p: GenericExecutor(
            target,
            options,
            state,
            ignore_failed,
            lambda s, t: s.only_append(t, True),
            p,
            _columns_map,
        ),
    )
    cmd: Cmd[None] = executor.bind(lambda e: e.execute())
    cmd.compute()
