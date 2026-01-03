from enum import (
    Enum,
)

from fa_purity import (
    Result,
    ResultE,
    cast_exception,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitiveUnfolder,
    JsonUnfolder,
    Unfolder,
)
from redshift_client.core.data_type.core import (
    DataType,
    StaticTypes,
)


class _IntSizes(Enum):
    SMALL = "small"
    NORMAL = "normal"
    BIG = "big"


def _to_size(raw: str) -> ResultE[_IntSizes]:
    try:
        return Result.success(_IntSizes(raw.lower()))
    except ValueError as err:
        return Result.failure(cast_exception(err))


def _size_map(size: _IntSizes) -> DataType:
    if size is _IntSizes.SMALL:
        return DataType(StaticTypes.SMALLINT)
    if size is _IntSizes.NORMAL:
        return DataType(StaticTypes.INTEGER)
    if size is _IntSizes.BIG:
        return DataType(StaticTypes.BIGINT)


def int_handler(encoded: JsonObj) -> ResultE[DataType]:
    _size: ResultE[_IntSizes] = JsonUnfolder.optional(
        encoded,
        "size",
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_str).bind(_to_size),
    ).map(lambda m: m.value_or(_IntSizes.NORMAL))
    return _size.map(_size_map)
