from fa_purity import (
    FrozenDict,
    PureIterFactory,
)
from redshift_client.core.id_objs import (
    ColumnId,
    Identifier,
)

from fluidattacks_target_warehouse.data_schema.duplicates import (
    SingerToColumnMap,
    columns_map,
)


def test_duplicates() -> None:
    columns_1 = PureIterFactory.from_list(("foo", "Foo", "FOO", "fOO"))
    expected = FrozenDict(  # keys in alphabetical order i.e. capitals afeter lowercase
        {
            "fOO": ColumnId(Identifier.new("foo_2")),
            "Foo": ColumnId(Identifier.new("foo_3")),
            "FOO": ColumnId(Identifier.new("foo_4")),
        },
    )
    assert columns_map(columns_1) == SingerToColumnMap(expected)
    columns_2 = PureIterFactory.from_list(("foo", "FOO", "foo_3", "fOO", "foo_5", "Foo", "foo_2"))
    expected = FrozenDict(
        {
            "fOO": ColumnId(Identifier.new("foo_4")),
            "Foo": ColumnId(Identifier.new("foo_6")),
            "FOO": ColumnId(Identifier.new("foo_7")),
        },
    )
    assert columns_map(columns_2) == SingerToColumnMap(expected)
    columns_3 = PureIterFactory.from_list(
        (
            "FOO",
            "foo",
            "fOO",
        ),
    )
    expected = FrozenDict(
        {
            "foo": ColumnId(Identifier.new("foo_2")),
            "fOO": ColumnId(Identifier.new("foo_3")),
        },
    )
    assert columns_map(columns_3) == SingerToColumnMap(expected)
