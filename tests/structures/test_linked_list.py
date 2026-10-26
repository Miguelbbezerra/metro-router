import pytest
from hypothesis import given
from hypothesis import strategies as st

from metro_router.structures import LinkedList


def test_new_list_is_empty() -> None:
    linked: LinkedList[int] = LinkedList()

    assert len(linked) == 0
    assert not linked


def test_append_keeps_insertion_order() -> None:
    linked: LinkedList[str] = LinkedList()

    linked.append("a")
    linked.append("b")

    assert list(linked) == ["a", "b"]


def test_prepend_inserts_at_the_front() -> None:
    linked = LinkedList([2, 3])

    linked.prepend(1)

    assert list(linked) == [1, 2, 3]


def test_pop_left_removes_the_first_item() -> None:
    linked = LinkedList([1, 2, 3])

    assert linked.pop_left() == 1
    assert list(linked) == [2, 3]


def test_pop_left_on_last_item_resets_tail() -> None:
    linked = LinkedList([1])

    linked.pop_left()
    linked.append(2)

    assert list(linked) == [2]


def test_pop_left_on_empty_list_raises_index_error() -> None:
    with pytest.raises(IndexError, match="empty"):
        LinkedList[int]().pop_left()


def test_peek_left_returns_first_item_without_removing() -> None:
    linked = LinkedList([7, 8])

    assert linked.peek_left() == 7
    assert len(linked) == 2


def test_peek_left_on_empty_list_raises_index_error() -> None:
    with pytest.raises(IndexError, match="empty"):
        LinkedList[int]().peek_left()


def test_repr_shows_items() -> None:
    assert repr(LinkedList([1, 2])) == "LinkedList([1, 2])"


@given(st.lists(st.integers()))
def test_behaves_like_list_for_append_and_pop_left(values: list[int]) -> None:
    linked: LinkedList[int] = LinkedList()
    for value in values:
        linked.append(value)

    popped = [linked.pop_left() for _ in range(len(values))]

    assert popped == values
    assert len(linked) == 0
