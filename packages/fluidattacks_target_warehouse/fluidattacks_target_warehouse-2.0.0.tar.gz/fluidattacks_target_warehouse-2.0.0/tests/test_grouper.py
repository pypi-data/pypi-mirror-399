import pytest
from fa_purity import (
    Cmd,
    FrozenList,
    PureIterFactory,
    Stream,
    Unsafe,
)
from fa_purity.json import (
    JsonValueFactory,
    Unfolder,
)
from fa_singer_io.json_schema import (
    JSchemaFactory,
)
from fa_singer_io.singer import (
    SingerMessage,
    SingerRecord,
    SingerSchema,
)

from fluidattacks_target_warehouse.grouper import (
    Grouper,
    PackagedSinger,
)


def _mock_record(stream: str) -> SingerRecord:
    return SingerRecord(
        stream,
        JsonValueFactory.from_any({"foo": 123})
        .bind(lambda j: Unfolder.to_json(j))
        .alt(Unsafe.raise_exception)
        .to_union(),
        None,
    )


def _mock_schema(stream: str) -> SingerSchema:
    return (
        SingerSchema.new(stream, JSchemaFactory.datetime_schema(), frozenset(), None)
        .alt(Unsafe.raise_exception)
        .to_union()
    )


def _equal_package(item_1: PackagedSinger, item_2: PackagedSinger) -> bool:
    return item_1.map(
        lambda p: item_2.map(
            lambda p2: p.to_list() == p2.to_list(),
            lambda _: False,
            lambda _: False,
        ),
        lambda s: item_2.map(
            lambda _: False,
            lambda s2: s == s2,
            lambda _: False,
        ),
        lambda s: item_2.map(lambda _: False, lambda _: False, lambda s2: s == s2),
    )


def test_grouper() -> None:
    mock_record_size = Grouper._record_size(_mock_record("foo"))  # noqa: SLF001
    # for allow testing the inners of the package
    _mock_stream: FrozenList[SingerMessage] = (
        SingerMessage.from_schema(_mock_schema("stream_1")),
        SingerMessage.from_schema(_mock_schema("stream_2")),
        SingerMessage.from_schema(_mock_schema("stream_3")),
        # ---
        SingerMessage.from_record(_mock_record("stream_1")),
        SingerMessage.from_record(_mock_record("stream_2")),
        SingerMessage.from_record(_mock_record("stream_2")),
        SingerMessage.from_record(_mock_record("stream_1")),
        SingerMessage.from_record(_mock_record("stream_3")),
        SingerMessage.from_record(_mock_record("stream_2")),
        SingerMessage.from_record(_mock_record("stream_1")),
    )
    mock_stream: Stream[SingerMessage] = Unsafe.stream_from_cmd(
        Cmd.wrap_impure(lambda: iter(_mock_stream)),
    )

    def assert_result(result: FrozenList[PackagedSinger]) -> None:
        expected = (
            PackagedSinger.new(_mock_schema("stream_1")),
            PackagedSinger.new(_mock_schema("stream_2")),
            PackagedSinger.new(_mock_schema("stream_3")),
            PackagedSinger.new(
                PureIterFactory.from_list((_mock_record("stream_2"), _mock_record("stream_2"))),
            ),
            PackagedSinger.new(
                PureIterFactory.from_list((_mock_record("stream_1"), _mock_record("stream_1"))),
            ),
        )
        equal_pkgs = 4
        for n, e in enumerate(expected):
            if n <= equal_pkgs:
                assert _equal_package(result[n], e)
        last_records = frozenset(
            (
                (_mock_record("stream_1"),),
                (_mock_record("stream_2"),),
                (_mock_record("stream_3"),),
            ),
        )
        assert last_records == frozenset(
            PureIterFactory.from_list(result[5:]).map(
                lambda p: p.map(
                    lambda i: i.to_list(),
                    lambda _: Unsafe.raise_exception(ValueError("unexpected singer schema")),
                    lambda _: Unsafe.raise_exception(ValueError("unexpected singer schema")),
                ),
            ),
        )
        expected_len = 8
        assert len(result) == expected_len

    with pytest.raises(SystemExit):
        Grouper.new(mock_record_size * 2).bind(
            lambda g: g.group_records(mock_stream).to_list(),
        ).map(assert_result).compute()
