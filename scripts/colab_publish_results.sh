#!/usr/bin/env bash
# Pushes the Colab run's results into the repository, on their own branch.
#
# **Why the repository and not Drive.** Two mechanisms were considered.
#
# *Drive, read later from `/mnt/c`.* Needs no token, but it creates a second copy
# that can drift from the first, and — the deciding reason — a file on Drive has
# no commit identity. This repository's whole discipline is that every number
# travels with the commit that produced it: the manifest carries `code_commit`,
# the reports name a series, and `check_merged_artefacts.py` can only verify what
# is in git. A result read off Drive would be a number nobody can bind to a tree
# state, which is the thing K-116 was written about.
#
# *A push from the notebook.* Costs a token, and gives the result a commit. The
# manifest's `code_commit` then points at code that is reachable, the artefact
# check covers it, and the run can be re-derived. That is the one chosen.
#
# **What it will not do.** It never pushes to `main` and never force-pushes. The
# results land on their own branch and a person merges them, so an automated push
# can add history but never rewrite it.
#
# **The token.** Read from Colab Secrets by the notebook and passed in the
# environment. It is never written to a file, never echoed, and never committed.
# It also never enters `argv` or the remote URL: git reads it through an askpass
# helper. That is not caution, it is a measured lesson — the first form put the
# token in a clone URL, the clone failed, and Python's `CalledProcessError`
# printed `process.args`, so the secret left the runtime inside a traceback and
# had to be revoked (K-124). `~/.zihin-env` does not apply on Colab — that file
# is a WSL arrangement.
#
# Usage, from the notebook:
#
#     GITHUB_TOKEN=... bash scripts/colab_publish_results.sh b14
#
set -euo pipefail

# The prefix is resolved from the run's own declaration, the same source the run
# uses. It was an argument here and an argument in the run command - one value in
# two places, and a publish that reads a prefix nobody ran finds an empty set
# (K-138). An argument still overrides, for republishing an older run by hand.
PREFIX="${1:-}"
if [ -z "$PREFIX" ]; then
  PREFIX="$(uv run python -c 'from zihin.declared import run_prefix; print(run_prefix())')"
fi
[ -n "$PREFIX" ] || { echo "the run prefix could not be resolved" >&2; exit 1; }
WORKDIR="${ZIHIN_WORKDIR:-/content/zihin}"
BRANCH="${ZIHIN_RESULT_BRANCH:-colab-sonuclari}"
SLUG="${ZIHIN_REPO_SLUG:-yusuferengerek/zihin}"

cd "$WORKDIR"
[ -n "${GITHUB_TOKEN:-}" ] || { echo "GITHUB_TOKEN is not set; the notebook reads it from Colab Secrets" >&2; exit 1; }

CODE_COMMIT="$(git rev-parse HEAD)"

# **Was anything produced at all.** Asked before anything is staged, because the
# two answers below are not the same answer and the old script gave them the same
# words. An empty results directory is not the result of a successful run; it is
# the absence of a run. Measured the hard way: the scan never started, and the
# script's only complaint was a KeyError from a variable nobody had exported.
SUMMARY="$(PREFIX="$PREFIX" uv run python - <<'PY'
import os
import sqlite3
import sys

prefix = os.environ.get("PREFIX")
if not prefix:
    sys.exit(
        "PREFIX is not in the environment. The shell variable exists but was "
        "never exported, so this block could not read it. A missing value must "
        "say its own name (K-125)."
    )
from zihin.records import ACTIVE_SERIES

db = ACTIVE_SERIES
if not os.path.exists(db):
    sys.exit(
        f"{db} does not exist. NO RESULT WAS PRODUCED: the scan did not run, or "
        "it wrote somewhere else. This is not 'nothing to publish' - there is "
        "nothing to publish because there is nothing."
    )
