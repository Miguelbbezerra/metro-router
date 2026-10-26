import pytest
from hypothesis import given
from hypothesis import strategies as st

from metro_router.structures import HashMap


def test_set_then_get_returns_value() -> None:
    table: HashMap[str, int] = HashMap()

    table["a"] = 1

    assert table["a"] == 1


def test_setting_existing_key_overwrites_without_growing() -> None:
    table: HashMap[str, int] = HashMap()

    table["a"] = 1
    table["a"] = 2

    assert table["a"] == 2
    assert len(table) == 1


def test_missing_key_raises_key_error() -> None:
    with pytest.raises(KeyError):
        HashMap[str, int]()["missing"]


def test_get_returns_default_for_missing_key() -> None:
    assert HashMap[str, int]().get("missing", 0) == 0


def test_delete_removes_key() -> None:
    table: HashMap[str, int] = HashMap()
    table["a"] = 1

    del table["a"]

    assert "a" not in table
    assert len(table) == 0


def test_delete_missing_key_raises_key_error() -> None:
    with pytest.raises(KeyError):
        del HashMap[str, int]()["missing"]


def test_grows_beyond_initial_capacity() -> None:
    table: HashMap[int, int] = HashMap(capacity=2)

    for number in range(100):
        table[number] = number * number

    assert len(table) == 100
    assert table[99] == 9801
    assert table.capacity > 2


def test_colliding_keys_are_stored_separately() -> None:
    # In CPython hash(-1) == hash(-2), so both land in the same bucket.
    table: HashMap[int, str] = HashMap()

    table[-1] = "minus one"
    table[-2] = "minus two"

    assert table[-1] == "minus one"
    assert table[-2] == "minus two"


def test_items_keys_and_values_iterate_all_entries() -> None:
    table: HashMap[str, int] = HashMap()
    table["a"] = 1
    table["b"] = 2

    assert sorted(table.items()) == [("a", 1), ("b", 2)]
    assert sorted(table) == ["a", "b"]
    assert sorted(table.values()) == [1, 2]


def test_repr_lists_entries() -> None:
    table: HashMap[str, int] = HashMap()
    table["a"] = 1

    assert repr(table) == "HashMap({'a': 1})"


def test_capacity_must_be_positive() -> None:
    with pytest.raises(ValueError, match="capacity"):
        HashMap[str, int](capacity=0)


operations = st.lists(
    st.tuples(st.sampled_from(["set", "delete"]), st.integers(-20, 20), st.integers()),
)


@given(operations)
def test_behaves_like_dict_under_random_operations(ops: list[tuple[str, int, int]]) -> None:
    table: HashMap[int, int] = HashMap(capacity=1)
    oracle: dict[int, int] = {}

    for action, key, value in ops:
        if action == "set":
            table[key] = value
            oracle[key] = value
        elif key in oracle:
            del table[key]
            del oracle[key]

    assert dict(table.items()) == oracle
    assert len(table) == len(oracle)
