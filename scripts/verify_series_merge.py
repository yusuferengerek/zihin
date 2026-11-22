"""Records what a series merge restored, and shows it changed nothing else.

**Why `merge_series.py` is not enough on its own.** It proves that every row
arrived and every reference resolves. It does not say whether the rows that
arrived are the rows that left, whether the series now holds every run its
artefacts say it holds, or whether anything that was mined from the series before
the merge would be mined differently after it. Those three questions are what a
merge that restores a lost half has to answer, so they are answered here and
written down (S-74).

**What it compares.**

1. *Content, not only counts.* Every run in either half has a fingerprint - task,
   seed, termination, model calls, tokens, step and action counts, the verdict,
   and a digest of the generated code - and the fingerprint in the merged file is
   compared with the one it came from.
2. *The artefacts' claim.* Every scan artefact that names this series as its
   `database` must find its prefix there. That claim was false for four of them
   between 2026-09-13 and this merge, and nothing asked.
3. *The corpus rule.* The library and the index were mined from the declared
   model's `train` episodes (K-159). The number of episodes that rule selects is
   compared before and after: if it moved, the library would have been mined from
   a different corpus than the one the merged series now holds.

**The standing check (`--check`).** A check that runs once is a check that did
not run. The merge wrote down how many episodes each prefix held when it was done;
the record is append-only, so from then on every prefix must still be there with
at least that many. A prefix that shrank or vanished means the file at
`ACTIVE_SERIES` was replaced - which is how the split in `S-74` happened, and
nothing asked. The same mode asks for the ledger table branch A reads (`K-171`).
It writes nothing, and it takes `--database` so a Colab session can point it at
the copy on Drive before anything writes there.

Usage:

    uv run python scripts/verify_series_merge.py --before <old.sqlite> \
        --source <restored-half.sqlite> --merged <merged.sqlite>
    uv run python scripts/verify_series_merge.py --check
    uv run python scripts/verify_series_merge.py --check --database <path>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sqlite3
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "src"))

from zihin.declared import declared_model  # noqa: E402
from zihin.records import ACTIVE_SERIES, table_matches_schema  # noqa: E402

OUTPUT = REPOSITORY / "results/series-3-merge.json"
# The run whose declaration names the model the library was mined from.
CORPUS_RUN = "bir1"
CORPUS_SPLIT = "train"


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprints(connection: sqlite3.Connection) -> dict[str, tuple]:
    """Run id -> what that run's episode was, in enough detail to tell two apart."""
    found = {}
    episodes = connection.execute(
        "SELECT episode_id, run_id, task_id, seed, termination_reason, total_model_calls, "
        "input_tokens, output_tokens FROM episodes"
    ).fetchall()
    for episode_id, run_id, *fields in episodes:
        steps = connection.execute(
            "SELECT COUNT(*) FROM steps WHERE episode_id = ?", (episode_id,)
        ).fetchone()[0]
        actions = connection.execute(
            "SELECT COUNT(*) FROM actions a JOIN steps s ON s.step_id = a.step_id "
            "WHERE s.episode_id = ?",
            (episode_id,),
        ).fetchone()[0]
        verdict = connection.execute(
            "SELECT passed, num_passed_tests, num_failed_tests FROM verifier_results "
            "WHERE episode_id = ?",
            (episode_id,),
        ).fetchone()
        code = hashlib.sha256(
            "\x00".join(
                row[0] or ""
                for row in connection.execute(
                    "SELECT generated_code FROM steps WHERE episode_id = ? ORDER BY step_index",
                    (episode_id,),
                )
            ).encode("utf-8")
        ).hexdigest()
        found[run_id] = (*fields, steps, actions, tuple(verdict) if verdict else None, code)
    return found


def prefix_counts(connection: sqlite3.Connection) -> dict[str, int]:
    counts: dict[str, int] = {}
    for (run_id,) in connection.execute("SELECT run_id FROM episodes"):
        head = run_id.split("-")[0]
        counts[head] = counts.get(head, 0) + 1
    return dict(sorted(counts.items()))


def corpus_size(connection: sqlite3.Connection, model: str) -> int:
    return connection.execute(
        "SELECT COUNT(*) FROM episodes WHERE model_ref = ? AND split = ?",
        (model, CORPUS_SPLIT),
    ).fetchone()[0]


