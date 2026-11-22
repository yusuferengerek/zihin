"""How many groups the failure index came from, and how many it comes from today.

**Why it exists.** The report says 767 failed actions were reduced to 22 groups
and 15 of them became cards. Fifteen is in the record — the `failure_patterns`
table holds it. Twenty-two was printed by the builder and stored nowhere, so a
number that carries an elimination argument had no artefact.

**Two corpora, because the corpus moved.** The stored index was mined before the
three-arm run's forty-five episodes entered the series, and it has not been
re-mined since (`S-65`). So there are two honest answers and this measures both:
the corpus as the index saw it, and the corpus as it is now. Re-mining is a
design decision and this script does not make it — it reads and counts, it
writes no index.

**How the index-time corpus is reconstructed.** By removing the episodes whose
run id carries the three-arm prefix. That is a reconstruction, not a snapshot,
and it is right only because those forty-five episodes are the only ones that
entered after the build.

Usage:

    uv run python scripts/setup/measure_failure_index_build.py
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))
sys.path.insert(0, str(REPOSITORY / "scripts/setup"))

from build_failure_index import every_observed_episode  # noqa: E402

from zihin.failure_index import mine_failure_patterns  # noqa: E402
from zihin.records import CALIBRATION_SERIES  # noqa: E402

OUTPUT = REPOSITORY / "results/failure-index-build.json"
# The prefix of the run that entered after the index was built.
LATER_PREFIX = "uckol"
MIN_SUPPORT = 1


def counts(episodes: dict, min_support: int) -> dict:
    patterns, tally = mine_failure_patterns(episodes, min_support=min_support)
    return {
        "episodes": len(episodes),
        "actions": sum(len(v) for v in episodes.values()),
        "groups": tally["groups"],
        "cards": len(patterns),
        "eliminated": tally["groups"] - len(patterns),
        "eliminated_breakdown": {
            "no_expressible_condition": tally["no_expressible_condition"],
            "below_support": tally["below_support"],
        },
        "kept_breakdown": {
            "discriminated_by_condition": tally["discriminated_by_condition"],
            "discriminated_by_shape": tally["discriminated_by_shape"],
            "no_known_success": tally["no_known_success"],
        },
        "status_codes": {},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default=CALIBRATION_SERIES)
    options = parser.parse_args()

    path = REPOSITORY / options.database
    if not path.exists():
        sys.exit(f"{options.database} does not exist; the counts are read from the record.")
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row

    everything = every_observed_episode(connection)
    later = {
        row[0]
        for row in connection.execute(
            "SELECT episode_id FROM episodes WHERE run_id LIKE ?", (LATER_PREFIX + "-%",)
        )
    }
    at_build = {k: v for k, v in everything.items() if k not in later}
    if not at_build or len(at_build) == len(everything):
        sys.exit(
            f"the {LATER_PREFIX!r} episodes could not be separated ({len(later)} found). "
            "Without that split there is one corpus, not two, and this measurement "
            "declines rather than reporting the same number twice."
        )

    stored = connection.execute(
        "SELECT index_id, COUNT(*) FROM failure_patterns GROUP BY index_id"
    ).fetchall()
    codes = dict(
        connection.execute(
            "SELECT status_code, COUNT(*) FROM failure_patterns GROUP BY status_code"
        )
    )
    connection.close()

    report = {
        "what": "the group count behind the failure index, at build time and today",
        "database": options.database,
        "min_support": MIN_SUPPORT,
        "stored_index": [{"index_id": r[0], "cards": r[1]} for r in stored],
        "stored_cards_by_status_code": {str(k): v for k, v in codes.items()},
        "at_build": counts(at_build, MIN_SUPPORT),
        "today": counts(everything, MIN_SUPPORT),
        "later_episodes_excluded": len(later),
        "later_prefix": LATER_PREFIX,
        "note": (
            "The stored index matches the at_build column. The today column is the "
            "gap S-65 records; re-mining is a design decision and this script does "
            "not make it."
        ),
    }
    report["at_build"]["status_codes"] = {str(k): v for k, v in codes.items()}
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"database {options.database}, min_support {MIN_SUPPORT}")
    print(f"stored index: {[(r[0], r[1]) for r in stored]}")
    print(f"cards by status code: {report['stored_cards_by_status_code']}")
    print()
    print(
        f"  {'corpus':<12} {'episodes':>9} {'actions':>8} {'groups':>7} "
        f"{'cards':>6} {'eliminated':>11}"
    )
    for label in ("at_build", "today"):
        c = report[label]
        print(
            f"  {label:<20} {c['episodes']:>9} {c['actions']:>8} {c['groups']:>7} "
            f"{c['cards']:>6} {c['eliminated']:>11}"
        )
    print()
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
