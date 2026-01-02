from __future__ import (
    annotations,
)

import logging
from tempfile import (
    TemporaryFile,
)
from typing import TYPE_CHECKING

import boto3
from fa_purity import (
    Cmd,
)
from fa_purity.json import (
    JsonUnfolder,
)
from fa_singer_io.singer import (
    SingerState,
)

from fluidattacks_target_warehouse._s3 import (
    S3URI,
)

if TYPE_CHECKING:
    from mypy_boto3_s3 import (
        S3Client,
    )
LOG = logging.getLogger(__name__)


def _new_s3_client() -> Cmd[S3Client]:
    return Cmd.wrap_impure(lambda: boto3.client("s3"))


def _save(client: S3Client, file: S3URI, state: SingerState) -> Cmd[None]:
    def _action() -> None:
        LOG.info("Uploading new state")
        LOG.debug("Uploading state to %s", file)
        with TemporaryFile() as data:
            data.write(JsonUnfolder.dumps(state.value).encode("UTF-8"))
            data.seek(0)
            client.upload_fileobj(data, file.bucket, file.file_path)

    return Cmd.wrap_impure(_action)


def save_to_s3(file: S3URI, state: SingerState) -> Cmd[None]:
    return _new_s3_client().bind(lambda c: _save(c, file, state))
