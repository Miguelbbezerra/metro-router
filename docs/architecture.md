---
purpose: Architecture design for metro-router
---

# Architecture — metro-router

## 1. Requirements

### Functional

- Load a metro network (lines, ordered stations, segment times, walking transfers) from a JSON file.
  A São Paulo network ships with the package; users can pass their own file with `--network`.
- `metro route A B` — fastest route (minutes), counting a penalty for changing lines.
- `metro route A B --by stops` — route with the fewest stations.
- Output itinerary as legs ("Take Line 1-Azul from Sé, ride 4 stops to Paraíso") as text or JSON.
- `metro search <prefix>` — autocomplete station names.
- `metro stations [--line ID]` — alphabetical station listing (or one line, in order).
- `metro lines` — list lines with their station counts.
- `metro check` — validate a network file (every station reachable from every other).
- Accent- and case-insensitive station names (`se` → `Sé`), with "did you mean?" suggestions on typos.

### Non-functional

- Educational/portfolio goal: the core data structures and algorithms are implemented from
  scratch (no `heapq`, `collections.deque`, `bisect`, `sorted`), each with documented Big O.
- Zero runtime dependencies (stdlib only).
- Fully typed (`mypy --strict`), linted (`ruff`), tested (`pytest` + `hypothesis`, ≥ 95 % coverage).
- Unix-friendly CLI: meaningful exit codes, errors on stderr, `--format json` for piping into `jq`,
  `--verbose` logging for debugging.

## 2. Technology selection

### Selected

| Tool | Purpose | Why |
|---|---|---|
| `uv` | Packaging, venv, lockfile | Fast, single tool, reproducible `uv.lock` |
| `argparse` (stdlib) | CLI parsing | No dependency needed for 5 subcommands |
| `json` / `pathlib` / `importlib.resources` (stdlib) | File I/O, bundled data | Stdlib, portable |
| `logging` (stdlib) | Diagnostics | Standard, controllable via `--verbose` |
| `pytest`, `pytest-cov` | Tests, coverage | De facto standard |
| `hypothesis` | Property-based tests | Compares each structure against Python built-ins over random inputs |
| `ruff`, `mypy` | Lint/format, strict typing | Modern standard tooling |

### Rejected

| Option | Reason |
|---|---|
| `networkx` | Would hide the graph algorithms the project exists to demonstrate |
| `click` / `typer` | Nice, but a dependency for something `argparse` handles fine |
| `heapq`, `deque`, `bisect` | Used only as test oracles, never in production code — the point is to build them |

## 3. Patterns

- **Pipes & Filters (lightweight):** `load JSON → validate → build Graph → search → segment → format`.
  Each stage is a pure function, which keeps every stage independently testable.
- **Value Objects:** `Edge`, `Line`, `Hop`, `Leg`, `Itinerary` are frozen dataclasses.
- **Dependency inversion for algorithms:** graph algorithms take a `neighbors(node)` callable instead
  of a concrete graph class, so the same Dijkstra runs on the station graph or on the
  `(station, line)` state graph used for transfer penalties.

No other patterns are needed.

## 4. Architecture

```
          ┌──────────────────────────── cli.py ────────────────────────────┐
 argv ──▶ │ argparse → commands → formatters (text / json) → stdout/stderr │ ──▶ exit code
          └──────┬──────────────────────┬───────────────────────┬──────────┘
                 │                      │                       │
          network.py              planner.py              station_index.py
   (load + validate JSON,    (fastest / fewest stops,   (merge sort + binary search
    build Graph)              legs via segmentation)     exact lookup, Trie prefix,
                 │                      │                 Levenshtein suggestions)
                 ▼                      ▼                       │
            graph.py ◀──────── algorithms/ ◀────────────────────┘
       (adjacency on HashMap)   graph_search  (BFS·Queue, DFS·Stack, Dijkstra·MinHeap)
                 │              sorting       (merge sort — recursion)
                 ▼              searching     (binary search / lower bound)
          structures/           edit_distance (Levenshtein — dynamic programming)
   LinkedList → Stack, Queue    segments      (two pointers / sliding window)
   MinHeap · HashMap · Trie
```

| Component | Responsibility |
|---|---|
| `structures/` | Generic containers: `LinkedList`, `Stack`, `Queue`, `MinHeap`, `HashMap`, `Trie` |
| `algorithms/` | Pure, generic algorithms; no knowledge of metros |
| `text.py` | Name normalisation (strip accents, casefold) |
| `graph.py` | Undirected multigraph of stations; edges carry `line` and `minutes` |
| `network.py` | Parse + validate JSON into a `Network` (graph + line metadata) |
| `station_index.py` | Resolve user input to a station; autocomplete; suggestions |
| `planner.py` | Turn a search result into an `Itinerary` of `Leg`s |
| `cli.py` | Argument parsing, output formatting, exit codes, logging setup |

### Error handling

All domain errors derive from `MetroRouterError` (`NetworkFileError`, `StationNotFoundError`,
`NoRouteError`). The CLI catches only that base class, prints a one-line message to stderr and
exits with code `1` (usage errors exit `2`, via argparse). Unexpected exceptions keep their
traceback, because hiding bugs makes debugging harder.

## 5. Data layer

No database. Static JSON file:

```json
{
  "name": "São Paulo Metro",
  "transfer_minutes": 5,
  "lines": [{"id": "1", "name": "Azul", "color": "#0455A1",
             "segment_minutes": 2, "stations": ["Tucuruvi", "..."]}],
  "walkways": [{"from": "Paulista", "to": "Consolação", "minutes": 6}]
}
```

Travel times are uniform per line and approximate — this is a demonstration dataset, not an
official timetable.

## 6. TDD-ready implementation plan

1. **LinkedList** — append/prepend/pop-left/iterate; test: order preserved vs `list` (hypothesis).
2. **Stack / Queue** — LIFO/FIFO on top of LinkedList; test: behaves like `list` / `deque`.
3. **MinHeap** — push/pop/peek; test: pop order equals `sorted(values)`.
4. **HashMap** — set/get/delete/resize; test: behaves like `dict` under random operations.
5. **Trie** — insert/starts_with; test: equals filtering a list by `startswith`.
6. **merge_sort / binary_search** — test: equals `sorted` / `bisect_left`.
7. **levenshtein** — test: known pairs + symmetry/identity properties.
8. **split_runs** — test: groups consecutive equal keys.
9. **bfs / reachable / dijkstra** — test on small hand-made graphs.
10. **text.normalize** — test: accents and case removed.
11. **Graph + network loader** — test: valid file builds graph; invalid files raise `NetworkFileError`.
12. **StationIndex** — test: resolve, autocomplete, suggestions.
13. **Planner** — test: fastest vs fewest-stops on a toy network with a transfer trade-off.
14. **CLI** — test: each subcommand's output and exit codes via `main(argv)`.

## 7. Open questions

None blocking. Future ideas: real per-segment times, CPTM lines, an interactive mode.
