"""Hash table using separate chaining."""

from collections.abc import Hashable, Iterator

_MAX_LOAD_FACTOR = 0.75


class HashMap[K: Hashable, V]:
    """Mapping from keys to values backed by an array of buckets.

    Each bucket is a small list of ``(key, value)`` pairs. Keys that hash to the
    same bucket (collisions) simply share that list. When the number of entries
    exceeds 75 % of the bucket count, the table doubles and every entry is
    re-hashed, which keeps buckets short.

    Complexity (average, assuming a good hash function):
        get, set, delete, contains: O(1); worst case O(n) if every key collides
        resize: O(n), amortised O(1) per insertion
        iteration: O(n + capacity)

    Example:
        >>> ages = HashMap[str, int]()
        >>> ages["ana"] = 30
        >>> ages["ana"]
        30
    """

    __slots__ = ("_buckets", "_size")

    def __init__(self, capacity: int = 8) -> None:
        if capacity < 1:
            raise ValueError(f"capacity must be positive, got {capacity}")
        self._buckets: list[list[tuple[K, V]]] = [[] for _ in range(capacity)]
        self._size = 0

    @property
    def capacity(self) -> int:
        """Current number of buckets."""
        return len(self._buckets)

    def get[D](self, key: K, default: D) -> V | D:
        """Return the value for ``key``, or ``default`` if it is absent."""
        for stored_key, value in self._bucket_for(key):
            if stored_key == key:
                return value
        return default

    def items(self) -> Iterator[tuple[K, V]]:
        """Iterate over ``(key, value)`` pairs in no particular order."""
        for bucket in self._buckets:
            yield from bucket

    def values(self) -> Iterator[V]:
        """Iterate over values in no particular order."""
        for _, value in self.items():
            yield value

    def __getitem__(self, key: K) -> V:
        for stored_key, value in self._bucket_for(key):
            if stored_key == key:
                return value
        raise KeyError(key)

    def __setitem__(self, key: K, value: V) -> None:
        bucket = self._bucket_for(key)
        for index, (stored_key, _) in enumerate(bucket):
            if stored_key == key:
                bucket[index] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1
        if self._size > _MAX_LOAD_FACTOR * len(self._buckets):
            self._resize(2 * len(self._buckets))

    def __delitem__(self, key: K) -> None:
        bucket = self._bucket_for(key)
        for index, (stored_key, _) in enumerate(bucket):
            if stored_key == key:
                del bucket[index]
                self._size -= 1
                return
        raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        bucket = self._buckets[hash(key) % len(self._buckets)]
        return any(stored_key == key for stored_key, _ in bucket)

    def __iter__(self) -> Iterator[K]:
        for key, _ in self.items():
            yield key

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        entries = ", ".join(f"{key!r}: {value!r}" for key, value in self.items())
        return f"{type(self).__name__}({{{entries}}})"

    def _bucket_for(self, key: K) -> list[tuple[K, V]]:
        return self._buckets[hash(key) % len(self._buckets)]

    def _resize(self, capacity: int) -> None:
        old_entries = list(self.items())
        self._buckets = [[] for _ in range(capacity)]
        for key, value in old_entries:
            self._bucket_for(key).append((key, value))
