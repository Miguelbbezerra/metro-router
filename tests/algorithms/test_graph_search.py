from collections.abc import Iterable

import pytest

from metro_router.algorithms import bfs_path, dijkstra_path, reachable

#   A --1-- B --1-- C
#   |               |
#   +------5--------+     D (isolated)
WEIGHTED: dict[str, list[tuple[str, float]]] = {
    "A": [("B", 1), ("C", 5)],
    "B": [("A", 1), ("C", 1)],
    "C": [("B", 1), ("A", 5)],
    "D": [],
}


def weighted(node: str) -> Iterable[tuple[str, float]]:
    return WEIGHTED[node]


def unweighted(node: str) -> Iterable[str]:
    return (neighbor for neighbor, _ in WEIGHTED[node])


def test_bfs_finds_path_with_fewest_edges() -> None:
    assert bfs_path("A", "C", unweighted) == ["A", "C"]


def test_bfs_path_to_itself_is_single_node() -> None:
    assert bfs_path("A", "A", unweighted) == ["A"]


def test_bfs_returns_none_when_unreachable() -> None:
    assert bfs_path("A", "D", unweighted) is None


def test_dijkstra_finds_cheapest_path_even_with_more_edges() -> None:
    assert dijkstra_path("A", lambda node: node == "C", weighted) == (2, ["A", "B", "C"])


def test_dijkstra_returns_none_when_goal_unreachable() -> None:
    assert dijkstra_path("A", lambda node: node == "D", weighted) is None


def test_dijkstra_stops_at_first_goal_reached() -> None:
    cost, path = dijkstra_path("A", lambda node: node in {"B", "C"}, weighted) or (0, [])

    assert (cost, path) == (1, ["A", "B"])


def test_dijkstra_rejects_negative_weights() -> None:
    with pytest.raises(ValueError, match="negative"):
        dijkstra_path("A", lambda node: node == "B", lambda _: [("B", -1.0)])


def test_reachable_visits_connected_component() -> None:
    assert reachable("A", unweighted) == {"A", "B", "C"}


def test_reachable_from_isolated_node_is_only_itself() -> None:
    assert reachable("D", unweighted) == {"D"}


def test_reachable_handles_long_chains_without_recursion_limit() -> None:
    size = 10_000

    def chain(node: int) -> Iterable[int]:
        return [node + 1] if node + 1 < size else []

    assert len(reachable(0, chain)) == size
