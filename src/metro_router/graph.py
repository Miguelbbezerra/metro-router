"""Undirected multigraph of stations."""

from collections.abc import Iterator
from dataclasses import dataclass

from metro_router.structures import HashMap

WALK = "walk"
"""Pseudo line id used for walkways between nearby stations."""


@dataclass(frozen=True, slots=True)
class Edge:
    """A direct connection from one station to ``to``."""

    to: str
    line: str
    minutes: float


class Graph:
    """Stations connected by edges labelled with a line and a travel time.

    It is a *multigraph*: two stations served by two lines (like Paraíso and
    Ana Rosa in São Paulo) are joined by one edge per line. Adjacency lists
    are stored in the hand-written :class:`HashMap`.

    Complexity:
        add_station, add_edge: O(1) average
        edges(station): O(1) average to find the list
    """

    __slots__ = ("_adjacency",)

    def __init__(self) -> None:
        self._adjacency: HashMap[str, list[Edge]] = HashMap()

    def add_station(self, name: str) -> None:
        """Add ``name`` with no connections; does nothing if it already exists."""
        if name not in self._adjacency:
            self._adjacency[name] = []

    def add_edge(self, first: str, second: str, line: str, minutes: float) -> None:
        """Connect ``first`` and ``second`` in both directions."""
        self.add_station(first)
        self.add_station(second)
        self._adjacency[first].append(Edge(second, line, minutes))
        self._adjacency[second].append(Edge(first, line, minutes))

    def edges(self, station: str) -> list[Edge]:
        """Return the edges leaving ``station``.

        Raises:
            KeyError: If the station does not exist.
        """
        return self._adjacency[station]

    def edges_between(self, first: str, second: str) -> list[Edge]:
        """Return every edge going directly from ``first`` to ``second``."""
        return [edge for edge in self.edges(first) if edge.to == second]

    def edge_on(self, first: str, second: str, line: str) -> Edge:
        """Return the edge from ``first`` to ``second`` on ``line``.

        Raises:
            KeyError: If no such edge exists.
        """
        for edge in self.edges(first):
            if edge.to == second and edge.line == line:
                return edge
        raise KeyError((first, second, line))

    def stations(self) -> Iterator[str]:
        """Iterate over station names in no particular order."""
        return iter(self._adjacency)

    def __contains__(self, station: object) -> bool:
        return station in self._adjacency

    def __len__(self) -> int:
        return len(self._adjacency)
