import inspect
from collections.abc import Callable
from dataclasses import (
    dataclass,
)
from typing import (
    Generic,
    TypeVar,
)

from fa_purity import (
    FrozenDict,
    PureIter,
    PureIterFactory,
)
from fa_purity.json import (
    JsonUnfolder,
    Primitive,
    UnfoldedFactory,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)
from redshift_client.core.id_objs import (
    ColumnId,
    Identifier,
)

from ._classifier import (
    DuplicateClassifier,
)

_A = TypeVar("_A")
_B = TypeVar("_B")


@dataclass(frozen=True)
class _State(Generic[_A, _B]):
    values: frozenset[_B]
    transform_map: FrozenDict[_A, _B]


def _update(original: FrozenDict[_A, _B], append: FrozenDict[_A, _B]) -> FrozenDict[_A, _B]:
    return FrozenDict(dict(original) | dict(append))


def _append(original: frozenset[_A], append: frozenset[_A]) -> frozenset[_A]:
    return original | append


def _no_duplicate_append(
    state: _State[_A, _B],
    item: _A,
    transform: Callable[[_A], _B],
    next_name: Callable[[int, _B], _B],
) -> _State[_A, _B]:
    result = next_name(2, transform(item))
    if result not in state.values:
        return _State(
            _append(state.values, frozenset({result})),
            _update(state.transform_map, FrozenDict({item: result})),
        )
    new_name = (
        PureIterFactory.from_range(range(3, 21))
        .map(lambda i: next_name(i, transform(item)))
        .find_first(lambda b: b not in state.values)
        .or_else_call(
            lambda: Bug.new(
                "new_name_generation",
                inspect.currentframe(),
                Exception("new name generation limit exceeded"),
                (str(result),),
            ).explode(),
        )
    )
    return _State(
        _append(state.values, frozenset({new_name})),
        _update(state.transform_map, FrozenDict({item: new_name})),
    )


def _duplicates_map(
    original: PureIter[_A],
    duplicates: PureIter[_A],
    transform: Callable[[_A], _B],
    next_name: Callable[[int, _B], _B],
) -> FrozenDict[_A, _B]:
    init: _State[_A, _B] = _State(frozenset(original.map(transform)), FrozenDict({}))
    result = duplicates.reduce(lambda s, i: _no_duplicate_append(s, i, transform, next_name), init)
    return result.transform_map


def _int_to_str(number: int) -> str:
    return str(number)


ColumnPair = tuple[str, ColumnId]


def _id_is_present(column: ColumnPair, items: frozenset[ColumnPair]) -> bool:
    return any(column[1] == i[1] for i in items)


def _detect_duplicates(
    raw_columns: PureIter[str],
    transform: Callable[[str], ColumnId],
) -> frozenset[str]:
    duplicates = DuplicateClassifier.classify(
        _id_is_present,
        raw_columns.map(lambda s: (s, transform(s))),
    ).duplicates
    return frozenset(d[0] for d in duplicates)


@dataclass(frozen=True)
class SingerToColumnMap:
    value: FrozenDict[str, ColumnId]

    def encode(self) -> str:
        raw: FrozenDict[str, Primitive] = FrozenDict(
            {k: v.name.to_str() for k, v in self.value.items()},
        )
        return JsonUnfolder.dumps(UnfoldedFactory.from_dict(raw))


def _raw_to_column_id(raw: str) -> ColumnId:
    return ColumnId(Identifier.new(raw))


def columns_map(column_names: PureIter[str]) -> SingerToColumnMap:
    def _next_name(index: int, column: ColumnId) -> ColumnId:
        return ColumnId(Identifier.new(column.name.to_str() + "_" + _int_to_str(index)))

    duplicates = _detect_duplicates(column_names, _raw_to_column_id)
    the_map = _duplicates_map(
        column_names,
        PureIterFactory.from_list(sorted(duplicates, reverse=True)),
        _raw_to_column_id,
        _next_name,
    )
    result = PureIterFactory.from_list(tuple(the_map.items())).filter(lambda t: t[0] in duplicates)
    return SingerToColumnMap(FrozenDict(dict(result.to_list())))
