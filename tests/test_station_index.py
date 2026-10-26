import pytest

from metro_router.errors import StationNotFoundError
from metro_router.station_index import StationIndex

NAMES = ["Santana", "Santa Cruz", "Santa Cecília", "Sé", "São Bento", "Paraíso", "Paulista"]


@pytest.fixture
def index() -> StationIndex:
    return StationIndex(NAMES)


def test_sorted_names_ignores_accents(index: StationIndex) -> None:
    assert index.sorted_names() == [
        "Paraíso",
        "Paulista",
        "Santa Cecília",
        "Santa Cruz",
        "Santana",
        "São Bento",
        "Sé",
    ]


@pytest.mark.parametrize("query", ["Sé", "se", "SE", " sé "])
def test_resolve_is_accent_and_case_insensitive(index: StationIndex, query: str) -> None:
    assert index.resolve(query) == "Sé"


def test_resolve_unknown_station_raises_with_suggestions(index: StationIndex) -> None:
    with pytest.raises(StationNotFoundError) as caught:
        index.resolve("Paraizo")

    assert caught.value.suggestions == ["Paraíso"]
    assert "Did you mean: Paraíso?" in str(caught.value)


def test_resolve_gibberish_has_no_suggestions(index: StationIndex) -> None:
    with pytest.raises(StationNotFoundError) as caught:
        index.resolve("xyzxyzxyz")

    assert caught.value.suggestions == []
    assert "Did you mean" not in str(caught.value)


def test_autocomplete_returns_sorted_matches(index: StationIndex) -> None:
    assert index.autocomplete("santa") == ["Santa Cecília", "Santa Cruz", "Santana"]


def test_autocomplete_respects_limit(index: StationIndex) -> None:
    assert index.autocomplete("sa", limit=2) == ["Santa Cecília", "Santa Cruz"]


def test_autocomplete_with_accents_in_prefix(index: StationIndex) -> None:
    assert index.autocomplete("SÃO") == ["São Bento"]


def test_suggest_orders_by_distance(index: StationIndex) -> None:
    assert index.suggest("santa cruiz")[0] == "Santa Cruz"
