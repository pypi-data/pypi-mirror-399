from typing import (
    TypeVar,
)

from arch_lint.dag import (
    DagMap,
)
from arch_lint.graph import (
    FullPathModule,
)

_T = TypeVar("_T")


def _raise_or_return(item: _T | Exception) -> _T:
    if isinstance(item, Exception):
        raise item
    return item


_dag: dict[str, tuple[tuple[str, ...] | str, ...]] = {
    "fluidattacks_target_warehouse": (
        "_cli",
        "executor",
        ("loader", "strategy"),
        ("data_schema", "grouper"),
        ("_s3", "_utils", "_logger"),
    ),
    "fluidattacks_target_warehouse.executor": (
        "_generic",
        ("_input", "_output"),
    ),
    "fluidattacks_target_warehouse.loader": (
        "_loaders",
        "_handlers",
        "_core",
        "_truncate",
    ),
    "fluidattacks_target_warehouse.loader._handlers": (("_records", "_schema", "_state"),),
    "fluidattacks_target_warehouse.loader._handlers._records": (
        "_handler",
        "_stream_records",
    ),
    "fluidattacks_target_warehouse.strategy": (
        ("_only_append", "_recreate_all", "_per_stream"),
        "_move_data",
        "_staging",
        "_core",
    ),
    "fluidattacks_target_warehouse.data_schema": (
        "duplicates",
        "_data_types",
    ),
    "fluidattacks_target_warehouse.data_schema._data_types": (
        "_number",
        "_string",
        "_integer",
    ),
    "fluidattacks_target_warehouse._cli": (
        ("_recreate", "_append"),
        "_decode",
    ),
}


def project_dag() -> DagMap:
    return _raise_or_return(DagMap.new(_dag))


def forbidden_allowlist() -> dict[FullPathModule, frozenset[FullPathModule]]:
    _raw: dict[str, frozenset[str]] = {
        "fa_singer_io.singer.deserializer": frozenset(
            ["fluidattacks_target_warehouse.executor._input"],
        ),
    }
    return {
        FullPathModule.assert_module(k): frozenset(FullPathModule.assert_module(i) for i in v)
        for k, v in _raw.items()
    }
