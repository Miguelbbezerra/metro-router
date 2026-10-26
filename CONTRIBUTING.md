# Contributing

## Setup

```bash
git clone https://github.com/Miguelbbezerra/metro-router.git
cd metro-router
uv sync              # creates .venv and installs dev dependencies from uv.lock
./scripts/check.sh   # lint, format, types and tests: the same gates CI runs
```

## Workflow

1. **Branch from `main`**, named after the type of change:
   `feat/…`, `fix/…`, `docs/…`, `chore/…`, `refactor/…`.
   ```bash
   git switch main && git pull
   git switch -c feat/interactive-mode
   ```
2. **Work in TDD cycles.** Write a failing test (red), make it pass with the smallest
   change (green), clean up while the tests stay green (refactor).
3. **Commit small, logical changes** using [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat(planner): support per-segment travel times
   fix(cli): exit 1 when the network file is empty
   ```
4. **Open a pull request** against `main`. CI must be green before merging.
   Merge with a merge commit (`--no-ff`) so the history shows each feature branch.

## Resolving merge conflicts

If `main` moved while you were working:

```bash
git switch feat/my-change
git merge main             # or: git rebase main
# Git marks conflicting regions in the files:
#   <<<<<<< HEAD           your version
#   =======
#   >>>>>>> main           incoming version
# Edit each file to the correct final content and remove the markers, then:
git add <file>
git commit                 # (or `git rebase --continue`)
./scripts/check.sh         # never push a resolution you have not tested
```

## Code standards

- `ruff` for linting and formatting, `mypy --strict` for types. Both run in CI.
- Google-style docstrings on public functions and classes, including Big O for
  structures and algorithms.
- Production code must not use `heapq`, `bisect`, `collections.deque` or `sorted`.
  Tests may use them as oracles to check the hand-written versions.
