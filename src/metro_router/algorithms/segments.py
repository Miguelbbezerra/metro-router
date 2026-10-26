"""Split a sequence into runs of consecutive items sharing a key."""

from collections.abc import Callable, Hashable, Sequence


def split_runs[T](items: Sequence[T], key: Callable[[T], Hashable]) -> list[list[T]]:
    """Group consecutive items whose ``key`` is equal.

    Uses two pointers that define a variable-size sliding window: ``left`` marks
    the start of the current run and ``right`` advances until the key changes,
    at which point the window ``items[left:right]`` is emitted and ``left``
    jumps to ``right``.

    Complexity:
        time O(n); space O(n) for the output

    Example:
        >>> split_runs([1, 1, 2, 1], key=lambda x: x)
        [[1, 1], [2], [1]]
    """
    runs: list[list[T]] = []
    left = 0
    for right in range(1, len(items) + 1):
        if right == len(items) or key(items[right]) != key(items[left]):
            runs.append(list(items[left:right]))
            left = right
    return runs
