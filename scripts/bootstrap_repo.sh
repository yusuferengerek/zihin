#!/usr/bin/env bash
# Brings a checkout to a runnable state. Nothing here knows about Colab.
#
# **Why it is separate.** The Colab bootstrap mixed two kinds of step: things any
# Linux checkout needs (LFS, uv, dependencies, AppWorld, the data) and things only
# Colab needs (a GPU, Drive, Ollama). Mixing them means the portable half cannot be
# reused and cannot be tested anywhere else — and this repository has already
# measured what an environment-specific check costs when it cannot be run in a
# second environment (K-117).
#
# **What it deliberately does not do.** No GPU check, no model server, no cloud
# storage. If a caller needs those it adds them around this script, which is what
# `colab_bootstrap.sh` does.
#
# **Where the steps come from.** REPRODUCE.md, executed from a clean clone and
# verified; the four defects that run found are already fixed in it.
#
# Usage:
#
#     bash scripts/bootstrap_repo.sh                 # in the checkout
#     ZIHIN_DATA_CACHE=/some/dir bash scripts/bootstrap_repo.sh
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE"

DATA_CACHE="${ZIHIN_DATA_CACHE:-}"

step() { printf '\n=== %s\n' "$*"; }
fail() { printf 'FAILED: %s\n' "$*" >&2; exit 1; }

step "1. Git LFS"
# REPRODUCE.md's prerequisite: without the filter `appworld install` fails on a
# 131-byte pointer instead of a bundle. Installing the package is not enough; the
# filter has to be written into the git config.
command -v git-lfs >/dev/null || fail "git-lfs is not installed (apt-get install git-lfs)"
git lfs install --skip-repo
git lfs pull
echo "lfs: filter installed, objects pulled"

step "2. uv and dependencies"
command -v uv >/dev/null || fail "uv is not installed (https://astral.sh/uv)"
uv --version
# `--frozen` applies the lock as it stands: if the lock and pyproject.toml have
# drifted it errors instead of silently updating.
#
# **Upstream is tried first, always.** The mirror in `vendor/appworld/` exists
# because the upstream repository's Git LFS budget ran out on 2026-08-20 and the
# pinned commit's bundle objects stopped being served — measured from two
# networks, so it is upstream's state and not either network's. The mirror is a
# fallback, not a path: when upstream returns this branch stops being taken by
# itself and nothing has to be undone.
SYNC_LOG=/tmp/zihin-sync.log
APPWORLD_SOURCE=upstream
if uv sync --all-groups --frozen >"$SYNC_LOG" 2>&1; then
  tail -2 "$SYNC_LOG"
