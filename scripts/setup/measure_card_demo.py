"""End-to-end demo: did the card enter the context, and did the model use it?

**Two measurements, and keeping them apart is deliberate.** The model can parse the
card and still ignore it; showing that the card entered the context does not show
that it was used.

  * **Entry.** The card block is inside the prompt file, byte for byte. It is
    measured mechanically, without looking at the model at all: we regenerate the
    block and search for it in the written file, verify that the two prompts differ
    only by the block, and record the difference in the manifest's
    `instruction_file_digest`.

  * **Use.** Does the call sequence the model produces match the sequence on the
    card, and **what happens in the card-free run.** A matching sequence says
    nothing on its own: the model might have made those calls without the card too.
    That is why every task runs twice, with the same seed and the same model, and
    the comparison is paired.

**This is not a pilot.** The precondition gate fired (K-58), the baseline solves
zero, and the primary metric is undefined. The demo does not measure success; it
measures whether the card entered the context and whether it changed the
behaviour.

**There is no skill executor.** The card writes the call sequence and invites the
model to make that sequence itself. Atomic execution (`06-skill-language.tr.md`) is
still not built, so what is tested here is the card's **content**, not its
atomicity.

The run goes through production's own executor: every episode runs with
`scripts/record_run.py`, so the manifest, the shield, the stopping rule and the
recording path are the same as they will be when the experiment runs. This script
only selects tasks, drives the run and measures from the record.

Usage:

    MODEL_SERVER_URL=http://127.0.0.1:11434 uv run python scripts/setup/measure_card_demo.py
"""

from __future__ import annotations

import collections
import json
import os
import pathlib
import sqlite3
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")

from appworld.task import load_task_ids  # noqa: E402

from zihin.allowed_apps import task_instruction  # noqa: E402
from zihin.cards import render_card_block  # noqa: E402
from zihin.compiler import EpisodeSequence, call_from_action, occurrences_of  # noqa: E402
from zihin.config import load_condition_config  # noqa: E402
from zihin.model_server import count_tokens  # noqa: E402
from zihin.records import load_model_config, open_library  # noqa: E402
from zihin.retriever import retrieve  # noqa: E402
from zihin.scaffold import episode_prompt_path, reference_prompt  # noqa: E402

OUTPUT = "results/card-demo.json"
FULL_CONDITION = "config/skills_failures.yaml"
SPLIT = "test_normal"
# How many tasks. The demo is not a statistic; three tasks are enough to say "the
# card entered and this happened", and every task means two episodes.
TASK_COUNT = 3
MAX_STEPS = 20


def base_url() -> str:
    address = os.environ.get("MODEL_SERVER_URL")
    if not address:
        sys.exit("MODEL_SERVER_URL is not set.")
    return address.rstrip("/")


def mined_tasks(connection: sqlite3.Connection, library_id: str) -> set[str]:
    tasks: set[str] = set()
    for row in connection.execute(
        "SELECT supporting_tasks FROM skills WHERE library_id = ?", (library_id,)
    ):
        tasks |= set(json.loads(row["supporting_tasks"]))
    return tasks


