import inspect
import sys
from dataclasses import (
    dataclass,
)
from io import (
    BufferedReader,
    TextIOWrapper,
)
from typing import (
    IO,
    TypeVar,
)

from fa_purity import (
    Cmd,
    PureIter,
    Stream,
    Unsafe,
)
from fa_singer_io.singer import (
    SingerMessage,
)
from fa_singer_io.singer.deserializer import (
    from_file_ignore_failed,
    try_from_file,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)

_T = TypeVar("_T")


def _ensure_stdin_type(raw: BufferedReader | _T) -> BufferedReader:
    if isinstance(raw, BufferedReader):
        return raw
    msg = f"Expected a `BufferedReader` but got {type(raw)}"
    raise TypeError(msg)


@dataclass(frozen=True)
class InputEmitter:
    ignore_failed: bool

    @property
    def input_stream(self) -> Stream[SingerMessage]:
        def deserializer(file: IO[str]) -> PureIter[SingerMessage]:
            if self.ignore_failed:
                return from_file_ignore_failed(file)
            return try_from_file(file).map(
                lambda r: Bug.assume_success(
                    "input_singer_decode_from_file",
                    inspect.currentframe(),
                    (),
                    r,
                ),
            )

        cmd = Cmd.wrap_impure(
            lambda: TextIOWrapper(
                _ensure_stdin_type(sys.stdin.buffer),  # type: ignore[misc]
                encoding="utf-8",
            ),
        )
        return Unsafe.stream_from_cmd(cmd.map(deserializer).map(lambda x: iter(x)))
