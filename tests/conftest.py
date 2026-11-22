"""Shared pinning for every test.

The dirty-working-tree gate reads the real `git status` and affects every test
that writes a manifest. Unpinned, the tests fail during development and pass in
CI; what a test checks would depend on the repository's state at that moment.

The gate's own tests override this explicitly, so the gate stays under test.

## When the installed AppWorld app modules are absent

`route_table()` builds endpoint resolution out of AppWorld's **app modules**
(`appworld.apps.venmo` and its siblings). Those modules come with `appworld
install`, not with the package itself: the package carries only
`appworld.apps.lib`. CI installs the package and does not run `appworld install`
(K-32).

The consequence was measured and it was a defect: 45 tests pass locally and fail
in CI with `ModuleNotFoundError`. They did not carry the `appworld` marker, so
`-m "not appworld"` did not filter them out, and a four-item test suite had
**never run** them — CI never saw them because the branch was never pushed
(S-49).

The fix is not a marker list but a skip at call time: when the app modules are
absent, a call to `route_table` skips the test. The reason is list maintenance —
which module touches resolution changes over time and a hand-kept list goes stale
in silence. This hook covers a new test on its own.

With the app modules present nothing changes; the full suite runs locally.
"""

from __future__ import annotations

import pytest


def _app_modules_present() -> bool:
    """Has `appworld install` run: can an app module be imported."""
    try:
        import appworld.apps.admin  # noqa: F401
    except Exception:
        return False
    return True


APP_MODULES_PRESENT = _app_modules_present()


@pytest.fixture(autouse=True)
def clean_working_tree(monkeypatch):
    monkeypatch.setattr("zihin.records.working_tree", lambda: "clean")


@pytest.fixture(autouse=True)
def kurulu_appworld_gerekiyorsa_atla(monkeypatch):
    """When the app modules are absent, a test that needs them is skipped.

    The patch goes on **AppWorld's own** `import_apis_module`, not on our
    `route_table`. The reason was measured: the tests import `route_table`
    directly (`from zihin.api_routes import route_table`), so patching the module
    attribute does not change the name the caller holds and the test fails anyway.
    The missing capability is one layer down already: importing the app module.

    The skip happens at call time. A test that does not touch resolution keeps
    running, and a new test is covered on its own — a hand-kept module list went
    stale in silence.
    """
    if APP_MODULES_PRESENT:
        return

    def atla(*_args, **_kwargs):
        pytest.skip(
            "no installed AppWorld app modules; endpoint resolution requires `appworld install`"
        )

    monkeypatch.setattr("appworld.common.imports.import_apis_module", atla)