def demo_tasks(connection: sqlite3.Connection, library_id: str, index_id: str) -> list[dict]:
    """Deterministic task selection, with its criteria written before the result.

    Four criteria: the task must **not** be one the library was mined from
    (otherwise the demo measures memory), it must receive at least one skill card
    (otherwise the use question cannot be asked), it must name a single app (so the
    card set stays small and the login sequence fits comfortably under the
    twenty-step ceiling), and **every task must come from a different scenario**.

    The order follows the task id, so the selection is known before the run.

    **The fourth criterion was added later and its reason is a defect.** The first
    version sorted by id alone and the first three matches came out as `0a9d82a_1`,
    `0a9d82a_2`, `0a9d82a_3` — three variants of the same scenario, the same app,
    the same card. Three variants are not "three tasks": the use question would
    have been answered on a single card and nothing could be said about the
    behaviour of other cards. The AppWorld id has the form `scenario_variant`, so
    the distinction is mechanical.

    By the time the defect was found, the episodes of the first two variants had
    already run; they were not deleted, they stay in the record, and in the report
    they are labelled separately as **within-scenario repetition**.
    """
    seen = mined_tasks(connection, library_id)
    chosen: list[dict] = []
    scenarios: set[str] = set()
    for task_id in sorted(load_task_ids(SPLIT)):
        if task_id in seen:
            continue
        scenario = task_id.rsplit("_", 1)[0]
        if scenario in scenarios:
            continue
        try:
            instruction = task_instruction(task_id)
        except FileNotFoundError:
            continue
        found = retrieve(
            connection,
            instruction,
            library_id=library_id,
            index_id=index_id,
            min_expected_saving=0,
            max_discriminating_conditions=None,
            include_unverified_cards=True,
            task_id=task_id,
        )
        if not found.skills or len(found.apps) != 1:
            continue
        scenarios.add(scenario)
        chosen.append(
            {
                "task_id": task_id,
                "scenario": scenario,
                "apps": sorted(found.apps),
                "skill_cards": [s.skill_id for s in found.skills],
                "failure_cards": [f.pattern_id for f in found.failures],
                "effects": [e for s in found.skills for e in s.effect_suffix],
                "bodies": {s.skill_id: list(s.body) for s in found.skills},
            }
        )
        if len(chosen) == TASK_COUNT:
            break
    return chosen


def run_episode(connection: sqlite3.Connection, task_id: str, tag: str, with_cards: bool) -> dict:
    """Runs an episode with the production executor, or not at all if it is already
    recorded.

    Skipping is required for two reasons. The first is the record: `UNIQUE (run_id,
    task_id, condition, seed)` refuses a second write of the same episode, so
    re-running means crashing. The second is cost: on the local 7B a twenty-step
    episode can run past fifteen minutes and six episodes do not finish in one
    session. With skipping, the script carries on from where it left off.
    """
    experiment = f"demo-{task_id}-{'kart' if with_cards else 'taban'}"
    run_id = f"{experiment}-{task_id}-{tag.split(':')[1].split('-')[0]}"
    if connection.execute("SELECT 1 FROM episodes WHERE run_id = ? LIMIT 1", (run_id,)).fetchone():
        return {
            "experiment": experiment,
            "run_id": run_id,
            "exit_code": 0,
            "already_recorded": True,
            "stdout_tail": [],
            "stderr_tail": [],
        }
    environment = {
        **os.environ,
        "ZIHIN_TASK_ID": task_id,
        "ZIHIN_SPLIT": SPLIT,
        "ZIHIN_MODEL": tag,
        "ZIHIN_MAX_STEPS": str(MAX_STEPS),
        "ZIHIN_EXPERIMENT": experiment,
    }
    command = [".venv/bin/python", "scripts/record_run.py"]
    if with_cards:
        command.append("--cards")
    finished = subprocess.run(command, env=environment, capture_output=True, text=True)
    return {
        "experiment": experiment,
        "run_id": run_id,
        "exit_code": finished.returncode,
        "already_recorded": False,
        "stdout_tail": finished.stdout.strip().splitlines()[-12:],
        "stderr_tail": finished.stderr.strip().splitlines()[-6:],
    }


def episode_calls(connection: sqlite3.Connection, run_id: str) -> list[dict]:
    """The episode's calls step by step, from the record."""
    rows = connection.execute(
        "SELECT s.step_index, a.action_index, a.app, a.api, a.http_method, a.result_status "
        "FROM steps s JOIN episodes e ON e.episode_id = s.episode_id "
        "LEFT JOIN actions a ON a.step_id = s.step_id "
        "WHERE e.run_id = ? ORDER BY s.step_index, a.action_index",
        (run_id,),
    )
    return [
        {
            "step": r["step_index"],
            "call": (None if r["app"] is None else f"{r['http_method']} {r['app']}.{r['api']}"),
            "status": r["result_status"],
        }
        for r in rows
    ]


