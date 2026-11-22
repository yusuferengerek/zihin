"""Resolves a concrete URL to AppWorld's route template.

Why this exists: the reported diagnostic "how many distinct operations did this
episode touch" needs an identity that is free of concrete ids. `notes/3084` and
`notes/3085` are the same operation; the `notes` list and the `notes/{note_id}`
detail are different ones.

**This is not the stopping rule's criterion.** The rule compares concrete calls
(`step_progress_identities`). Route templates feed the per-episode diagnostic
`distinct_endpoints`, whose ratio to `distinct_resources` separates exploration
from repetition (K-63).

Why a route table rather than a hand-written rule: ids are not only numeric.
`friends/{user_email}` carries an email, `files/{file_path}` carries a path. A
heuristic that drops numeric path segments catches none of them. AppWorld's own
route table is the authoritative definition and it is exact: every app's `apis`
module holds the FastAPI routes, each route has a compiled `path_regex`, and
the server already matches requests with those very patterns.

No extra cost: the `apis` modules are already imported into the same process
when the AppWorld world is created, and the table is built from them on first
use.

Coverage was measured: 7138 of the 7138 calls across 239 recorded episodes
resolve.

**The HTTP method is not part of the identity.** `GET /transactions` and
`POST /transactions` map to the same endpoint. A writing call changes
verifiable state and so passes the first criterion anyway; a failing write is
genuine stagnation. The boundary is deliberate and recorded here.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

# FastAPI adds these to every app by itself; they are not endpoints the agent
# reaches.
FRAMEWORK_ROUTES = frozenset({"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"})


@lru_cache(maxsize=1)
def route_table() -> dict[str, tuple[tuple[re.Pattern[str], str, frozenset[str]], ...]]:
    """App name to (compiled pattern, template, methods) triples.

    The methods are kept because the path alone is not always enough to
    identify a route. `phone` declares two pairs whose patterns match exactly
    the same strings:

        GET, DELETE  /messages/text/{text_message_id}
        POST         /messages/text/{phone_number}

    and the same for voice messages. Resolving by path alone returns whichever
    comes first, which was measured to be wrong for 26 recorded calls (S-36).
    The methods are disjoint within each pair, so the method resolves them.
    """
    from appworld.apps import get_all_apps
    from appworld.common.imports import import_apis_module

    table: dict[str, tuple[tuple[re.Pattern[str], str, frozenset[str]], ...]] = {}
    for app in get_all_apps():
        module = import_apis_module(app)
        by_path: dict[str, tuple[re.Pattern[str], set[str]]] = {}
        for route in module.app.routes:
            # `path_format` exists only on path routes, not on mounts.
            if getattr(route, "path_format", None) is None:
                continue
            if route.path in FRAMEWORK_ROUTES:
                continue
            pattern, methods = by_path.setdefault(route.path, (route.path_regex, set()))
            methods |= set(route.methods or ())
        table[app] = tuple(
            (pattern, path, frozenset(methods)) for path, (pattern, methods) in by_path.items()
        )
    return table


def split_endpoint(url: str) -> tuple[str, str]:
    """Splits a recorded URL into its app and its path.

    It lives here because it is the entry to route resolution: everything that
    resolves an endpoint starts with this split, and a second copy of the
    parsing would be a second interface for the same string. It used to sit in
    `recording_agent`, but the shield's mount point needs it and that module
    already imports the capture layer.
    """
    parts = [p for p in url.split("/") if p]
    app = parts[0] if parts else "unknown"
    endpoint = "/".join(parts[1:]) if len(parts) > 1 else ""
    return app, endpoint


def route_template(app: str, path: str, method: str | None = None) -> str | None:
    """The route template for `path`, or None when there is no match.

    `path` comes in the shape `split_endpoint` produces, without the leading
    slash. The returned template uses the same shape:
    `transactions/{transaction_id}`.

    **Pass the method whenever it is known.** Two templates can match the same
    string, and without the method the answer is whichever route the table
    happens to hold first. With the method given, a path that matches no route
    accepting that method returns None — the honest answer for a call the
    server would refuse anyway.

    Returning None means "unknown endpoint" and the caller decides what to do
    with it.
    """
    records = route_table().get(app)
    if not records:
        return None
    target = "/" + path
    wanted = method.upper() if method else None
    fallback: str | None = None
    for pattern, template, methods in records:
        if not pattern.match(target):
            continue
        if wanted is None:
            return template.lstrip("/")
        if wanted in methods:
            return template.lstrip("/")
        fallback = fallback or template.lstrip("/")
    # A path matched but no route accepts this method. That is a 405, not an
    # endpoint we failed to find; `fallback` is deliberately not returned.
    return None if wanted else fallback


def path_parameters(app: str, path: str, method: str | None = None) -> dict[str, str]:
    """The values the path template captured: `{"note_id": "3084"}`.

    The compiler needs them because a path parameter is an argument like any
    other — `notes/3084` and `notes/3085` are the same call with a different
    argument, and a classifier that only looked at the request body would treat
    them as two different calls and no pattern would ever gain support.

    Resolution goes through the same matcher as `route_template`, method and
    all, rather than re-parsing the path. Returns an empty dict when nothing
    matches, which is also the honest answer for a template with no parameters.
    """
    records = route_table().get(app)
    if not records:
        return {}
    target = "/" + path
    wanted = method.upper() if method else None
    for pattern, _template, methods in records:
        match = pattern.match(target)
        if not match:
            continue
        if wanted is not None and wanted not in methods:
            continue
        return {k: v for k, v in match.groupdict().items() if v is not None}
    return {}


@lru_cache(maxsize=1)
def route_objects() -> dict[str, tuple[Any, ...]]:
    """App name to route **objects**.

    `route_table` gives the patterns and the templates; here the object itself is
    needed, because what converts a query parameter to its type is the route's
    `dependant` fields. Both tables are built from the same source and both use
    the same filter.
    """
    from appworld.apps import get_all_apps
    from appworld.common.imports import import_apis_module

    table: dict[str, tuple[Any, ...]] = {}
    for app in get_all_apps():
        module = import_apis_module(app)
        table[app] = tuple(
            route
            for route in module.app.routes
            if getattr(route, "path_format", None) is not None
            and route.path not in FRAMEWORK_ROUTES
        )
    return table


def route_object(app: str, path: str, method: str) -> Any | None:
    """The route object for a call, or None when nothing matches.

    The method is mandatory, for the same reason as in `route_template`: two
    route patterns can match exactly the same strings, and without the method
    which one comes back is left to the table's order (S-36).
    """
    target = "/" + path
    for route in route_objects().get(app, ()):
        if route.path_regex.match(target) and method.upper() in (route.methods or ()):
            return route
    return None


def _is_sequence_field(field: Any) -> bool:
    annotation = str(getattr(field.field_info, "annotation", ""))
    return any(mark in annotation for mark in ("list[", "List[", "tuple[", "set["))


def _coerce_by_annotation(field: Any, value: Any) -> Any:
    """Converts to the declared type, ignoring constraints.

    A validation error need not be a type problem: the `page_limit` field is
    `int` but carries `le=20`, and validation fails when the agent writes 50.
    What we are after is the type, not validity; the constraint is the server's
    business and the server enforces it itself.
    """
    annotation = str(getattr(field.field_info, "annotation", ""))
    if isinstance(value, list):
        return value
    try:
        if "bool" in annotation:
            return {"true": True, "false": False}[str(value).strip().lower()]
        if "int" in annotation:
            return int(value)
        if "float" in annotation:
            return float(value)
    except (ValueError, KeyError):
        return value
    return value


def typed_parameters(route: Any | None, raw: dict[str, list[str]]) -> dict[str, Any]:
    """Converts the query string's text values to types using the route's signature.

    **Why it is needed.** There are no types on the wire: `params={"page_index": 0}`
    writes `page_index=0` into the query string, and `0` is text there. The
    identity the stopping rule sees is the JSON of that dict, so losing the type
    changes the identity — in 1090 of the record's 5261 actions (K-92).

    **What converts is the server's own code.** `ModelField.validate`, the same
    validator AppWorld uses when it serves the request. A type table of our own
    writing would go stale in silence the moment a signature changed.

    When the route does not resolve there is no type information and the value
    stays text: the server does not know that call either, so this is the honest
    answer.
    """
    if route is None:
        return {key: (values[0] if len(values) == 1 else values) for key, values in raw.items()}

    dependant = route.dependant
    fields = {
        field.name: field for field in list(dependant.query_params) + list(dependant.body_params)
    }
    typed: dict[str, Any] = {}
    for key, values in raw.items():
        field = fields.get(key)
        if field is None:
            typed[key] = values[0] if len(values) == 1 else values
            continue
        candidate: Any = values if _is_sequence_field(field) else values[0]
        value, errors = field.validate(candidate, {}, loc=("query", key))
        typed[key] = _coerce_by_annotation(field, candidate) if errors else value
    return typed


def endpoint_identity(app: str, path: str, method: str | None = None) -> str:
    """Endpoint identity for the diagnostic: `venmo.transactions/{id}`.

    A path that does not resolve is used as-is, with no marker prepended: two
    different unresolved paths count as two different endpoints.
    """
    template = route_template(app, path, method)
    return f"{app}.{path if template is None else template}"
