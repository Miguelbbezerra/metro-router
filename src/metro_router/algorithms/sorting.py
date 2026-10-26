"""Merge sort: recursive divide and conquer."""

from collections.abc import Callable, Sequence
from typing import Any, overload

from metro_router.structures import SupportsLessThan


@overload
def merge_sort[T: SupportsLessThan](items: Sequence[T]) -> list[T]: ...
@overload
def merge_sort[T](items: Sequence[T], *, key: Callable[[T], SupportsLessThan]) -> list[T]: ...
def merge_sort[T](
    items: Sequence[T], *, key: Callable[[T], SupportsLessThan] | None = None
) -> list[T]:
    """Return a new list with ``items`` in ascending order.

    The sequence is split in half, each half is sorted recursively, and the two
    sorted halves are merged with two pointers. The sort is stable: items with
    equal keys keep their original relative order.

    Complexity:
        time O(n log n) in every case; space O(n)

    Args:
        items: Sequence to sort. It is not modified.
        key: Optional function computing the value to compare, like ``sorted``.

    Example:
        >>> merge_sort(["bb", "a"], key=len)
        ['a', 'bb']
    """
    # Each key is computed once, then carried alongside its item.
    project = key if key is not None else _identity
    keyed = [(project(item), item) for item in items]
    return [item for _, item in _merge_sort(keyed)]


def _merge_sort[T](keyed: list[tuple[SupportsLessThan, T]]) -> list[tuple[SupportsLessThan, T]]:
    if len(keyed) <= 1:
        return keyed
    middle = len(keyed) // 2
    return _merge(_merge_sort(keyed[:middle]), _merge_sort(keyed[middle:]))


def _merge[T](
    left: list[tuple[SupportsLessThan, T]], right: list[tuple[SupportsLessThan, T]]
) -> list[tuple[SupportsLessThan, T]]:
    merged: list[tuple[SupportsLessThan, T]] = []
    i = j = 0
    while i < len(left) and j < len(right):
        # Taking from the left on ties is what makes the sort stable.
        if right[j][0] < left[i][0]:
            merged.append(right[j])
            j += 1
        else:
            merged.append(left[i])
            i += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def _identity(value: Any) -> Any:
    return value
