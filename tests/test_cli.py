import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from metro_router.cli import main


def run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    code = main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_route_prints_legs_and_summary(capsys: pytest.CaptureFixture[str], toy_file: Path) -> None:
    code, out, _ = run(capsys, "--network", str(toy_file), "route", "xis", "WE")

    assert code == 0
    assert "Xis → Wê" in out
    assert "Line B-Fast" in out
    assert "Change to Line C-Short at Zeta" in out
    assert "Total: 9 min · 4 stops · 1 transfer" in out


def test_route_by_stops(capsys: pytest.CaptureFixture[str], toy_file: Path) -> None:
    _, out, _ = run(capsys, "--network", str(toy_file), "route", "Xis", "Zeta", "--by", "stops")

    assert "Line A-Slow" in out
    assert "Total: 20 min · 2 stops · 0 transfers" in out


def test_route_shows_walk_legs(capsys: pytest.CaptureFixture[str], toy_file: Path) -> None:
    _, out, _ = run(capsys, "--network", str(toy_file), "route", "Xis", "Psi")

    assert "Walk from Quê to Ômega (2 min)" in out


def test_route_to_same_station(capsys: pytest.CaptureFixture[str], toy_file: Path) -> None:
    code, out, _ = run(capsys, "--network", str(toy_file), "route", "Xis", "xis")

    assert code == 0
    assert "already at Xis" in out


def test_route_as_json_is_machine_readable(
    capsys: pytest.CaptureFixture[str], toy_file: Path
) -> None:
    _, out, _ = run(capsys, "--network", str(toy_file), "route", "Xis", "Wê", "--format", "json")

    data: dict[str, Any] = json.loads(out)

    assert data["total_minutes"] == 9
    assert data["criterion"] == "time"
    assert [leg["line"] for leg in data["legs"]] == ["B", "C"]
    assert data["legs"][0]["stations"] == ["Xis", "Pê", "Quê", "Zeta"]


def test_unknown_station_fails_with_suggestion(
    capsys: pytest.CaptureFixture[str], toy_file: Path
) -> None:
    code, out, err = run(capsys, "--network", str(toy_file), "route", "Xiz", "Zeta")

    assert code == 1
    assert out == ""
    assert "metro: error: Unknown station 'Xiz'. Did you mean: Xis?" in err


def test_disconnected_route_fails(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, toy_data: dict[str, Any]
) -> None:
    toy_data["lines"].append(
        {
            "id": "Z",
            "name": "Island",
            "color": "#000",
            "segment_minutes": 1,
            "stations": ["I1", "I2"],
        }
    )
    path = tmp_path / "islands.json"
    path.write_text(json.dumps(toy_data), encoding="utf-8")

    code, _, err = run(capsys, "--network", str(path), "route", "Xis", "I1")

    assert code == 1
    assert "No route between 'Xis' and 'I1'" in err


def test_search_lists_matches(capsys: pytest.CaptureFixture[str], toy_file: Path) -> None:
    code, out, _ = run(capsys, "--network", str(toy_file), "search", "x")

    assert code == 0
    assert out.splitlines() == ["Xis"]


def test_search_without_matches_exits_1_like_grep(
    capsys: pytest.CaptureFixture[str], toy_file: Path
) -> None:
    code, out, _ = run(capsys, "--network", str(toy_file), "search", "nothing")

    assert code == 1
    assert out == ""


def test_stations_lists_all_names_one_per_line(
    capsys: pytest.CaptureFixture[str], toy_file: Path
) -> None:
    _, out, _ = run(capsys, "--network", str(toy_file), "stations")

    assert out.splitlines() == ["Ômega", "Pê", "Psi", "Quê", "Wê", "Xis", "Ypsilon", "Zeta"]


def test_stations_filtered_by_line_keeps_line_order(
    capsys: pytest.CaptureFixture[str], toy_file: Path
) -> None:
    _, out, _ = run(capsys, "--network", str(toy_file), "stations", "--line", "B")

    assert out.splitlines() == ["Xis", "Pê", "Quê", "Zeta"]


def test_stations_with_unknown_line_fails(
    capsys: pytest.CaptureFixture[str], toy_file: Path
) -> None:
    code, _, err = run(capsys, "--network", str(toy_file), "stations", "--line", "Q")

    assert code == 1
    assert "Unknown line 'Q'" in err


def test_lines_lists_ids_names_and_sizes(
    capsys: pytest.CaptureFixture[str], toy_file: Path
) -> None:
    _, out, _ = run(capsys, "--network", str(toy_file), "lines")

    assert out.splitlines() == [
        "A\tSlow\t3 stations",
        "B\tFast\t4 stations",
        "C\tShort\t2 stations",
        "D\tOther\t2 stations",
    ]


def test_check_reports_connected_network(
    capsys: pytest.CaptureFixture[str], toy_file: Path
) -> None:
    code, out, _ = run(capsys, "--network", str(toy_file), "check")

    assert code == 0
    assert "OK: Toy Metro — 4 lines, 8 stations, all connected." in out


def test_check_reports_unreachable_stations(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, toy_data: dict[str, Any]
) -> None:
    toy_data["lines"].append(
        {
            "id": "Z",
            "name": "Island",
            "color": "#000",
            "segment_minutes": 1,
            "stations": ["I1", "I2"],
        }
    )
    path = tmp_path / "islands.json"
    path.write_text(json.dumps(toy_data), encoding="utf-8")

    code, _, err = run(capsys, "--network", str(path), "check")

    assert code == 1
    assert "2 stations unreachable from Xis: I1, I2" in err


def test_invalid_network_file_fails_cleanly(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    code, _, err = run(capsys, "--network", str(tmp_path / "missing.json"), "check")

    assert code == 1
    assert "network file not found" in err


def test_missing_command_is_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        main([])

    assert caught.value.code == 2


def test_verbose_flag_enables_debug_logging(
    capsys: pytest.CaptureFixture[str], toy_file: Path
) -> None:
    run(capsys, "--verbose", "--network", str(toy_file), "check")

    assert logging.getLogger("metro_router").getEffectiveLevel() == logging.DEBUG


def test_default_network_is_sao_paulo(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, _ = run(capsys, "route", "Sé", "Paulista")

    assert code == 0
    assert "Sé → Paulista" in out


def test_module_is_executable_with_python_m() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "metro_router", "search", "paul"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "Paulista"
