from enum import (
    Enum,
)

from fa_purity import (
    Maybe,
    Result,
    ResultE,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitiveUnfolder,
    JsonUnfolder,
    Unfolder,
)
from redshift_client.core.data_type.core import (
    DataType,
    PrecisionType,
    PrecisionTypes,
    StaticTypes,
)

from fluidattacks_target_warehouse._utils import (
    cast_exception,
)


class _MetaType(Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"


class _StringFormat(Enum):
    DATE_TIME = "date-time"
    TIME = "time"
    DATE = "date"


def _to_meta_type(raw: str) -> ResultE[_MetaType]:
    try:
        return Result.success(_MetaType(raw.lower()))
    except ValueError as err:
        return Result.failure(cast_exception(err))


def _to_str_format(raw: str) -> ResultE[_StringFormat]:
    try:
        return Result.success(_StringFormat(raw.lower()))
    except ValueError as err:
        return Result.failure(cast_exception(err))


def _format_handler(str_format: _StringFormat, encoded: JsonObj) -> ResultE[DataType]:
    timezone: ResultE[bool] = JsonUnfolder.optional(
        encoded,
        "timezone",
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_bool),
    ).map(lambda m: m.value_or(False))
    if str_format is _StringFormat.DATE_TIME:
        return timezone.map(lambda t: StaticTypes.TIMESTAMPTZ if t else StaticTypes.TIMESTAMP).map(
            DataType,
        )
    if str_format is _StringFormat.TIME:
        return timezone.map(
            lambda t: StaticTypes.TIMETZ if t else StaticTypes.TIME,
        ).map(DataType)
    if str_format is _StringFormat.DATE:
        return Result.success(StaticTypes.DATE, Exception).map(lambda x: DataType(x))


def _string_handler(encoded: JsonObj) -> ResultE[DataType]:
    precision: ResultE[int] = JsonUnfolder.optional(
        encoded,
        "precision",
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_int),
    ).map(lambda m: m.value_or(256))
    meta_type: ResultE[_MetaType] = JsonUnfolder.optional(
        encoded,
        "metatype",
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_str).bind(_to_meta_type),
    ).map(lambda m: m.value_or(_MetaType.DYNAMIC))
    p_type = meta_type.map(
        lambda m: PrecisionTypes.CHAR if m is _MetaType.STATIC else PrecisionTypes.VARCHAR,
    )
    return p_type.bind(lambda t: precision.map(lambda p: PrecisionType(t, p))).map(DataType)


def string_format_handler(encoded: JsonObj) -> ResultE[DataType]:
    _format: ResultE[Maybe[_StringFormat]] = JsonUnfolder.optional(
        encoded,
        "format",
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_str).bind(_to_str_format),
    )
    return _format.bind(
        lambda f: f.map(lambda sf: _format_handler(sf, encoded)).or_else_call(
            lambda: _string_handler(encoded),
        ),
    )
