import bisect

import pytest
from hypothesis import given
from hypothesis import strategies as st

from metro_router.algorithms import binary_search, lower_bound, merge_sort


def test_merge_sort_orders_numbers() -> None:
    assert merge_sort([3, 1, 2]) == [1, 2, 3]


def test_merge_sort_accepts_key_function() -> None:
    assert merge_sort(["bb", "a", "ccc"], key=len) == ["a", "bb", "ccc"]


def test_merge_sort_is_stable() -> None:
    pairs = [("b", 1), ("a", 1), ("c", 0)]

    assert merge_sort(pairs, key=lambda pair: pair[1]) == [("c", 0), ("b", 1), ("a", 1)]


def test_merge_sort_does_not_mutate_input() -> None:
    original = [2, 1]

    merge_sort(original)

    assert original == [2, 1]


@given(st.lists(st.integers()))
def test_merge_sort_matches_builtin_sorted(values: list[int]) -> None:
    assert merge_sort(values) == sorted(values)


@pytest.mark.parametrize(
    ("target", "expected"),
    [(1, 0), (5, 2), (9, 4), (0, None), (4, None), (10, None)],
)
def test_binary_search_finds_index_or_none(target: int, expected: int | None) -> None:
    assert binary_search([1, 3, 5, 7, 9], target) == expected


def test_binary_search_with_key_compares_projected_values() -> None:
    words = ["a", "bb", "ccc"]

    assert binary_search(words, 2, key=len) == 1


@given(st.lists(st.integers(-50, 50)), st.integers(-60, 60))
def test_lower_bound_matches_bisect_left(values: list[int], target: int) -> None:
    ordered = sorted(values)

    assert lower_bound(ordered, target) == bisect.bisect_left(ordered, target)


@given(st.lists(st.integers(-50, 50)), st.integers(-60, 60))
def test_binary_search_agrees_with_membership(values: list[int], target: int) -> None:
    ordered = sorted(values)

    index = binary_search(ordered, target)

    if target in ordered:
        assert index is not None
        assert ordered[index] == target
    else:
        assert index is None
