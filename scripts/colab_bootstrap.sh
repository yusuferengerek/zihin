#!/usr/bin/env bash
# The Colab-specific half: GPU, Drive, Ollama, model. The portable half is
# `bootstrap_repo.sh`, which this calls.
#
# **Why the split.** Everything below is a fact about Colab. Everything in
# `bootstrap_repo.sh` is true of any Linux checkout, so it can be run on WSL and
# in CI as well — and a check that can only run in one environment is the class
# this repository keeps getting bitten by (K-117).
#
# **Its own limit.** This script was not executed on Colab by its author. Every
# step therefore fails loudly rather than continuing, and the guard sweep inside
# `bootstrap_repo.sh` is what says whether the environment is sound.
#
# Usage, from the notebook:
#
#     !bash scripts/colab_bootstrap.sh
#
set -Eeuo pipefail

WORKDIR="${ZIHIN_WORKDIR:-/content/zihin}"
DRIVE_ROOT="${ZIHIN_DRIVE_ROOT:-/content/drive/MyDrive/zihin}"
# Resolved after the checkout exists, in step F, from the run's own declaration.
# It used to be a default here, which is how this script pulled 14B while the
# measurement asked for 32B (K-138).
MODEL_TAG=""

# The step names, so a death can say which one it died on. Measured the hard way:
# step D failed, `set -e` ended the script, and E, F and G - the Drive database
# link, the Ollama install, the model pull - never ran and said nothing about it.
# The output stopped, and a stopped output looks like a finished one. A step that
# did not run must not be indistinguishable from a step that passed (K-128).
CURRENT_STEP="(before the first step)"
# Per-step wall clock. The design's cost projection is a LOWER bound precisely
# because per-session setup is outside the measurement window and had never been
# measured; 1845 episodes do not fit one session, so this repeats per session and
# belongs in the estimate. It is written to a file rather than printed, because a
# number that only exists in a scrollback is a number nobody can cite.
BOOTSTRAP_STARTED="$(date +%s)"
STEP_STARTED="$BOOTSTRAP_STARTED"
STEP_TIMINGS=""
close_step() {
  [ -z "$CURRENT_STEP" ] && return 0
  case "$CURRENT_STEP" in "(before the first step)"|"Colab bootstrap finished") return 0;; esac
  local now elapsed
  now="$(date +%s)"
  elapsed=$(( now - STEP_STARTED ))
  STEP_TIMINGS="${STEP_TIMINGS}${STEP_TIMINGS:+,}$(printf '{"step":"%s","seconds":%d}' "$CURRENT_STEP" "$elapsed")"
  STEP_STARTED="$now"
}
step() { close_step; CURRENT_STEP="$*"; printf '\n=== %s\n' "$*"; }
fail() { printf 'FAILED: %s\n' "$*" >&2; exit 1; }

on_error() {
  echo "" >&2
  echo "=======================================================" >&2
  echo "THE BOOTSTRAP STOPPED AT: $CURRENT_STEP" >&2
  echo "exit code $1" >&2
  echo "Every step after this one did NOT run. Ollama and the model come after" >&2
  echo "step D, so if it stopped before them they are not installed and the run" >&2
  echo "cannot start. Fix what is named above and run this cell again." >&2
  echo "=======================================================" >&2
}
trap 'on_error $?' ERR


step "A. GPU"
command -v nvidia-smi >/dev/null || fail "no nvidia-smi; switch the runtime type to a GPU"
nvidia-smi --query-gpu=name,memory.total,memory.free,driver_version --format=csv,noheader
# Nothing is decided here. The GPU is compared against the declared model's
# registry size in step E2 (`check_prerequisites.py`), and residency is decided
# after loading by `measure_colab_environment.py`. This line used to carry the
# 14B estimate against a measured T4, for a run that declares neither: the
# declared runtime is in the conditions table (`runtime`), and the model is the
# 32B.

step "B. Drive"
# Two things must survive a session: the record database and the model cache.
# Without them the model is pulled every session and the result disappears
# when the session ends.
[ -d "$(dirname "$DRIVE_ROOT")" ] || fail "Drive is not mounted; run drive.mount('/content/drive') first"
# No ollama directory here any more: the model cache lives on the runtime disk.
mkdir -p "$DRIVE_ROOT/results" "$DRIVE_ROOT/data"
echo "drive root: $DRIVE_ROOT"

