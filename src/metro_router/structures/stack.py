"""LIFO stack backed by a linked list."""

from metro_router.structures.linked_list import LinkedList


class Stack[T]:
    """Last-in, first-out container.

    Pushing and popping both happen at the head of a linked list.

    Complexity:
        push, pop, peek, len: O(1)
    """

    __slots__ = ("_items",)

    def __init__(self) -> None:
        self._items: LinkedList[T] = LinkedList()

    def push(self, value: T) -> None:
        """Put ``value`` on top of the stack."""
        self._items.prepend(value)

    def pop(self) -> T:
        """Remove and return the top item.

        Raises:
            IndexError: If the stack is empty.
        """
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop_left()

    def peek(self) -> T:
        """Return the top item without removing it.

        Raises:
            IndexError: If the stack is empty.
        """
        if not self._items:
            raise IndexError("peek from empty stack")
        return self._items.peek_left()

    def __len__(self) -> int:
        return len(self._items)
