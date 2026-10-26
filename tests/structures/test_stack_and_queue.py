import pytest
from hypothesis import given
from hypothesis import strategies as st

from metro_router.structures import Queue, Stack


def test_stack_pops_in_lifo_order() -> None:
    stack: Stack[int] = Stack()
    stack.push(1)
    stack.push(2)

    assert stack.pop() == 2
    assert stack.pop() == 1


def test_stack_peek_returns_top_without_removing() -> None:
    stack: Stack[str] = Stack()
    stack.push("x")

    assert stack.peek() == "x"
    assert len(stack) == 1


def test_stack_pop_on_empty_raises_index_error() -> None:
    with pytest.raises(IndexError, match="empty stack"):
        Stack[int]().pop()


def test_stack_peek_on_empty_raises_index_error() -> None:
    with pytest.raises(IndexError, match="empty stack"):
        Stack[int]().peek()


def test_queue_dequeues_in_fifo_order() -> None:
    queue: Queue[int] = Queue()
    queue.enqueue(1)
    queue.enqueue(2)

    assert queue.dequeue() == 1
    assert queue.dequeue() == 2


def test_queue_peek_returns_front_without_removing() -> None:
    queue: Queue[str] = Queue()
    queue.enqueue("first")
    queue.enqueue("second")

    assert queue.peek() == "first"
    assert len(queue) == 2


def test_queue_dequeue_on_empty_raises_index_error() -> None:
    with pytest.raises(IndexError, match="empty queue"):
        Queue[int]().dequeue()


def test_queue_peek_on_empty_raises_index_error() -> None:
    with pytest.raises(IndexError, match="empty queue"):
        Queue[int]().peek()


def test_empty_containers_are_falsy() -> None:
    assert not Stack[int]()
    assert not Queue[int]()


@given(st.lists(st.integers()))
def test_stack_reverses_any_sequence(values: list[int]) -> None:
    stack: Stack[int] = Stack()
    for value in values:
        stack.push(value)

    assert [stack.pop() for _ in values] == values[::-1]


@given(st.lists(st.integers()))
def test_queue_preserves_any_sequence(values: list[int]) -> None:
    queue: Queue[int] = Queue()
    for value in values:
        queue.enqueue(value)

    assert [queue.dequeue() for _ in values] == values
