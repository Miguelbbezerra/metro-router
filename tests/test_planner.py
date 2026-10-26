import pytest

from metro_router.errors import NoRouteError
from metro_router.graph import WALK
from metro_router.network import Network, parse_network
from metro_router.planner import Criterion, Planner


@pytest.fixture
def planner(toy_network: Network) -> Planner:
    return Planner(toy_network)


def test_fastest_route_prefers_quick_line_with_more_stops(planner: Planner) -> None:
    itinerary = planner.plan("Xis", "Zeta", Criterion.TIME)

    assert [leg.line for leg in itinerary.legs] == ["B"]
    assert itinerary.legs[0].stations == ("Xis", "Pê", "Quê", "Zeta")
    assert itinerary.total_minutes == 3


def test_fewest_stops_route_prefers_shorter_path(planner: Planner) -> None:
    itinerary = planner.plan("Xis", "Zeta", Criterion.STOPS)

    assert itinerary.legs[0].stations == ("Xis", "Ypsilon", "Zeta")
    assert itinerary.stops == 2
    assert itinerary.total_minutes == 20


def test_changing_lines_adds_transfer_penalty(planner: Planner) -> None:
    itinerary = planner.plan("Xis", "Wê", Criterion.TIME)

    assert [leg.line for leg in itinerary.legs] == ["B", "C"]
    assert itinerary.transfers == 1
    assert itinerary.total_minutes == 3 + 5 + 1


def test_walkway_replaces_transfer_penalty(planner: Planner) -> None:
    itinerary = planner.plan("Xis", "Psi", Criterion.TIME)

    assert [leg.line for leg in itinerary.legs] == ["B", WALK, "D"]
    assert itinerary.total_minutes == 2 + 2 + 1
    assert itinerary.transfers == 1


def test_leg_minutes_and_endpoints(planner: Planner) -> None:
    leg = planner.plan("Xis", "Wê", Criterion.TIME).legs[1]

    assert (leg.start, leg.end, leg.stops, leg.minutes) == ("Zeta", "Wê", 1, 1)


def test_same_origin_and_destination_has_no_legs(planner: Planner) -> None:
    itinerary = planner.plan("Xis", "Xis", Criterion.TIME)

    assert itinerary.legs == ()
    assert itinerary.total_minutes == 0
    assert itinerary.transfers == 0


@pytest.mark.parametrize("criterion", list(Criterion))
def test_unknown_station_raises_key_error(planner: Planner, criterion: Criterion) -> None:
    with pytest.raises(KeyError):
        planner.plan("Xis", "Atlantis", criterion)


@pytest.mark.parametrize("criterion", list(Criterion))
def test_disconnected_stations_raise_no_route(toy_network: Network, criterion: Criterion) -> None:
    toy_network.graph.add_station("Island")

    with pytest.raises(NoRouteError, match="Island"):
        Planner(toy_network).plan("Xis", "Island", criterion)


def test_fewest_stops_keeps_riding_the_same_line_when_possible() -> None:
    # Both lines serve the whole corridor; switching would add a useless transfer.
    network = parse_network(
        {
            "name": "Parallel",
            "transfer_minutes": 5,
            "lines": [
                {
                    "id": "1",
                    "name": "One",
                    "color": "#000",
                    "segment_minutes": 2,
                    "stations": ["A", "B", "C"],
                },
                {
                    "id": "2",
                    "name": "Two",
                    "color": "#fff",
                    "segment_minutes": 2,
                    "stations": ["A", "B", "C", "D"],
                },
            ],
        }
    )

    itinerary = Planner(network).plan("A", "D", Criterion.STOPS)

    assert [leg.line for leg in itinerary.legs] == ["2"]
    assert itinerary.transfers == 0
