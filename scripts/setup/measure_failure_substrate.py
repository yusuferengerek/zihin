"""What the failure index has to work with, measured before anything is built.

The index needs three things and none of them was guaranteed to exist in this
corpus.

  1. **Failing actions** with something that says how they failed.
  2. **A contrastive counterpart**: the same call succeeding somewhere, so the
     differentiating predicate can be looked for (`07-failure-taxonomy.tr.md`).
  3. **A condition expressible in the closed language**: object existence,
     object field values, or a prior call in the sequence. The response body is
     not persisted (S-40), so object state is not observable per call and only
     the third form is directly recorded.

Usage:

    uv run python scripts/setup/measure_failure_substrate.py
"""

from __future__ import annotations

import collections
import json
import pathlib
import sqlite3
import warnings

warnings.filterwarnings("ignore")

from zihin.api_routes import route_template  # noqa: E402

SERIES = "results/zihin-2.sqlite"
OUTPUT = "results/failure-substrate.json"


def element(app: str, api: str, method: str | None) -> str:
    http = (method or "GET").upper()
    return f"{http} {app}.{route_template(app, api, http) or api}"


def failed(row: sqlite3.Row) -> bool:
    if row["error_class"]:
        return True
    return row["result_status"] is not None and row["result_status"] != "200"


def token_of(row: sqlite3.Row) -> str | None:
    try:
        data = json.loads(row["raw_parameters"])
    except Exception:
        return None
    return data.get("access_token") if isinstance(data, dict) else None


def main() -> None:
    connection = sqlite3.connect(f"file:{SERIES}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    rows = connection.execute(
        """SELECT a.app, a.api, a.http_method, a.result_status, a.error_class,
                  a.raw_parameters, s.episode_id, s.step_index, a.action_index, e.task_id
           FROM actions a
           JOIN steps s USING(step_id)
           JOIN episodes e ON e.episode_id = s.episode_id
           ORDER BY s.episode_id, s.step_index, a.action_index"""
    ).fetchall()

    failures = [r for r in rows if failed(r)]
    status = collections.Counter(r["result_status"] for r in failures)
    # `error_class` is uniformly "Exception": AppWorld raises on every failed
    # response and the status code is parsed out of the exception text. The
    # column carries no signal on its own and the taxonomy has to read the code.
    classes = collections.Counter(r["error_class"] for r in failures)

    fail_by_element: collections.Counter = collections.Counter()
    ok_by_element: collections.Counter = collections.Counter()
    fail_tasks: dict[str, set[str]] = collections.defaultdict(set)
    for row in rows:
        name = element(row["app"], row["api"], row["http_method"])
        if failed(row):
            fail_by_element[name] += 1
            fail_tasks[name].add(row["task_id"])
        elif row["result_status"] == "200":
            ok_by_element[name] += 1

    contrastive = {n for n in fail_by_element if ok_by_element.get(n)}

    # The 401s, split by what the closed language can say about them.
    by_episode: dict[int, list[sqlite3.Row]] = collections.defaultdict(list)
    for row in rows:
        by_episode[row["episode_id"]].append(row)

    unauthorised: collections.Counter = collections.Counter()
    for calls in by_episode.items():
        logged_in: set[str] = set()
        for row in calls[1]:
            app = row["app"]
            if row["result_status"] == "401":
                if app not in logged_in:
                    unauthorised["no prior login"] += 1
                elif token_of(row) is None:
                    unauthorised["logged in, token omitted"] += 1
                else:
                    unauthorised["logged in, token supplied, still refused"] += 1
            method = (row["http_method"] or "").upper()
            if row["result_status"] == "200" and not row["error_class"]:
                if method == "POST" and row["api"].startswith("auth/token"):
                    logged_in.add(app)
            if method == "POST" and row["api"].startswith("auth/logout"):
                logged_in.discard(app)

    per_code_elements = {
        code: dict(
            collections.Counter(
                element(r["app"], r["api"], r["http_method"])
                for r in failures
                if r["result_status"] == code
            ).most_common(8)
        )
        for code in sorted({r["result_status"] for r in failures if r["result_status"]})
    }

    report = {
        "actions": len(rows),
        "failures": len(failures),
        "status_codes": dict(status.most_common()),
        "error_classes": dict(classes.most_common()),
        "distinct_failing_endpoints": len(fail_by_element),
        "with_a_contrastive_counterpart": len(contrastive),
        "failing_in_two_or_more_tasks": sum(1 for v in fail_tasks.values() if len(v) >= 2),
        "task_support_distribution": dict(
            sorted(collections.Counter(len(v) for v in fail_tasks.values()).items())
        ),
        "unauthorised_breakdown": dict(unauthorised.most_common()),
        "endpoints_per_code": per_code_elements,
    }
    pathlib.Path(OUTPUT).write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"actions {len(rows)}, failing {len(failures)} ({len(failures) / len(rows):.1%})")
    print(f"status codes: {dict(status.most_common())}")
    print(
        f"error_class  : {dict(classes.most_common())}  <- single-valued, the signal is in the code"
    )
    print()
    print(f"distinct failing endpoints      : {len(fail_by_element)}")
    print(f"with a contrastive counterpart  : {len(contrastive)}")
    print(f"in two or more tasks            : {report['failing_in_two_or_more_tasks']}")
    print(f"task-support distribution       : {report['task_support_distribution']}")
    print()
    print("--- the 401s, by what the closed condition language can say ---")
    total = sum(unauthorised.values())
    for key, count in unauthorised.most_common():
        print(f"   {count:>4}  {key}  ({count / total:.0%})")
    print()
    for code, elements in per_code_elements.items():
        print(f"--- {code} ---")
        for name, count in elements.items():
            print(f"   {count:>4}x  {name}")
    print(f"\nwritten: {OUTPUT}")


if __name__ == "__main__":
    main()
