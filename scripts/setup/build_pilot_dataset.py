"""Collects the mechanism pilot's numbers into one machine-readable file.

**Why one file.** Every number the pilot report cites was produced by a different
script on a different day, and this repository has already had the failure this
prevents: the write set changed twice in one day and the same measurement gave
two different numbers. A report that copies numbers out of eight files cannot be
checked; a report that points at one file can.

**Nothing is computed here that was not measured somewhere else.** This script
reads the record and the measurement outputs, copies them with their provenance,
and refuses to run when they disagree. The one thing it derives is arithmetic on
numbers it copied — a rate from its own numerator and denominator — and the
inputs stay next to the result.

**It checks that the sources are talking about the same library.** The coverage
measurement, the card measurement and the context measurement each name a
`library_id`; if two of them differ, the dataset would silently mix two
libraries and the report would read as one result. That is a hard stop, not a
warning.

Usage:

    uv run python scripts/setup/build_pilot_dataset.py
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import sqlite3
import subprocess
import sys

from zihin.allowed_apps import INFRASTRUCTURE_APPS
from zihin.records import ACTIVE_SERIES, open_library

OUTPUT = "results/pilot-dataset.json"

# Every input, and what the report is allowed to cite it for.
SOURCES = {
    "coverage": "results/retrieval-coverage.json",
    "card_tokens": "results/card-tokens.json",
    "context_cost": "results/context-cost.json",
    "shield_cost": "results/shield-cost.json",
    "shadow_mode": "results/shadow-mode.json",
    "mining": "results/mined-skills.json",
    "failure_substrate": "results/failure-substrate.json",
    "write_set": "inputs/write-set-static.json",
    "gate_local": "results/bant3-taramasi.json",
    "gate_local_rule_off": "results/bant3-kapali-taramasi.json",
    "gate_boundary": "results/sinir-kontrolu-4000.json",
}


def read(path: str) -> dict:
    text = pathlib.Path(path).read_text(encoding="utf-8")
    return json.loads(text)


def digest(path: str) -> dict:
    raw = pathlib.Path(path).read_bytes()
    return {
        "path": path,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def code_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return "unknown"


def rows(connection: sqlite3.Connection, query: str, *parameters) -> list[dict]:
    return [dict(r) for r in connection.execute(query, parameters)]


def appworld_commit(connection: sqlite3.Connection) -> str:
    """The pinned benchmark commit, and a stop if the record holds more than one."""
    pinned = [
        r[0] for r in connection.execute("SELECT DISTINCT appworld_commit FROM run_manifests")
    ]
    if len(pinned) != 1:
        sys.exit(
            f"the record carries {len(pinned)} different AppWorld commits: "
            f"{pinned}. Not one corpus."
        )
    return pinned[0]


def corpus_diversity(connection: sqlite3.Connection) -> dict:
    """How the passing tasks spread over apps, and which calls recur.

    The library has four skills and all four are logins. Whether that is a
    property of the miner or of the corpus cannot be read off the mining grid:
    the grid records how many skills each threshold produced, not which. So it is
    measured directly — what the passing tasks touch, and which calls recur in
    enough tasks to clear the support threshold at all.

    Infrastructure apps are dropped with the retriever's own set, not a list
    retyped here.
    """
    passing = [
        (r["episode_id"], r["task_id"])
        for r in connection.execute(
            "SELECT e.episode_id, e.task_id FROM episodes e "
            "JOIN verifier_results v ON v.episode_id = e.episode_id WHERE v.passed = 1"
        )
    ]
    apps_of_task: dict[str, set[str]] = {}
    tasks_of_call: dict[str, set[str]] = {}
    for episode_id, task_id in passing:
        apps_of_task.setdefault(task_id, set())
        for row in connection.execute(
            "SELECT DISTINCT a.app, a.api, a.http_method FROM actions a "
            "JOIN steps s ON s.step_id = a.step_id WHERE s.episode_id = ?",
            (episode_id,),
        ):
            if row["app"] not in INFRASTRUCTURE_APPS:
                apps_of_task[task_id].add(row["app"])
            call = f"{row['http_method']} {row['app']}.{row['api']}"
            tasks_of_call.setdefault(call, set()).add(task_id)

    app_sets = collections.Counter(tuple(sorted(v)) for v in apps_of_task.values())
    tasks_per_app = collections.Counter(a for v in apps_of_task.values() for a in v)
    recurring = {c: len(t) for c, t in tasks_of_call.items() if len(t) >= 3}
    return {
        "passing_tasks": len(apps_of_task),
        "distinct_app_sets": len(app_sets),
        "app_sets": {", ".join(k) or "(none)": n for k, n in app_sets.most_common()},
        "tasks_per_app": dict(tasks_per_app.most_common()),
        "support_threshold": 3,
        "calls_in_three_or_more_tasks": dict(
            sorted(recurring.items(), key=lambda kv: (-kv[1], kv[0]))
        ),
        "recurring_infrastructure_calls": {
            c: n
            for c, n in recurring.items()
            if c.split(" ", 1)[1].split(".", 1)[0] in INFRASTRUCTURE_APPS
        },
        "recurring_session_calls": {c: n for c, n in recurring.items() if "auth/" in c},
        "recurring_ordinary_calls": {
            c: n
            for c, n in sorted(recurring.items(), key=lambda kv: (-kv[1], kv[0]))
            if c.split(" ", 1)[1].split(".", 1)[0] not in INFRASTRUCTURE_APPS and "auth/" not in c
        },
        "recurring_ordinary_writes": {
            c: n
            for c, n in sorted(recurring.items(), key=lambda kv: (-kv[1], kv[0]))
            if c.split(" ", 1)[1].split(".", 1)[0] not in INFRASTRUCTURE_APPS
            and "auth/" not in c
            and c.split(" ", 1)[0] in ("POST", "PUT", "PATCH", "DELETE")
        },
    }


def record_summary(connection: sqlite3.Connection, database: str) -> dict:
    """What the corpus is, counted from the record rather than from memory.

    The path is passed in rather than read from a constant: the summary has to
    name the file it actually counted, and the constant moves when a new series
    opens (K-143).
    """
    episodes = connection.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
    steps = connection.execute("SELECT COUNT(*) FROM steps").fetchone()[0]
    actions = connection.execute("SELECT COUNT(*) FROM actions").fetchone()[0]
    passing = connection.execute(
        "SELECT COUNT(*) FROM verifier_results WHERE passed = 1"
    ).fetchone()[0]
    return {
        "database": database,
        "episodes": episodes,
        "steps": steps,
        "actions": actions,
        "passing_episodes": passing,
        "passing_tasks": connection.execute(
            "SELECT COUNT(DISTINCT e.task_id) FROM episodes e "
            "JOIN verifier_results v ON v.episode_id = e.episode_id WHERE v.passed = 1"
        ).fetchone()[0],
        "distinct_tasks": connection.execute(
            "SELECT COUNT(DISTINCT task_id) FROM episodes"
        ).fetchone()[0],
        "models": [
            dict(r)
            for r in connection.execute(
                "SELECT m.model_tag, m.serving_mode, COUNT(e.episode_id) AS episodes "
                "FROM run_manifests m LEFT JOIN episodes e ON e.run_id = m.run_id "
                "GROUP BY m.model_tag, m.serving_mode ORDER BY episodes DESC"
            )
        ],
        "shield_modes": [
            dict(r)
            for r in connection.execute(
                "SELECT shield_mode, COUNT(*) AS runs FROM run_manifests GROUP BY shield_mode"
            )
        ],
        # Distribution by condition. The demo episodes (item 7) write into the
        # same database and run with library cards; they have to be tellable
        # apart from the setup measurements, otherwise "the corpus" becomes the
        # sum of two different things and grows in silence.
        "episodes_per_condition": [
            dict(r)
            for r in connection.execute(
                "SELECT condition, COUNT(*) AS episodes FROM episodes "
                "GROUP BY condition ORDER BY episodes DESC"
            )
        ],
        "episodes_with_a_library": connection.execute(
            "SELECT COUNT(*) FROM episodes e JOIN run_manifests m ON m.run_id = e.run_id "
            "WHERE m.library_id IS NOT NULL"
        ).fetchone()[0],
    }


def consistency(sources: dict, library_id: str, index_id: str) -> dict:
    """Are the measurements about the same library and the same index?"""
    claims = {
        name: (data.get("library_id"), data.get("index_id"))
        for name, data in sources.items()
        if isinstance(data, dict) and "library_id" in data
    }
    disagreeing = {name: claim for name, claim in claims.items() if claim != (library_id, index_id)}
    return {
        "database_library_id": library_id,
        "database_index_id": index_id,
        "claims": {name: {"library_id": c[0], "index_id": c[1]} for name, c in claims.items()},
        "disagreeing": sorted(disagreeing),
    }


def coverage_section(data: dict) -> dict:
    """Coverage per split and per mechanism, plus the full threshold grid.

    Per mechanism matters because the pilot runs "skills only" and "failures
    only" as separate conditions: a task with a failure card and no skill card is
    covered for one condition and uncovered for the other.
    """
    return {
        "falsification_gate": 0.25,
        "per_split": {
            split: {
                "tasks": block["tasks"],
                "any": block["ceiling"]["coverage"],
                "skills_only": block["ceiling"]["skill_coverage"],
                "failures_only": block["ceiling"]["failure_coverage"],
                "skill_cards_total": block["ceiling"]["skill_cards"],
                "failure_cards_total": block["ceiling"]["failure_cards"],
                "unseen_tasks": block["unseen_tasks"],
                "unseen_coverage": block["unseen_coverage"],
                "apps_named_per_task": block["apps_named_per_task"],
            }
            for split, block in data["splits"].items()
        },
        "threshold_grid": {split: block["grid"] for split, block in data["splits"].items()},
    }


def shield_section(cost: dict, shadow: dict, write_set: dict) -> dict:
    """The two rates, kept apart (K-72).

    The false-positive rate is only measurable where a reference solution exists
    — train and dev. The block rate is measurable over the whole corpus, but
    there it cannot be said whether any individual block was right.
    """
    train_dev_tasks = 90 + 57
    blocked_endpoints = shadow.get("most_blocked_endpoints") or []
    writers = [e for e in write_set["endpoints"].values() if e.get("writes")]
    return {
        "false_positive_rate": {
            "tasks_a_legitimate_write_would_be_blocked": cost["false_positives"][
                "tasks_a_legitimate_write_would_be_blocked"
            ],
            "tasks_with_ground_truth": train_dev_tasks,
            "rate": round(
                cost["false_positives"]["tasks_a_legitimate_write_would_be_blocked"]
                / train_dev_tasks,
                4,
            ),
            "splits": ["train", "dev"],
            "per_app_missed": cost["false_positives"]["per_app_missed"],
        },
        "block_rate": {
            "episodes": shadow["episodes"],
            "distinct_tasks": shadow["distinct_tasks"],
            "calls": shadow["calls"],
            "blocked_calls": shadow["blocked_calls"],
            "call_rate": shadow["call_block_rate"],
            "episode_rate": shadow["episode_block_rate"],
            "task_rate": shadow["task_block_rate"],
            "predicates": shadow["predicates"],
            "blocked_endpoints": blocked_endpoints,
            "blocks_are_harness_probes": True,
        },
        "fail_open_branch": cost["unknown_branch"],
        "write_set": {
            "named_apis": cost["coverage"]["named_apis"],
            "keys": cost["coverage"]["write_set_keys"],
            "endpoints_without_a_method": cost["coverage"]["named_apis_without_a_method"],
            "writing_endpoints": len(writers),
            "session_endpoints": len(write_set["session_endpoints"]),
            "known_over_inclusion": sum(
                1
                for e in write_set["endpoints"].values()
                if e.get("writes") and e.get("body_write") is False and e.get("method") != "GET"
            ),
        },
    }


def gate_section(local: dict, rule_off: dict, boundary: dict) -> dict:
    """The precondition gate: what fired it, and what showed the zeros were the model's.

    The date is the one recorded in `05-experiment-design.tr.md`; it is not
    re-derived here, because the file timestamps of a re-run measurement would
    silently move it.
    """
    return {
        "fired_on": "2026-08-11",
        "decision": "K-58",
        "local_axis": {
            "model": local["model"],
            "split": local["split"],
            "tasks": len(local["episodes"]),
            "passed": sum(e["passed"] for e in local["episodes"]),
            "band_size": local["band_size"],
            "ceiling_multiplier": local["multiplier"],
        },
        "local_axis_stopping_rule_off": {
            "tasks": len(rule_off["episodes"]),
            "passed": rule_off["gecen"],
            "threshold": rule_off["durma_esigi"],
        },
        "boundary_control": {
            "model": boundary["model"],
            "split": boundary["split"],
            "tasks": len(boundary["episodes"]),
            "passed": boundary["gecen"],
            "note": "ran with thinking on (S-34); not on the local axis",
        },
        "consequence": (
            "the primary comparison metric is the step difference; because the baseline "
            "solved zero, the step difference is undefined and mechanism results "
            "cannot be reported as a comparison"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    # Which record is being summarised is a choice, not a default that follows
    # whichever series is active. The pilot was built from series 2 and saying
    # so is part of the dataset.
    parser.add_argument("--database", default=ACTIVE_SERIES)
    options = parser.parse_args()

    connection = sqlite3.connect(f"file:{options.database}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    # The library comes from its own series, which is not necessarily the one
    # being summarised.
    library, library_id, index_id = open_library()
    library.close()

    missing = [p for p in SOURCES.values() if not pathlib.Path(p).exists()]
    if missing:
        sys.exit(
            f"missing measurement output: {missing}. The dataset is not built "
            "from incomplete input."
        )
    data = {name: read(path) for name, path in SOURCES.items()}

    checks = consistency(data, library_id, index_id)
    if checks["disagreeing"]:
        sys.exit(
            f"the measurements name different library/index ids: "
            f"{checks['disagreeing']}. "
            "The dataset does not mix two libraries; the measurements must be re-run."
        )

    dataset = {
        "meta": {
            "library_id": library_id,
            "index_id": index_id,
            "code_commit": code_commit(),
            # Every manifest carries the same pinned AppWorld commit; that they
            # really are the same is asserted rather than assumed, because a
            # corpus recorded against two benchmark versions is not one corpus.
            "appworld_commit": appworld_commit(connection),
            "sources": {name: digest(path) for name, path in SOURCES.items()},
            "consistency": checks,
        },
        "record": record_summary(connection, options.database),
        "corpus_diversity": corpus_diversity(connection),
        "skills": rows(
            connection,
            "SELECT * FROM skills WHERE library_id = ? ORDER BY support DESC, skill_id",
            library_id,
        ),
        "failure_patterns": rows(
            connection,
            "SELECT * FROM failure_patterns WHERE index_id = ? "
            "ORDER BY failure_count DESC, pattern_id",
            index_id,
        ),
        "coverage": coverage_section(data["coverage"]),
        "shield": shield_section(data["shield_cost"], data["shadow_mode"], data["write_set"]),
        "card_tokens": data["card_tokens"],
        "context_cost": data["context_cost"],
        "mining_grid": {
            "episodes": data["mining"]["episodes"],
            "tasks": data["mining"]["tasks"],
            "calls": data["mining"]["calls"],
            "alphabet": data["mining"]["alphabet"],
            "constant_threshold": data["mining"]["constant_threshold"],
            "lead_configuration": data["mining"]["lead_configuration"],
            "grid": data["mining"]["grid"],
        },
        "failure_substrate": data["failure_substrate"],
        "precondition_gate": gate_section(
            data["gate_local"], data["gate_local_rule_off"], data["gate_boundary"]
        ),
    }

    pathlib.Path(OUTPUT).write_text(
        json.dumps(dataset, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    size = pathlib.Path(OUTPUT).stat().st_size

    print(f"library {library_id}, index {index_id}")
    print(f"source files: {len(SOURCES)}, each recorded with its digest")
    print(f"consistency: {len(checks['claims'])} measurements name an id, none disagree")
    print()
    diversity = dataset["corpus_diversity"]
    print(
        f"passing tasks            : {diversity['passing_tasks']}, "
        f"{diversity['distinct_app_sets']} distinct app sets, "
        f"{len(diversity['tasks_per_app'])} apps"
    )
    print(
        f"recurring in 3+ tasks    : {len(diversity['calls_in_three_or_more_tasks'])} calls; "
        f"infrastructure {len(diversity['recurring_infrastructure_calls'])}, "
        f"oturum {len(diversity['recurring_session_calls'])}, "
        f"ordinary {len(diversity['recurring_ordinary_calls'])} "
        f"(yazan {len(diversity['recurring_ordinary_writes'])})"
    )
    print(f"skill rows               : {len(dataset['skills'])}")
    print(f"failure pattern rows     : {len(dataset['failure_patterns'])}")
    print(f"coverage splits          : {len(dataset['coverage']['per_split'])}")
    print(
        f"threshold grid cells     : "
        f"{sum(len(g) for g in dataset['coverage']['threshold_grid'].values())} getirici, "
        f"{len(dataset['mining_grid']['grid'])} madencilik"
    )
    print(f"card token rows          : {len(dataset['card_tokens']['cards'])}")
    print(
        f"shield               : false positive "
        f"{dataset['shield']['false_positive_rate']['rate']:.1%}, engelleme "
        f"{dataset['shield']['block_rate']['call_rate']:.2%}"
    )
    print(f"\nwritten: {OUTPUT} ({size / 1024:.0f} KiB)")


if __name__ == "__main__":
    main()
