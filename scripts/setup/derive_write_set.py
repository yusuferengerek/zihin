"""Derives the static half of the shield's write set.

The shield's first-stage predicate has to answer two questions about a call:
does it write, and **which app does it write to**. The second question is not
decoration. K-41 measured that nine `download_*` endpoints are GETs on one app
that write into `file_system` through a separate access token. A predicate that
looked only at the calling app would wave all nine through, and those nine are
not the shield's blind spot but the hole in the middle of its reason to exist.

**The method decides first; the body scan is the fallback.**

1. *The HTTP method.* POST, PUT, PATCH and DELETE write into the app they are
   addressed to. This is a declared rule, not an inference: a DELETE endpoint
   changing state is what the protocol means, and reading it out of the handler
   body was reading the wrong evidence. The body scan runs **only for GET**.
2. *Session endpoints are the one exception* — see below.
3. *Cross-app writes.* The handler calls a helper from
   `appworld/apps/lib/apis/callers.py`, and that helper calls
   `call_api("<app>", ...)`. The target is the app named in that literal. This
   runs for every endpoint regardless of method.

**Why the method rule.** The body scan was reaching the right answer for DELETE
endpoints through an accident: `ast.walk` descends into a function's decorator
list, every DELETE endpoint carries `@app.delete("/path")`, and the decorator
was being counted as a write call (S-38). Nine `delete_account` endpoints — the
most destructive operations on the whole surface — were in the write set for
that reason alone. Declaring the rule turns an accident into a statement, and
narrows the fragile half of the derivation to the 176 GET endpoints. Verb-name
matching and delegation blindness, the two failures that have already bitten,
stop applying to the other 302.

**Why session endpoints are exempt, and this is prior to the measurement.**
K-69 leaves reads unconditionally free. Logging in is the precondition of
reading: the agent cannot read from an app it has not authenticated to. So if
`login` counts as a write, the shield blocks it on any app the allowed-set
inference missed, the read behind it dies with it, and K-69 becomes
unenforceable. The exemption is derived from K-69, not fitted to a number. The
measurement confirms the derivation rather than producing it: with `login` and
`logout` counted as writes the false-positive rate goes from 4.1% to 24.5%, and
all 30 of the new failures are the same call, `POST /auth/token`.

`logout` goes with `login`. It drops a session token, touches no user data, and
blocking it would leave sessions open while protecting nothing.

**The rule over-includes, knowingly.** 82 of the 302 non-GET endpoints have no
write call in their bodies, and two of them are verified readers:
`admin.show_card_balance` and `admin.validate_card` both look a card up and
return a value. They are in the write set anyway. In a safety mechanism the
directions of error are not symmetric — calling a reader a writer blocks a
legitimate read, and that cost was measured at zero here, while calling a
writer a reader lets a real write through unchecked. Over-inclusion is the safe
direction. Recorded in S-38.

**This is only half the write set.** K-41 fixes the write set as
`static ∪ empirical`, because the two have blind spots in different places: the
static scan cannot see calls delegated to a helper it does not know, and the
empirical side (row-count deltas) cannot see updates that leave the row count
alone. The empirical half is still empty; until it is filled the shield runs on
the static half alone and that is recorded as a limitation.

**Validation.** The scan re-derives a recorded finding. K-41 records 15 GET
endpoints that write, 9 of them `download_*` targeting `file_system`. This
re-derivation finds 12 and 9: the load-bearing half matches exactly, and the
difference is an open item (S-35). Two of the three are explained — they were
never writes at all (S-37) — and one is still open.

The numbers are asserted below. If they move, the detection rule has drifted and
the difference must be understood before the shield uses the output.

Usage:

    uv run python scripts/setup/derive_write_set.py
"""

from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import sys
import warnings

warnings.filterwarnings("ignore")

OUTPUT = pathlib.Path("inputs/write-set-static.json")

# Model write methods. Read from the sources rather than guessed: these are the
# names that appear as write calls in the handler bodies.
WRITE_METHODS = frozenset(
    {
        "save",
        "create",
        "delete",
        "create_save",
        "save_new",
        "delete_all",
        "create_all",
        "save_all",
    }
)

