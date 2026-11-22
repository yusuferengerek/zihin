#!/usr/bin/env bash
# Runs a declared measurement: the check first, then exactly what was declared.
#
# **Why the command is not written here.** The conditions table declares it, and
# this script executes that row. A command written in a runner and a command
# written in a protocol are two places for one value, which is the defect three
# separate rounds were spent on (S-58, K-136, K-138).
#
# **Why the check runs first.** A condition that disagrees with its declaration
# is found before the episodes are spent, not in the manifest afterwards.
#
# Usage:
#
#     bash scripts/run_declared.sh b7l
#     bash scripts/run_declared.sh b15l b3l b7l
#
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
export PATH="$HOME/.local/bin:$PATH"

[ "$#" -gt 0 ] || { echo "usage: run_declared.sh <prefix> [prefix ...]" >&2; exit 1; }

for prefix in "$@"; do
  printf '\n=== %s: the declared conditions\n' "$prefix"
  if ! uv run python scripts/check_declared_conditions.py "$prefix"; then
    echo "FAILED: $prefix — the declaration and the run disagree; nothing was spent" >&2
    exit 1
  fi

  command="$(uv run python -c "
from zihin.declared import declared_command
print(' '.join(declared_command('$prefix')))
")"
  [ -n "$command" ] || { echo "FAILED: $prefix declares no command" >&2; exit 1; }

  printf '\n=== %s: running the declared command\n%s\n\n' "$prefix" "$command"
  started=$(date +%s)
  # shellcheck disable=SC2086
  $command
  status=$?
  printf '\n=== %s finished: exit %s, %s seconds\n' "$prefix" "$status" "$(( $(date +%s) - started ))"
  if [ "$status" -ne 0 ]; then
    echo "FAILED: $prefix exited $status; the runs after it were not started" >&2
    exit "$status"
  fi
done
