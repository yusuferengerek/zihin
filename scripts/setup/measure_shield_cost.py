"""Measures what the shield would actually cost and what it cannot see.

Three measurements, all of them prerequisites for mounting the shield.

**1. The real false-positive rate.** The app-set error rate is 24.5%, but that
is not the shield's false-positive rate. The shield only blocks *writes*. A
task whose instruction says "roommates" needs to *read* `phone` contact
records; if the reference solution never writes to `phone`, missing that app
costs nothing. So: of the app instances the proxy misses, in how many does the
reference solution actually write to that app?

**2. Coverage of the write set.** `UNKNOWN_ENDPOINT` is a fail-open branch and
every other contract in this repository is fail-closed. Fail-open may be
defensible here — the write set is a known lower bound — but it has to be
measured rather than assumed: how many named APIs are missing from the set, and
how many calls in the recorded episodes land in that branch.

Measured on `train` and `dev`, the only splits carrying reference solutions.

Usage:

    uv run python scripts/setup/measure_shield_cost.py
"""

from __future__ import annotations

import collections
import json
import pathlib
import sqlite3
import warnings

warnings.filterwarnings("ignore")

from appworld.task import load_task_ids  # noqa: E402

from zihin.allowed_apps import (  # noqa: E402
    INFRASTRUCTURE_APPS,
    infer_allowed_apps,
    reference_apps,
    task_instruction,
)
from zihin.api_routes import route_template, split_endpoint  # noqa: E402
from zihin.shield import Call, evaluate, load_write_set  # noqa: E402

WRITE_SET_PATH = "inputs/write-set-static.json"
OUTPUT = "results/shield-cost.json"
SPLITS = ("train", "dev")
SERIES = "results/zihin-2.sqlite"


def reference_calls(task_id: str) -> list[dict]:
    path = pathlib.Path("data/tasks") / task_id / "ground_truth" / "api_calls.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def writes_of(calls: list[dict], write_set) -> collections.Counter:
    """Which apps the reference solution writes into, and how often."""
    written: collections.Counter = collections.Counter()
    for call in calls:
        app, path = split_endpoint(call["url"])
        template = route_template(app, path, call["method"])
        if template is None:
            continue
        targets = write_set.get((app, template, call["method"].upper()))
        for target in targets or ():
            written[target] += 1
    return written


def measure_false_positives(write_set) -> dict:
    """How many missed apps are apps the reference solution actually writes to."""
    missed_total = 0
    missed_written = 0
    per_app: collections.Counter = collections.Counter()
    per_app_written: collections.Counter = collections.Counter()
    affected_tasks = set()

    for split in SPLITS:
        for task_id in load_task_ids(split):
            reference = reference_apps(task_id)
            if reference is None:
                continue
            inferred = infer_allowed_apps(task_instruction(task_id)) - INFRASTRUCTURE_APPS
            missing = (reference - INFRASTRUCTURE_APPS) - inferred
            if not missing:
                continue
            written = writes_of(reference_calls(task_id), write_set)
            for app in missing:
                missed_total += 1
                per_app[app] += 1
                if written.get(app):
                    missed_written += 1
                    per_app_written[app] += 1
                    affected_tasks.add(task_id)

    return {
        "missed_app_instances": missed_total,
        "missed_where_reference_writes": missed_written,
        "per_app_missed": dict(per_app),
        "per_app_missed_and_written": dict(per_app_written),
        "tasks_a_legitimate_write_would_be_blocked": len(affected_tasks),
    }


def measure_write_set_coverage(write_set) -> dict:
    """How many named APIs the write set does not cover."""
    raw = json.loads(pathlib.Path(WRITE_SET_PATH).read_text(encoding="utf-8"))
    named = raw["endpoints"]
    without_method = [k for k, v in named.items() if not v["methods"]]
    return {
        "named_apis": len(named),
        "write_set_keys": len(write_set),
        "named_apis_without_a_method": len(without_method),
        "examples": without_method[:5],
    }


def measure_unknown_branch(write_set) -> dict:
    """How many recorded calls land in the fail-open branch."""
    connection = sqlite3.connect(f"file:{SERIES}?mode=ro", uri=True)
    outcomes: collections.Counter = collections.Counter()
    unresolved: collections.Counter = collections.Counter()
    for app, api, method in connection.execute(
        "SELECT app, api, http_method FROM actions"
    ).fetchall():
        template = route_template(app, api, method)
        if template is None:
            unresolved[f"{app}.{api}"] += 1
            outcomes["url_did_not_resolve"] += 1
            continue
        decision = evaluate(Call(app, template, method or "GET"), frozenset({app}), write_set)
        outcomes[decision.predicate.value] += 1
    return {
        "recorded_calls": sum(outcomes.values()),
        "by_predicate": dict(outcomes),
        "unresolved_examples": dict(unresolved.most_common(5)),
    }


def main() -> None:
    write_set = load_write_set(WRITE_SET_PATH)

    fp = measure_false_positives(write_set)
    coverage = measure_write_set_coverage(write_set)
    unknown = measure_unknown_branch(write_set)

    print("--- 1. the shield's real false-positive cost ---")
    print(f"  missed app instances                : {fp['missed_app_instances']}")
    print(f"  of those, reference actually writes : {fp['missed_where_reference_writes']}")
    print(
        f"  tasks where a write would be blocked: {fp['tasks_a_legitimate_write_would_be_blocked']}"
    )
    print(f"  missed per app                      : {fp['per_app_missed']}")
    print(f"  missed AND written per app          : {fp['per_app_missed_and_written']}")
    print()
    print("--- 2. write set coverage ---")
    for key, value in coverage.items():
        print(f"  {key:34s}: {value}")
    print()
    print("--- 3. the fail-open branch on recorded calls ---")
    print(f"  recorded calls: {unknown['recorded_calls']}")
    for name, count in sorted(unknown["by_predicate"].items(), key=lambda kv: -kv[1]):
        print(f"    {name:38s} {count:6d}")
    if unknown["unresolved_examples"]:
        print(f"  URLs that did not resolve: {unknown['unresolved_examples']}")

    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(
            {"false_positives": fp, "coverage": coverage, "unknown_branch": unknown},
            handle,
            ensure_ascii=False,
            indent=2,
        )
    print()
    print(f"written: {OUTPUT}")
    print()
    print("note: branch 3 uses allowed_apps = {the call's own app}, so it isolates")
    print("      UNKNOWN_ENDPOINT and READ; it is not a shadow-mode run.")


if __name__ == "__main__":
    main()
