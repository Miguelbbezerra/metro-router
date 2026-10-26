#!/usr/bin/env bash
# Run every quality gate the CI runs: lint, format, types and tests with coverage.
# Usage: ./scripts/check.sh
set -euo pipefail

cd "$(dirname "$0")/.."

step() { printf '\n\033[1;34m==> %s\033[0m\n' "$1"; }

step "ruff (lint)"
uv run ruff check .

step "ruff (format)"
uv run ruff format --check .

step "mypy (strict)"
uv run mypy

step "pytest (with coverage)"
uv run pytest --cov --cov-report=term-missing:skip-covered

printf '\n\033[1;32mAll checks passed.\033[0m\n'