step "C. Repository"
# The checkout is the notebook's job, not this script's: the repository is
# private and cloning it needs a credential. Credentials belong to the caller
# that can read Colab Secrets; this script never touches one. Measured the hard
# way — the first Colab attempt cloned without a token and git asked for a
# username nobody could answer.
[ -d "$WORKDIR/.git" ] || fail "$WORKDIR is not a checkout. The notebook clones it with the token before calling this script."
cd "$WORKDIR"
echo "commit: $(git rev-parse --short HEAD)  branch: $(git branch --show-current)"

step "D. Portable bootstrap"
# Its exit code is not this script's gate. The portable bootstrap both installs
# (LFS, dependencies, AppWorld, the data) and verifies (ruff, build, tests, the
# guard sweep). A verification that disagrees in a new environment is a report,
# not a reason to leave the machine without a model server - a new environment is
# exactly where a guard is expected to disagree (K-117). So its failure is shown
# loudly, and then what this script actually needs is checked here, by name.
if ZIHIN_DATA_CACHE="$DRIVE_ROOT/data" bash scripts/bootstrap_repo.sh; then
  echo "portable bootstrap: finished without a failure"
else
  echo ""
  echo "!!! the portable bootstrap reported a failure; its own output is above."
  echo "!!! continuing to the environment steps, then checking the requirements."
fi

# The portable bootstrap exports this for its own steps, but that export dies
# with its process. Every `uv run` below needs it too: without it uv re-syncs the
# project and goes straight back to the upstream source that refused.
export UV_NO_SYNC=1

step "D2. What the run actually requires"
# Checked here rather than inherited from someone else's exit code. If one of
# these is missing the run cannot start, whatever anything else reported.
uv run python -c "import appworld, appworld_agents" >/dev/null 2>&1 || fail "appworld or appworld_agents does not import; the install in step D did not finish"
[ -d "$WORKDIR/data/tasks" ] || fail "$WORKDIR/data/tasks is missing; the AppWorld data was not installed"
echo "appworld imports; task directories present: $(find "$WORKDIR/data/tasks" -mindepth 1 -maxdepth 1 | wc -l)"

step "E. Record database from Drive"
# The series name lives in the record layer; reading it here rather than
# repeating it means a series change moves one line, not four (K-138).
SERIES="$(uv run python -c 'from zihin.records import ACTIVE_SERIES; print(ACTIVE_SERIES)')"
SERIES_NAME="$(basename "$SERIES")"
echo "series: $SERIES_NAME"
mkdir -p "$WORKDIR/results"
# The series exists and holds the merged record (S-74, K-165). A session that
# found no file here used to start a fresh series on Drive, and a session that
# found the wrong one used to write into it: that is how series 3 split twice.
# So there is no "create" branch any more, and the file that is here is checked
# before anything can write to it: every prefix the merge left, with at least as
# many episodes, and the ledger table branch A reads (K-171, K-173).
[ -f "$DRIVE_ROOT/results/$SERIES_NAME" ] || fail "series 3 is not on Drive at $DRIVE_ROOT/results/$SERIES_NAME. Copy the merged record there first (experiments/colab/README.md); a new, empty series would split it again."
uv run python scripts/verify_series_merge.py --check --database "$DRIVE_ROOT/results/$SERIES_NAME" \
  || fail "the series on Drive is not the one the merge left, or it lacks the ledger table. Its problems are listed above; replace it with the merged record."
ln -sfn "$DRIVE_ROOT/results/$SERIES_NAME" "$WORKDIR/results/$SERIES_NAME"
echo "series 3: verified on Drive and linked; resume will skip what is already written"

step "E2. Every remaining step's prerequisites, asked at once"
# Measured cost of not doing this: five rounds, each spent on one missing
# precondition, and each round revealing the next one. The check installs nothing
# and starts nothing; it names everything that is missing and stops (K-130).
# The prefix names the run about to happen, so requirements that belong to one
# kind of run are not asked of another. Without it the check asks for the skill
# library, which a baseline run never reads (K-152).
# No prefix argument. `ZIHIN_PREFIX` used to be spliced in here and no notebook
# cell ever set it, so the expansion was always empty - a knob with no hand on
# it. The preflight resolves the prefix from the notebook's run command, which
# is the same single source the conditions check reads. To ask about another
# run, pass `--prefix` to the script directly.
uv run python scripts/setup/check_prerequisites.py || fail "prerequisites are missing. They are listed above, all of them, each with its fix."