def first_step_of(calls: list[dict], element: str, only_successful: bool = False) -> int | None:
    """The first step at which the `element` call appears.

    `only_successful` is a separate measurement, and the distinction was forced by
    a fact found during measurement: in the baseline run `POST
    simple_note.auth/token` appears **twice** and both times returns `401`. Same
    endpoint, same method, but it produces no token. Counted as "reached the
    effect", the place where the card worked and the place where it did not would
    look the same.
    """
    for row in calls:
        if row["call"] != element:
            continue
        if only_successful and str(row["status"]) != "200":
            continue
        return row["step"]
    return None


def episode_sequence(connection: sqlite3.Connection, run_id: str) -> EpisodeSequence:
    """Reads the episode in the compiler's own sequence form.

    The match search uses the compiler's `occurrences_of` function, that is, the
    same search the card was produced with: writing a second matching
    implementation would produce two different right answers, and which one was
    right would not be visible from the number. Only the rows are turned into a
    sequence here.

    The postcondition fields are empty: this measurement searches over `elements`
    alone.
    """
    rows = connection.execute(
        "SELECT s.step_id, a.app, a.api, a.http_method, a.raw_parameters "
        "FROM actions a JOIN steps s ON s.step_id = a.step_id "
        "JOIN episodes e ON e.episode_id = s.episode_id WHERE e.run_id = ? "
        "ORDER BY s.step_index, a.action_index",
        (run_id,),
    ).fetchall()
    calls = tuple(
        call_from_action(r["app"], r["api"], r["http_method"], r["raw_parameters"]) for r in rows
    )
    step_ids = tuple(r["step_id"] for r in rows)
    counts = collections.Counter(step_ids)
    return EpisodeSequence(
        episode_id=0,
        task_id="",
        calls=calls,
        step_ids=step_ids,
        step_call_counts=tuple(counts[s] for s in step_ids),
        step_deltas={},
        observations=(),
    )


def body_appears(sequence: EpisodeSequence, body: list[str], max_gap: int) -> dict:
    """Does the card body appear in the call sequence, under the gap constraint.

    The constraint is the same one the compiler uses when mining (K-81, gap 2): the
    card was produced under that constraint, so the match is searched for under the
    same one. A looser search would count a sequence unrelated to the card while
    saying "the card was used".

    Partial matches are reported as well: how many elements of the body hold in
    order. In a seven-call body, six elements holding and none holding are not the
    same thing.
    """
    found = occurrences_of(tuple(body), sequence, max_gap)
    partial = 0
    for length in range(len(body), 0, -1):
        if occurrences_of(tuple(body[:length]), sequence, max_gap):
            partial = length
            break
    return {
        "matched": bool(found),
        "occurrences": len(found),
        "longest_prefix": partial,
        "body_length": len(body),
        "first_occurrence": list(found[0]) if found else [],
    }


