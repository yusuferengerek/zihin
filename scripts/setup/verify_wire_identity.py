"""Is the identity the proxy builds from the wire the same as the recorded typed
identity.

**Why it is needed.** The recording proxy sees the call on the wire, and there
are no types on the wire: `requests.get(url, params={"page_index": 0})` writes
`page_index=0` into the query string, and there `0` is text. The identity the
stopping rule sees, however, is the JSON of that dict
(`recording_agent.step_progress_identities`), so a loss of type would change the
identity of 1090 GET actions.

**How the decision is applied.** The type is derived from AppWorld's own route
signature (K-92). The code that does the conversion is not in this script but in
`zihin.api_routes.typed_parameters` — that is, the very code the proxy uses is
what is tested. Were there two copies, this verification would test itself rather
than the proxy.

**What this script does.** It puts every action in the record through the wire
and rebuilds it: it encodes the dict the way `Requester` sends it, then decodes it
with the route's signature, then compares the canonical JSON with the recorded
one. If they match, the proxy will produce the same identity.

**The control arm.** An arm that never looks at the signature is computed as well.
A verification burning green is not proof that it burned for the right reason
(K-49): if the signature-free arm matches too, the measurement tests nothing, and
seeing that requires measuring it.

Output: `results/wire-identity.json`.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from typing import Any
from urllib.parse import parse_qs, urlencode

from zihin.api_routes import route_object, typed_parameters
from zihin.records import ACTIVE_SERIES, open_database

OUTPUT = "results/wire-identity.json"


def wire_form(method: str, path: str, data: dict[str, Any]) -> tuple[str, str]:
    """The encoding `Requester` uses for this call and the body that goes on the
    wire.

    There are three encodings and `Requester` picks between them: GET query
    string, `auth/token` form, the rest JSON. The condition is the same one the
    reference uses; picking again here would be a second source of truth.
    """
    if method.upper() == "GET":
        return "query", urlencode(_requests_params(data), doseq=True)
    if method.upper() == "POST" and "auth/token" in path:
        return "form", urlencode(_requests_params(data), doseq=True)
    return "json", json.dumps(data, ensure_ascii=False)


def _requests_params(data: dict[str, Any]) -> list[tuple[str, Any]]:
    """The pairs the `requests` library writes into the query string.

    It imitates two behaviours, both of which affect the measurement: a parameter
    whose value is `None` is not sent at all, and a parameter whose value is a
    list goes out as a repeated key.
    """
    pairs: list[tuple[str, Any]] = []
    for key, value in data.items():
        if value is None:
            continue
        if isinstance(value, list | tuple):
            pairs.extend((key, str(v)) for v in value)
        else:
            pairs.append((key, str(value)))
    return pairs


def rebuild(encoding: str, body: str, route: Any | None, *, use_signature: bool = True) -> dict:
    """Rebuilds what came off the wire; with `use_signature` false it never looks
    at the signature."""
    if encoding == "json":
        return json.loads(body) if body else {}
    raw = parse_qs(body, keep_blank_values=True)
    return typed_parameters(route if use_signature else None, raw)


def canonical(data: Any) -> str:
    """The same serialization as `insert_action`. Two forms in two places would
    produce a silent divergence."""
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def _reason(recorded: dict[str, Any], rebuilt: dict[str, Any]) -> str:
    if set(recorded) - set(rebuilt):
        return "telde kaybolan parametre"
    if set(rebuilt) - set(recorded):
        return "telde eklenen parametre"
    for key in recorded:
        if type(recorded[key]) is not type(rebuilt[key]):
            return f"type changed: {type(recorded[key]).__name__} -> {type(rebuilt[key]).__name__}"
    return "value changed"


def main() -> None:
    connection = open_database(ACTIVE_SERIES)

    total = 0
    matched = 0
    matched_without_signature = 0
    by_method: Counter[str] = Counter()
    mismatched_by_method: Counter[str] = Counter()
    unresolved = 0
    mismatches: list[dict[str, Any]] = []
    reasons: Counter[str] = Counter()

    for row in connection.execute(
        "SELECT action_id, app, api, http_method, raw_parameters FROM actions ORDER BY action_id"
    ):
        total += 1
        method = row["http_method"] or ""
        by_method[method] += 1
        recorded = json.loads(row["raw_parameters"]) if row["raw_parameters"] else {}
        route = route_object(row["app"], row["api"], method)
        if route is None:
            unresolved += 1
        encoding, body = wire_form(method, row["api"], recorded)
        if canonical(rebuild(encoding, body, route, use_signature=False)) == canonical(recorded):
            matched_without_signature += 1
        rebuilt = rebuild(encoding, body, route)
        if canonical(rebuilt) == canonical(recorded):
            matched += 1
            continue
        mismatched_by_method[method] += 1
        reason = _reason(recorded, rebuilt)
        reasons[reason] += 1
        if len(mismatches) < 40:
            mismatches.append(
                {
                    "action_id": row["action_id"],
                    "app": row["app"],
                    "api": row["api"],
                    "method": method,
                    "encoding": encoding,
                    "recorded": recorded,
                    "rebuilt": rebuilt,
                    "reason": reason,
                }
            )

    report = {
        "ne": "Is the identity the proxy builds from the wire the same as the recorded typed one",
        "kaynak": ACTIVE_SERIES,
        "ceviren_kod": "zihin.api_routes.typed_parameters",
        "toplam_eylem": total,
        "eslesen": matched,
        "eslesmeyen": total - matched,
        "eslesme_orani_yuzde": round(100 * matched / total, 3) if total else None,
        "kontrol_kolu_imzasiz_eslesen": matched_without_signature,
        "kontrol_kolu_imzasiz_eslesmeyen": total - matched_without_signature,
        "kontrol_kolu_notu": (
            "How many actions the signature-free arm fails to match tells how many "
            "actions deriving the type from the signature saved. Zero would have "
            "meant the measurement tests nothing."
        ),
        "yontem_dagilimi": dict(by_method),
        "yonteme_gore_eslesmeyen": dict(mismatched_by_method),
        "rotasi_cozulmeyen_eylem": unresolved,
        "eslesmeme_sebepleri": dict(reasons),
        "ornekler": mismatches,
    }
    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print(f"total action                : {total}")
    print(f"matching with signature     : {matched}  ({report['eslesme_orani_yuzde']}%)")
    print(f"not matching with signature : {total - matched}")
    saved = total - matched_without_signature
    print(f"control: no-signature misses: {saved}  (what the signature saved)")
    print(f"route not resolved          : {unresolved}")
    if matched_without_signature == total:
        print(
            "WARNING: the signature-free arm matched fully too, so this measurement tests nothing."
        )
    if reasons:
        print("mismatch reasons:")
        for reason, count in reasons.most_common():
            print(f"  {reason}: {count}")
    for example in mismatches[:5]:
        print(f"  sample {example['method']} {example['app']}.{example['api']}")
        print(f"    recorded: {example['recorded']}")
        print(f"    rebuilt : {example['rebuilt']}")
    print(f"written: {OUTPUT}")

    # If a single action does not match, the decision counts as untested: on that
    # action the proxy produces an identity other than the recorded one.
    sys.exit(0 if matched == total else 1)


if __name__ == "__main__":
    main()
