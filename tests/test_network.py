import json
from pathlib import Path
from typing import Any

import pytest

from metro_router.errors import NetworkFileError
from metro_router.graph import WALK
from metro_router.network import Network, load_network, parse_network


def test_parse_builds_every_station(toy_network: Network) -> None:
    assert sorted(toy_network.graph.stations()) == [
        "Psi",
        "Pê",
        "Quê",
        "Wê",
        "Xis",
        "Ypsilon",
        "Zeta",
        "Ômega",
    ]


def test_parse_connects_consecutive_stations_in_both_directions(toy_network: Network) -> None:
    forward = [(edge.to, edge.line) for edge in toy_network.graph.edges("Pê")]

    assert sorted(forward) == [("Quê", "B"), ("Xis", "B")]


def test_parse_adds_walkways_as_walk_edges(toy_network: Network) -> None:
    walks = [edge for edge in toy_network.graph.edges("Ômega") if edge.line == WALK]

    assert [(edge.to, edge.minutes) for edge in walks] == [("Quê", 2)]


def test_lines_at_lists_lines_serving_a_station(toy_network: Network) -> None:
    assert [line.id for line in toy_network.lines_at("Zeta")] == ["A", "B", "C"]


def test_line_lookup_by_id(toy_network: Network) -> None:
    assert toy_network.line("B").name == "Fast"


def test_line_lookup_with_unknown_id_raises_key_error(toy_network: Network) -> None:
    with pytest.raises(KeyError):
        toy_network.line("Z")


def test_load_network_reads_json_file(toy_file: Path) -> None:
    assert load_network(toy_file).name == "Toy Metro"


def test_load_bundled_sao_paulo_network() -> None:
    network = load_network()

    assert network.name == "São Paulo Metro"
    assert "Sé" in network.graph


def test_load_missing_file_raises_network_file_error(tmp_path: Path) -> None:
    with pytest.raises(NetworkFileError, match="not found"):
        load_network(tmp_path / "missing.json")


def test_load_invalid_json_reports_line_number(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text('{\n  "name": \n}', encoding="utf-8")

    with pytest.raises(NetworkFileError, match="line 3"):
        load_network(path)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        pytest.param(lambda data: data.pop("name"), "missing 'name'", id="missing-name"),
        pytest.param(
            lambda data: data.update(lines="nope"), "'lines' must be", id="lines-not-list"
        ),
        pytest.param(lambda data: data.update(lines=[]), "at least one line", id="no-lines"),
        pytest.param(
            lambda data: data["lines"][0].update(stations=["Xis"]),
            "at least two stations",
            id="single-station-line",
        ),
        pytest.param(
            lambda data: data["lines"][0].update(segment_minutes=0),
            "must be positive",
            id="zero-minutes",
        ),
        pytest.param(
            lambda data: data["lines"][1].update(id="A"), "duplicate line id 'A'", id="duplicate-id"
        ),
        pytest.param(
            lambda data: data["lines"][0].update(stations=["Xis", "Xis"]),
            "repeats station 'Xis'",
            id="repeated-station",
        ),
        pytest.param(
            lambda data: data["walkways"][0].update(to="Nowhere"),
            "unknown station 'Nowhere'",
            id="walkway-unknown-station",
        ),
        pytest.param(
            lambda data: data.update(transfer_minutes=-1),
            "must not be negative",
            id="negative-transfer",
        ),
        pytest.param(
            lambda data: data.update(transfer_minutes=True),
            "must be a number",
            id="bool-is-not-number",
        ),
    ],
)
def test_parse_rejects_invalid_definitions(
    toy_data: dict[str, Any], mutate: Any, message: str
) -> None:
    mutate(toy_data)

    with pytest.raises(NetworkFileError, match=message):
        parse_network(toy_data)


def test_parse_rejects_non_object_root() -> None:
    with pytest.raises(NetworkFileError, match="must be a JSON object"):
        parse_network([1, 2])


def test_walkways_are_optional(toy_data: dict[str, Any], tmp_path: Path) -> None:
    del toy_data["walkways"]
    path = tmp_path / "no_walkways.json"
    path.write_text(json.dumps(toy_data), encoding="utf-8")

    edges = load_network(path).graph.edges("Ômega")

    assert all(edge.line != WALK for edge in edges)
