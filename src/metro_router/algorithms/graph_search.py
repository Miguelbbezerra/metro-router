"""Graph traversals: BFS, DFS and Dijkstra.

Every function receives the graph as a ``neighbors`` callable instead of a
concrete class, so the same code works for any graph shape, including implicit
graphs that are never fully built in memory.
"""

from collections.abc import Callable, Hashable, Iterable
from itertools import count

from metro_router.structures import HashMap, MinHeap, Queue, Stack

type Neighbors[N] = Callable[[N], Iterable[N]]
type WeightedNeighbors[N] = Callable[[N], Iterable[tuple[N, float]]]


def bfs_path[N: Hashable](start: N, goal: N, neighbors: Neighbors[N]) -> list[N] | None:
    """Return a path from ``start`` to ``goal`` with the fewest edges, or ``None``.

    Breadth-first search explores nodes in waves of increasing distance using a
    FIFO queue, so the first time ``goal`` is reached is via a shortest path.

    Complexity:
        time O(V + E); space O(V)
    """
    parents: HashMap[N, N | None] = HashMap()
    parents[start] = None
    frontier: Queue[N] = Queue()
    frontier.enqueue(start)
    while frontier:
        node = frontier.dequeue()
        if node == goal:
            return _rebuild_path(parents, goal)
        for neighbor in neighbors(node):
            if neighbor not in parents:
                parents[neighbor] = node
                frontier.enqueue(neighbor)
    return None


def reachable[N: Hashable](start: N, neighbors: Neighbors[N]) -> set[N]:
    """Return every node reachable from ``start``, including itself.

    Iterative depth-first search with an explicit stack. Unlike the recursive
    version it cannot hit Python's recursion limit on long paths.

    Complexity:
        time O(V + E); space O(V)
    """
    visited: set[N] = set()
    pending: Stack[N] = Stack()
    pending.push(start)
    while pending:
        node = pending.pop()
        if node in visited:
            continue
        visited.add(node)
        for neighbor in neighbors(node):
            if neighbor not in visited:
                pending.push(neighbor)
    return visited


def dijkstra_path[N: Hashable](
    start: N, is_goal: Callable[[N], bool], neighbors: WeightedNeighbors[N]
) -> tuple[float, list[N]] | None:
    """Return ``(cost, path)`` of the cheapest path to any goal node, or ``None``.

    The min-heap always yields the unexplored node with the lowest known cost.
    Stale heap entries (a node pushed again after a cheaper route was found)
    are skipped when popped, instead of being updated in place.

    Complexity:
        time O((V + E) log V); space O(V + E)

    Raises:
        ValueError: If an edge with negative weight is found, since Dijkstra's
            greedy choice is only correct for non-negative weights.
    """
    best: HashMap[N, float] = HashMap()
    best[start] = 0.0
    parents: HashMap[N, N | None] = HashMap()
    parents[start] = None
    # The counter breaks ties, so nodes themselves never need to be comparable.
    tie_breaker = count()
    frontier: MinHeap[tuple[float, int, N]] = MinHeap([(0.0, next(tie_breaker), start)])
    settled: set[N] = set()
    while frontier:
        cost, _, node = frontier.pop()
        if node in settled:
            continue
        settled.add(node)
        if is_goal(node):
            return cost, _rebuild_path(parents, node)
        for neighbor, weight in neighbors(node):
            if weight < 0:
                raise ValueError(f"negative edge weight {weight} from {node!r} to {neighbor!r}")
            new_cost = cost + weight
            if new_cost < best.get(neighbor, float("inf")):
                best[neighbor] = new_cost
                parents[neighbor] = node
                frontier.push((new_cost, next(tie_breaker), neighbor))
    return None


def _rebuild_path[N: Hashable](parents: HashMap[N, N | None], goal: N) -> list[N]:
    path: list[N] = []
    node: N | None = goal
    while node is not None:
        path.append(node)
        node = parents[node]
    path.reverse()
    return path
