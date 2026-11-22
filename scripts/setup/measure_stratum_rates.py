"""Every measured model's pass rate on the action stratum, on the same thirty tasks.

**Why it exists.** Path (a) out of the power problem is "a model with a higher
pass rate", and the threshold it has to clear is on the **action stratum**
(K-144, K-146). Headline rates mix the two strata, and the answer stratum is
where an agent that does nothing collects a free test — so a headline rate is the
wrong number to compare against the threshold, systematically on the high side.

**The strongest point we have decides it.** DeepSeek V4 Flash is the highest rate
this project has measured anywhere. If its action-stratum rate is below the
derived threshold, path (a) is closed for every model measured, and that is a
finding about the design rather than about any model.

**The qualification travels with the number.** DeepSeek's 20/30 is the union of
two runs: thirteen with the stopping rule on, and seven more when the sixteen the
rule had cut short were re-run with it off. In those runs thinking was on, which
was not the declared condition (`S-34`). Both halves are reported separately here
so the union is never read as one run.

**Read from the record, no model call.** The pass sets come from the scans; the
type of each task from `scripts/analyze_passes.py`, imported rather than
re-implemented.

Usage:

    uv run python scripts/setup/measure_stratum_rates.py
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))

OUTPUT = REPOSITORY / "results/stratum-rates.json"
# The thirty tasks, taken from a scan rather than typed out again.
TASK_SET = "results/b32c-taramasi.json"
# The threshold path (a) has to clear, from the derivation.
THRESHOLD = REPOSITORY / "results/pass-threshold.json"


def shape():
    path = REPOSITORY / "scripts/analyze_passes.py"
    spec = importlib.util.spec_from_file_location("analyze_passes", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["analyze_passes"] = module
    spec.loader.exec_module(module)
    return module.task_shape


def scan_passes(name: str) -> set[str] | None:
    path = REPOSITORY / name
    if not path.exists():
        return None
    blob = json.loads(path.read_text(encoding="utf-8"))
    episodes = blob.get("episodes_with_steps") or blob.get("episodes") or []
    return {e["task"] for e in episodes if e.get("passed")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-set", default=TASK_SET)
    options = parser.parse_args()

    task_shape = shape()
    path = REPOSITORY / options.task_set
    if not path.exists():
        sys.exit(f"{options.task_set} is absent; the thirty tasks are read from a scan.")
    thirty = sorted(
        {e["task"] for e in json.loads(path.read_text(encoding="utf-8"))["episodes_with_steps"]}
    )
    if len(thirty) != 30:
        sys.exit(
            f"{options.task_set} carries {len(thirty)} tasks, not thirty. This "
            "measurement declines rather than dividing by a denominator it did not expect."
        )
    action = {t for t in thirty if task_shape(t)["kind"] != "answer"}
    answer = set(thirty) - action

    rule_on = scan_passes("results/sinir3-kontrolu.json")
    rule_off = scan_passes("results/sinir3-kapali-kontrolu.json")
    overlap = REPOSITORY / "results/gpt4o-kesisim.json"
    gpt4o = (
        set(json.loads(overlap.read_text(encoding="utf-8"))["overlap_tasks"])
        if overlap.exists()
        else None
    )
    if rule_on is None or rule_off is None or gpt4o is None:
        sys.exit("a reference run's artefact is missing; the comparison declines.")

    arms = [
        (
            "deepseek-v4-flash-0731, union",
            rule_on | rule_off,
            "the union of two runs; thinking was on (S-34)",
        ),
        ("  .. stopping rule on", rule_on, "thirteen passes"),
        ("  .. rule off, on the sixteen it cut", rule_off, "seven more passes"),
        ("gpt-4o-2024-05-13, published", gpt4o, "no stopping rule, no shield; not our run"),
        ("qwen2.5-coder:32b", scan_passes("results/b32c-taramasi.json"), "our own axis point"),
        ("qwen2.5-coder:14b", scan_passes("results/b14-taramasi.json"), "our own axis point"),
    ]

    thresholds = (
        sorted(
            {
                value
                for derivation in json.loads(THRESHOLD.read_text(encoding="utf-8"))[
                    "derivation"
                ].values()
                for value in derivation["threshold"].values()
                if value
            }
        )
        if THRESHOLD.exists()
        else []
    )

    rows = []
    print(f"the thirty tasks: {len(action)} action-type, {len(answer)} answer-type")
    print(f"answer-type: {sorted(answer)}")
    if thresholds:
        print(f"derived threshold: {thresholds[0]}-{thresholds[-1]} (K-146)")
    print()
    print(f"  {'run':<38} {'total':>7} {'action':>9} {'rate':>7} {'answer':>8}  note")
    for name, passes, note in arms:
        if passes is None:
            continue
        in_action = passes & action
        rate = len(in_action) / len(action)
        rows.append(
            {
                "run": name.strip(),
                "total": len(passes),
                "action_passed": len(in_action),
                "action_total": len(action),
                "action_rate": round(rate, 4),
                "answer_passed": len(passes & answer),
                "answer_total": len(answer),
                "clears_threshold": (None if not thresholds else rate >= thresholds[0]),
                "note": note,
            }
        )
        print(
            f"  {name:<38} {len(passes):>4}/30 {len(in_action):>6}/{len(action)} "
            f"{rate:>7.3f} {len(passes & answer):>5}/{len(answer)}  {note}"
        )

    report = {
        "what": "each measured run's pass rate on the action stratum, on the same thirty tasks",
        "task_set_from": options.task_set,
        "action_tasks": len(action),
        "answer_tasks": len(answer),
        "answer_task_ids": sorted(answer),
        "derived_threshold": thresholds,
        "runs": rows,
        "qualification": (
            "DeepSeek's 20/30 is the union of two runs -- thirteen with the stopping "
            "rule on, seven more when the sixteen it cut were re-run with it off -- and "
            "in those runs thinking was on, which was not the declared condition (S-34)."
        ),
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
