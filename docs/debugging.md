# Debugging guide

## 1. Turn on logs

Every module logs through `logging` under the `metro_router` namespace. Logs go to
**stderr**, so they never mix with the output you pipe into other tools:

```bash
uv run metro --verbose route "Sé" "Paulista"
# DEBUG metro_router.network: loading network from <bundled sao_paulo.json>
# DEBUG metro_router.network: parsed 4 lines and 61 stations
# DEBUG metro_router.planner: planning Sé -> Paulista by time
```

```bash
uv run metro --verbose route Sé Paulista --format json 2>debug.log | jq .total_minutes
```

## 2. Read the stack trace

Expected problems, such as an unknown station or a broken network file, become one
line on stderr with exit code 1. Anything else is a bug, and the full traceback is
printed on purpose. Read it **from the bottom up** (illustrative example):

```
Traceback (most recent call last):
  File ".../metro_router/cli.py", line 38, in main          ← where it entered
    return command(args, network)
  File ".../metro_router/planner.py", line 112, in plan
    ...
  File ".../metro_router/graph.py", line 71, in edge_on     ← where it failed
    raise KeyError((first, second, line))
KeyError: ('Sé', 'Luz', '4')                               ← what failed
```

1. The last line gives the exception type and its value.
2. The last frame shows the line that raised it.
3. Walk up the frames until you reach the first one in *your* code that passed
   a wrong value.

## 3. Use the debugger (`pdb`)

Add a breakpoint anywhere:

```python
breakpoint()  # stops here; type `help` in the prompt
```

Or start the CLI under the debugger without touching code:

```bash
uv run python -m pdb -m metro_router route Sé Paulista
(Pdb) b metro_router/planner.py:112   # set breakpoint
(Pdb) c                               # continue until it is hit
(Pdb) p hops                          # print a variable
(Pdb) n / s / u / d                   # next line, step into, frame up, frame down
```

Useful pytest flags:

| Command | What it does |
|---|---|
| `uv run pytest -x` | stop at the first failure |
| `uv run pytest -k dijkstra` | run only tests whose name matches |
| `uv run pytest --pdb` | open the debugger at the failing assertion |
| `uv run pytest -l` | show local variables in tracebacks |
| `uv run pytest --lf` | re-run only the tests that failed last time |

## 4. Property-based test failures

When a `hypothesis` test fails, it **shrinks** the input to the smallest example
that still fails and prints it, for example `values=[0, -1]`. Copy that input into a
normal example-based test. Hypothesis also stores failing inputs in `.hypothesis/`
and replays them first on the next run.

## 5. Scratch experiments

For quick experiments, use a `scratch.py` at the project root. It is in
`.gitignore`, so experiments never end up in a commit:

```bash
uv run python scratch.py
```