def measure_pair(
    connection: sqlite3.Connection, task_id: str, tag: str, skills: list, slots
) -> dict:
    """The use measurement for one carded/card-free pair.

    The selected tasks and the within-scenario repetition go through the same
    function: two measurements that do not use the same definition cannot be
    compared.
    """
    short_tag = tag.split(":")[1].split("-")[0]
    card_run = f"demo-{task_id}-kart-{task_id}-{short_tag}"
    base_run = f"demo-{task_id}-taban-{task_id}-{short_tag}"
    card_calls = episode_calls(connection, card_run)
    base_calls = episode_calls(connection, base_run)
    card_seq = episode_sequence(connection, card_run)
    base_seq = episode_sequence(connection, base_run)
    detail: dict = {"skills": {}}
    for skill in skills[: slots.skill_slots]:
        body = list(skill.body)
        effect = skill.effect_suffix[0] if skill.effect_suffix else None
        detail["skills"][skill.skill_id] = {
            "effect": effect,
            "effect_step_with_cards": first_step_of(card_calls, effect) if effect else None,
            "effect_step_without_cards": first_step_of(base_calls, effect) if effect else None,
            "successful_effect_step_with_cards": (
                first_step_of(card_calls, effect, only_successful=True) if effect else None
            ),
            "successful_effect_step_without_cards": (
                first_step_of(base_calls, effect, only_successful=True) if effect else None
            ),
            "body_with_cards": body_appears(card_seq, body, max_gap=2),
            "body_without_cards": body_appears(base_seq, body, max_gap=2),
        }
    card_sequence = [r["call"] for r in card_calls if r["call"]]
    base_sequence = [r["call"] for r in base_calls if r["call"]]
    detail["identical_trajectory"] = card_sequence == base_sequence
    detail["calls_with_cards"] = len(card_sequence)
    detail["calls_without_cards"] = len(base_sequence)
    detail["steps_with_cards"] = max((r["step"] for r in card_calls), default=0)
    detail["steps_without_cards"] = max((r["step"] for r in base_calls), default=0)
    # If neither arm produced a call at all, the use question **cannot be asked**,
    # and that is not the same thing as "the card was ignored". The equality of two
    # empty sequences is not an identity claim; the same distinction as K-79's.
    detail["answerable"] = bool(card_sequence or base_sequence)
    detail["card_id_echoed"] = parse_signal(connection, card_run, [s.skill_id for s in skills])
    detail["verdicts"] = {
        name: dict(row) if row else None
        for name, row in (
            (
                name,
                connection.execute(
                    "SELECT v.passed, v.num_passed_tests, v.num_failed_tests, "
                    "e.termination_reason FROM episodes e "
                    "LEFT JOIN verifier_results v ON v.episode_id = e.episode_id "
                    "WHERE e.run_id = ?",
                    (run,),
                ).fetchone(),
            )
            for name, run in (("kartlı", card_run), ("taban", base_run))
        )
    }
    return detail


def within_scenario_repetition(
    connection: sqlite3.Connection, tag: str, slots, library_id: str, index_id: str
) -> dict:
    """Other variants of the same scenario: the bonus pairs sitting in the record.

    The episodes that ran before the selection criterion was corrected
    (`0a9d82a_2`, `0a9d82a_3`). They were not deleted and they are not part of the
    corrected demo either; they show what the same card does in different variants
    of the same app, and they are labelled separately.
    """
    short_tag = tag.split(":")[1].split("-")[0]
    pairs: dict = {}
    for row in connection.execute(
        "SELECT DISTINCT task_id FROM episodes WHERE run_id LIKE 'demo-%' ORDER BY task_id"
    ):
        task_id = row["task_id"]
        card_run = f"demo-{task_id}-kart-{task_id}-{short_tag}"
        base_run = f"demo-{task_id}-taban-{task_id}-{short_tag}"
        complete = all(
            connection.execute("SELECT 1 FROM episodes WHERE run_id = ? LIMIT 1", (run,)).fetchone()
            for run in (card_run, base_run)
        )
        if not complete:
            pairs[task_id] = {"incomplete": True}
            continue
        found = retrieve(
            connection,
            task_instruction(task_id),
            library_id=library_id,
            index_id=index_id,
            min_expected_saving=0,
            max_discriminating_conditions=None,
            include_unverified_cards=True,
            task_id=task_id,
        )
        pairs[task_id] = measure_pair(connection, task_id, tag, found.skills, slots)
    return pairs


def parse_signal(connection: sqlite3.Connection, run_id: str, card_ids: list[str]) -> dict:
    """Did the model repeat the card's id in the text it produced itself?

    A weak but one-directional signal: the id is a sixteen-digit digest, and
    without the card there is no reason for the model to write it. Not repeating it
    says nothing; repeating it says the model read the card.
    """
    metin = "\n".join(
        (r[0] or "")
        for r in connection.execute(
            "SELECT s.generated_code FROM steps s JOIN episodes e "
            "ON e.episode_id = s.episode_id WHERE e.run_id = ?",
            (run_id,),
        )
    )
    return {card_id: (card_id in metin) for card_id in card_ids}