else
  tail -15 "$SYNC_LOG"
  # Only the known upstream failure takes the fallback. Any other sync failure is
  # a different problem, and a mirror that swallowed it would answer a question
  # nobody asked (K-123: a symptom is not a cause).
  grep -qi "lfs" "$SYNC_LOG" || fail "uv sync failed and the reason is not the LFS budget; see $SYNC_LOG"
  [ -d vendor/appworld ] || fail "upstream LFS refused and there is no mirror in vendor/appworld"
  echo
  echo "upstream Git LFS refused; falling back to the mirror in vendor/appworld"
  echo "provenance: vendor/appworld/PROVENANCE.json — recorded in the manifest, not silent"
  uv sync --all-groups --frozen     --no-install-package appworld --no-install-package appworld-agents     || fail "the sync failed even with the two packages left out"
  # The target environment is NAMED, not discovered. Measured: with
  # `UV_SYSTEM_PYTHON=1` in the environment — which is how a Colab runtime comes,
  # since that is what makes a bare `!uv pip install` work in a notebook —
  # `uv pip install` answers "Using Python 3.12 environment at: /usr" and puts the
  # wheels into the system interpreter while everything else lives in `.venv`.
  # The packages then exist and are still unusable (K-129). The same measurement
  # showed `uv run` is NOT affected and picks the project environment, so this one
  # line is the whole of it.
  uv pip install --no-deps --python "$HERE/.venv/bin/python" vendor/appworld/*.whl || fail "the mirror wheels did not install. If vendor/appworld contains no wheels, see vendor/appworld/README.md"
  # Where they landed, asked of the interpreter itself. Not through `uv run`: at
  # this point `UV_NO_SYNC` is not exported yet, so `uv run` would re-sync and go
  # straight back to the upstream source that just refused.
  "$HERE/.venv/bin/python" -c "import appworld, appworld_agents" >/dev/null 2>&1 || fail "the mirror wheels installed but $HERE/.venv cannot import them. They went somewhere else; the line above names the environment they went to."
  APPWORLD_SOURCE=mirror
fi

# What was actually built, printed rather than assumed. A log that names its own
# interpreter answers "which environment" without anyone having to reconstruct it.
echo "project environment: $("$HERE/.venv/bin/python" -c 'import sys; print(sys.executable, sys.version.split()[0])')"

# From here on `uv run` uses the environment as it stands. Measured: `uv run`
# re-syncs the project before every command, so on the mirror path the very next
# `uv run` goes back to the upstream git source and fails again — the fallback
# installs and is undone one line later. It is exported on both paths because
# after step 2 the environment is deliberately built, and a silent re-resolution
# in the middle of a bootstrap is not something to keep on the upstream path
# either. Callers outside this script need it too; the notebook sets it.
export UV_NO_SYNC=1

step "3. AppWorld package"
uv run appworld install
# Which source, and is it the same artefact. The bundles are hashed and compared
# with the pinned commit's LFS object ids; the answer goes into the manifest.
uv run python scripts/setup/record_appworld_source.py "$APPWORLD_SOURCE"

step "4. AppWorld data"
# The question is whether the cache **holds** the data, not whether the directory
# exists. Measured the hard way, and it cost a Colab round: the Colab bootstrap
# creates `$DRIVE_ROOT/data` on Drive before this runs, so "the directory exists"
# was true while it was empty. This linked the empty directory, skipped the
# download, and the check at the bottom failed — taking Ollama and the model
# with it, because they come after (K-127).
if [ -n "$DATA_CACHE" ] && [ -d "$DATA_CACHE/tasks" ]; then
  ln -sfn "$DATA_CACHE" "$HERE/data"
  echo "data: linked from the cache at $DATA_CACHE"
elif [ -d "$HERE/data/tasks" ]; then
  echo "data: already present"
else
  # A link left by an earlier attempt would make the download write into the
  # cache through it, and then "the cache is populated" would be true for the
  # wrong reason.
  if [ -L "$HERE/data" ]; then
    rm -f "$HERE/data"
    echo "data: an empty cache link from an earlier attempt was removed"
  fi
  uv run appworld download data
  [ -d "$HERE/data/tasks" ] || fail "appworld download data finished but data/tasks is absent"
  if [ -n "$DATA_CACHE" ]; then
    mkdir -p "$DATA_CACHE"
    cp -r "$HERE/data/." "$DATA_CACHE/"
    echo "data: downloaded and copied into the cache at $DATA_CACHE"
  fi
fi
[ -d "$HERE/data/tasks" ] || fail "the data directory is still missing after step 4"

step "5. The checks REPRODUCE.md lists"
uv run ruff check .
uv run ruff format --check .
uv run python -c "import zihin"
uv build >/dev/null
uv run pytest -m "not model_server and not sandbox" -q 2>&1 | tail -2

step "6. Every guard, once, in this environment"
# Three guards in this repository turned out to give a different answer in a
# different environment, and a clean-clone run found a fourth. A new environment
# is where a fifth shows itself (K-117), so the sweep reports rather than stops:
# the point is to see what diverges here, not to judge the environment.
guards=(
  "scripts/check_docs_parity.py"
  "scripts/build_limitations_index.py --check"
  "scripts/build_skeleton_coverage.py --check"
  "scripts/build_decisions_csv.py --check"
  "scripts/count_guards.py --check"
  "scripts/check_declared_conditions.py"
  "scripts/check_language.py"
  "scripts/check_merged_artefacts.py"
)
failed=0
for guard in "${guards[@]}"; do
  if uv run python $guard >/tmp/zihin-guard.out 2>&1; then
    printf '  ok   %s\n' "$guard"
  else
    failed=$((failed + 1))
    printf '  FAIL %s\n' "$guard"
    tail -2 /tmp/zihin-guard.out | sed 's/^/         /'
  fi
done
printf '\nguards: %d of %d disagreed in this environment\n' "$failed" "${#guards[@]}"

step "Repository bootstrap finished"
echo "commit: $(git rev-parse --short HEAD)  modified files: $(git status --porcelain | wc -l)"
