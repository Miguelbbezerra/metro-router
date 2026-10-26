import pytest

from metro_router.text import normalize


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Sé", "se"),
        ("CONSOLAÇÃO", "consolacao"),
        ("  Santa   Cecília ", "santa cecilia"),
        ("Trianon-Masp", "trianon masp"),
        ("Japão-Liberdade", "japao liberdade"),
    ],
)
def test_normalize_strips_accents_case_hyphens_and_extra_spaces(raw: str, expected: str) -> None:
    assert normalize(raw) == expected
