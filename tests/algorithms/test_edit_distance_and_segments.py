from itertools import pairwise

import pytest
from hypothesis import given
from hypothesis import strategies as st

from metro_router.algorithms import levenshtein, split_runs


@pytest.mark.parametrize(
    ("source", "target", "expected"),
    [
        ("", "", 0),
        ("abc", "", 3),
        ("", "abc", 3),
        ("kitten", "sitting", 3),
        ("paraiso", "paraizo", 1),
        ("se", "sé", 1),
        ("flaw", "lawn", 2),
    ],
)
def test_levenshtein_known_distances(source: str, target: str, expected: int) -> None:
    assert levenshtein(source, target) == expected


words = st.text(alphabet="abcd", max_size=8)


@given(words, words)
def test_levenshtein_is_symmetric(source: str, target: str) -> None:
    assert levenshtein(source, target) == levenshtein(target, source)


@given(words)
def test_levenshtein_of_identical_strings_is_zero(word: str) -> None:
    assert levenshtein(word, word) == 0


@given(words, words)
def test_levenshtein_is_bounded_by_longer_length(source: str, target: str) -> None:
    assert levenshtein(source, target) <= max(len(source), len(target))


def test_split_runs_groups_consecutive_equal_keys() -> None:
    hops = [("A", "1"), ("B", "1"), ("C", "2"), ("D", "1")]

    runs = split_runs(hops, key=lambda hop: hop[1])

    assert runs == [[("A", "1"), ("B", "1")], [("C", "2")], [("D", "1")]]


def test_split_runs_of_empty_sequence_is_empty() -> None:
    assert split_runs([], key=str) == []


@given(st.lists(st.integers(0, 2)))
def test_split_runs_concatenates_back_to_input(values: list[int]) -> None:
    runs = split_runs(values, key=lambda value: value)

    assert [value for run in runs for value in run] == values
    assert all(len(set(run)) == 1 for run in runs)
    assert all(left[-1] != right[0] for left, right in pairwise(runs))
