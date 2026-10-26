import pytest
from hypothesis import given
from hypothesis import strategies as st

from metro_router.structures import MinHeap


def test_pop_returns_smallest_item() -> None:
    heap = MinHeap([5, 1, 3])

    assert heap.pop() == 1


def test_push_then_peek_returns_new_minimum() -> None:
    heap = MinHeap([5, 3])

    heap.push(2)

    assert heap.peek() == 2
    assert len(heap) == 3


def test_tuples_are_ordered_by_first_element_then_next() -> None:
    heap = MinHeap([(2, "b"), (1, "z"), (2, "a")])

    assert [heap.pop() for _ in range(3)] == [(1, "z"), (2, "a"), (2, "b")]


def test_pop_on_empty_heap_raises_index_error() -> None:
    with pytest.raises(IndexError, match="empty heap"):
        MinHeap[int]().pop()


def test_peek_on_empty_heap_raises_index_error() -> None:
    with pytest.raises(IndexError, match="empty heap"):
        MinHeap[int]().peek()


def test_empty_heap_is_falsy() -> None:
    assert not MinHeap[int]()


@given(st.lists(st.integers()))
def test_popping_everything_yields_sorted_order(values: list[int]) -> None:
    heap: MinHeap[int] = MinHeap()
    for value in values:
        heap.push(value)

    assert [heap.pop() for _ in values] == sorted(values)


@given(st.lists(st.integers()))
def test_heapify_constructor_matches_sorted(values: list[int]) -> None:
    heap = MinHeap(values)

    assert [heap.pop() for _ in values] == sorted(values)
