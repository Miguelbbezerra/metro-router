"""Binary min-heap stored in a flat array."""

from collections.abc import Iterable
from typing import Any, Protocol


class SupportsLessThan(Protocol):
    """Anything that can be ordered with ``<``."""

    def __lt__(self, other: Any, /) -> bool: ...


class MinHeap[T: SupportsLessThan]:
    """Priority queue that always yields its smallest item first.

    The tree is stored implicitly in a list: the children of index ``i`` are
    ``2i + 1`` and ``2i + 2`` and its parent is ``(i - 1) // 2``.

    Complexity:
        push, pop: O(log n)
        peek, len: O(1)
        construction from n items: O(n) (bottom-up heapify)

    Example:
        >>> heap = MinHeap([3, 1, 2])
        >>> heap.pop()
        1
    """

    __slots__ = ("_items",)

    def __init__(self, items: Iterable[T] = ()) -> None:
        self._items: list[T] = list(items)
        for index in range(len(self._items) // 2 - 1, -1, -1):
            self._sift_down(index)

    def push(self, value: T) -> None:
        """Insert ``value`` keeping the heap property."""
        self._items.append(value)
        self._sift_up(len(self._items) - 1)

    def pop(self) -> T:
        """Remove and return the smallest item.

        Raises:
            IndexError: If the heap is empty.
        """
        if not self._items:
            raise IndexError("pop from empty heap")
        last = self._items.pop()
        if not self._items:
            return last
        smallest, self._items[0] = self._items[0], last
        self._sift_down(0)
        return smallest

    def peek(self) -> T:
        """Return the smallest item without removing it.

        Raises:
            IndexError: If the heap is empty.
        """
        if not self._items:
            raise IndexError("peek from empty heap")
        return self._items[0]

    def __len__(self) -> int:
        return len(self._items)

    def _sift_up(self, index: int) -> None:
        items = self._items
        while index > 0:
            parent = (index - 1) // 2
            if not items[index] < items[parent]:
                break
            items[index], items[parent] = items[parent], items[index]
            index = parent

    def _sift_down(self, index: int) -> None:
        items = self._items
        size = len(items)
        while True:
            smallest = index
            for child in (2 * index + 1, 2 * index + 2):
                if child < size and items[child] < items[smallest]:
                    smallest = child
            if smallest == index:
                return
            items[index], items[smallest] = items[smallest], items[index]
            index = smallest
