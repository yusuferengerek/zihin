"""How many of our thirty tasks the published gpt-4o run solves.

**Why it exists.** "gpt-4o solves 15 of the same thirty tasks" is quoted as the
independent reference next to our own 20/30, and it lived only in the prose of a
report. The two sets it is computed from are both in the record — the published
run's solved list, and the thirty tasks of our band scan — so the intersection is
arithmetic and belongs in a file.

**It is not our run.** The solved list comes from AppWorld's published
`gpt-4o-2024-05-13` output, downloaded, not re-run here. The comparison is
therefore a reference point and not a controlled contrast: the published run had
no stopping rule and no shield, and this file says so rather than leaving it to
be remembered.

Usage:

    uv run python scripts/setup/measure_gpt4o_overlap.py
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
OUTPUT = REPOSITORY / "results/gpt4o-kesisim.json"
SOLVED = REPOSITORY / "results/gpt4o-cozulen.json"
# Our thirty tasks: the band scan's task set, taken from a scan rather than from a
# list typed out again. Any of the axis scans carries the same thirty.
OUR_SCAN = "results/b32c-taramasi.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan", default=OUR_SCAN)
    options = parser.parse_args()

    if not SOLVED.exists():
        sys.exit(f"{SOLVED.name} is absent; the published run's solved set is the input.")
    scan_path = REPOSITORY / options.scan
    if not scan_path.exists():
        sys.exit(f"{options.scan} is absent; our thirty tasks are read from a scan.")

    published = json.loads(SOLVED.read_text(encoding="utf-8"))
    scan = json.loads(scan_path.read_text(encoding="utf-8"))
    episodes = scan.get("episodes_with_steps") or []
    ours = sorted({episode["task"] for episode in episodes})
    if not ours:
        sys.exit(f"{options.scan} carries no episodes; there is no task set to intersect.")

    solved = set(published["cozulen"])
    overlap = sorted(set(ours) & solved)
    ours_passed = sorted({e["task"] for e in episodes if e.get("passed")})

    report = {
        "what": "how many of our thirty tasks the published gpt-4o run solves",
        "published_model": published["model"],
        "published_split": published["bolme"],
        "published_solved": len(solved),
        "published_source": "results/gpt4o-cozulen.json",
        "our_task_set_from": options.scan,
        "our_tasks": len(ours),
        "overlap": len(overlap),
        "overlap_tasks": overlap,
        "our_model": scan.get("model"),
        "our_passed": len(ours_passed),
        "solved_by_both": sorted(set(overlap) & set(ours_passed)),
        "solved_only_by_gpt4o": sorted(set(overlap) - set(ours_passed)),
        "solved_only_by_us": sorted(set(ours_passed) - set(overlap)),
        "caveat": (
            "Not our run. The published run carried no stopping rule and no shield, "
            "so this is a reference point, not a controlled contrast."
        ),
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"published: {published['model']} solves {len(solved)} of {published['bolme']}")
    print(f"ours     : {len(ours)} tasks, from {options.scan}")
    print(f"overlap  : {len(overlap)}/{len(ours)}")
    print(f"  our own model ({scan.get('model')}) passes {len(ours_passed)}/{len(ours)}")
    print(f"  both     : {len(report['solved_by_both'])}")
    print(f"  gpt-4o only: {len(report['solved_only_by_gpt4o'])}")
    print(f"  us only    : {len(report['solved_only_by_us'])}")
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
