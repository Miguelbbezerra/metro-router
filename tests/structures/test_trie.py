from hypothesis import given
from hypothesis import strategies as st

from metro_router.structures import Trie


def test_starts_with_returns_values_sharing_the_prefix() -> None:
    trie: Trie[str] = Trie()
    trie.insert("santana", "Santana")
    trie.insert("santa cruz", "Santa Cruz")
    trie.insert("se", "Sé")

    assert sorted(trie.starts_with("sant")) == ["Santa Cruz", "Santana"]


def test_starts_with_unknown_prefix_returns_empty_list() -> None:
    trie: Trie[int] = Trie()
    trie.insert("abc", 1)

    assert trie.starts_with("x") == []


def test_empty_prefix_returns_every_value() -> None:
    trie: Trie[int] = Trie()
    trie.insert("a", 1)
    trie.insert("b", 2)

    assert sorted(trie.starts_with("")) == [1, 2]


def test_contains_matches_whole_keys_only() -> None:
    trie: Trie[int] = Trie()
    trie.insert("santana", 1)

    assert "santana" in trie
    assert "santa" not in trie
    assert "santanas" not in trie


def test_inserting_same_key_replaces_value_without_growing() -> None:
    trie: Trie[int] = Trie()
    trie.insert("key", 1)
    trie.insert("key", 2)

    assert trie.starts_with("key") == [2]
    assert len(trie) == 1


@given(st.lists(st.text(alphabet="abc", max_size=5)), st.text(alphabet="abc", max_size=3))
def test_matches_filtering_with_startswith(words: list[str], prefix: str) -> None:
    trie: Trie[str] = Trie()
    for word in words:
        trie.insert(word, word)

    expected = sorted({word for word in words if word.startswith(prefix)})

    assert sorted(trie.starts_with(prefix)) == expected
