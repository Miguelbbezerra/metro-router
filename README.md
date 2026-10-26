# metro-router 🚇

[![CI](https://github.com/Miguelbbezerra/metro-router/actions/workflows/ci.yml/badge.svg)](https://github.com/Miguelbbezerra/metro-router/actions/workflows/ci.yml)
![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)
![Typed: mypy strict](https://img.shields.io/badge/typed-mypy%20strict-informational)
![Coverage ≥ 95%](https://img.shields.io/badge/coverage-%E2%89%A595%25-brightgreen)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A command-line route planner for the **São Paulo metro**. The data structures and
graph algorithms behind it are **written from scratch**: no `heapq`, no `deque`,
no `bisect`, no `networkx`.

```console
$ metro route tucuruvi "vila madalena"
Tucuruvi → Vila Madalena  (fastest route)

  Take Line 1-Azul from Tucuruvi
      ride 8 stops to Luz (16 min)
  Change to Line 4-Amarela at Luz
      ride 3 stops to Paulista (7.5 min)
  Walk from Paulista to Consolação (6 min)
  Take Line 2-Verde from Consolação
      ride 3 stops to Vila Madalena (6 min)

Total: 40.5 min · 14 stops · 2 transfers
```

## Why this project

Each piece of computer science here solves a concrete problem in the app:

| Problem in the app | Solution | Where |
|---|---|---|
| Fastest route, with a penalty for changing lines | **Dijkstra** + hand-written **min-heap** on a `(station, line)` state graph | [`graph_search.py`](src/metro_router/algorithms/graph_search.py), [`planner.py`](src/metro_router/planner.py) |
| Route with the fewest stops | **BFS** + **queue** built on a **linked list** | [`graph_search.py`](src/metro_router/algorithms/graph_search.py) |
| Is every station reachable? | Iterative **DFS** with a **stack** | [`graph_search.py`](src/metro_router/algorithms/graph_search.py) |
| Store the graph | Adjacency lists in a **hash table** (separate chaining, resizing) | [`hash_map.py`](src/metro_router/structures/hash_map.py), [`graph.py`](src/metro_router/graph.py) |
| Autocomplete station names | **Trie** (prefix tree) with **recursive** traversal | [`trie.py`](src/metro_router/structures/trie.py) |
| Exact lookup ignoring accents (`se` → `Sé`) | **Merge sort** + **binary search** | [`sorting.py`](src/metro_router/algorithms/sorting.py), [`searching.py`](src/metro_router/algorithms/searching.py) |
| "Did you mean *Paraíso*?" on typos | **Levenshtein** distance (**dynamic programming**) | [`edit_distance.py`](src/metro_router/algorithms/edit_distance.py) |
| Group hops into "take line X from A to B" | **Two pointers / sliding window** | [`segments.py`](src/metro_router/algorithms/segments.py) |

Big O of every operation, plus a benchmark that measures it: **[docs/complexity.md](docs/complexity.md)**.

## Installation

Requires [uv](https://docs.astral.sh/uv/) (it installs Python 3.12 for you if needed).

```bash
git clone https://github.com/Miguelbbezerra/metro-router.git
cd metro-router
uv sync
uv run metro --help
```

To install it as a global command: `uv tool install .` and then run `metro …` directly.

## Usage

```bash
metro route "Sé" "Paulista"                  # fastest route (default)
metro route "Corinthians-Itaquera" "Butantã" --by stops
metro route se consolacao --format json      # accents and case don't matter
metro search san                             # autocomplete
metro stations --line 4                      # stations of a line, in order
metro lines                                  # list lines
metro check                                  # validate the network
metro --network my_city.json route A B       # use your own network file
metro --verbose route Sé Luz                 # debug logs on stderr
```

Typos get suggestions:

```console
$ metro route paraizo luz
metro: error: Unknown station 'paraizo'. Did you mean: Paraíso?
$ echo $?
1
```

### Plays well with Unix pipes

Output is one item per line or JSON, errors go to stderr, and exit codes mean
something (`0` ok, `1` failure or no match, `2` bad usage). That makes the CLI easy to script:

```bash
metro stations | wc -l                                   # count stations
metro stations --line 1 | grep '^S'                      # filter with grep
metro route Sé Pinheiros --format json | jq '.legs[].line'
metro search xyz || echo "nothing found"                 # exit code 1 like grep
```

[`scripts/demo.sh`](scripts/demo.sh) puts these together, for example by computing
the travel time from Sé to every Line 4 station with a `while read` loop.

### Custom networks

Any city can be described in JSON. See the bundled
[`sao_paulo.json`](src/metro_router/data/sao_paulo.json):

```json
{
  "name": "My Metro",
  "transfer_minutes": 5,
  "lines": [
    { "id": "1", "name": "Blue", "color": "#0455A1", "segment_minutes": 2,
      "stations": ["A", "B", "C"] }
  ],
  "walkways": [{ "from": "C", "to": "D", "minutes": 4 }]
}
```

Invalid files are rejected with a precise message, such as
`lines[2]: repeats station 'Sé'` or `invalid JSON at line 3, column 1`.

> **Data note:** The station order of Lines 1-Azul, 2-Verde, 3-Vermelha and 4-Amarela is
> real. Travel times are uniform approximations, so this is not an official timetable.

## Project structure

```
src/metro_router/
├── structures/        # LinkedList, Stack, Queue, MinHeap, HashMap, Trie
├── algorithms/        # sorting, searching, edit distance, segments, graph search
├── graph.py           # station multigraph (one edge per line)
├── network.py         # JSON loading + validation
├── station_index.py   # lookup, autocomplete, suggestions
├── planner.py         # fastest / fewest-stops itineraries
├── cli.py             # argparse CLI
└── data/sao_paulo.json
tests/                 # mirrors src/; pytest + hypothesis
benchmarks/            # empirical Big O measurements
scripts/               # check.sh (quality gates), demo.sh (pipes)
docs/                  # architecture, complexity, debugging
```

The design decisions are explained in [docs/architecture.md](docs/architecture.md).

## Development

```bash
uv sync
./scripts/check.sh          # ruff + mypy --strict + pytest with coverage
uv run pytest -k heap       # run a subset
uv run python benchmarks/bench_complexity.py
```

- **Tests:** 150+ tests. Each data structure is checked against Python's built-in
  equivalent on random inputs with [Hypothesis](https://hypothesis.readthedocs.io/),
  for example `HashMap` vs. `dict` and `merge_sort` vs. `sorted`.
- **Quality gates:** `ruff` (lint + format), `mypy --strict`, coverage ≥ 95 %, all
  enforced in [GitHub Actions](.github/workflows/ci.yml).
- **Workflow:** TDD (red → green → refactor), feature branches and Conventional
  Commits. See [CONTRIBUTING.md](CONTRIBUTING.md).
- **Debugging:** logs, `pdb` and reading stack traces. See [docs/debugging.md](docs/debugging.md).

## License

[MIT](LICENSE)