# `update` was in this set and is not a model method. It appears exactly twice
# in the whole surface, both times on a local Python container —
# `relationships.update(...)` on a set and `project_dict.update(...)` on a dict
# — and nowhere as a write. No model class defines it and `callers.py` never
# calls it.
#
# The scan matches on the attribute name alone, with no idea what the receiver
# is, so a container method with a write-sounding name is indistinguishable
# from a model write. That marked two pure reads as writers:
# `phone.show_contact_relationships` and `todoist.show_projects`. Both went on
# to be blocked in shadow mode.
#
# The other eight names carry no such collision: Python containers have no
# `save`, `create`, `delete_all` or `create_save`.

# HTTP methods that write by declaration. Not measured — stated. See the module
# docstring for why the statement replaced the body scan here.
WRITING_HTTP_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})

# The one exemption from the method rule, derived from K-69 rather than fitted
# to a measurement. Reads are unconditionally free; logging in is the
# precondition of reading; therefore login has to be free too, or K-69 cannot be
# enforced. `logout` is its pair: it drops a session token and touches no user
# data.
#
# Named by API rather than by path so that a path rename cannot silently widen
# the exemption. There are 18 of them, `login` and `logout` on each of the nine
# apps that have accounts.
SESSION_APIS = frozenset({"login", "logout"})


def _module_path(module) -> pathlib.Path:
    return pathlib.Path(module.__file__)


def helper_calls() -> dict[str, set[tuple[str, str]]]:
    """Helper function name -> the (app, api) pairs it calls.

    A helper reaches another app through `call_api("<app>", "<api>", ...)`.
    Only literal names are resolved; a computed one would be invisible here and
    that is part of the static half's declared blind spot.

    **The call is recorded, not classified.** `does_file_exist` and
    `enlist_files` also cross the app boundary but they *read*
    (`file_exists`, `show_directory`). Treating every cross-app call as a write
    would inflate the write set and make the shield reject legitimate reads.
    Whether the target writes is decided by looking at the target's own handler.
    """
    from appworld.apps.lib.apis import callers

    tree = ast.parse(_module_path(callers).read_text(encoding="utf-8"))
    calls: dict[str, set[tuple[str, str]]] = {}
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        pairs: set[tuple[str, str]] = set()
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Call):
                continue
            name = inner.func.id if isinstance(inner.func, ast.Name) else None
            if name == "call_api" and len(inner.args) >= 2:
                app_arg, api_arg = inner.args[0], inner.args[1]
                if (
                    isinstance(app_arg, ast.Constant)
                    and isinstance(app_arg.value, str)
                    and isinstance(api_arg, ast.Constant)
                    and isinstance(api_arg.value, str)
                ):
                    pairs.add((app_arg.value, api_arg.value))
        if pairs:
            calls[node.name] = pairs
    return calls


def _body_nodes(handler: ast.FunctionDef):
    """Every node in the handler's body, **excluding its decorators**.

    `ast.walk(handler)` descends into `decorator_list`, and every endpoint is
    decorated with `@app.<method>(...)`. For DELETE endpoints that made the
    decorator itself look like a `.delete()` write call (S-38). Iterating the
    statements instead of the function node is the whole fix.
    """
    for statement in handler.body:
        yield from ast.walk(statement)


def writes_by_method(methods: list[str] | set[str], api: str) -> bool:
    """Does the HTTP method alone settle it.

    Session endpoints are exempt; the docstring at the top of the module gives
    the derivation from K-69.
    """
    return api not in SESSION_APIS and bool(set(methods) & WRITING_HTTP_METHODS)


def writes_directly(handler: ast.FunctionDef) -> bool:
    """Does this handler call a model write method in its own body.

    The fallback, and after the method rule it applies to GET endpoints only.
    """
    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in WRITE_METHODS
        for node in _body_nodes(handler)
    )


def api_writes(handler: ast.FunctionDef, methods: list[str] | set[str], api: str) -> bool:
    """Does this API write into its own app. Method first, body scan second."""
    return writes_by_method(methods, api) or writes_directly(handler)


