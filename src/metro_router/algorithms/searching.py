"""Binary search over sorted sequences."""

from collections.abc import Callable, Sequence
from typing import Any, overload

from metro_router.structures import SupportsLessThan


@overload
def lower_bound[T: SupportsLessThan](items: Sequence[T], target: T) -> int: ...
@overload
def lower_bound[T](
    items: Sequence[T], target: SupportsLessThan, *, key: Callable[[T], Any]
) -> int: ...
def lower_bound[T](
    items: Sequence[T], target: Any, *, key: Callable[[T], Any] | None = None
) -> int:
    """Return the first index whose value is not less than ``target``.

    That is the position where ``target`` would be inserted to keep ``items``
    sorted (same as ``bisect.bisect_left``). Every iteration halves the search
    window ``[low, high)``.

    Complexity:
        time O(log n); space O(1)

    Args:
        items: Sequence sorted in ascending order (by ``key`` if given).
        target: Value to look for.
        key: Optional function projecting each item to the compared value.
    """
    low, high = 0, len(items)
    while low < high:
        middle = (low + high) // 2
        value = items[middle] if key is None else key(items[middle])
        if value < target:
            low = middle + 1
        else:
            high = middle
    return low


@overload
def binary_search[T: SupportsLessThan](items: Sequence[T], target: T) -> int | None: ...
@overload
def binary_search[T](
    items: Sequence[T], target: SupportsLessThan, *, key: Callable[[T], Any]
) -> int | None: ...
def binary_search[T](
    items: Sequence[T], target: Any, *, key: Callable[[T], Any] | None = None
) -> int | None:
    """Return the index of an item equal to ``target``, or ``None`` if absent.

    Complexity:
        time O(log n); space O(1)

    Example:
        >>> binary_search([1, 3, 5], 3)
        1
    """
    index = lower_bound(items, target, key=key if key is not None else _identity)
    if index == len(items):
        return None
    value = items[index] if key is None else key(items[index])
    # lower_bound guarantees value >= target, so "not target < value" means equal.
    return None if target < value else index


def _identity(value: Any) -> Any:
    return value
