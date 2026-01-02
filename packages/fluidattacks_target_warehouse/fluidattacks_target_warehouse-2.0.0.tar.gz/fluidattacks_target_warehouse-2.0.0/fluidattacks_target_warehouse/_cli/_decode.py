from typing import (
    IO,
)

from fa_purity import (
    FrozenDict,
    Result,
    ResultE,
)
from fa_purity.json import (
    JsonPrimitiveUnfolder,
    JsonUnfolder,
    JsonValueFactory,
    Unfolder,
)
from redshift_client.core.id_objs import (
    ColumnId,
    Identifier,
)

from fluidattacks_target_warehouse.data_schema.duplicates import (
    SingerToColumnMap,
)


def _decode_columns_map(raw: FrozenDict[str, str]) -> SingerToColumnMap:
    return SingerToColumnMap(FrozenDict({k: ColumnId(Identifier.new(v)) for k, v in raw.items()}))


def decode_columns_map(raw: IO[str] | None) -> ResultE[SingerToColumnMap]:
    if raw is not None:
        return (
            JsonValueFactory.load(raw)
            .bind(Unfolder.to_json)
            .bind(
                lambda j: JsonUnfolder.map_values(
                    j,
                    lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_str),
                ),
            )
            .map(_decode_columns_map)
        )
    return Result.success(SingerToColumnMap(FrozenDict({})))