def helper_targets(
    handlers_by_app: dict[str, dict[str, ast.FunctionDef]],
    methods_by_api: dict[tuple[str, str], list[str]],
) -> dict[str, set[str]]:
    """Helper name -> the apps it *writes* into.

    A cross-app call counts only if the target API itself writes, and "writes"
    means the same thing here as everywhere else. Asking the body scan alone
    would give the helper path a different definition of writing from the direct
    path, and the two would drift.
    """
    targets: dict[str, set[str]] = {}
    for helper, pairs in helper_calls().items():
        apps = set()
        for app, api in pairs:
            handler = handlers_by_app.get(app, {}).get(api)
            if handler is None:
                continue
            if api_writes(handler, methods_by_api.get((app, api), []), api):
                apps.add(app)
        if apps:
            targets[helper] = apps
    return targets


def written_apps(
    body: ast.FunctionDef,
    app: str,
    api: str,
    methods: list[str],
    helpers: dict[str, set[str]],
) -> set[str]:
    """Which apps this API writes into."""
    apps: set[str] = set()
    if api_writes(body, methods, api):
        apps.add(app)
    for node in _body_nodes(body):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in helpers:
                apps |= helpers[node.func.id]
    return apps


def scan() -> dict[str, dict]:
    """One record per **named API**, not per path.

    Keying by path merges the methods that share it and hides GET writers: the
    splitwise receipt download shares `/expenses/{expense_id}/file` with a
    DELETE, so a path-keyed view never shows it as a GET that writes. AppWorld's
    own unit is the named API, and so is the shield's.
    """
    from appworld.apps import get_all_apps
    from appworld.common.imports import import_apis_module

    handlers_by_app: dict[str, dict[str, ast.FunctionDef]] = {}
    routes_by_app: dict[str, list] = {}
    for app in get_all_apps():
        module = import_apis_module(app)
        tree = ast.parse(_module_path(module).read_text(encoding="utf-8"))
        handlers_by_app[app] = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        routes_by_app[app] = [
            r for r in module.app.routes if getattr(r, "path_format", None) is not None
        ]

    # The method rule needs the route's methods, and the helper scan needs them
    # for its targets too, so they are collected before either runs.
    methods_by_api = {
        (app, route.name): sorted(route.methods or [])
        for app, routes in routes_by_app.items()
        for route in routes
    }
    helpers = helper_targets(handlers_by_app, methods_by_api)

    records: dict[str, dict] = {}
    for app, routes in routes_by_app.items():
        for route in routes:
            handler = handlers_by_app[app].get(route.name)
            if handler is None:
                continue
            methods = sorted(route.methods or [])
            # One `writes_to` per named API is only sound because no API carries
            # both GET and a writing method; verified below, and the assertion
            # fails if that ever stops being true.
            records[f"{app}.{route.name}"] = {
                "app": app,
                "api": route.name,
                "path": route.path,
                "methods": methods,
                "writes_to": sorted(written_apps(handler, app, route.name, methods, helpers)),
                # Did the body scan agree? Recorded per endpoint so the
                # over-inclusion the method rule buys stays visible in the
                # artefact itself, not only in a report someone has to find.
                "body_write": writes_directly(handler),
            }
    return records