step "F. Ollama"
# The Colab image does not carry zstd, and the Ollama installer unpacks a
# zstd-compressed bundle with it. Measured on the runtime on 2026-08-20; the
# installer failed with zstd named in its own error text.
if ! command -v zstd >/dev/null; then
  echo "zstd: absent; installing it, because the Ollama installer unpacks with it"
  APT="apt-get"
  if [ "$(id -u)" != "0" ] && command -v sudo >/dev/null; then APT="sudo apt-get"; fi
  if ! $APT install -y zstd >/tmp/zihin-zstd.log 2>&1; then
    echo "zstd: the first attempt failed; refreshing the package lists and retrying"
    $APT update >>/tmp/zihin-zstd.log 2>&1 || true
    $APT install -y zstd >>/tmp/zihin-zstd.log 2>&1 || { tail -15 /tmp/zihin-zstd.log >&2; fail "zstd could not be installed; its log is above and in /tmp/zihin-zstd.log"; }
  fi
  command -v zstd >/dev/null || fail "apt-get finished but zstd is still not on PATH; see /tmp/zihin-zstd.log"
  echo "zstd: installed, $(zstd --version 2>&1 | head -1)"
fi
# Four separate things, each with its own sentence when it fails. The previous
# form was one `||` chain: when Ollama had not been installed at all, the failure
# surfaced three steps later as "the Ollama server did not come up", which is a
# symptom of four different causes and names none of them (K-125).
OLLAMA_LOG=/tmp/zihin-ollama-install.log
if command -v ollama >/dev/null; then
  echo "ollama: already installed, $(ollama --version 2>&1 | head -1)"
else
  command -v curl >/dev/null || fail "curl is not installed, so the Ollama installer cannot be fetched. On a Debian-like runtime: apt-get install -y curl"
  echo "ollama: not installed; fetching the installer"
  if ! curl -fsSL https://ollama.com/install.sh -o /tmp/ollama-install.sh; then
    fail "the Ollama installer could not be downloaded (curl failed). Check the runtime's network, then run this cell again."
  fi
  if ! sh /tmp/ollama-install.sh > "$OLLAMA_LOG" 2>&1; then
    echo "--- the last 20 lines of the installer log ($OLLAMA_LOG)" >&2
    tail -20 "$OLLAMA_LOG" >&2
    fail "the Ollama installer exited non-zero. Its log is above and in $OLLAMA_LOG."
  fi
  command -v ollama >/dev/null || fail "the installer finished but ollama is still not on PATH. The log is in $OLLAMA_LOG; PATH is $PATH"
  echo "ollama: installed, $(ollama --version 2>&1 | head -1)"
fi
# The model cache is on the runtime disk, NOT on Drive. Drive keeps only what
# must survive the session: the record database. Two reasons, and the second is
# the reason it moved. Drive is a FUSE mount and the model is read
# through it on every load; the first Colab measurement gave a load median of
# 44.5 s with a range of 43.6 to 117.6 s, against 3.6 s locally. Drive I/O is a
# candidate for that, not a demonstrated cause — moving the cache is what makes
# it testable. The price is explicit: the model is pulled once per session
# instead of being kept, and the size is announced from the declared table.
MODEL_TAG="$(uv run python -c 'from zihin.declared import declared_model; print(declared_model())')"
# The size is read from the same table as the tag. It used to be the literal
# 8.99 GB in the line that announces the pull - the 14B's registry size, left
# behind when the declared model became the 32B, whose measured file is 19.851
# GB. A user watching a twenty-gigabyte pull was told to expect nine.
# The decimal separator is converted, not the number: the conditions table is a
# Turkish document and declares 19,851, while this line is read in English and
# "19,851 GB" reads as nineteen thousand.
MODEL_GB="$(uv run python -c 'from zihin.declared import declared_field; print(declared_field("model_file_gb").replace(",", "."))' 2>/dev/null || echo "?")"
[ -n "$MODEL_TAG" ] || fail "the model tag could not be resolved from the protocol's conditions table"
echo "model tag (from the declared conditions): $MODEL_TAG"
export ZIHIN_MODEL="$MODEL_TAG"
export OLLAMA_MODELS="${ZIHIN_MODEL_CACHE:-/content/ollama}"
mkdir -p "$OLLAMA_MODELS"
# The settings the manifest records and the resume check compares. Given here
# rather than defaulted, because they enter the measurement (§15.2).
export OLLAMA_CONTEXT_LENGTH=32768
export OLLAMA_KV_CACHE_TYPE=q8_0
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_HOST=127.0.0.1:11434
# The manifest reads the server's settings out of this file, and the configured
# default is a path on the development machine. The environment that starts the
# server is the one that knows where it logs.
export ZIHIN_SERVER_LOG=/tmp/zihin-ollama.log
if pgrep -x ollama >/dev/null; then
  echo "ollama: a server process is already running"
