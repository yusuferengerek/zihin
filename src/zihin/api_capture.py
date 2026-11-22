"""Wraps AppWorld's API client and records the response and status code.

Why it is needed: `logs/api_calls.jsonl` carries only `method`, `url` and
`data`. Neither the response body nor the status code is there (S-05). The
action-level error taxonomy, failure-index mining and the three-gate blame
attribution all rest on that data, and because collection is one-shot it
cannot be added retroactively (S-16).

Why here: what gets wrapped is the transport layer. The agent's prompt, parser
and loop are untouched, so this is outside the scope of the scaffold
constraint (K-19).

**The recording-order rule.** `Requester._get` and its siblings call
`raise_if_failure` before returning, and raise on a failed response. If the
recording is taken after the exception, exactly the cases we care about are
lost. In the first probe seven of seven calls were reported as 200, while two
of them had failed.

So the recording is taken on both the success and the exception path, and the
exception is re-raised. The order is pinned by a separate test in
`tests/test_api_capture.py`; if a refactor breaks the order, that test fails.

**The shield mounts here too.** This is the last point at which a call is still
a call and not yet a request, so it is where a filter belongs. The wrapper only
asks and records; the decision itself is `shield.evaluate`, and the resolution
is `ShieldMount.check`. Nothing about the predicate lives in this module, so the
move to the loopback proxy (K-65) rewrites the mount and leaves the predicate
alone.

**The shield is consulted before the call runs.** The check happens above the
tracker read, so it applies to the framework's own internal calls as well; those
are reads and pass unconditionally, so nothing is recorded for them.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass, field
from typing import Any

from appworld.requester import Requester

from zihin.shield_mount import ShieldMount

WRAPPED_METHODS = ("_get", "_post", "_patch", "_delete", "_put")


@dataclass
class CapturedCall:
    """A single API call's request and response."""

    method: str
    url: str
    data: dict[str, Any] | None
    status_code: int | None
    response: Any
    error_class: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.error_class is None and self.status_code == 200


@dataclass
class ApiCapture:
    """Accumulates captured calls in order.

    `shield` is optional: when it is None the wrapper does exactly what it did
    before the shield existed. Six conditions share one capture layer and the
    shield is open in all of them (`03-architecture.tr.md`), but the tools that
    replay or probe without a task have no allowed set to give it.
    """

    calls: list[CapturedCall] = field(default_factory=list)
    shield: ShieldMount | None = None

    def reset(self) -> None:
        self.calls.clear()
        if self.shield is not None:
            self.shield.reset()

    def drain(self) -> list[CapturedCall]:
        """Returns the accumulated calls and empties the buffer.

        Called at the step boundary: the calls accumulated between two
        `execute` invocations are that step's actions.
        """
        taken = list(self.calls)
        self.calls.clear()
        return taken


def _status_from_error(error: BaseException) -> int | None:
    """Extracts the HTTP status code from the exception text.

    AppWorld wraps a failed response in an exception shaped like
    `Response status code is 401:` and does not attach the response object to
    the exception.
    """
    response = getattr(error, "response", None)
    if response is not None and getattr(response, "status_code", None) is not None:
        return int(response.status_code)
    text = str(error)
    marker = "Response status code is "
    if marker in text:
        with contextlib.suppress(ValueError):
            return int(text.split(marker, 1)[1].split(":", 1)[0].strip())
    return None


def _body(response: Any) -> Any:
    try:
        return response.json()
    except Exception:
        return getattr(response, "text", None)


def install(capture: ApiCapture, requester_cls: type = Requester) -> dict[str, Any]:
    """Installs the wrappers and returns the original methods for undoing."""
    originals: dict[str, Any] = {}
    for name in WRAPPED_METHODS:
        if not hasattr(requester_cls, name):
            continue
        real = getattr(requester_cls, name)
        originals[name] = real
        setattr(requester_cls, name, _wrap(name, real, capture))
    if not originals:
        raise RuntimeError("no method to wrap was found on Requester")
    return originals


def uninstall(originals: dict[str, Any], requester_cls: type = Requester) -> None:
    for name, real in originals.items():
        setattr(requester_cls, name, real)


def _tracked_count(self: Any) -> int | None:
    """AppWorld's own request counter. None when there isn't one."""
    tracker = getattr(self, "request_tracker", None)
    if tracker is None:
        return None
    requests = getattr(tracker, "requests", None)
    return len(requests) if requests is not None else None


def _wrap(name: str, real: Any, capture: ApiCapture):
    http = name.lstrip("_")

    def wrapped(self, url, data=None, *args: Any, **kwargs: Any):
        # AppWorld does not write the framework's own internal calls (for
        # instance `/supervisor/active_task`) into its tracker. Those calls are
        # not the agent's actions, and recording them would add a phantom
        # action to every step. AppWorld's own counter is used as the test: if
        # the counter grew, the call is the agent's action. Behaviour, not a
        # flag.
        before = _tracked_count(self)

        # The shield sees the call before it becomes a request. In shadow mode
        # the decision changes nothing about what happens next; it is recorded
        # and the call proceeds.
        if capture.shield is not None:
            capture.shield.check(http, url, data)

        try:
            response = real(self, url, data, *args, **kwargs)
        except Exception as error:
            # The recording is taken BEFORE the exception propagates. If the
            # order breaks, failed calls are never recorded and the
            # measurement looks green.
            if _was_tracked(self, before):
                capture.calls.append(
                    CapturedCall(
                        method=http,
                        url=url,
                        data=data,
                        status_code=_status_from_error(error),
                        response=str(error)[:2000],
                        error_class=type(error).__name__,
                    )
                )
            raise
        if _was_tracked(self, before):
            capture.calls.append(
                CapturedCall(
                    method=http,
                    url=url,
                    data=data,
                    status_code=getattr(response, "status_code", None),
                    response=_body(response),
                    error_class=None,
                )
            )
        return response

    return wrapped


def _was_tracked(self: Any, before: int | None) -> bool:
    """Did the call land in AppWorld's own counter?

    When there is no counter (as with the fake client in the tests), every
    call is recorded.
    """
    if before is None:
        return True
    current = _tracked_count(self)
    return current is None or current > before


@contextlib.contextmanager
def capturing(requester_cls: type = Requester, shield: ShieldMount | None = None):
    """Installs the wrapper and undoes it on exit."""
    capture = ApiCapture(shield=shield)
    originals = install(capture, requester_cls)
    try:
        yield capture
    finally:
        uninstall(originals, requester_cls)