def main() -> None:
    records = scan()
    writers = {k: v for k, v in records.items() if v["writes_to"]}
    get_writers = {k: v for k, v in writers.items() if "GET" in v["methods"]}
    downloads = {k: v for k, v in get_writers.items() if v["api"].startswith("download_")}
    cross_app = {k: v for k, v in writers.items() if set(v["writes_to"]) - {v["app"]}}
    non_get = {k: v for k, v in records.items() if writes_by_method(v["methods"], v["api"])}
    session = {k: v for k, v in records.items() if v["api"] in SESSION_APIS}
    # The over-inclusion the method rule buys, counted rather than left implicit.
    no_body_write = {k: v for k, v in non_get.items() if not v["body_write"]}

    print(f"named API               : {len(records)}")
    print(f"writing API             : {len(writers)}")
    print(f"GET API that writes     : {len(get_writers)}")
    print(f"  of those, download_*  : {len(downloads)}")
    print(f"cross-app writer        : {len(cross_app)}")
    print(f"by the method rule      : {len(non_get)}")
    print(f"  no write in the body  : {len(no_body_write)}  (knowingly over-included, S-38)")
    print(f"session APIs exempted   : {len(session)}")
    print()
    print("--- GET APIs that write ---")
    for key, record in sorted(get_writers.items()):
        print(f"  {key:52s} -> {record['writes_to']}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(
        {
            "source": "static AST scan of the AppWorld apis modules",
            "write_methods": sorted(WRITE_METHODS),
            # The session endpoints are named in the output, not only
            # subtracted from it. The compiler needs to know which endpoints
            # were exempted, because it answers a different question from
            # the shield and reaches the opposite conclusion about them
            # (K-78). Publishing the list means the compiler reads it rather
            # than guessing which path string means "login".
            "session_endpoints": sorted(
                f"{v['app']}.{v['api']}" for v in records.values() if v["api"] in SESSION_APIS
            ),
            "endpoints": records,
        },
        ensure_ascii=False,
        indent=2,
    )

    # Bytes, not text. A text comparison passes on a CRLF/LF difference and the
    # file that reaches the shield is then not the file that was checked; this
    # repository has already paid for that once, in the decisions CSV.
    fresh = rendered.encode("utf-8")
    if "--check" in sys.argv:
        if not OUTPUT.exists():
            sys.exit(
                f"{OUTPUT} does not exist. The shield reads it, so the run cannot "
                "start without it. It belongs in the repository, not in a results "
                "directory: run this script without --check to write it, and commit it."
            )
        held = OUTPUT.read_bytes()
        if held == fresh:
            print()
            print(f"write set: {OUTPUT} matches the installed appworld package, byte for byte")
            return
        sys.exit(
            f"{OUTPUT} does NOT match what the installed appworld package derives.\n"
            f"  held  : {len(held)} bytes, sha256 {hashlib.sha256(held).hexdigest()[:16]}\n"
            f"  fresh : {len(fresh)} bytes, sha256 {hashlib.sha256(fresh).hexdigest()[:16]}\n"
            "The shield would block and allow different calls here than it did where "
            "this file was written, and every number derived from it — 296 writing "
            "endpoints, 19 crossing the boundary — would be a number from another "
            "environment. Nothing is regenerated automatically: decide which one is "
            "right, then write it deliberately."
        )

    OUTPUT.write_bytes(fresh)
    print()
    print(f"written: {OUTPUT}")

    # The findings this scan has to reproduce.
    #
    # K-41 records 15 GET writers. This scan finds 12, and the difference is
    # settled rather than open: two were the `update` false positives (S-37) and
    # the third, `splitwise.show_group_balance`, was an overcount by K-41 (S-35).
    # The download_* count is the load-bearing half and it has never moved.
    #
    # The method rule's own numbers are asserted too. If the session exemption
    # ever widens or the route table shifts, that must fail here rather than
    # quietly change what the shield blocks.
    problems = []
    if len(get_writers) != 12:
        problems.append(f"GET endpoints that write: expected 12, got {len(get_writers)}")
    if len(downloads) != 9:
        problems.append(f"download_* among them: expected 9, got {len(downloads)}")
    if len(session) != 18:
        problems.append(f"session APIs: expected 18, got {len(session)}")
    if any(w["writes_to"] for w in session.values()):
        still_writing = sorted(k for k, w in session.items() if w["writes_to"])
        problems.append(f"exempted session APIs still marked as writers: {still_writing}")
    # One `writes_to` per named API only holds while no API mixes GET with a
    # writing method. If one ever does, the record shape is wrong and its GET
    # would inherit the write.
    mixed = sorted(
        k
        for k, v in records.items()
        if "GET" in v["methods"] and set(v["methods"]) & WRITING_HTTP_METHODS
    )
    if mixed:
        problems.append(f"APIs carrying both GET and a writing method: {mixed}")
    if problems:
        print()
        for line in problems:
            print(f"  MISMATCH: {line}")
        sys.exit(
            "The scan does not reproduce the recorded findings. The detection rule is not "
            "the one that produced them; the difference must be understood before the shield "
            "uses this output."
        )
    print("Reproduced: 12 GET writers, 9 of them download_*, 18 session APIs exempt.")
    print("K-41 records 15 GET writers; all three of the difference are accounted")
    print("for — two were never writes (S-37), one was K-41's overcount (S-35).")


if __name__ == "__main__":
    main()