else
  echo "ollama: starting the server, log in /tmp/zihin-ollama.log"
  nohup ollama serve > /tmp/zihin-ollama.log 2>&1 &
fi
for _ in $(seq 1 30); do
  if curl -sf "http://$OLLAMA_HOST/api/tags" >/dev/null; then break; fi
  sleep 2
done
if ! curl -sf "http://$OLLAMA_HOST/api/tags" >/dev/null; then
  echo "--- the last 20 lines of the server log (/tmp/zihin-ollama.log)" >&2
  tail -20 /tmp/zihin-ollama.log 2>&1 >&2 || echo "(the log does not exist: the server never started)" >&2
  echo "--- ollama processes" >&2
  pgrep -a ollama >&2 || echo "(no ollama process)" >&2
  fail "the server did not answer on $OLLAMA_HOST within 60 seconds. The log and the process list are above; they say which of the two it is."
fi
echo "ollama: answering on $OLLAMA_HOST; models cached in $OLLAMA_MODELS"

step "G. Model"
# It says what it did. Two runs of this step are indistinguishable in silence -
# a pull of nine gigabytes and a cache hit look the same when neither speaks,
# and on a cache that moved off Drive this session the difference is the whole
# question.
CACHE_BEFORE="$(du -sm "$OLLAMA_MODELS" 2>/dev/null | cut -f1)"
CACHE_BEFORE="${CACHE_BEFORE:-0}"
if ollama list | grep -qF "$MODEL_TAG"; then
  echo "model: $MODEL_TAG already in the cache at $OLLAMA_MODELS"
else
  echo "model: $MODEL_TAG not in the cache; pulling it (about ${MODEL_GB} GB, once per session)"
fi
PULL_STARTED="$(date +%s)"
ollama pull "$MODEL_TAG"
PULL_SECONDS="$(( $(date +%s) - PULL_STARTED ))"
CACHE_AFTER="$(du -sm "$OLLAMA_MODELS" 2>/dev/null | cut -f1)"
CACHE_AFTER="${CACHE_AFTER:-0}"
ollama list | grep -F "${MODEL_TAG%%:*}" >/dev/null || fail "the model is absent after the pull"
echo "model: present. cache ${CACHE_AFTER} MB (grew $(( CACHE_AFTER - CACHE_BEFORE )) MB), pull took ${PULL_SECONDS}s"

step "Colab bootstrap finished"

# The artefact. It carries the total and the per-step breakdown, plus the two
# facts that decide whether a later session repeats the expensive part: whether
# the model was already cached, and how long the pull took.
BOOTSTRAP_SECONDS=$(( $(date +%s) - BOOTSTRAP_STARTED ))
BOOTSTRAP_OUTPUT="${WORKDIR}/results/colab-bootstrap.json"
mkdir -p "$(dirname "$BOOTSTRAP_OUTPUT")"
cat > "$BOOTSTRAP_OUTPUT" <<JSON
{
  "what": "how long the per-session Colab setup takes; the term missing from the cost projection",
  "measured_at_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "total_seconds": ${BOOTSTRAP_SECONDS},
  "total_minutes": $(awk "BEGIN{printf \"%.2f\", ${BOOTSTRAP_SECONDS}/60}"),
  "model_tag": "${MODEL_TAG}",
  "model_pull_seconds": ${PULL_SECONDS:-0},
  "model_was_cached": $( [ "${PULL_SECONDS:-0}" -lt 30 ] && echo true || echo false ),
  "model_cache_mb_after": ${CACHE_AFTER:-0},
  "steps": [${STEP_TIMINGS}],
  "note": "This is one session's setup. results/compute-cost.json projects episode time only, so the design's real cost is that projection plus this number once per session."
}
JSON
echo "bootstrap took ${BOOTSTRAP_SECONDS}s; written to ${BOOTSTRAP_OUTPUT}"
echo "next: uv run python scripts/setup/measure_colab_environment.py"
