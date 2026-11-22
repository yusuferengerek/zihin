#!/usr/bin/env bash
# Checks run on this machine before every stage merge.
#
# What it runs, in order:
#   1. `pytest -m "appworld or model_server"`. The `model_server` tests need a
#      running Ollama server, which CI does not have; one of them checks that the
#      effective context window is 32768. The `appworld` tests run in CI as well
#      since K-100, the per-episode database reset among them.
#   2. The CI simulation (`ci_simulasyonu.sh`): CI's two test selections in a clean
#      checkout, `not model_server and not sandbox` and, when podman is present,
#      `sandbox`. Together with step 1 that is the whole suite.
#   3. The language check, then citations, dates, merged-PR artefacts, the Colab
#      notebook, and the `--check` modes of the touched-task list, the series merge
#      and the experiment sets. Some need what CI does not have: the record and
#      `results/` (the language check), the whole git history (the dates) and an
#      authenticated `gh` (the merged-PR artefacts).
#
# The `model_server` tests need the server's address:
#   MODEL_SERVER_URL=http://127.0.0.1:11434 bash scripts/local_checks.sh
set -u
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export PATH="$HOME/.local/bin:$PATH"

cd "$(dirname "$0")/.."

echo "ZİHİN: local-only checks"
echo "date  : $(date --iso-8601=seconds)"
echo "commit: $(git rev-parse --short HEAD)"
echo

echo "=== 1/3: local-only tests ==="
uv run pytest -m "appworld or model_server"
yerel=$?

# The CI simulation is part of this script, not a separate habit. The reason was
# measured: two faults of the same class broke CI in two separate rounds, and in
# the first one the simulation had been set up by hand and then deleted. A check
# set up once is a check never set up.
echo
echo "=== 2/3: CI simulation ==="
bash "$(dirname "$0")/ci_simulasyonu.sh"
simulasyon=$?

# The language check is wired here, not into a tool run by hand. The reason was
# measured: the first round of the language migration used a scanner that looked
# for diacritics, Turkish without diacritics got through, and the leftover was
# found after the PR merged. A check set up once is a check never set up (K-99).
echo
echo "=== 3/3: language check ==="
uv run python scripts/check_language.py | tail -4
dil=${PIPESTATUS[0]}

# Does every citation in the presentation skeleton and the pilot report resolve.
# A check that runs once is a check that never ran (K-99): this scan found two
# stale citations and a number without an artefact, and both had been seen only
# because someone looked by hand.
echo
echo "=== extra: citations ==="
uv run python scripts/check_citations.py | tail -3
atif=${PIPESTATUS[0]}

# Does every addendum that dates itself match the date of the commit that wrote it
# (K-140). A pre-registration is worth what its dates are worth: "declared before
# the run" is a claim about time, and only the record settles it. One addendum
# dated itself four days before the run; it was in fact four hours.
echo
echo "=== extra: dates ==="
uv run python scripts/check_dates.py | tail -4
tarih=${PIPESTATUS[0]}

# Do the artefacts named in merged PR reports exist in main's tree. A narrow
# check: file presence only. The risk it targets has one shape and happened once:
# the branch's last commit is not pushed, earlier pushes keep CI green, the PR
# merges and everything in that commit is lost (K-116). Local, because it needs
# `gh` and the network. Its blind spot is in S-64: its subject is merged PRs, so
# work that never merged does not exist for this check.
echo
echo "=== extra: merged-PR artefacts ==="
uv run python scripts/check_merged_artefacts.py | tail -3
eser=${PIPESTATUS[0]}

# Every notebook cell, against every script it calls and the declared conditions.
# It runs in CI too, and here as well, because the twelve faults fixed in that
# round were all found only by running on Colab, and each one cost a session.
echo
echo "=== extra: Colab notebook ==="
uv run python scripts/check_colab_notebook.py | tail -3
defter=${PIPESTATUS[0]}

# The touched-task list, derived again from the record and compared. Local, because
# the record is not in git and CI cannot see it; CI checks the file's structure and
# the derivation on synthetic records (tests/test_touched_tasks.py). The list fell
# four tasks behind the record once, all four in the evaluation sample (K-166).
echo
echo "=== extra: touched-task list against the record ==="
uv run python scripts/setup/build_touched_tasks.py --check | tail -1
touched=${PIPESTATUS[0]}

# Series 3 still holds what the merge left, and the ledger table. The series was
# overwritten once by a file without four prefixes and nothing asked (S-74); the
# merge's own verification ran once, and a check that runs once did not run.
echo
echo "=== extra: series 3 against what the merge left ==="
uv run python scripts/verify_series_merge.py --check | tail -1
series=${PIPESTATUS[0]}

# The experiment's analysis sets, built again from the runner's own slots. Local
# for the same reason as the touched list: the library is in the record (K-184).
echo "=== extra: experiment analysis sets against the runner's slots ==="
uv run python scripts/setup/measure_experiment_sets.py --check | tail -1
sets=${PIPESTATUS[0]}

echo
if [ "$yerel" -eq 0 ] && [ "$simulasyon" -eq 0 ] && [ "$dil" -eq 0 ] && [ "$eser" -eq 0 ] && [ "$atif" -eq 0 ] && [ "$tarih" -eq 0 ] && [ "$defter" -eq 0 ] && [ "$touched" -eq 0 ] && [ "$series" -eq 0 ] && [ "$sets" -eq 0 ]; then
  echo "RESULT: passed"
  exit 0
fi
echo "RESULT: FAILED (local-only $yerel, CI simulation $simulasyon, language $dil, artefacts $eser, citations $atif, dates $tarih, touched-list $touched, series $series, sets $sets)"
exit 1