def open_read_only(path: pathlib.Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def scan_claims(results: pathlib.Path) -> list[tuple[str, str]]:
    """(artefact name, prefix) for every scan artefact that names this series."""
    claims = []
    for path in sorted(results.glob("*-taramasi.json")):
        claim = json.loads(path.read_text(encoding="utf-8"))
        if claim.get("database") == ACTIVE_SERIES and claim.get("prefix"):
            claims.append((path.name, claim["prefix"]))
    return claims


def standing_problems(
    database: pathlib.Path, floor: dict[str, int], claims: list[tuple[str, str]]
) -> tuple[dict[str, int], list[str]]:
    """What the series holds now, and every way it falls short of what it held."""
    connection = open_read_only(database)
    try:
        counts = prefix_counts(connection)
        ledger = table_matches_schema(connection, "run_ledger")
    finally:
        connection.close()
    problems = []
    for prefix, least in sorted(floor.items()):
        have = counts.get(prefix, 0)
        if have < least:
            problems.append(
                f"{prefix}: {have} episode(s), the merge left {least}; an append-only "
                "record does not shrink, so this file is not the series"
            )
    for artefact, prefix in claims:
        if not counts.get(prefix):
            problems.append(f"{artefact} names this series but {prefix!r} is not in it")
    if ledger is None:
        problems.append("no run_ledger table; branch A could not be evaluated (K-171)")
    elif not ledger:
        problems.append("run_ledger is not the schema's table")
    return counts, problems


def check(database: pathlib.Path) -> None:
    if not database.exists():
        sys.exit(f"{database} does not exist; there is no series here to check")
    floor = json.loads(OUTPUT.read_text(encoding="utf-8"))["episodes_by_prefix"]["after"]
    counts, problems = standing_problems(database, floor, scan_claims(REPOSITORY / "results"))
    total, least = sum(counts.values()), sum(floor.values())
    print(f"series: {database}")
    print(f"episodes: {total} (the merge left {least}); prefixes: {counts}")
    if problems:
        print(f"\n{len(problems)} PROBLEM(S) with this series:")
        for line in problems:
            print(f"  - {line}")
        sys.exit(1)
    print("the series holds everything the merge left, and the ledger table")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="the standing check; writes nothing")
    parser.add_argument("--database", type=pathlib.Path, default=REPOSITORY / ACTIVE_SERIES)
    parser.add_argument("--before", type=pathlib.Path)
    parser.add_argument("--source", type=pathlib.Path)
    parser.add_argument("--merged", type=pathlib.Path)
    options = parser.parse_args()
    if options.check:
        check(options.database)
        return
    if not (options.before and options.source and options.merged):
        parser.error("--before, --source and --merged are needed unless --check is given")
    for path in (options.before, options.source, options.merged):
        if not path.exists():
            sys.exit(f"{path} does not exist")

    before = open_read_only(options.before)
    source = open_read_only(options.source)
    merged = open_read_only(options.merged)
    problems: list[str] = []

    # 1. every run in either half arrived unchanged
    merged_prints = fingerprints(merged)
    carried = {}
    for label, connection in (("before", before), ("source", source)):
        prints = fingerprints(connection)
        same = sum(1 for run, value in prints.items() if merged_prints.get(run) == value)
        carried[label] = {"runs": len(prints), "identical_in_merged": same}
        if same != len(prints):
            problems.append(f"{label}: {len(prints) - same} run(s) differ in the merged file")
    extra = len(merged_prints) - carried["before"]["runs"] - carried["source"]["runs"]
    if extra > 0:
        problems.append(f"the merged file holds {extra} run(s) that came from neither half")
    elif extra < 0:
        problems.append(f"the merged file is {-extra} run(s) short of the two halves together")

    # 2. every scan artefact that names this series finds its prefix there
    counts = prefix_counts(merged)
    scans = []
    for path in sorted((REPOSITORY / "results").glob("*-taramasi.json")):
        claim = json.loads(path.read_text(encoding="utf-8"))
        if claim.get("database") != ACTIVE_SERIES or not claim.get("prefix"):
            continue
        prefix = claim["prefix"]
        present_before = prefix_counts(before).get(prefix, 0)
        present_after = counts.get(prefix, 0)
        scans.append(
            {
                "artefact": f"results/{path.name}",
                "prefix": prefix,
                "episodes_before": present_before,
                "episodes_after": present_after,
            }
        )
        if not present_after:
            problems.append(f"{path.name} names {ACTIVE_SERIES} but {prefix!r} is not in it")

    # 3. the corpus the library was mined from did not move
    model = declared_model(CORPUS_RUN)
    corpus = {"model": model, "split": CORPUS_SPLIT}
    corpus["before"] = corpus_size(before, model)
    corpus["after"] = corpus_size(merged, model)
    if corpus["before"] != corpus["after"]:
        problems.append(f"the corpus rule selects {corpus['before']} then {corpus['after']}")

    report = {
        "what": "what the series-3 merge restored, and that it changed nothing the library read",
        "limitation": "S-74",
        "files": {
            label: {"name": path.name, "bytes": path.stat().st_size, "sha256": digest(path)}
            for label, path in (
                ("before", options.before),
                ("source", options.source),
                ("merged", options.merged),
            )
        },
        "episodes_by_prefix": {"before": prefix_counts(before), "after": counts},
        "carried_unchanged": carried,
        "scan_artefacts_naming_the_series": scans,
        "corpus_rule": corpus,
        "problems": problems,
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({k: report[k] for k in ("episodes_by_prefix", "carried_unchanged")}, indent=1))
    for scan in scans:
        print(
            f"{scan['artefact']:36} {scan['prefix']:6} {scan['episodes_before']:4} -> "
            f"{scan['episodes_after']:4}"
        )
    print(f"corpus rule ({model}, {CORPUS_SPLIT}): {corpus['before']} -> {corpus['after']}")
    print(f"written: {OUTPUT}")
    if problems:
        print(f"\n{len(problems)} PROBLEM(S):")
        for line in problems:
            print(f"  - {line}")
        sys.exit(1)
    print("\nthe merge restored the missing half and moved nothing the library was mined from")


if __name__ == "__main__":
    main()
