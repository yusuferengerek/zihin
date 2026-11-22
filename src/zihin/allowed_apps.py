"""Infers the task's allowed app set from the task instruction.

**This is the specification, not an approximation of one.** The shield's
first-stage predicate is defined as: reads are free, an attempt to write into an
app the task text does not mention is flagged. The allowed set therefore comes
from the instruction — the only source a real deployment has.

`ground_truth/required_apps.json` is this module's **validator, not its input**.
Deriving the set from ground truth would give the shield an oracle it would not
have outside the benchmark, and the accuracy figure below would become
meaningless.

**The accuracy bound is a property of the deployment, not of the experiment.**
Whatever this module gets wrong, the shield gets wrong: a missed app means a
legitimate write is blocked, an extra app means an illegitimate write passes.
The measured figures are in `docs/reports/izinli-uygulama-vekili.md` and the
bound is recorded in S-03.

Infrastructure apps are excluded on purpose. `supervisor` carries the task's own
credentials and addresses and every task touches it; `admin` and `api_docs` are
framework surface. Including them would make the set useless as a boundary, and
the first version of this proxy failed exactly there — 0 of 147 exact, Jaccard
0.227, because evaluation-infrastructure imports were being counted.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

# Apps the agent may always reach. `supervisor` is the task's own account and
# address book; `api_docs` is documentation; `admin` is framework surface.
# `file_system` is deliberately NOT here: a download that writes into it is
# exactly what the shield is built to catch.
INFRASTRUCTURE_APPS = frozenset({"admin", "api_docs", "supervisor"})

# Surface forms per app. The key is the app name AppWorld uses; the values are
# what a task instruction actually says. Written from the instruction texts, not
# guessed: "Venmo" appears capitalised, "simple note" appears spaced, and
# `file_system` is almost never named directly.
APP_SURFACE_FORMS: dict[str, tuple[str, ...]] = {
    "amazon": ("amazon",),
    "file_system": ("file system", "file_system", "filesystem", "downloads folder"),
    "gmail": ("gmail", "email", "e-mail", "inbox", "mail"),
    "phone": ("phone", "contact", "text message", "sms", "alarm"),
    "simple_note": ("simple note", "simple_note", "simplenote", "note"),
    "splitwise": ("splitwise",),
    "spotify": ("spotify", "song", "playlist", "album", "artist"),
    "todoist": ("todoist", "todo", "to-do", "task list"),
    "venmo": ("venmo",),
}


def _pattern(form: str) -> re.Pattern[str]:
    """Word-boundary match, tolerant of the space/underscore split."""
    escaped = re.escape(form).replace(r"\ ", r"[\s_-]+")
    return re.compile(rf"\b{escaped}\b", re.IGNORECASE)


_COMPILED = {app: tuple(_pattern(f) for f in forms) for app, forms in APP_SURFACE_FORMS.items()}


def infer_allowed_apps(instruction: str) -> frozenset[str]:
    """The apps a task instruction mentions.

    Infrastructure apps are always included: the agent needs them to read its
    own credentials and the API documentation, and blocking them would stop
    every task rather than the dangerous ones.
    """
    named = {
        app for app, patterns in _COMPILED.items() if any(p.search(instruction) for p in patterns)
    }
    return frozenset(named | INFRASTRUCTURE_APPS)


def task_instruction(task_id: str, root: str | Path = "data/tasks") -> str:
    """Reads a task's instruction from its `specs.json`."""
    spec = Path(root) / task_id / "specs.json"
    return json.loads(spec.read_text(encoding="utf-8"))["instruction"]


def reference_apps(task_id: str, root: str | Path = "data/tasks") -> frozenset[str] | None:
    """The reference app list, where the split carries one.

    Only `train` and `dev` have it (S-03). Returns None when absent — the
    caller must not mistake "no reference" for "empty reference".
    """
    path = Path(root) / task_id / "ground_truth" / "required_apps.json"
    if not path.exists():
        return None
    return frozenset(json.loads(path.read_text(encoding="utf-8")))