connection = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
connection.row_factory = sqlite3.Row
rows = connection.execute(
    "SELECT e.termination_reason t, COALESCE(v.passed,0) p FROM episodes e "
    "LEFT JOIN verifier_results v USING(episode_id) WHERE e.run_id LIKE ?",
    (prefix + "-%",),
).fetchall()
if not rows:
    total = connection.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
    sys.exit(
        f"the database holds {total} episode(s) but none with the prefix "
        f"{prefix!r}. NO RESULT WAS PRODUCED FOR THIS RUN. An empty set is not a "
        "successful run with nothing to say."
    )
term: dict = {}
for row in rows:
    term[row["t"]] = term.get(row["t"], 0) + 1
print(f"epizot {len(rows)}, gecen {sum(r['p'] or 0 for r in rows)}, sonlanma {term}")
PY
)" || { echo "$SUMMARY" >&2; exit 1; }
echo "$SUMMARY"

# **A link is not a database.** The bootstrap links `results/zihin-3.sqlite` to
# Drive so the record survives the session, and `git add` on a symlink stores the
# link *target* - fifty-one bytes of path. Measured: the first published run put
# a 51-byte blob on the branch and the episodes stayed on somebody's Drive. What
# is published has to be the bytes, so a link is dereferenced here.
for database in results/*.sqlite; do
  [ -e "$database" ] || continue
  if [ -L "$database" ]; then
    target="$(readlink -f "$database")"
    [ -f "$target" ] || { echo "$database points at $target, which does not exist" >&2; exit 1; }
    rm -f "$database"
    cp "$target" "$database"
    echo "results: $database was a link to $target; the bytes are published instead"
  fi
done

# Only results. Source changes are never published from a runtime: the code that
# ran has to be the code that was reviewed, and a push that carries both would
# make "which commit produced this number" unanswerable.
git add -f results/*.json results/*.sqlite 2>/dev/null || true

# The guard for the line above, because a green `git add` proved nothing here.
# Mode 120000 is a symlink blob; 100644 is a file.
for staged in $(git ls-files -s results/ | awk '$1 == "120000" {print $4}'); do
  echo "$staged is staged as a symlink, not as content. Publishing it would push a path." >&2
  exit 1
done
if git diff --cached --quiet; then
  # Reached only when episodes exist: the run produced results and they are
  # already in the tree. That is a different sentence from the ones above.
  echo "the run produced results and they are already published; nothing new to push"
  exit 0
fi

git config user.email "colab@zihin.local"
git config user.name "zihin colab runner"
git checkout -q -B "$BRANCH"

git commit -q -m "colab sonuçları: ${PREFIX}

Colab çalışma zamanından itilen ölçüm çıktıları. Yalnız results/ altındaki
dosyalar; kaynak değişikliği bu yoldan hiç gelmiyor.

${SUMMARY}

Koşan kod: ${CODE_COMMIT}
Yorum ve şartlar: experiments/setup-protocol.tr.md §15, koşudan önce yazıldı."

# The credential reaches git through the environment, not the command line.
ASKPASS=/tmp/zihin-askpass.sh
cat > "$ASKPASS" <<'HELPER'
#!/bin/sh
case "$1" in
  Username*) echo "x-access-token" ;;
  *) echo "$GITHUB_TOKEN" ;;
esac
HELPER
chmod 700 "$ASKPASS"
export GIT_ASKPASS="$ASKPASS" GIT_TERMINAL_PROMPT=0
URL="https://github.com/${SLUG}.git"

git push -q "$URL" "HEAD:${BRANCH}"

# K-116: the push is verified, not assumed. A green-looking step that pushed
# nothing is exactly the failure this repository already paid for once.
REMOTE="$(git ls-remote "$URL" "refs/heads/${BRANCH}" | cut -f1)"
LOCAL="$(git rev-parse HEAD)"
if [ "$REMOTE" = "$LOCAL" ]; then
  echo "published: ${BRANCH} at ${LOCAL}"
else
  echo "PUSH DID NOT LAND: local ${LOCAL}, remote ${REMOTE:-<none>}" >&2
  exit 1
fi
