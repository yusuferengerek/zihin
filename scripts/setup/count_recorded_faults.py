"""Two counts the reports quote and neither had a source: silent faults, and the
design decisions the external review produced.

**A number needs a definition before it needs a source.** "More than twenty silent
faults" cannot be checked until "silent fault" is defined, and no definition was
written down. One is written here, and the classification it produces is stored
rather than recomputed from keywords — a keyword count over a record that
discusses silence constantly would count the discussion, not the faults.

**Definition.** A limitation record is a *silent fault* when all three hold:

1. **It is a fault.** Something behaved differently from what it was written to
   do. Not an external fact, not a scope limit, not a measurement's own bound.
2. **It was silent.** While it was live nothing went red: no test failed, no run
   stopped, no error surfaced.
3. **Something else found it.** A separate measurement, a mutation, a different
   environment, or a hand look — not the fault announcing itself.

**What the definition excludes, deliberately.** External facts (a server state we
cannot see), scope limits (a class the index does not cover), and the bounds of a
measurement (an interval that is a lower bound). Those are limitations too, and
they are not faults.

**The boundary of this count.** Limitation records only. The decision record holds
faults of the same kind — the residency check that worked on no machine is one —
and classifying 146 decisions is not done here. So this number is a **floor over
one file**, and it says so in the artefact rather than being quoted as a total.

**The classification is a judgment, and that is why it is stored.** Each id below
carries the reason it qualifies. Arguing with the list is the point; arguing with
a number that has no list is not possible.

**The second count is mechanical.** The external review's section 4 is one
paragraph per decision — its own opening sentence says so — so the decisions are
counted by counting the paragraphs.

Usage:

    uv run python scripts/setup/count_recorded_faults.py
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[2]
OUTPUT = REPOSITORY / "results/recorded-faults.json"
LIMITATIONS = REPOSITORY / "docs/09-limitations.tr.md"
REVIEW = REPOSITORY / "docs/10-external-review.tr.md"

# The classification. One line each, and the line is the reason.
SILENT_FAULTS = {
    "S-19": "3B's zero calls were a systematic fault, not a capability floor",
    "S-25": "the stopping rule counted a successful read as progress; 736 calls, never fired",
    "S-26": "the same output budget was believed to be the same condition and was not",
    "S-27": "the band scan ran with the superseded stopping rule and nothing said so",
    "S-32": "the endpoint criterion of the stopping rule had never been in force",
    "S-34": "the boundary control ran with thinking on, which was not the declared condition",
    "S-35": "the two sources of the write set disagreed on one endpoint",
    "S-38": "the write-set derivation read an `@app.delete` decorator as a write call",
    "S-42": "binding was looked for across the episode instead of inside the body",
    "S-44": "`actions.error_class` carried one value; the signal was in the status code",
    "S-45": "an index card's condition could discriminate by coincidence",
    "S-46": "the fixed-block share in the architecture document was unmeasured and wrong",
    "S-47": "the binding context limit was characters, not the token window, "
    "and was never measured",
    "S-48": "the index's most frequent pattern could be retrieved by no task",
    "S-49": "forty-five tests never ran in CI, and two environment differences "
    "were invisible locally",
    "S-53": "the recorder's mount point did not fire in remote mode, and it was silent",
    "S-54": "the state probe had a blind spot",
    "S-58": "the 32B measurement ran with two declared conditions drifted",
    "S-59": "the 32B result was read off an incomplete set and a binding ceiling",
    "S-63": "K-60's ceiling rule existed and had never been applied to the three runs",
    "S-64": "unmerged work is the subject of no check; main was a week stale and nothing said so",
    "S-65": "the failure index fell behind the corpus and no check noticed",
}


def limitation_ids(text: str) -> set[str]:
    return set(re.findall(r"^## (S-\d+)", text, re.M))


def review_decisions(text: str) -> list[str]:
    """One paragraph, one decision — the section's own opening sentence says so."""
    section = re.search(r"^## 4\. .*?\n(.*?)^## 5\. ", text, re.M | re.S)
    if not section:
        return []
    body = section.group(1)
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    # The first paragraph introduces the list rather than being a decision.
    return paragraphs[1:] if paragraphs else []


def main() -> None:
    if not LIMITATIONS.exists() or not REVIEW.exists():
        sys.exit("a source document is missing; this count declines rather than guessing.")
    limitations = LIMITATIONS.read_text(encoding="utf-8")
    present = limitation_ids(limitations)
    if len(present) < 40:
        sys.exit(
            f"only {len(present)} limitation ids were found. The document's shape "
            "changed and this parser no longer reads it."
        )
    missing = sorted(set(SILENT_FAULTS) - present)
    if missing:
        sys.exit(
            f"the classification names records that are not in the document: {missing}. "
            "A stored judgment that points at nothing is worse than no judgment."
        )

    decisions = review_decisions(REVIEW.read_text(encoding="utf-8"))
    if not decisions:
        sys.exit("section 4 of the external review could not be read; the count declines.")

    report = {
        "what": "silent faults, and the design decisions the external review produced",
        "silent_fault_definition": [
            "it is a fault: something behaved differently from what it was written to do",
            "it was silent: nothing went red while it was live",
            "something else found it, not the fault announcing itself",
        ],
        "silent_fault_scope": (
            "limitation records only. The decision record holds faults of the same kind "
            "and was not classified, so this is a floor over one file, not a total."
        ),
        "limitation_records": len(present),
        "silent_faults": len(SILENT_FAULTS),
        "silent_fault_ids": {k: SILENT_FAULTS[k] for k in sorted(SILENT_FAULTS)},
        "external_review_decisions": len(decisions),
        "external_review_rule": "one paragraph of section 4 is one decision",
        "external_review_first_words": [d.split(".")[0][:60] for d in decisions],
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"limitation records            : {len(present)}")
    print(f"of them, silent faults        : {len(SILENT_FAULTS)}")
    print("  " + ", ".join(sorted(SILENT_FAULTS)))
    print(f"external review decisions     : {len(decisions)}")
    for line in report["external_review_first_words"]:
        print(f"  - {line}")
    print(f"written: {OUTPUT}")


if __name__ == "__main__":
    main()
