"""FIFO queue backed by a linked list."""

from metro_router.structures.linked_list import LinkedList


class Queue[T]:
    """First-in, first-out container.

    Items enter at the tail of a linked list and leave from the head. A plain
    Python ``list`` would make ``dequeue`` O(n), because ``list.pop(0)`` shifts
    every remaining element.

    Complexity:
        enqueue, dequeue, peek, len: O(1)
    """

    __slots__ = ("_items",)

    def __init__(self) -> None:
        self._items: LinkedList[T] = LinkedList()

    def enqueue(self, value: T) -> None:
        """Add ``value`` to the back of the queue."""
        self._items.append(value)

    def dequeue(self) -> T:
        """Remove and return the front item.

        Raises:
            IndexError: If the queue is empty.
        """
        if not self._items:
            raise IndexError("dequeue from empty queue")
        return self._items.pop_left()

    def peek(self) -> T:
        """Return the front item without removing it.

        Raises:
            IndexError: If the queue is empty.
        """
        if not self._items:
            raise IndexError("peek from empty queue")
        return self._items.peek_left()

    def __len__(self) -> int:
        return len(self._items)
