from __future__ import (
    annotations,
)

from collections.abc import Callable
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    Generic,
    TypeVar,
)

from fa_purity import (
    PureIter,
)

_T = TypeVar("_T")


@dataclass(frozen=True)
class _Private:
    pass


def _append_set(items: frozenset[_T], item: _T) -> frozenset[_T]:
    return frozenset(items | {item})


@dataclass(frozen=True)
class DuplicateClassifier(Generic[_T]):
    _private: _Private = field(repr=False, hash=False, compare=False)
    unique: frozenset[_T]
    duplicates: frozenset[_T]
    is_present: Callable[[_T, frozenset[_T]], bool]

    def append(self, item: _T) -> DuplicateClassifier[_T]:
        if self.is_present(item, self.unique):
            return DuplicateClassifier(
                _Private(),
                self.unique,
                _append_set(self.duplicates, item),
                self.is_present,
            )
        return DuplicateClassifier(
            _Private(),
            _append_set(self.unique, item),
            self.duplicates,
            self.is_present,
        )

    @staticmethod
    def empty(
        is_present: Callable[[_T, frozenset[_T]], bool],
    ) -> DuplicateClassifier[_T]:
        empty: frozenset[_T] = frozenset({})
        return DuplicateClassifier(_Private(), empty, empty, is_present)

    @classmethod
    def classify(
        cls,
        is_present: Callable[[_T, frozenset[_T]], bool],
        items: PureIter[_T],
    ) -> DuplicateClassifier[_T]:
        return items.reduce(lambda s, i: s.append(i), cls.empty(is_present))
