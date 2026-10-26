# Complexity reference

Every structure and algorithm in `metro_router` is written from scratch. This
table lists their cost and where the application uses them.

n = number of items · V = stations · E = connections · m = length of a string

## Data structures — `src/metro_router/structures/`

| Structure | Operation | Time | Space | Used by |
|---|---|---|---|---|
| `LinkedList` | append / prepend / pop_left | O(1) | O(n) | backs `Stack` and `Queue` |
| `Stack` (LIFO) | push / pop / peek | O(1) | O(n) | iterative DFS (`reachable`) |
| `Queue` (FIFO) | enqueue / dequeue / peek | O(1) | O(n) | BFS (`bfs_path`) |
| `MinHeap` | push / pop | O(log n) | O(n) | Dijkstra frontier |
| | build from n items | O(n) | | |
| `HashMap` (separate chaining) | get / set / delete | O(1) average, O(n) worst | O(n) | graph adjacency, BFS/Dijkstra bookkeeping, trie children |
| `Trie` | insert / contains | O(m) | O(total characters) | `metro search` autocomplete |
| | starts_with | O(m + matches subtree) | | |

## Algorithms — `src/metro_router/algorithms/`

| Algorithm | Technique | Time | Space | Used by |
|---|---|---|---|---|
| `merge_sort` | divide and conquer, **recursion**, two-pointer merge | O(n log n) | O(n) | station listing, suggestion ranking |
| `lower_bound`, `binary_search` | halving the search window | O(log n) | O(1) | exact station lookup |
| `levenshtein` | **dynamic programming** (two rows) | O(n·m) | O(min(n, m)) | "Did you mean?" suggestions |
| `split_runs` | **two pointers / sliding window** | O(n) | O(n) | grouping hops into legs by line |
| `bfs_path` | breadth-first search with a queue | O(V + E) | O(V) | `route --by stops` |
| `reachable` | depth-first search with a stack (no recursion limit) | O(V + E) | O(V) | `metro check` |
| `dijkstra_path` | greedy + min-heap, lazy deletion | O((V + E) log V) | O(V + E) | `route --by time` |

## Design notes

- **Why a linked list for the queue?** `list.pop(0)` is O(n) because it shifts every
  element. The benchmark shows the difference: draining a list from the front
  grows ~4× when n doubles (O(n²) total), the linked queue ~2× (O(n) total).
- **Why both a sorted array and a trie?** Binary search answers "is this exact
  name a station?" in O(log n) with almost no extra memory. A trie answers "which
  names start with this?" without scanning everything. Each fits its job.
- **Transfer penalties make the graph bigger.** For the fastest route, Dijkstra runs on
  `(station, line)` states rather than on stations. Changing lines then becomes an
  edge with a cost. This is a standard trick: grow the state space so that a
  simple algorithm stays correct.
- **Choosing lines for the fewest-stops route.** BFS gives the station sequence.
  Then a greedy pass picks, at each hop, the line that covers the most following
  hops. This keeps line changes to a minimum, by the same argument used for
  interval covering.

## Measuring it

```bash
uv run python benchmarks/bench_complexity.py
```

Sample output (ratios are what matter — they show how time grows when n doubles):

```
experiment                     expected             2,000       4,000       8,000      16,000
---------------------------------------------------------------------------------------------
Queue: n enqueue + n dequeue   O(n)                0.80ms        1.9x        2.0x        1.9x
list.pop(0) n times            O(n²)               0.14ms        3.4x        5.4x        5.2x
200 linear searches            O(n) each           0.86ms        2.0x        1.9x        2.2x
200 binary searches            O(log n) each       0.19ms        1.0x        1.1x        1.1x
200 HashMap lookups            O(1) each           0.03ms        0.9x        1.0x        1.0x
merge_sort                     O(n log n)          2.13ms        2.3x        2.2x        2.1x
```

`list.pop(0)` starts out faster, because it runs C code that moves memory in
bulk, but it grows much faster. Big O describes growth, not raw speed.