def main() -> None:
    base = base_url()
    tag = load_model_config("config/models.yaml").models[-1]
    slots = load_condition_config(FULL_CONDITION)
    # The library is read from the series it was mined from, not from
    # whichever series runs are being written to (K-143).
    connection, library_id, index_id = open_library()

    tasks = demo_tasks(connection, library_id, index_id)
    print(f"model {tag}, library {library_id}, slot {slots.skill_slots}+{slots.failure_slots}")
    print(f"selected tasks: {[t['task_id'] for t in tasks]}")
    if len(tasks) < TASK_COUNT:
        sys.exit(f"only {len(tasks)} tasks match the criteria; the demo asks for {TASK_COUNT}.")
    print()

    report: list[dict] = []
    for task in tasks:
        task_id = task["task_id"]
        print(f"--- {task_id} ({', '.join(task['apps'])}) ---")
        with_cards = run_episode(connection, task_id, tag, with_cards=True)
        baseline = run_episode(connection, task_id, tag, with_cards=False)
        for name, run in (("kartlı", with_cards), ("taban", baseline)):
            status = (
                "already in the record" if run["already_recorded"] else f"exit {run['exit_code']}"
            )
            print(f"   {name}: {status}")
            if run["exit_code"] != 0:
                for line in run["stderr_tail"] or run["stdout_tail"]:
                    print(f"      {line}")

        # --- first measurement: did the card enter the context ---
        found = retrieve(
            connection,
            task_instruction(task_id),
            library_id=library_id,
            index_id=index_id,
            min_expected_saving=0,
            max_discriminating_conditions=None,
            include_unverified_cards=True,
            task_id=task_id,
        )
        block = render_card_block(
            found, skill_slots=slots.skill_slots, failure_slots=slots.failure_slots
        )
        card_prompt = pathlib.Path(episode_prompt_path(with_cards["run_id"], task_id, 0))
        base_prompt = pathlib.Path(episode_prompt_path(baseline["run_id"], task_id, 0))
        card_text = card_prompt.read_text(encoding="utf-8") if card_prompt.exists() else ""
        base_text = base_prompt.read_text(encoding="utf-8") if base_prompt.exists() else ""
        entry = {
            "block_in_prompt": bool(block) and block in card_text,
            "prompts_differ_only_by_the_block": bool(block)
            and card_text.replace(block, "", 1) == base_text,
            # The card-free arm's prompt has to be byte-identical to the reference
            # (K-25). Otherwise the baseline is no longer the reference scaffold and
            # the paired comparison compares two different scaffolds.
            "baseline_is_the_reference_prompt": bool(base_text) and base_text == reference_prompt(),
            "block_characters": len(block),
            "block_tokens": count_tokens(base, tag, block) if block else 0,
        }
        # The manifest is read from the record itself: the prompt file is on disk,
        # while the manifest carries that file's digest at the moment of the run.
        # Keeping the two apart matters — the file can be rewritten afterwards, the
        # manifest cannot.
        digests = {}
        for name, run in (("kartlı", with_cards), ("taban", baseline)):
            row = connection.execute(
                "SELECT m.instruction_file_digest, m.library_id, e.condition "
                "FROM run_manifests m JOIN episodes e ON e.run_id = m.run_id WHERE m.run_id = ?",
                (run["run_id"],),
            ).fetchone()
            digests[name] = dict(row) if row else None
        entry["prompt_digests"] = digests
        entry["digests_differ"] = (
            digests["kartlı"] is not None
            and digests["taban"] is not None
            and digests["kartlı"]["instruction_file_digest"]
            != digests["taban"]["instruction_file_digest"]
        )
        print(
            f"   entry: block in prompt {entry['block_in_prompt']}, "
            f"difference is only the block {entry['prompts_differ_only_by_the_block']}, "
            f"baseline equals reference {entry['baseline_is_the_reference_prompt']}, "
            f"digests differ {entry['digests_differ']}, block {entry['block_tokens']} tokens"
        )

        # --- second measurement: did the model use it ---
        # The selected tasks and the within-scenario repetition go through the same
        # function.
        use = measure_pair(connection, task_id, tag, list(found.skills), slots)
        for skill_id, detail in use["skills"].items():
            body_with_cards = detail["body_with_cards"]
            body_without_cards = detail["body_without_cards"]
            print(
                f"   use {skill_id}: step reaching the effect, with cards "
                f"{detail['effect_step_with_cards']}, without cards "
                f"{detail['effect_step_without_cards']}"
            )
            print(
                f"      **successful** effect step, with cards "
                f"{detail['successful_effect_step_with_cards']}, without cards "
                f"{detail['successful_effect_step_without_cards']}"
            )
            print(
                f"      body prefix match, with cards "
                f"{body_with_cards['longest_prefix']}/"
                f"{body_with_cards['body_length']}, without cards "
                f"{body_without_cards['longest_prefix']}/"
                f"{body_without_cards['body_length']}"
            )
        print(
            f"   trajectory identical: {use['identical_trajectory']}; "
            f"calls {use['calls_without_cards']} → {use['calls_with_cards']}"
        )
        print()

        report.append(
            {
                "task": task,
                "runs": {"kartlı": with_cards, "taban": baseline},
                "entry": entry,
                "use": use,
            }
        )

    repetition = within_scenario_repetition(connection, tag, slots, library_id, index_id)
    selected = {t["task"]["task_id"] for t in report}
    bonus = {k: v for k, v in repetition.items() if k not in selected}
    print("--- within-scenario repetition (pairs run before the selection was fixed) ---")
    for task_id, detail in sorted(bonus.items()):
        if detail.get("incomplete"):
            print(f"   {task_id}: the pair was not completed, it does not enter the measurement")
            continue
        successful = [
            d["successful_effect_step_with_cards"] is not None for d in detail["skills"].values()
        ]
        print(
            f"   {task_id}: calls {detail['calls_without_cards']} → "
            f"{detail['calls_with_cards']}, trajectory identical "
            f"{detail['identical_trajectory']}, successful effect with cards {sum(successful)}"
            f"/{len(successful)}"
        )
    print()

    pathlib.Path(OUTPUT).write_text(
        json.dumps(
            {
                "model": tag,
                "library_id": library_id,
                "index_id": index_id,
                "split": SPLIT,
                "step_ceiling": MAX_STEPS,
                "skill_slots": slots.skill_slots,
                "failure_slots": slots.failure_slots,
                "tasks": report,
                "within_scenario_repetition": bonus,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"written: {OUTPUT}")

    entered = sum(1 for r in report if r["entry"]["block_in_prompt"])
    only_difference = sum(1 for r in report if r["entry"]["prompts_differ_only_by_the_block"])
    reference = sum(1 for r in report if r["entry"]["baseline_is_the_reference_prompt"])
    answerable = [r for r in report if r["use"]["answerable"]]
    changed = [r for r in answerable if not r["use"]["identical_trajectory"]]
    print()
    print("--- summary ---")
    print("entry measurement, without looking at the model:")
    print(f"   card entered the context    : {entered}/{len(report)}")
    print(f"   difference is only the block: {only_difference}/{len(report)}")
    print(f"   baseline is reference prompt: {reference}/{len(report)}")
    print("use measurement:")
    print(
        f"   task where it can be asked  : {len(answerable)}/{len(report)}"
        f"  (in the rest neither arm produced a call)"
    )
    print(f"   trajectory differs from card-free: {len(changed)}/{len(answerable)}")
    matches = sum(
        1 for r in report for d in r["use"]["skills"].values() if d["body_with_cards"]["matched"]
    )
    total = sum(len(r["use"]["skills"]) for r in report)
    print(f"   body match (with cards)     : {matches}/{total}")
    successful = sum(
        1
        for r in report
        for d in r["use"]["skills"].values()
        if d["successful_effect_step_with_cards"] is not None
    )
    successful_baseline = sum(
        1
        for r in report
        for d in r["use"]["skills"].values()
        if d["successful_effect_step_without_cards"] is not None
    )
    print(
        f"   reaching a successful effect: with cards {successful}/{total}, "
        f"without cards {successful_baseline}"
    )
    if entered != len(report):
        sys.exit(
            "There is an episode where the card did not enter the context; "
            "the use measurement is meaningless."
        )


if __name__ == "__main__":
    main()
