"""Merges one half of a measurement series into another, and verifies the merge.

**Why a series can be split at all.** Series 3 was run on two machines: the local
axis here, the 14B and 32B points on Colab. Each machine wrote its own file. That
is not a mistake — an append-only record cannot be written to from two places at
once — but leaving it split is: an analysis that says "read series 3" would see
half of it and report a number nobody could reproduce.

**What it will not do.** It does not rewrite, deduplicate or reconcile anything.
It appends, and it refuses when appending would not be safe:

*Colliding run ids.* Two halves that name the same run cannot be appended without
deciding which is real, and that is not a decision a script makes.

*Tables it does not understand.* `skills` and `failure_patterns` carry their own
identifiers and cross-references; if either half holds rows the merge stops
rather than guessing how they renumber.

**Integer keys are offset, not reused.** Every integer primary key in the source
is shifted past the target's maximum, and the foreign keys that point at them are
shifted by the same amount. The merge then checks `PRAGMA foreign_key_check` and
the row counts, because a merge that silently drops a child row would leave a
record that looks complete.

Usage:

    uv run python scripts/merge_series.py <target.sqlite> <source.sqlite> -o <merged.sqlite>
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
import sqlite3
import sys

# Child tables in dependency order, with the key to offset and the parent key to
# follow. Order matters: a child is inserted only after its parent exists.
PLAN = (
    ("episodes", "episode_id", None),
    ("steps", "step_id", ("episode_id", "episodes")),
    ("actions", "action_id", ("step_id", "steps")),
    ("observations", "observation_id", ("step_id", "steps")),
    ("shield_violations", "violation_id", ("step_id", "steps")),
    ("verifier_results", "verifier_result_id", ("episode_id", "episodes")),
)
UNHANDLED = ("skills", "failure_patterns")


def columns(connection: sqlite3.Connection, table: str) -> list[str]:
    return [row[1] for row in connection.execute(f"PRAGMA table_info({table})")]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target")
    parser.add_argument("source")
    parser.add_argument("-o", "--output", required=True)
    options = parser.parse_args()

    target_path = pathlib.Path(options.target)
    source_path = pathlib.Path(options.source)
    out_path = pathlib.Path(options.output)
    for path in (target_path, source_path):
        if not path.exists():
            sys.exit(f"{path} does not exist")

    source = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True)
    source.row_factory = sqlite3.Row

    # Refusals, before anything is copied.
    for table in UNHANDLED:
        count = source.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        if count:
            sys.exit(
                f"{source_path} holds {count} row(s) in {table}, whose identifiers this "
                "merge does not know how to renumber. Nothing was written."
            )

    target_read = sqlite3.connect(f"file:{target_path}?mode=ro", uri=True)
    target_read.row_factory = sqlite3.Row
    target_runs = {r[0] for r in target_read.execute("SELECT run_id FROM run_manifests")}
    source_runs = {r[0] for r in source.execute("SELECT run_id FROM run_manifests")}
    shared = sorted(target_runs & source_runs)
    if shared:
        sys.exit(
            f"{len(shared)} run id(s) are in both halves: {shared[:5]}. Appending would "
            "mean choosing which one is the record, and that is not a choice this "
            "script makes. Nothing was written."
        )

    before = {
        table: target_read.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table, _, _ in PLAN
    }
    before["run_manifests"] = target_read.execute("SELECT COUNT(*) FROM run_manifests").fetchone()[
        0
    ]
    coming = {
        table: source.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table, _, _ in PLAN
    }
    coming["run_manifests"] = source.execute("SELECT COUNT(*) FROM run_manifests").fetchone()[0]

    # The merge is built as a new file. The two halves are left untouched, so a
    # merge that turns out wrong costs nothing.
    shutil.copy2(target_path, out_path)
    merged = sqlite3.connect(out_path)
    merged.execute("PRAGMA foreign_keys = ON")

    offsets: dict[str, int] = {}
    for table, key, _ in PLAN:
        top = merged.execute(f"SELECT COALESCE(MAX({key}), 0) FROM {table}").fetchone()[0]
        offsets[table] = top

    print(f"target : {target_path}")
    print(f"source : {source_path}")
    print(f"merged : {out_path}")
    print(f"offsets: {offsets}")
    print()

    names = columns(merged, "run_manifests")
    placeholders = ", ".join("?" for _ in names)
    for row in source.execute("SELECT * FROM run_manifests"):
        merged.execute(
            f"INSERT INTO run_manifests ({', '.join(names)}) VALUES ({placeholders})",
            tuple(row[name] for name in names),
        )

    for table, key, parent in PLAN:
        names = columns(merged, table)
        placeholders = ", ".join("?" for _ in names)
        shift = offsets[table]
        parent_shift = offsets[parent[1]] if parent else 0
        parent_key = parent[0] if parent else None
        for row in source.execute(f"SELECT * FROM {table}"):
            values = []
            for name in names:
                value = row[name]
                if name == key and value is not None:
                    value = value + shift
                elif parent_key and name == parent_key and value is not None:
                    value = value + parent_shift
                values.append(value)
            merged.execute(
                f"INSERT INTO {table} ({', '.join(names)}) VALUES ({placeholders})",
                tuple(values),
            )
    merged.commit()

    # Verification. A merge is a claim about rows; it is checked, not asserted.
    problems: list[str] = []
    print(f"{'table':20} {'before':>7} {'added':>7} {'after':>7}")
    for table in ["run_manifests"] + [t for t, _, _ in PLAN]:
        after = merged.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        want = before[table] + coming[table]
        mark = "" if after == want else "  MISMATCH"
        print(f"{table:20} {before[table]:7} {coming[table]:7} {after:7}{mark}")
        if after != want:
            problems.append(f"{table}: expected {want} rows, found {after}")

    broken = merged.execute("PRAGMA foreign_key_check").fetchall()
    if broken:
        problems.append(f"{len(broken)} foreign key violation(s) after the merge")
    print(f"\nforeign keys: {'clean' if not broken else str(len(broken)) + ' broken'}")

    # Every run that was in either half is in the merged file, with its episodes.
    for prefix_source, label in ((target_read, "target"), (source, "source")):
        for row in prefix_source.execute("SELECT run_id, COUNT(*) n FROM episodes GROUP BY run_id"):
            after = merged.execute(
                "SELECT COUNT(*) FROM episodes WHERE run_id = ?", (row["run_id"],)
            ).fetchone()[0]
            if after != row["n"]:
                problems.append(
                    f"{label} run {row['run_id']}: {row['n']} episodes before, {after} after"
                )

    if problems:
        print(f"\n{len(problems)} PROBLEM(S); the merged file is not to be used:")
        for line in problems:
            print(f"  - {line}")
        sys.exit(1)
    print("\nmerge verified: every row is present and every reference resolves")


if __name__ == "__main__":
    main()
