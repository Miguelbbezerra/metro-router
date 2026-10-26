"""Command-line interface: ``metro route``, ``search``, ``stations``, ``lines`` and ``check``."""

import argparse
import json
import logging
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from metro_router import __version__
from metro_router.algorithms import merge_sort, reachable
from metro_router.errors import MetroRouterError
from metro_router.network import Network, load_network
from metro_router.planner import Criterion, Itinerary, Leg, Planner
from metro_router.station_index import StationIndex
from metro_router.text import normalize

logger = logging.getLogger("metro_router")

EXIT_OK = 0
EXIT_FAILURE = 1

type Command = Callable[[argparse.Namespace, Network], int]


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return the process exit code.

    Exit codes: 0 on success, 1 on an expected failure (unknown station, no
    route, invalid network file, no search results), 2 on invalid usage.
    """
    args = _build_parser().parse_args(argv)
    _configure_logging(verbose=args.verbose)
    command: Command = args.command
    try:
        network = load_network(args.network)
        return command(args, network)
    except MetroRouterError as error:
        _fail(str(error))
        return EXIT_FAILURE


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="metro",
        description="Plan routes on a metro network (São Paulo by default).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--network",
        type=Path,
        metavar="FILE",
        help="network JSON file (default: bundled São Paulo network)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="log debug details to stderr")
    commands = parser.add_subparsers(title="commands", required=True, metavar="COMMAND")

    route = commands.add_parser("route", help="find a route between two stations")
    route.add_argument("origin")
    route.add_argument("destination")
    route.add_argument(
        "--by",
        type=Criterion,
        choices=list(Criterion),
        default=Criterion.TIME,
        help="minimise travel time (default) or number of stops",
    )
    route.add_argument("--format", choices=["text", "json"], default="text")
    route.set_defaults(command=_route)

    search = commands.add_parser("search", help="autocomplete station names")
    search.add_argument("prefix")
    search.add_argument("--limit", type=int, default=10)
    search.set_defaults(command=_search)

    stations = commands.add_parser("stations", help="list stations, one per line")
    stations.add_argument("--line", metavar="ID", help="only stations of this line, in order")
    stations.set_defaults(command=_stations)

    lines = commands.add_parser("lines", help="list lines")
    lines.set_defaults(command=_lines)

    check = commands.add_parser("check", help="validate that every station is reachable")
    check.set_defaults(command=_check)
    return parser


def _route(args: argparse.Namespace, network: Network) -> int:
    index = StationIndex(network.graph.stations())
    origin = index.resolve(args.origin)
    destination = index.resolve(args.destination)
    itinerary = Planner(network).plan(origin, destination, args.by)
    if args.format == "json":
        print(
            json.dumps(
                _itinerary_to_dict(itinerary, network, args.by), ensure_ascii=False, indent=2
            )
        )
    else:
        print(_format_itinerary(itinerary, network, args.by))
    return EXIT_OK


def _search(args: argparse.Namespace, network: Network) -> int:
    matches = StationIndex(network.graph.stations()).autocomplete(args.prefix, limit=args.limit)
    for name in matches:
        print(name)
    # Like grep: exit 1 when nothing matched, so scripts can test the result.
    return EXIT_OK if matches else EXIT_FAILURE


def _stations(args: argparse.Namespace, network: Network) -> int:
    if args.line is None:
        names = StationIndex(network.graph.stations()).sorted_names()
    else:
        try:
            names = list(network.line(args.line).stations)
        except KeyError:
            known = ", ".join(line.id for line in network.lines)
            _fail(f"Unknown line {args.line!r}. Available lines: {known}.")
            return EXIT_FAILURE
    for name in names:
        print(name)
    return EXIT_OK


def _lines(_: argparse.Namespace, network: Network) -> int:
    for line in network.lines:
        print(f"{line.id}\t{line.name}\t{len(line.stations)} stations")
    return EXIT_OK


def _check(_: argparse.Namespace, network: Network) -> int:
    start = network.lines[0].stations[0]
    graph = network.graph
    connected = reachable(start, lambda station: (edge.to for edge in graph.edges(station)))
    missing = merge_sort([s for s in graph.stations() if s not in connected], key=normalize)
    if missing:
        _fail(f"{len(missing)} stations unreachable from {start}: {', '.join(missing)}")
        return EXIT_FAILURE
    print(f"OK: {network.name} — {len(network.lines)} lines, {len(graph)} stations, all connected.")
    return EXIT_OK


def _format_itinerary(itinerary: Itinerary, network: Network, criterion: Criterion) -> str:
    if not itinerary.legs:
        return f"You are already at {itinerary.origin}."
    label = "fastest route" if criterion is Criterion.TIME else "fewest stops"
    lines = [f"{itinerary.origin} → {itinerary.destination}  ({label})", ""]
    previous: Leg | None = None
    for leg in itinerary.legs:
        if leg.is_walk:
            lines.append(f"  Walk from {leg.start} to {leg.end} ({_minutes(leg.minutes)} min)")
        else:
            verb = "Take" if previous is None or previous.is_walk else "Change to"
            where = "from" if verb == "Take" else "at"
            lines.append(f"  {verb} {_line_label(network, leg.line)} {where} {leg.start}")
            stop_word = "stop" if leg.stops == 1 else "stops"
            lines.append(
                f"      ride {leg.stops} {stop_word} to {leg.end} ({_minutes(leg.minutes)} min)"
            )
        previous = leg
    transfer_word = "transfer" if itinerary.transfers == 1 else "transfers"
    lines += [
        "",
        f"Total: {_minutes(itinerary.total_minutes)} min · {itinerary.stops} stops · "
        f"{itinerary.transfers} {transfer_word}",
    ]
    return "\n".join(lines)


def _itinerary_to_dict(
    itinerary: Itinerary, network: Network, criterion: Criterion
) -> dict[str, Any]:
    return {
        "origin": itinerary.origin,
        "destination": itinerary.destination,
        "criterion": str(criterion),
        "total_minutes": itinerary.total_minutes,
        "stops": itinerary.stops,
        "transfers": itinerary.transfers,
        "legs": [
            {
                "line": leg.line,
                "line_name": None if leg.is_walk else network.line(leg.line).name,
                "from": leg.start,
                "to": leg.end,
                "stations": list(leg.stations),
                "stops": leg.stops,
                "minutes": leg.minutes,
            }
            for leg in itinerary.legs
        ],
    }


def _line_label(network: Network, line_id: str) -> str:
    return f"Line {line_id}-{network.line(line_id).name}"


def _minutes(value: float) -> str:
    """Format minutes without a useless ``.0``: 4.0 → "4", 2.5 → "2.5"."""
    return f"{value:g}"


def _fail(message: str) -> None:
    print(f"metro: error: {message}", file=sys.stderr)


def _configure_logging(*, verbose: bool) -> None:
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if verbose else logging.WARNING)
