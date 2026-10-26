"""Find stations from what the user typed."""

from collections.abc import Iterable

from metro_router.algorithms import binary_search, levenshtein, merge_sort
from metro_router.errors import StationNotFoundError
from metro_router.structures import Trie
from metro_router.text import normalize


class StationIndex:
    """Lookup structure over station names, tolerant to accents and typos.

    Three structures, each picked for one job:

    * a sorted array of normalised names + binary search for exact lookup,
    * a trie for prefix autocomplete,
    * Levenshtein distance for "did you mean?" suggestions.

    Complexity (n stations, m = query length, L = average name length):
        build: O(n log n)
        resolve: O(m log n) on a hit, plus suggestions on a miss
        autocomplete: O(m + k log k) for k matches
        suggest: O(n * m * L)
    """

    __slots__ = ("_keys", "_names", "_trie")

    def __init__(self, names: Iterable[str]) -> None:
        entries = merge_sort([(normalize(name), name) for name in names], key=lambda e: e[0])
        self._keys = [key for key, _ in entries]
        self._names = [name for _, name in entries]
        self._trie: Trie[str] = Trie()
        for key, name in entries:
            self._trie.insert(key, name)

    def sorted_names(self) -> list[str]:
        """Return every station name in alphabetical order, ignoring accents."""
        return list(self._names)

    def resolve(self, query: str) -> str:
        """Return the official station name matching ``query``.

        Raises:
            StationNotFoundError: If nothing matches; it carries suggestions.
        """
        index = binary_search(self._keys, normalize(query))
        if index is None:
            raise StationNotFoundError(query.strip(), self.suggest(query))
        return self._names[index]

    def autocomplete(self, prefix: str, limit: int = 10) -> list[str]:
        """Return up to ``limit`` station names starting with ``prefix``, sorted."""
        matches = self._trie.starts_with(normalize(prefix))
        return merge_sort(matches, key=normalize)[:limit]

    def suggest(self, query: str, limit: int = 3) -> list[str]:
        """Return up to ``limit`` names closest to ``query`` by edit distance.

        Only names within a distance proportional to the query length are
        considered, so random input yields no suggestions.
        """
        key = normalize(query)
        max_distance = max(2, len(key) // 3)
        scored = [
            (distance, name)
            for stored, name in zip(self._keys, self._names, strict=True)
            if (distance := levenshtein(key, stored)) <= max_distance
        ]
        return [name for _, name in merge_sort(scored, key=lambda pair: pair[0])[:limit]]
