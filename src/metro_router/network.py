"""Load and validate metro network definitions from JSON."""

import json
import logging
from dataclasses import dataclass
from importlib import resources
from itertools import pairwise
from pathlib import Path
from typing import Any

from metro_router.errors import NetworkFileError
from metro_router.graph import WALK, Graph

logger = logging.getLogger(__name__)

BUNDLED_NETWORK = "sao_paulo.json"


@dataclass(frozen=True, slots=True)
class Line:
    """A metro line: an ordered sequence of stations."""

    id: str
    name: str
    color: str
    segment_minutes: float
    stations: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Network:
    """A parsed network: line metadata plus the station graph."""

    name: str
    transfer_minutes: float
    lines: tuple[Line, ...]
    graph: Graph

    def line(self, line_id: str) -> Line:
        """Return the line with ``line_id``.

        Raises:
            KeyError: If no line has that id.
        """
        for line in self.lines:
            if line.id == line_id:
                return line
        raise KeyError(line_id)

    def lines_at(self, station: str) -> list[Line]:
        """Return the lines that stop at ``station``, in file order."""
        return [line for line in self.lines if station in line.stations]


def load_network(path: Path | None = None) -> Network:
    """Read a network JSON file, or the bundled São Paulo network if ``path`` is ``None``.

    Raises:
        NetworkFileError: If the file cannot be read, is not valid JSON, or
            does not describe a valid network.
    """
    if path is None:
        source = resources.files("metro_router").joinpath("data", BUNDLED_NETWORK)
        label = f"<bundled {BUNDLED_NETWORK}>"
        text = source.read_text(encoding="utf-8")
    else:
        label = str(path)
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise NetworkFileError(f"network file not found: {path}") from None
        except OSError as error:
            raise NetworkFileError(f"cannot read {path}: {error.strerror}") from error

    logger.debug("loading network from %s", label)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise NetworkFileError(
            f"{label}: invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}"
        ) from error
    return parse_network(data)


def parse_network(data: object) -> Network:
    """Validate decoded JSON and build a :class:`Network` from it.

    Raises:
        NetworkFileError: Describing the first problem found.
    """
    root = _as_object(data, "network")
    name = _string(root, "name", "network")
    transfer_minutes = _number(root, "transfer_minutes", "network", allow_zero=True)

    raw_lines = _list(root, "lines", "network")
    if not raw_lines:
        raise NetworkFileError("network: must have at least one line")

    graph = Graph()
    lines: list[Line] = []
    seen_ids: set[str] = set()
    for position, raw_line in enumerate(raw_lines):
        line = _parse_line(raw_line, f"lines[{position}]")
        if line.id in seen_ids:
            raise NetworkFileError(f"lines[{position}]: duplicate line id {line.id!r}")
        seen_ids.add(line.id)
        lines.append(line)
        for first, second in pairwise(line.stations):
            graph.add_edge(first, second, line.id, line.segment_minutes)

    rail_stations = set(graph.stations())
    raw_walkways = _list(root, "walkways", "network") if "walkways" in root else []
    for position, raw_walkway in enumerate(raw_walkways):
        where = f"walkways[{position}]"
        walkway = _as_object(raw_walkway, where)
        start = _string(walkway, "from", where)
        end = _string(walkway, "to", where)
        for station in (start, end):
            if station not in rail_stations:
                raise NetworkFileError(f"{where}: unknown station {station!r}")
        graph.add_edge(start, end, WALK, _number(walkway, "minutes", where))

    logger.debug("parsed %d lines and %d stations", len(lines), len(graph))
    return Network(name=name, transfer_minutes=transfer_minutes, lines=tuple(lines), graph=graph)


def _parse_line(raw: object, where: str) -> Line:
    line = _as_object(raw, where)
    stations = _list(line, "stations", where)
    if len(stations) < 2:
        raise NetworkFileError(f"{where}: must have at least two stations")
    names: list[str] = []
    for index, station in enumerate(stations):
        if not isinstance(station, str) or not station.strip():
            raise NetworkFileError(f"{where}.stations[{index}]: must be a non-empty string")
        if station in names:
            raise NetworkFileError(f"{where}: repeats station {station!r}")
        names.append(station)
    return Line(
        id=_string(line, "id", where),
        name=_string(line, "name", where),
        color=_string(line, "color", where),
        segment_minutes=_number(line, "segment_minutes", where),
        stations=tuple(names),
    )


def _as_object(value: object, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise NetworkFileError(f"{where}: must be a JSON object")
    return value


def _require(mapping: dict[str, Any], key: str, where: str) -> object:
    if key not in mapping:
        raise NetworkFileError(f"{where}: missing {key!r}")
    value: object = mapping[key]
    return value


def _string(mapping: dict[str, Any], key: str, where: str) -> str:
    value = _require(mapping, key, where)
    if not isinstance(value, str) or not value.strip():
        raise NetworkFileError(f"{where}: {key!r} must be a non-empty string")
    return value


def _list(mapping: dict[str, Any], key: str, where: str) -> list[object]:
    value = _require(mapping, key, where)
    if not isinstance(value, list):
        raise NetworkFileError(f"{where}: {key!r} must be a list")
    return value


def _number(mapping: dict[str, Any], key: str, where: str, *, allow_zero: bool = False) -> float:
    value = _require(mapping, key, where)
    # bool is a subclass of int in Python, but `true` is not a valid duration.
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise NetworkFileError(f"{where}: {key!r} must be a number")
    if value < 0:
        raise NetworkFileError(f"{where}: {key!r} must not be negative")
    if value == 0 and not allow_zero:
        raise NetworkFileError(f"{where}: {key!r} must be positive")
    return float(value)
