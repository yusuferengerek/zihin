"""The shield's mount point: where the pure predicate meets a live call.

`shield.py` decides; this module resolves and acts. The split is the one written
there: the mount point moves when the sandbox arrives (K-65) and the predicate
must not move with it.

Three jobs, and nothing else:

  1. **Resolve.** A live call carries a URL, a method and a body. The predicate
     wants an app, a route template and a method. The URL is split and resolved
     here, **with the method**, because two templates can match the same string
     (S-36).
  2. **Record.** Every decision is counted; denials also accumulate as rows in
     the shape `shield_violations` stores. The rows drain at the step boundary,
     exactly like `ApiCapture.calls`, so a violation attaches to the step whose
     code produced it.
  3. **Act.** In shadow mode the call proceeds whatever the decision was. Enforce
     is not implemented — see below.

**Why enforce is not implemented yet.** Blocking means the call never reaches
the server, so something has to stand in for the response the agent expected.
What that something is changes what the agent sees, and therefore changes the
measurement: an exception, a 403 body and a silently empty result produce three
different trajectories. That shape is not decided yet, and inventing one here
would be inventing a condition variable. Until it is decided, constructing an
enforcing mount raises.

Shadow mode needs none of it: the call runs, the decision is recorded, nothing
is substituted. The block rate can be measured without ever deciding what a
block looks like.

**Unresolved paths are passed through as themselves.** When the resolver returns
None the concrete path goes to the predicate, which will not find it in the
write set and will answer `UNKNOWN_ENDPOINT`. The key includes the method, so a
concrete path that happens to equal a parameterless template cannot collide with
a real entry under a method that endpoint does not accept.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from zihin.api_routes import route_template, split_endpoint
from zihin.shield import Call, Decision, ShieldMode, WriteSet, evaluate


@dataclass(frozen=True)
class Violation:
    """A denied call, in the columns `shield_violations` holds.

    `api` is the concrete path, not the template, so the row lines up with the
    `actions` row for the same call. The template is derivable from the pair.
    """

    app: str
    api: str
    http_method: str
    raw_parameters: dict[str, Any]
    predicate: str
    mode: str
    reason: str


@dataclass
class ShieldMount:
    """Holds the shield's inputs for one episode and accumulates its output."""

    allowed_apps: frozenset[str]
    write_set: WriteSet
    mode: ShieldMode = ShieldMode.SHADOW
    violations: list[Violation] = field(default_factory=list)
    predicate_counts: Counter[str] = field(default_factory=Counter)

    def __post_init__(self) -> None:
        if self.mode is not ShieldMode.SHADOW:
            raise NotImplementedError(
                "only shadow mode is mounted; enforce needs the substitute response "
                "shape to be decided first, and that shape changes the measurement"
            )

    def check(self, method: str, url: str, data: dict[str, Any] | None) -> Decision:
        """Decides on one live call and records the decision."""
        app, path = split_endpoint(url)
        template = route_template(app, path, method)
        decision = evaluate(
            Call(app=app, endpoint=template if template is not None else path, method=method),
            self.allowed_apps,
            self.write_set,
        )
        self.predicate_counts[str(decision.predicate)] += 1
        if not decision.allowed:
            self.violations.append(
                Violation(
                    app=app,
                    api=path,
                    http_method=method.upper(),
                    raw_parameters=data or {},
                    predicate=str(decision.predicate),
                    mode=str(self.mode),
                    reason=str(decision.reason),
                )
            )
        return decision

    def drain(self) -> list[Violation]:
        """Returns the accumulated violations and empties the buffer.

        Called at the step boundary, in the same place as `ApiCapture.drain`.
        """
        taken = list(self.violations)
        self.violations.clear()
        return taken

    def reset(self) -> None:
        self.violations.clear()
        self.predicate_counts.clear()


def config_digest(write_set_path: str) -> str:
    """Digest of everything that decides what the shield blocks.

    Three inputs, because all three change the answer: the write set, the
    cross-app mapping inside it (`writes_to`), and the allowed-app inferrer.

    A digest rather than a version number. A number has to be bumped by hand
    and the hand forgets; a digest is computed, so a change that nobody
    announced still shows up. The write set has already moved twice in one day
    and neither move would have bumped a number.

    The inferrer goes in as its whole source. Hashing only `APP_SURFACE_FORMS`
    would miss a change in the matching logic, and the matching logic decides
    which apps a task is allowed to touch just as much as the list does.
    """
    import hashlib
    import json
    import pathlib

    from zihin import allowed_apps

    raw = json.loads(pathlib.Path(write_set_path).read_text(encoding="utf-8"))
    payload = json.dumps(
        {
            "endpoints": raw["endpoints"],
            "write_methods": raw.get("write_methods"),
            "allowed_apps_source": pathlib.Path(allowed_apps.__file__).read_text(encoding="utf-8"),
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def mount_for_task(
    task_id: str,
    write_set: WriteSet,
    mode: ShieldMode = ShieldMode.SHADOW,
    task_root: str = "data/tasks",
) -> ShieldMount:
    """Builds the mount for one task.

    The allowed set comes from the task's own text (K-70). `required_apps.json`
    is the validator of that inference, never its input, so it is not read here.
    """
    from zihin.allowed_apps import infer_allowed_apps, task_instruction

    return ShieldMount(
        allowed_apps=infer_allowed_apps(task_instruction(task_id, task_root)),
        write_set=write_set,
        mode=mode,
    )
