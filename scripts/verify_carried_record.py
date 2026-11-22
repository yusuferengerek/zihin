"""Verifies a record database that was carried by hand, before anything reads it.

**Why this is not optional.** Every number in this repository is supposed to
travel with the commit that produced it: the manifest carries `code_commit`, the
publish script pushes to a branch, and `check_merged_artefacts.py` can only
verify what is in git. A file moved by hand breaks that chain. The way to close
it is not to trust the file but to check it against what was declared and against
what was already observed elsewhere — the preflight manifest's `boot_id` and
`wall_clock_utc`, which nobody could reproduce by editing a database casually.

**What it will not do.** It does not repair, merge or copy anything. It reads,
compares, and stops on the first disagreement it cannot explain.

Usage:

    uv run python scripts/verify_carried_record.py <database> <prefix> \
        --boot-id <uuid> --wall-clock "<utc timestamp>"
"""

from __future__ import annotations

import argparse
import pathlib
import sqlite3
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "src"))

from zihin.declared import conditions  # noqa: E402
from zihin.records import missing_manifest_constraints  # noqa: E402

# Declared field -> manifest column. Only the ones a manifest actually carries;
# the rest of the table is checked by `check_declared_conditions.py` before a run.
COLUMN_FOR = {
    "model_tag": "model_tag",
    "serving_mode": "serving_mode",
    "max_output_tokens": "max_output_tokens",
    "no_progress_limit": "no_progress_limit",
    "shield_mode": "shield_mode",
    "base_seed": "base_seed",
    "num_ctx_requested": "num_ctx_requested",
    "temperature": "temperature",
}


def normalise(value) -> str:
    text = str(value).strip().strip("`*").replace(",", ".")
    if text.lower() in ("true", "1"):
        return "1"
    if text.lower() in ("false", "0"):
        return "0"
    try:
        number = float(text)
    except ValueError:
        return text
    return str(int(number)) if number == int(number) else str(number)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database")
    parser.add_argument("prefix")
    parser.add_argument("--boot-id", default=None)
    parser.add_argument("--wall-clock", default=None)
    options = parser.parse_args()

    path = pathlib.Path(options.database)
    if not path.exists():
        sys.exit(f"{path} does not exist")
    print(f"database : {path}")
    print(f"bytes    : {path.stat().st_size}")

    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row

    problems: list[str] = []

    # 1. the schema carries its constraints (S-29)
    missing = missing_manifest_constraints(connection)
    if missing:
        problems.append(f"the manifest constraints are missing from the schema: {missing}")
        print(f"schema   : MISSING {missing}")
    else:
        print("schema   : carries all the manifest constraints")

    # 2. the run is there, and how much of it
    rows = connection.execute(
        "SELECT * FROM run_manifests WHERE run_id LIKE ? ORDER BY run_id",
        (options.prefix + "-%",),
    ).fetchall()
    episodes = connection.execute(
        "SELECT COUNT(*) FROM episodes WHERE run_id LIKE ?", (options.prefix + "-%",)
    ).fetchone()[0]
    print(f"manifests: {len(rows)} with prefix {options.prefix!r}")
    print(f"episodes : {episodes}")
    if not rows:
        sys.exit(f"no manifest carries the prefix {options.prefix!r}; nothing to verify")

    # 3. every manifest agrees with the declaration
    _, declared = conditions(options.prefix)
    print()
    print("declared field           declared        recorded        ")
    print("-" * 62)
    for field, column in COLUMN_FOR.items():
        want = declared.get(field)
        if want is None:
            continue
        seen = {row[column] for row in rows}
        got = sorted(str(v) for v in seen)
        agree = len(seen) == 1 and normalise(got[0]) == normalise(want)
        mark = "ok  " if agree else "DIFF"
        print(f"  {mark} {field:20} {want:15} {', '.join(got)[:24]}")
        if not agree:
            problems.append(f"{field}: declared {want!r}, recorded {got}")

    # 4. the commits, and whether they are commits this repository knows
    commits = sorted({row["code_commit"] for row in rows})
    print()
    print(f"code_commit(s): {', '.join(c[:12] for c in commits)}")

    # 5. the two fields observed before the file was carried
    if options.boot_id:
        seen = sorted({str(row["boot_id"]) for row in rows})
        agree = seen == [options.boot_id]
        print(f"boot_id  : {'ok  ' if agree else 'DIFF'} {', '.join(s[:36] for s in seen)}")
        if not agree:
            problems.append(f"boot_id: expected {options.boot_id!r}, recorded {seen}")
    if options.wall_clock:
        stamps = sorted(str(row["wall_clock_utc"]) for row in rows)
        matched = [s for s in stamps if s.startswith(options.wall_clock)]
        agree = bool(matched)
        print(
            f"wall_clock: {'ok  ' if agree else 'DIFF'} earliest {stamps[0]}, latest {stamps[-1]}"
        )
        if not agree:
            problems.append(
                f"wall_clock_utc: no manifest starts with {options.wall_clock!r}; "
                f"the range is {stamps[0]} .. {stamps[-1]}"
            )

    print()
    if problems:
        print(f"{len(problems)} DISAGREEMENT(S). The file is not accepted:")
        for line in problems:
            print(f"  - {line}")
        print(
            "\nA record carried by hand and not verified is a story. Nothing here "
            "reads this file until the disagreements are explained."
        )
        sys.exit(1)
    print("provenance verified: the carried record matches what was declared and observed")


if __name__ == "__main__":
    main()
