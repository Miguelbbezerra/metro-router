#!/usr/bin/env bash
# Show how `metro` composes with other Unix tools through pipes.
# Usage: ./scripts/demo.sh
set -euo pipefail

cd "$(dirname "$0")/.."
metro() { uv run --quiet metro "$@"; }

# Read one field from JSON on stdin; uses jq when available, Python otherwise.
json_field() {
    if command -v jq >/dev/null 2>&1; then
        jq -r ".$1"
    else
        python3 -c "import json, sys; print(json.load(sys.stdin)['$1'])"
    fi
}

echo "# How many stations are there?"
metro stations | wc -l

echo
echo "# Which Line 1 stations start with 'S'?"
metro stations --line 1 | grep '^S'

echo
echo "# Minutes from Sé to every Line 4 station (sorted, fastest first)"
metro stations --line 4 \
    | while read -r station; do
        minutes=$(metro route "Sé" "$station" --format json | json_field total_minutes)
        printf '%6s min  %s\n' "$minutes" "$station"
    done \
    | sort -n

echo
echo "# Exit codes are scriptable: search exits 1 when nothing matches"
if metro search "xyz" >/dev/null; then
    echo "found something"
else
    echo "no station starts with 'xyz' (exit code $?)"
fi
