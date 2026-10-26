"""Singly linked list with O(1) operations at both ends."""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass


@dataclass(slots=True)
class _Node[T]:
    value: T
    next: "_Node[T] | None" = None


class LinkedList[T]:
    """Singly linked list keeping references to both head and tail.

    Complexity:
        append, prepend, pop_left, peek_left, len: O(1)
        iteration: O(n)

    Example:
        >>> items = LinkedList([1, 2])
        >>> items.append(3)
        >>> list(items)
        [1, 2, 3]
    """

    __slots__ = ("_head", "_size", "_tail")

    def __init__(self, items: Iterable[T] = ()) -> None:
        self._head: _Node[T] | None = None
        self._tail: _Node[T] | None = None
        self._size = 0
        for item in items:
            self.append(item)

    def append(self, value: T) -> None:
        """Add ``value`` to the end of the list."""
        node = _Node(value)
        if self._tail is None:
            self._head = node
        else:
            self._tail.next = node
        self._tail = node
        self._size += 1

    def prepend(self, value: T) -> None:
        """Add ``value`` to the front of the list."""
        self._head = _Node(value, self._head)
        if self._tail is None:
            self._tail = self._head
        self._size += 1

    def pop_left(self) -> T:
        """Remove and return the first item.

        Raises:
            IndexError: If the list is empty.
        """
        if self._head is None:
            raise IndexError("pop from empty linked list")
        node = self._head
        self._head = node.next
        if self._head is None:
            self._tail = None
        self._size -= 1
        return node.value

    def peek_left(self) -> T:
        """Return the first item without removing it.

        Raises:
            IndexError: If the list is empty.
        """
        if self._head is None:
            raise IndexError("peek from empty linked list")
        return self._head.value

    def __iter__(self) -> Iterator[T]:
        node = self._head
        while node is not None:
            yield node.value
            node = node.next

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"{type(self).__name__}({list(self)!r})"
