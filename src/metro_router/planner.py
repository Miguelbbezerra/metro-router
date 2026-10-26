"""Turn graph searches into human-readable itineraries."""

import logging
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from enum import StrEnum
from itertools import pairwise

from metro_router.algorithms import bfs_path, dijkstra_path, merge_sort, split_runs
from metro_router.errors import NoRouteError
from metro_router.graph import WALK
from metro_router.network import Network

logger = logging.getLogger(__name__)

# Search state for the fastest route: the station, plus the line used to reach it.
type State = tuple[str, str | None]


class Criterion(StrEnum):
    """What the planner should minimise."""

    TIME = "time"
    STOPS = "stops"


@dataclass(frozen=True, slots=True)
class Hop:
    """One edge travelled: between two adjacent stations on one line."""

    start: str
    end: str
    line: str
    minutes: float


@dataclass(frozen=True, slots=True)
class Leg:
    """A stretch of the journey on a single line (or on foot)."""

    line: str
    stations: tuple[str, ...]
    minutes: float

    @property
    def start(self) -> str:
        return self.stations[0]

    @property
    def end(self) -> str:
        return self.stations[-1]

    @property
    def stops(self) -> int:
        return len(self.stations) - 1

    @property
    def is_walk(self) -> bool:
        return self.line == WALK


@dataclass(frozen=True, slots=True)
class Itinerary:
    """A complete journey, already split into legs."""

    origin: str
    destination: str
    legs: tuple[Leg, ...]
    total_minutes: float

    @property
    def stops(self) -> int:
        return sum(leg.stops for leg in self.legs if not leg.is_walk)

    @property
    def transfers(self) -> int:
        rides = sum(1 for leg in self.legs if not leg.is_walk)
        return max(rides - 1, 0)


class Planner:
    """Plans routes on a :class:`Network`."""

    __slots__ = ("_network",)

    def __init__(self, network: Network) -> None:
        self._network = network

    def plan(self, origin: str, destination: str, criterion: Criterion) -> Itinerary:
        """Return the best itinerary from ``origin`` to ``destination``.

        Args:
            origin: Exact station name (see ``StationIndex.resolve``).
            destination: Exact station name.
            criterion: ``TIME`` for the fastest route, counting transfer
                penalties; ``STOPS`` for the route through the fewest stations.

        Raises:
            KeyError: If a station does not exist in the network.
            NoRouteError: If the stations are not connected.
        """
        for station in (origin, destination):
            if station not in self._network.graph:
                raise KeyError(station)
        logger.debug("planning %s -> %s by %s", origin, destination, criterion)
        hops = (
            self._fastest_hops(origin, destination)
            if criterion is Criterion.TIME
            else self._fewest_stops_hops(origin, destination)
        )
        return self._build_itinerary(origin, destination, hops)

    def _fastest_hops(self, origin: str, destination: str) -> list[Hop]:
        """Dijkstra over (station, line) states, so changing lines can cost extra."""
        initial: State = (origin, None)
        result = dijkstra_path(
            initial, lambda state: state[0] == destination, self._weighted_neighbors
        )
        if result is None:
            raise NoRouteError(origin, destination)
        _, states = result
        hops: list[Hop] = []
        for (start, _), (end, line) in pairwise(states):
            assert line is not None  # every state after the first was reached by an edge
            hops.append(self._hop(start, end, line))
        return hops

    def _weighted_neighbors(self, state: State) -> Iterator[tuple[State, float]]:
        station, current_line = state
        for edge in self._network.graph.edges(station):
            cost = edge.minutes
            if self._is_transfer(current_line, edge.line):
                cost += self._network.transfer_minutes
            yield (edge.to, edge.line), cost

    def _fewest_stops_hops(self, origin: str, destination: str) -> list[Hop]:
        """BFS on stations, then pick lines that minimise changes along that path."""
        graph = self._network.graph
        path = bfs_path(origin, destination, lambda node: (e.to for e in graph.edges(node)))
        if path is None:
            raise NoRouteError(origin, destination)
        pairs = list(pairwise(path))
        lines = self._fewest_changes(pairs)
        return [
            self._hop(start, end, line) for (start, end), line in zip(pairs, lines, strict=True)
        ]

    def _fewest_changes(self, pairs: Sequence[tuple[str, str]]) -> list[str]:
        """Choose a line for each hop of a fixed path, minimising line changes.

        Greedy: from the current hop, ride the line that covers the most
        consecutive hops. Always taking the farthest-reaching option is optimal
        for this problem (the same argument as for interval covering).
        """
        graph = self._network.graph
        serving = [{edge.line for edge in graph.edges_between(*pair)} for pair in pairs]
        chosen: list[str] = []
        index = 0
        while index < len(pairs):
            best_line, best_reach = "", index
            for line in merge_sort(list(serving[index])):
                reach = index + 1
                while reach < len(pairs) and line in serving[reach]:
                    reach += 1
                if reach > best_reach:
                    best_line, best_reach = line, reach
            chosen.extend([best_line] * (best_reach - index))
            index = best_reach
        return chosen

    def _hop(self, start: str, end: str, line: str) -> Hop:
        return Hop(start, end, line, self._network.graph.edge_on(start, end, line).minutes)

    def _build_itinerary(self, origin: str, destination: str, hops: Sequence[Hop]) -> Itinerary:
        legs: list[Leg] = []
        total = 0.0
        previous_line: str | None = None
        for run in split_runs(hops, key=lambda hop: hop.line):
            line = run[0].line
            if self._is_transfer(previous_line, line):
                total += self._network.transfer_minutes
            minutes = sum(hop.minutes for hop in run)
            total += minutes
            stations = (run[0].start, *(hop.end for hop in run))
            legs.append(Leg(line=line, stations=stations, minutes=minutes))
            previous_line = line
        return Itinerary(origin, destination, tuple(legs), total)

    @staticmethod
    def _is_transfer(current_line: str | None, next_line: str) -> bool:
        """Changing between two different trains costs a penalty; walking does not."""
        return (
            current_line is not None
            and WALK not in (current_line, next_line)
            and current_line != next_line
        )
