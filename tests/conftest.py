"""Shared fixtures.

The toy network is small enough to reason about by hand, and is shaped so
that the fastest route and the route with fewest stops differ:

    Line A (10 min/segment):  Xis ── Ypsilon ── Zeta
    Line B ( 1 min/segment):  Xis ── Pê ── Quê ── Zeta
    Line C ( 1 min/segment):                      Zeta ── Wê
    Line D ( 1 min/segment):               Ômega ── Psi
    Walkway (2 min):          Quê ┄┄ Ômega
"""

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from metro_router.network import Network, parse_network

TOY_NETWORK: dict[str, Any] = {
    "name": "Toy Metro",
    "transfer_minutes": 5,
    "lines": [
        {
            "id": "A",
            "name": "Slow",
            "color": "#111111",
            "segment_minutes": 10,
            "stations": ["Xis", "Ypsilon", "Zeta"],
        },
        {
            "id": "B",
            "name": "Fast",
            "color": "#222222",
            "segment_minutes": 1,
            "stations": ["Xis", "Pê", "Quê", "Zeta"],
        },
        {
            "id": "C",
            "name": "Short",
            "color": "#333333",
            "segment_minutes": 1,
            "stations": ["Zeta", "Wê"],
        },
        {
            "id": "D",
            "name": "Other",
            "color": "#444444",
            "segment_minutes": 1,
            "stations": ["Ômega", "Psi"],
        },
    ],
    "walkways": [{"from": "Quê", "to": "Ômega", "minutes": 2}],
}


@pytest.fixture
def toy_data() -> dict[str, Any]:
    """A fresh, mutable copy of the toy network definition."""
    return copy.deepcopy(TOY_NETWORK)


@pytest.fixture
def toy_network(toy_data: dict[str, Any]) -> Network:
    return parse_network(toy_data)


@pytest.fixture
def toy_file(tmp_path: Path, toy_data: dict[str, Any]) -> Path:
    path = tmp_path / "toy.json"
    path.write_text(json.dumps(toy_data), encoding="utf-8")
    return path
