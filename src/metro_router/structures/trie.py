"""Prefix tree for autocomplete."""

from dataclasses import dataclass, field

from metro_router.structures.hash_map import HashMap


@dataclass(slots=True)
class _TrieNode[V]:
    children: HashMap[str, "_TrieNode[V]"] = field(default_factory=HashMap)
    # A 1-tuple instead of a bare value, so that ``None`` can be stored as a value too.
    entry: tuple[V] | None = None


class Trie[V]:
    """Tree where each edge is one character, so shared prefixes share nodes.

    Looking up a prefix costs only its length, no matter how many keys are
    stored. That is what makes tries a good fit for autocomplete.

    Complexity (m = key or prefix length, k = number of matches):
        insert, contains: O(m)
        starts_with: O(m + size of the matching subtree)

    Example:
        >>> trie = Trie[int]()
        >>> trie.insert("car", 1)
        >>> trie.insert("cat", 2)
        >>> sorted(trie.starts_with("ca"))
        [1, 2]
    """

    __slots__ = ("_root", "_size")

    def __init__(self) -> None:
        self._root: _TrieNode[V] = _TrieNode()
        self._size = 0

    def insert(self, key: str, value: V) -> None:
        """Store ``value`` under ``key``, replacing any previous value."""
        node = self._root
        for char in key:
            child = node.children.get(char, None)
            if child is None:
                child = _TrieNode()
                node.children[char] = child
            node = child
        if node.entry is None:
            self._size += 1
        node.entry = (value,)

    def starts_with(self, prefix: str) -> list[V]:
        """Return the values of every key that begins with ``prefix``.

        The order of the result is unspecified.
        """
        node = self._find(prefix)
        if node is None:
            return []
        found: list[V] = []
        self._collect(node, found)
        return found

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        node = self._find(key)
        return node is not None and node.entry is not None

    def __len__(self) -> int:
        return self._size

    def _find(self, prefix: str) -> _TrieNode[V] | None:
        node: _TrieNode[V] | None = self._root
        for char in prefix:
            if node is None:
                return None
            node = node.children.get(char, None)
        return node

    def _collect(self, node: _TrieNode[V], found: list[V]) -> None:
        """Depth-first, recursive walk that gathers every value below ``node``."""
        if node.entry is not None:
            found.append(node.entry[0])
        for child in node.children.values():
            self._collect(child, found)
