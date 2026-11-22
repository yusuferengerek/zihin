#!/usr/bin/env bash
# Reproduces locally the environment CI sees, and runs the selections CI runs.
#
# **Why it exists.** Two faults of the same class broke CI in two separate rounds,
# and neither was visible locally: a test passes locally because the local
# environment is not the same as CI's.
#
# In the first round (S-49) this simulation was set up by hand for the occasion,
# it worked, and it was **deleted**. In the second round a fault of the same class
# showed up in CI again. A check set up once is a check never set up (K-99).
#
# **What it imitates.** The differences left between local and CI after CI got
# `appworld install` and the data (K-100):
#
#   1. Clean checkout: the working directory is built only from the files git
#                      sees. `results/` and `experiments/outputs/` are
#                      gitignored, so they are absent here, as they are in
#                      CI's checkout. A test that rests on a stale output file
#                      shows up here.
#   2. sys.path:       the `pytest` script is called, not `python -m pytest`.
#                      The first does not add the working directory to
#                      sys.path, and that was exactly S-49's second fault.
#
# **What it no longer imitates:** the absence of the app modules. A
# `sitecustomize` hook used to refuse importing `appworld.apps.<app>`, because CI
# did not run `appworld install`. Now it does, and imitating a machine that does
# not exist would produce false reds. `data/` is linked to the real directory for
# the same reason.
#
# **The second thing it does not imitate:** a clean `uv sync`. Dependencies come
# from the same lock and the existing virtual environment is used. A dependency
# fault shows up in CI's `Bağımlılık kurulumu` job, not here.
#
# Usage: bash scripts/ci_simulasyonu.sh

set -u
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

cd "$(dirname "$0")/.."
DEPO="$(pwd)"
SANAL="$DEPO/.venv"
CALISMA="${TMPDIR:-/tmp}/zihin-ci-simulasyonu"

if [ ! -x "$SANAL/bin/pytest" ]; then
  echo "ERROR: $SANAL/bin/pytest is missing. First run: uv sync --all-groups --frozen"
  exit 2
fi

echo "ZİHİN: CI simulation"
echo "commit : $(git rev-parse --short HEAD)"
echo "workdir: $CALISMA"
echo

# The working directory is built **from the working tree**, not from HEAD.
#
# The first version used `git worktree add HEAD` and silently tested the wrong
# thing: an uncommitted change never entered the simulation. The hook was caught in
# its own test. When I removed a test's marker and ran it, it went green, because
# the copy still carried the marked version. A check going green does not mean it
# went green looking at the right thing (K-49).
#
# Tracked files plus untracked files outside gitignore, that is, "what CI would
# see if I committed everything".
rm -rf "$CALISMA"
mkdir -p "$CALISMA"
{
  git ls-files
  git ls-files --others --exclude-standard
} | sort -u | while IFS= read -r dosya; do
  mkdir -p "$CALISMA/$(dirname "$dosya")"
  cp -p "$DEPO/$dosya" "$CALISMA/$dosya" 2>/dev/null
done

# `data/` exists in CI now (it comes from the cache). It is linked rather than
# copied: there is no reason to copy 198 MB on every run.
if [ -d "$DEPO/data" ]; then
  ln -s "$DEPO/data" "$CALISMA/data"
else
  echo "WARNING: no data/ locally; the appworld-marked tests will be skipped here too"
fi

dus=0
kos() {
  ad="$1"
  shift
  echo "--- $ad ---"
  (
    cd "$CALISMA" || exit 2
    # The `pytest` script, not `python -m pytest`: their sys.path differs.
    PATH="$SANAL/bin:$PATH" PYTHONPATH="$CALISMA" "$SANAL/bin/pytest" "$@"
  )
  sonuc=$?
  if [ "$sonuc" -ne 0 ]; then
    echo "FAILED: $ad (exit $sonuc)"
    dus=1
  fi
  echo
}

# The same selections CI's two test jobs run.
kos "Testler" -m "not model_server and not sandbox" -rs
if command -v podman > /dev/null 2>&1; then
  kos "Sandbox" -m sandbox -rs
else
  echo "--- Sandbox: no podman, skipped ---"
  echo
fi

rm -rf "$CALISMA"

if [ "$dus" -eq 0 ]; then
  echo "RESULT: CI simulation passed"
else
  echo "RESULT: CI SIMULATION FAILED: pushed as it is, CI turns red"
fi
exit "$dus"
