"""The resume logic of an interrupted run.

The rule-off run was terminated from outside at 21/26 and the resume mechanism
ran here for the first time. The main run will rest on the same mechanism, so the
logic is not a one-off skip and its tests live here.

Two claims are checked. First, that completeness is read from the database and
under a **completeness** criterion. Second, and the real one: skipping can only
remove elements from the work list, it cannot change how a remaining episode
runs. The second falls into the "expected to have no effect" class, and this
repository measures such things.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

from zihin import records
from zihin.records import (
    RecordError,
    completed_runs,
    insert_episode,
    insert_run_manifest,
    open_database,
    resume_check,
)

KOSUCU = Path(__file__).resolve().parents[1] / "scripts" / "setup" / "measure_rule_off.py"


@pytest.fixture(scope="module")
def kosucu():
    """Loads `measure_rule_off.py` as a module.

    The real file is checked, not a copy: a copied call site is exactly the thing
    that can drift away wholesale (S-28).
    """
    spec = importlib.util.spec_from_file_location("rule_off", KOSUCU)
    modul = importlib.util.module_from_spec(spec)
    previous, sys.argv = sys.argv, ["measure_rule_off.py", "bant3", "bant3-kapali"]
    try:
        spec.loader.exec_module(modul)
    finally:
        sys.argv = previous
    return modul


def _manifest(**degisiklik):
    fields = {
        "created_at": "uptime:1.0",
        "model_tag": "qwen2.5-coder:7b-instruct-q4_K_M",
        "num_ctx_requested": 32768,
        "num_ctx_effective": 32768,
        "context_verified": 1,
        "kv_cache_type": "q8_0",
        "flash_attention": 1,
        "temperature": 0.2,
        "base_seed": 123,
        "keep_alive": "30m0s",
        "no_progress_limit": 0,
        "max_output_tokens": 400,
        "max_prompt_characters": 50000,
        "model_server_env": {"OLLAMA_CONTEXT_LENGTH": "32768"},
        "appworld_version": "0.2.0.dev0",
        "appworld_commit": "a072b7a",
        "code_commit": "deadbeef",
        "instruction_file_digest": "0" * 64,
        "os_environment": "Linux / 3.11",
        "shield_mode": "shadow",
        "shield_config_digest": "a" * 64,
    }
    fields.update(degisiklik)
    return fields


def _write_episode(db, run_id: str, task: str, step: bool = True, verdict: bool = True) -> int:
    from zihin.records import insert_step, insert_verifier_result

    insert_run_manifest(db, **_manifest(run_id=run_id))
    episode_id = insert_episode(
        db,
        run_id=run_id,
        task_id=task,
        split="test_normal",
        condition="baseline",
        model_ref="qwen2.5-coder:7b-instruct-q4_K_M",
        seed=1,
        sequence_in_run=1,
        model_load_state="cold",
        started_at="uptime:1.0",
    )
    if step:
        insert_step(db, episode_id=episode_id, step_index=1, instruction_digest="0" * 64)
    if verdict:
        insert_verifier_result(db, episode_id=episode_id, passed=0)
    return episode_id


@pytest.fixture
def db(tmp_path):
    with open_database(tmp_path / "record.sqlite") as connection:
        yield connection


def test_a_complete_episode_counts_as_done(db):
    with db:
        _write_episode(db, "prefix-g1-g1-7b", "g1")
    assert completed_runs(db, ["prefix-g1-g1-7b"]) == {"prefix-g1-g1-7b"}


def test_an_episode_without_steps_does_not_count(db):
    with db:
        _write_episode(db, "prefix-g1-g1-7b", "g1", step=False)
    assert completed_runs(db, ["prefix-g1-g1-7b"]) == set()


def test_an_episode_without_a_verdict_does_not_count(db):
    with db:
        _write_episode(db, "prefix-g1-g1-7b", "g1", verdict=False)
    assert completed_runs(db, ["prefix-g1-g1-7b"]) == set()


def test_prefixes_do_not_bleed_into_each_other(db):
    """The pattern `bant3-` would catch `bant3-kapali-...` ids as well."""
    with db:
        _write_episode(db, "bant3-kapali-g1-g1-7b", "g1")
    assert completed_runs(db, ["bant3-g1-g1-7b"]) == set()


def test_an_empty_database_skips_nothing(db, kosucu):
    target = [{"task": f"g{i}", "ceiling": 20} for i in range(4)]
    assert kosucu.remaining_tasks(db, target, "prefix") == target


def test_only_completed_episodes_are_removed_and_order_is_kept(db, kosucu):
    target = [{"task": f"g{i}", "ceiling": 20 + i} for i in range(5)]
    with db:
        for task in ("g1", "g3"):
            _write_episode(db, kosucu.run_id_for(task, "prefix"), task)
    remaining = kosucu.remaining_tasks(db, target, "prefix")
    assert [s["task"] for s in remaining] == ["g0", "g2", "g4"]


def test_skipping_cannot_change_how_a_remaining_episode_runs(db, kosucu):
    """The real claim: skipping only removes elements.

    A remaining episode command and environment are identical regardless of which
    episodes were skipped. Nothing depends on position — neither the sequence
    number nor the seed is affected by skipping.
    """
    target = [{"task": f"g{i}", "ceiling": 20 + i} for i in range(5)]
    once = {
        s["task"]: kosucu.episode_command(s["task"], s["ceiling"], "prefix", False) for s in target
    }

    with db:
        for task in ("g0", "g1", "g3"):
            _write_episode(db, kosucu.run_id_for(task, "prefix"), task)
    remaining = kosucu.remaining_tasks(db, target, "prefix")

    assert [s["task"] for s in remaining] == ["g2", "g4"]
    for s in remaining:
        sonra = kosucu.episode_command(s["task"], s["ceiling"], "prefix", False)
        assert sonra == once[s["task"]], f"{s['task']} call was affected by skipping"


def test_options_are_parsed_without_module_state(kosucu):
    assert kosucu.parse_options(["bant3", "bant3-kapali"]) == ("bant3", "bant3-kapali", False)
    assert kosucu.parse_options(["bant3"]) == ("bant3", "bant3-kapali", False)
    assert kosucu.parse_options(["bant3", "--allow-dirty-tree"])[2] is True


def test_the_rule_is_off_in_the_command(kosucu):
    command, _ = kosucu.episode_command("g1", 20, "prefix", False)
    assert "--stop-threshold" in command
    assert command[command.index("--stop-threshold") + 1] == "0"


# ---------------------------------------------------------------------------
# Condition check
# ---------------------------------------------------------------------------
# Skipping alone is not enough. If the written episodes condition differs from
# the current one, resuming joins two different measurements into one set, and
# the manifest records that but does not prevent it. Caught during a real run
# (S-30).


def _yazili(db, run_id="prefix-g1-g1-7b", **degisiklik):
    with db:
        insert_run_manifest(db, **_manifest(run_id=run_id, **degisiklik))
        episode_id = insert_episode(
            db,
            run_id=run_id,
            task_id="g1",
            split="test_normal",
            condition="baseline",
            model_ref="qwen2.5-coder:7b-instruct-q4_K_M",
            seed=1,
            sequence_in_run=1,
            model_load_state="cold",
            step_ceiling=20,
            started_at="uptime:1.0",
        )
        from zihin.records import insert_step, insert_verifier_result

        insert_step(db, episode_id=episode_id, step_index=1, instruction_digest="0" * 64)
        insert_verifier_result(db, episode_id=episode_id, passed=0)
    return run_id


def _expected(**degisiklik):
    fields = {
        "model_tag": "qwen2.5-coder:7b-instruct-q4_K_M",
        "serving_mode": "local",
        "temperature": 0.2,
        "base_seed": 123,
        "max_output_tokens": 400,
        "max_prompt_characters": 50000,
        "no_progress_limit": 0,
        "library_id": None,
        "shield_mode": "shadow",
        "shield_config_digest": "a" * 64,
        "working_tree": "clean",
        "condition": "baseline",
        "split": "test_normal",
        "step_ceiling": 20,
    }
    fields.update(degisiklik)
    return fields


def test_matching_conditions_pass(db):
    run_id = _yazili(db)
    assert resume_check(db, {run_id: _expected()}).passed


def test_a_changed_output_budget_is_refused(db):
    """Today real scenario: resuming with 4000 on top of episodes budgeted at 400."""
    run_id = _yazili(db)
    check = resume_check(db, {run_id: _expected(max_output_tokens=4000)})
    assert not check.passed
    assert any("max_output_tokens" in s for s in check.reddet)


def test_a_changed_prompt_ceiling_is_refused(db):
    """This is the number that decides the effective context (S-47), in the same
    class as the output budget.

    A set running half at 50000 and half without a ceiling is a mixture of two
    context lengths, and the difference can only be read off the manifest.
    """
    run_id = _yazili(db)
    check = resume_check(db, {run_id: _expected(max_prompt_characters=-1)})
    assert not check.passed
    assert any("max_prompt_characters" in s for s in check.reddet)


def test_a_changed_stopping_threshold_is_refused(db):
    run_id = _yazili(db)
    assert not resume_check(db, {run_id: _expected(no_progress_limit=15)}).passed


def test_a_changed_condition_is_refused(db):
    """Episodes of the baseline condition and of a run with mechanisms cannot join one set."""
    run_id = _yazili(db)
    check = resume_check(db, {run_id: _expected(condition="skills")})
    assert not check.passed
    assert any("condition" in s for s in check.reddet)


def test_a_changed_split_is_refused(db):
    run_id = _yazili(db)
    assert not resume_check(db, {run_id: _expected(split="train")}).passed


def test_a_changed_step_ceiling_is_refused(db):
    """If the ceiling multiplier k changes, the per-task ceiling changes and shows up here."""
    run_id = _yazili(db)
    assert not resume_check(db, {run_id: _expected(step_ceiling=40)}).passed


def test_a_changed_library_is_refused(db):
    run_id = _yazili(db)
    assert not resume_check(db, {run_id: _expected(library_id="v3")}).passed


def test_a_dirty_half_is_refused(db):
    """A different commit is definable, a dirty tree is not."""
    run_id = _yazili(db)
    assert not resume_check(db, {run_id: _expected(working_tree="dirty")}).passed


def test_unlisted_fields_are_not_compared(db):
    """The caller need not know every field; a field left out passes in silence."""
    run_id = _yazili(db)
    assert resume_check(db, {run_id: {"model_tag": "qwen2.5-coder:7b-instruct-q4_K_M"}}).passed


def test_server_env_difference_warns_but_does_not_refuse(db):
    run_id = _yazili(db)
    check = resume_check(
        db,
        {run_id: _expected(model_server_env={"OLLAMA_CONTEXT_LENGTH": "16384"})},
    )
    assert check.passed
    assert any("OLLAMA_CONTEXT_LENGTH" in s for s in check.uyar)


def test_an_empty_target_passes(db):
    assert resume_check(db, {}).passed


def test_a_changed_shield_mode_is_refused(db):
    """A set running half in shadow and half in enforce is two different measurements."""
    run_id = _yazili(db)
    check = resume_check(db, {run_id: _expected(shield_mode="off")})
    assert not check.passed
    assert any("shield_mode" in s for s in check.reddet)


def test_a_changed_shield_configuration_is_refused(db):
    """Same mode, different write set: the violations produced are incomparable.

    This is not a theoretical risk. The write set changed twice in one day;
    neither change touched the mode and both changed which call the shield
    blocked.
    """
    run_id = _yazili(db)
    check = resume_check(db, {run_id: _expected(shield_config_digest="b" * 64)})
    assert not check.passed
    assert any("shield_config_digest" in s for s in check.reddet)


# ---------------------------------------------------------------------------
# The manifest half of the resume
# ---------------------------------------------------------------------------
# Everything above tests the episode side: which episodes are skipped, and
# whether the condition of the ones already written matches. The manifest side
# had no test, and it is the half that broke. A Colab session was reclaimed
# between the manifest write and the episode write; the task was therefore not
# complete, the runner started it again, and the insert failed on
# `UNIQUE constraint failed: run_manifests.run_id`. Two things had to agree and
# only one of them had been made resume-aware (K-155).
#
# Every case below leaves the record in that exact state - a manifest, no
# episode - because that is the state a timeout produces and the state no test
# was building.


def _manifest_only(db, run_id="prefix-g1-g1-7b", **degisiklik):
    """What a session killed between the two writes leaves behind."""
    with db:
        insert_run_manifest(db, **_manifest(run_id=run_id, **degisiklik))
    return run_id


def test_a_timeout_leaves_a_manifest_that_no_episode_completes(db):
    """The state the fix is about, asserted rather than assumed."""
    run_id = _manifest_only(db)
    assert completed_runs(db, [run_id]) == set()
    assert (
        db.execute("SELECT COUNT(*) FROM run_manifests WHERE run_id = ?", (run_id,)).fetchone()[0]
        == 1
    )


def test_restarting_after_a_timeout_writes_no_second_manifest(db):
    """The failure itself: the same run id, the same conditions, a second time."""
    run_id = _manifest_only(db)
    with db:
        insert_run_manifest(db, **_manifest(run_id=run_id))
    assert (
        db.execute("SELECT COUNT(*) FROM run_manifests WHERE run_id = ?", (run_id,)).fetchone()[0]
        == 1
    )


def test_a_restart_after_a_completed_episode_is_also_accepted(db):
    """The other partial state: manifest and episode written, the runner re-entered."""
    run_id = _yazili(db)
    with db:
        insert_run_manifest(db, **_manifest(run_id=run_id))
    assert (
        db.execute("SELECT COUNT(*) FROM run_manifests WHERE run_id = ?", (run_id,)).fetchone()[0]
        == 1
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("model_tag", "qwen2.5-coder:14b-instruct-q4_K_M"),
        ("max_output_tokens", 4000),
        ("max_prompt_characters", 20000),
        ("no_progress_limit", 40),
        ("shield_mode", "enforce"),
        ("shield_config_digest", "b" * 64),
        ("temperature", 0.7),
        ("base_seed", 7),
        ("num_ctx_requested", 8192),
    ],
)
def test_a_restart_onto_a_different_condition_is_refused(db, field, value):
    """Accepting the second write silently would put two conditions under one id.

    The same fields as the episode-side check, because it is the same check: the
    manifest write calls `resume_check` rather than carrying its own list.
    """
    run_id = _manifest_only(db)
    with pytest.raises(RecordError) as error:
        with db:
            insert_run_manifest(db, **_manifest(run_id=run_id, **{field: value}))
    assert field in str(error.value)
    assert (
        db.execute("SELECT COUNT(*) FROM run_manifests WHERE run_id = ?", (run_id,)).fetchone()[0]
        == 1
    )


def test_the_manifest_write_calls_the_episode_side_comparison(monkeypatch, db):
    """Not "does it behave the same" - does it call the same code.

    Two implementations that agree today are two implementations, and this
    repository's recurring defect is the second copy falling behind the first.
    """
    run_id = _manifest_only(db)
    calls = []
    gercek = records.resume_check

    def izle(*args, **kwargs):
        calls.append(kwargs)
        return gercek(*args, **kwargs)

    monkeypatch.setattr(records, "resume_check", izle)
    with db:
        insert_run_manifest(db, **_manifest(run_id=run_id))
    assert calls, "the manifest write did not go through resume_check"
    assert calls[0].get("require_episode") is False, (
        "the manifest write asked for the episode-joined comparison, which finds "
        "nothing in exactly the state a timeout leaves"
    )


def test_an_inner_join_would_have_compared_nothing_here(db):
    """Why `require_episode=False` is the fix and not a detail.

    With the default join a manifest without an episode is not returned at all,
    so every field agrees with nothing and the check reports agreement. An empty
    comparison is not an agreement, and the count says which one happened.
    """
    run_id = _manifest_only(db)
    expected = {run_id: {"model_tag": "something-entirely-different"}}
    joined = resume_check(db, expected)
    assert joined.passed and joined.karsilastirilan == 0
    left = resume_check(db, expected, require_episode=False)
    assert not left.passed and left.karsilastirilan == 1


def test_a_prefix_pattern_without_its_boundary_catches_a_sibling(db):
    """`b32%` matches `b32c-...`, and both prefixes live in the real record.

    27 episodes under `b32` and 31 under `b32c`, one file. The pattern without a
    separator returns 58 of them.
    """
    _yazili(db, run_id="b32-g1-g1-32b")
    _yazili(db, run_id="b32c-g2-g2-32b")

    def count(pattern):
        return db.execute(
            "SELECT COUNT(*) FROM episodes WHERE run_id LIKE ?", (pattern,)
        ).fetchone()[0]

    assert count("b32%") == 2, "without the separator the sibling is counted"
    assert count("b32-%") == 1, "with it, only the run itself"
    assert count("b32c-%") == 1


def test_the_accumulation_runner_builds_no_pattern_without_that_boundary():
    """And the runner's own patterns, because the test above only shows SQL.

    The counts these patterns produce are the ledger's `episodes_this_run` and
    `distinct_tasks_passed`, and the stopping decision is read off the ledger.
    A demonstration that a pattern *can* be wrong pins nothing; this reads the
    file that builds them.
    """
    source = (Path(__file__).resolve().parents[1] / "scripts/setup/run_accumulation.py").read_text(
        encoding="utf-8"
    )
    # `PREFLIGHT_PREFIX` is excluded by the lookbehind, and deliberately: it is a
    # family name that already ends in a distinctive word and its ids are
    # numbered (`bir1-onkontrol1-...`), so `bir1-onkontrol-%` would match none of
    # them. The rule is about patterns built from the run's own prefix, where
    # `b32%` catches `b32c-...`.
    patterns = re.findall(r'(?<![A-Z_])PREFIX \+ "([^"]*)"', source)
    assert patterns, "no prefix pattern was found at all; this test stopped reading the file"
    unbounded = [p for p in patterns if not p.startswith("-")]
    assert not unbounded, (
        f"prefix pattern(s) with no separator: {unbounded}. `b32%` matches `b32c-...`."
    )


def _accumulation():
    """`run_accumulation.py` as a module, with a prefix on the command line."""
    path = Path(__file__).resolve().parents[1] / "scripts/setup/run_accumulation.py"
    spec = importlib.util.spec_from_file_location("run_accumulation", path)
    module = importlib.util.module_from_spec(spec)
    previous, sys.argv = sys.argv, ["run_accumulation.py", "bir1"]
    try:
        spec.loader.exec_module(module)
    finally:
        sys.argv = previous
    return module


def test_the_preflight_writes_under_an_id_of_its_own():
    """It is a health check at a ceiling of three, not one of the run's episodes.

    `measure_band.py` gives its preflight `f"{PREFIX}-onkontrol"`; this runner
    was written from that one and dropped the argument, so the health check
    wrote under the id a swept task would use. The restart then collided on
    `run_manifests.run_id` (K-155).
    """
    runner = _accumulation()
    preflight_id = "-".join(
        [runner.PREFLIGHT_PREFIX + "1", runner.PREFLIGHT_TASK, runner.PREFLIGHT_TASK, runner.SHORT]
    )
    assert preflight_id != runner.run_identity(runner.PREFLIGHT_TASK, 0)
    assert runner.PREFLIGHT_PREFIX.startswith(runner.PREFIX + "-")


def test_the_runs_episode_count_excludes_the_preflight():
    """Counted in, it adds one to the run's total on every start.

    The total is what branch B is read against, so a run restarted eight times
    would reach the ceiling eight episodes early.
    """
    source = (Path(__file__).resolve().parents[1] / "scripts/setup/run_accumulation.py").read_text(
        encoding="utf-8"
    )
    # The SQL is split across lines, so the parameters are what is counted: every
    # place the run's pattern is passed, the preflight's exclusion is passed too.
    # Pairing, not counting: `PREFLIGHT_PREFIX` is also used on its own, to number
    # the next health check. What must hold is that wherever the run's pattern is
    # passed, the exclusion is passed beside it.
    run_pattern = re.findall(r'(?<![A-Z_])PREFIX \+ "-%"', source)
    # Whatever follows the pair (the swept task set does, since K-160) is not the
    # pin's business: what must hold is that the exclusion sits right beside the
    # run's pattern.
    paired = re.findall(r'\(\s*PREFIX \+ "-%",\s*PREFLIGHT_PREFIX \+ "%"', source)
    assert run_pattern, "no run pattern was found; this test stopped reading the file"
    assert len(run_pattern) == len(paired), (
        f"{len(run_pattern)} place(s) pass the run's pattern and {len(paired)} of them pass "
        "the preflight's exclusion beside it; the rest count the health check as an episode"
    )
