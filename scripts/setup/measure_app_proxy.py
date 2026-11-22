"""Measures the allowed-app proxy against the reference lists.

The proxy is the shield's specification, so its accuracy is the shield's
accuracy. Two error directions matter and they are not symmetric:

  **Missed app** — the proxy does not name an app the task needs. The shield
  then blocks a legitimate write and the task fails because of us.

  **Extra app** — the proxy names an app the task does not need. The shield
  then lets an illegitimate write through and the boundary is wider than
  declared.

Both are reported per app, because the error profile is what a caller needs:
knowing that the proxy over-counts one app and misses another is more useful
than a single accuracy number.

Measured on `train` and `dev`, the only splits carrying
`ground_truth/required_apps.json` (S-03).

Usage:

    uv run python scripts/setup/measure_app_proxy.py
"""

from __future__ import annotations

import collections
import json
import warnings

warnings.filterwarnings("ignore")

from appworld.task import load_task_ids  # noqa: E402

from zihin.allowed_apps import (  # noqa: E402
    INFRASTRUCTURE_APPS,
    infer_allowed_apps,
    reference_apps,
    task_instruction,
)

OUTPUT = "results/app-proxy-accuracy.json"
SPLITS = ("train", "dev")


def jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 1.0


def main() -> None:
    records = []
    missed: collections.Counter = collections.Counter()
    extra: collections.Counter = collections.Counter()

    for split in SPLITS:
        for task_id in load_task_ids(split):
            reference = reference_apps(task_id)
            if reference is None:
                continue
            # Infrastructure apps are outside the comparison: the proxy always
            # includes them and the reference never lists them, so leaving them
            # in would inflate the agreement.
            inferred = infer_allowed_apps(task_instruction(task_id)) - INFRASTRUCTURE_APPS
            reference = reference - INFRASTRUCTURE_APPS
            missed.update(reference - inferred)
            extra.update(inferred - reference)
            records.append(
                {
                    "task": task_id,
                    "split": split,
                    "inferred": sorted(inferred),
                    "reference": sorted(reference),
                    "exact": inferred == reference,
                    "jaccard": round(jaccard(inferred, reference), 4),
                }
            )

    total = len(records)
    exact = sum(1 for r in records if r["exact"])
    mean_jaccard = sum(r["jaccard"] for r in records) / total if total else 0.0
    complete = sum(1 for r in records if set(r["reference"]) <= set(r["inferred"]))

    print(f"reference list available : {total} tasks ({', '.join(SPLITS)})")
    print(f"exact match              : {exact}/{total} = {100 * exact / total:.1f}%")
    print(f"mean Jaccard             : {mean_jaccard:.3f}")
    print(f"reference fully covered  : {complete}/{total} = {100 * complete / total:.1f}%")
    print("  (the shield only blocks a legitimate write when an app is MISSED,")
    print("   so full coverage is the figure that bounds false positives)")
    print()
    print("--- missed apps (shield blocks a legitimate write) ---")
    for app, count in missed.most_common():
        print(f"  {app:14s} {count:4d}")
    print()
    print("--- extra apps (shield lets an illegitimate write through) ---")
    for app, count in extra.most_common():
        print(f"  {app:14s} {count:4d}")

    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "splits": list(SPLITS),
                "tasks": total,
                "exact_match": exact,
                "mean_jaccard": round(mean_jaccard, 4),
                "reference_fully_covered": complete,
                "missed_by_app": dict(missed),
                "extra_by_app": dict(extra),
                "records": records,
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )
    print()
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
