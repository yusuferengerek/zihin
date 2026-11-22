"""Writes the touched-task list from the record, or checks the committed one.

**What it writes.** `results/touched-tasks.json`: for each AppWorld split, every
task the record holds an episode of, and for each task the series, run, condition
and model that touched it and how many episodes each left. The derivation is in
`zihin.touched`; this script only decides whether to write it or compare it.

**`--check` needs the whole record.** A comparison against part of the record
cannot say the list is right, only that it is not behind that part. The loader
accepts that weaker answer where it has to (a Colab session holds one series);
this check does not, because it is the one place asked to say "the list is
current". With a series missing it declines and exits non-zero.

Usage:

    uv run python scripts/setup/build_touched_tasks.py
    uv run python scripts/setup/build_touched_tasks.py --check
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))

from zihin.touched import (  # noqa: E402
    RECORD_SERIES,
    SPLITS,
    TOUCHED,
    TouchedListError,
    derive,
    experiment_problems,
    load_touched,
    render,
    split_membership,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare, do not write")
    options = parser.parse_args()

    absent = [name for name in RECORD_SERIES if not (REPOSITORY / name).exists()]
    if absent:
        sys.exit(
            f"the record is incomplete here ({', '.join(absent)} absent). A list derived "
            "from part of it would drop what the rest touched, and a comparison against "
            "part of it cannot say the list is current. Nothing was written or compared."
        )

    if options.check:
        try:
            touched = load_touched(REPOSITORY)
        except TouchedListError as error:
            sys.exit(f"FAILED: {error}")
        counts = ", ".join(f"{split} {len(touched.tasks(split))}" for split in SPLITS)
        print(f"{TOUCHED}: {touched.basis}; {counts}")
        return

    series = [REPOSITORY / name for name in RECORD_SERIES]
    membership = split_membership()
    document = derive(series, membership)
    crossings = experiment_problems(series, membership, document)
    if crossings:
        sys.exit(
            "the experiment boundary is crossed; nothing was written:\n  - "
            + "\n  - ".join(crossings)
        )
    (REPOSITORY / TOUCHED).write_text(render(document), encoding="utf-8")
    for split in SPLITS:
        print(f"{split:15} {len(document[split]):4} touched")
    for task, disagreement in document["recorded_split_disagrees"].items():
        print(f"recorded split disagrees: {task} {disagreement}")
    print(f"written: {TOUCHED}")


if __name__ == "__main__":
    main()
