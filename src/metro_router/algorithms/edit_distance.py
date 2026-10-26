"""Levenshtein edit distance with dynamic programming."""


def levenshtein(source: str, target: str) -> int:
    """Return the minimum number of single-character edits turning ``source`` into ``target``.

    An edit is an insertion, a deletion or a substitution. ``table[i][j]`` is the
    distance between the first ``i`` characters of ``source`` and the first ``j``
    of ``target``; each cell only depends on the previous row, so only two rows
    are kept in memory.

    Complexity:
        time O(n * m); space O(min(n, m))

    Example:
        >>> levenshtein("kitten", "sitting")
        3
    """
    if len(source) < len(target):
        source, target = target, source
    previous = list(range(len(target) + 1))
    for i, source_char in enumerate(source, start=1):
        current = [i]
        for j, target_char in enumerate(target, start=1):
            current.append(
                min(
                    previous[j] + 1,  # deletion
                    current[j - 1] + 1,  # insertion
                    previous[j - 1] + (source_char != target_char),  # substitution
                )
            )
        previous = current
    return previous[-1]
