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
    DecimalType,
    StaticTypes,
)


class _NumSizes(Enum):
    FLOAT = "float"
    BIG_FLOAT = "big_float"
    EXACT = "exact"


def _to_size(raw: str) -> ResultE[_NumSizes]:
    try:
        return Result.success(_NumSizes(raw.lower()))
    except ValueError as err:
        return Result.failure(cast_exception(err))


def _decimal_handler(encoded: JsonObj) -> ResultE[DataType]:
    precision: ResultE[int] = JsonUnfolder.optional(
        encoded,
        "precision",
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_int),
    ).map(lambda m: m.value_or(18))
    scale: ResultE[int] = JsonUnfolder.optional(
        encoded,
        "scale",
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_int),
    ).map(lambda m: m.value_or(0))
    return precision.bind(lambda p: scale.map(lambda s: DataType(DecimalType(p, s))))


def _size_map(size: _NumSizes, encoded: JsonObj) -> ResultE[DataType]:
    if size is _NumSizes.EXACT:
        return _decimal_handler(encoded)
    if size is _NumSizes.FLOAT:
        return Result.success(StaticTypes.REAL, Exception).map(DataType)
    if size is _NumSizes.BIG_FLOAT:
        return Result.success(StaticTypes.DOUBLE_PRECISION, Exception).map(DataType)


def num_handler(encoded: JsonObj) -> ResultE[DataType]:
    _size: ResultE[_NumSizes] = JsonUnfolder.optional(
        encoded,
        "size",
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_str).bind(_to_size),
    ).map(lambda m: m.value_or(_NumSizes.FLOAT))
    return _size.bind(lambda s: _size_map(s, encoded))
