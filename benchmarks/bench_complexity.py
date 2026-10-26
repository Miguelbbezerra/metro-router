"""Measure how running time grows with input size, to see Big O in practice.

Each experiment runs at sizes n, 2n, 4n, ... and prints the time ratio between
consecutive sizes. When n doubles, the expected ratio is about:

    O(1)        → 1x
    O(log n)    → slightly above 1x
    O(n)        → 2x
    O(n log n)  → a bit more than 2x
    O(n²)       → 4x

Run with:  uv run python benchmarks/bench_complexity.py
"""

import random
import time
from collections.abc import Callable
from itertools import pairwise

from metro_router.algorithms import binary_search, merge_sort
from metro_router.structures import HashMap, Queue

SIZES = [2_000, 4_000, 8_000, 16_000]


def best_time(action: Callable[[], object], repeat: int = 3) -> float:
    """Return the fastest of ``repeat`` runs, which filters out noise."""
    timings = []
    for _ in range(repeat):
        start = time.perf_counter()
        action()
        timings.append(time.perf_counter() - start)
    return min(timings)


def drain_queue(n: int) -> Callable[[], object]:
    def run() -> None:
        queue: Queue[int] = Queue()
        for value in range(n):
            queue.enqueue(value)
        while queue:
            queue.dequeue()

    return run


def drain_list_from_front(n: int) -> Callable[[], object]:
    def run() -> None:
        items = list(range(n))
        while items:
            items.pop(0)  # shifts every remaining element

    return run


def linear_lookups(n: int) -> Callable[[], object]:
    items = list(range(n))
    targets = random.sample(items, 200)
    return lambda: [items.index(target) for target in targets]


def binary_lookups(n: int) -> Callable[[], object]:
    items = list(range(n))
    targets = random.sample(items, 200)
    return lambda: [binary_search(items, target) for target in targets]


def hash_map_lookups(n: int) -> Callable[[], object]:
    table: HashMap[int, int] = HashMap()
    for value in range(n):
        table[value] = value
    targets = random.sample(range(n), 200)
    return lambda: [table[target] for target in targets]


def sort_random(n: int) -> Callable[[], object]:
    values = [random.random() for _ in range(n)]
    return lambda: merge_sort(values)


EXPERIMENTS: list[tuple[str, str, Callable[[int], Callable[[], object]]]] = [
    ("Queue: n enqueue + n dequeue", "O(n)", drain_queue),
    ("list.pop(0) n times", "O(n²)", drain_list_from_front),
    ("200 linear searches", "O(n) each", linear_lookups),
    ("200 binary searches", "O(log n) each", binary_lookups),
    ("200 HashMap lookups", "O(1) each", hash_map_lookups),
    ("merge_sort", "O(n log n)", sort_random),
]


def main() -> None:
    random.seed(42)
    header = f"{'experiment':<30} {'expected':<14}" + "".join(f"{n:>12,}" for n in SIZES)
    print(header)
    print("-" * len(header))
    for name, expected, build in EXPERIMENTS:
        timings = [best_time(build(n)) for n in SIZES]
        cells = [f"{timings[0] * 1000:>10.2f}ms"]
        cells += [f"{later / earlier:>11.1f}x" for earlier, later in pairwise(timings)]
        print(f"{name:<30} {expected:<14}" + "".join(cells))
    print("\nFirst column: time at n = 2,000. Next columns: ratio vs. the previous size.")


if __name__ == "__main__":
    main()
