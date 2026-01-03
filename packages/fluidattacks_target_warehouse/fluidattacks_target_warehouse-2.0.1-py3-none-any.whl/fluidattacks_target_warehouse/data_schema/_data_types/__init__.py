from dataclasses import (
    dataclass,
)
from enum import (
    Enum,
)

from fa_purity import (
    FrozenList,
    FrozenTools,
    PureIterFactory,
    Result,
    ResultE,
    ResultFactory,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitiveUnfolder,
    JsonUnfolder,
    Unfolder,
)
from redshift_client.core.column import (
    Column,
)
from redshift_client.core.data_type.core import (
    DataType,
    StaticTypes,
)
from redshift_client.sql_client import (
    DbPrimitiveFactory,
)

from ._integer import (
    int_handler,
)
from ._number import (
    num_handler,
)
from ._string import (
    string_format_handler,
)


class _JschemaType(Enum):
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    OBJECT = "object"
    ARRAY = "array"
    BOOLEAN = "boolean"
    NULL = "null"


def _to_jschema_type(raw: str) -> ResultE[_JschemaType]:
    try:
        return Result.success(_JschemaType(raw.lower()))
    except ValueError as err:
        return Result.failure(err, _JschemaType).alt(Exception)


@dataclass(frozen=True)
class _RawType:
    raw_type: _JschemaType
    nullable: bool


def _simplify_type_list(types: FrozenList[str]) -> ResultE[_RawType]:
    nullable = "null" in types
    reduced = PureIterFactory.from_list(types).filter(lambda x: x != "null").to_list()
    if len(reduced) > 1:
        err = NotImplementedError("Generic union types not supported. Only Optional[_T] support")
        return Result.failure(err, _RawType).alt(Exception)
    if len(reduced) == 0:
        err = NotImplementedError(
            "None type field not supported. None type cannot hold information",
        )
        return Result.failure(err, _RawType).alt(Exception)
    return _to_jschema_type(reduced[0]).map(lambda t: _RawType(t, nullable))


def _to_column(raw: _RawType, encoded: JsonObj) -> ResultE[Column]:
    factory: ResultFactory[Column, Exception] = ResultFactory()
    empty = DbPrimitiveFactory.from_raw(None)
    if raw.raw_type is _JschemaType.INTEGER:
        return int_handler(encoded).map(lambda d: Column(d, raw.nullable, empty))
    if raw.raw_type is _JschemaType.NUMBER:
        return num_handler(encoded).map(lambda d: Column(d, raw.nullable, empty))
    if raw.raw_type is _JschemaType.STRING:
        return string_format_handler(encoded).map(lambda d: Column(d, raw.nullable, empty))
    if raw.raw_type is _JschemaType.BOOLEAN:
        return (
            Result.success(StaticTypes.BOOLEAN, Exception)
            .map(DataType)
            .map(lambda d: Column(d, raw.nullable, empty))
        )
    err = NotImplementedError(f"Unsupported json schema type `{raw.raw_type}`")
    return factory.failure(err)


def jschema_type_handler(encoded: JsonObj) -> ResultE[Column]:
    _types: ResultE[FrozenList[str]] = JsonUnfolder.require(
        encoded,
        "type",
        lambda v: Unfolder.to_primitive(v)
        .bind(JsonPrimitiveUnfolder.to_str)
        .map(lambda s: FrozenTools.freeze([s]))
        .lash(
            lambda _: Unfolder.to_list_of(
                v,
                lambda i: Unfolder.to_primitive(i).bind(JsonPrimitiveUnfolder.to_str),
            ),
        ),
    )
    return _types.bind(_simplify_type_list).bind(lambda r: _to_column(r, encoded))
