"""The shield's specification module, which had no tests at all.

`allowed_apps.py` decides which apps a task may be written to, so every shield
decision passes through it. It was written, measured and mounted without a
single test; this handle closes that.

The load-bearing case is the infrastructure rule. Three endpoints —
`amazon.add_payment_card`, `spotify.add_payment_card`, `venmo.add_payment_card`
— write into `admin` through the payment-card helpers, and `admin` is an app no
task instruction will ever name. If infrastructure apps were not unconditionally
allowed, every task that touches a payment card would be blocked. That claim was
made in a report before it was nailed anywhere, which is exactly the kind of
claim that has to become a test.

The tests use hand-written instructions rather than `data/tasks`, so they run
without the benchmark data on disk.
"""

from __future__ import annotations

import json

import pytest

from zihin.allowed_apps import (
    APP_SURFACE_FORMS,
    INFRASTRUCTURE_APPS,
    infer_allowed_apps,
    reference_apps,
)
from zihin.shield import Call, evaluate

# --- the infrastructure rule ---


def test_infrastructure_apps_are_allowed_no_matter_what_the_task_says():
    """The rule, stated directly.

    Mutation this kills: returning `named` instead of `named | INFRASTRUCTURE`.
    Nothing else in the suite would notice, because every other assertion here
    is about apps a task actually names.
    """
    assert INFRASTRUCTURE_APPS <= infer_allowed_apps("Play my most-liked song.")


def test_an_empty_instruction_still_allows_the_infrastructure_apps():
    """The extreme case: no app is named at all.

    `supervisor` carries the task's own credentials and address book, so an
    agent that cannot reach it cannot start any task. A shield that blocked it
    would stop every task rather than the dangerous ones.
    """
    assert infer_allowed_apps("") == INFRASTRUCTURE_APPS


def test_the_infrastructure_set_is_exactly_these_three():
    """Pinned. Widening it silently widens what the shield permits.

    `file_system` is deliberately not here: a download that writes into it is
    the case the shield exists to catch (K-41, nine `download_*` endpoints).
    """
    assert INFRASTRUCTURE_APPS == frozenset({"admin", "api_docs", "supervisor"})
    assert "file_system" not in INFRASTRUCTURE_APPS


def test_a_payment_card_write_into_admin_is_not_blocked():
    """The concrete consequence, checked through the predicate itself.

    `amazon.add_payment_card` writes into `admin` as well as `amazon`, because
    the card helpers call `admin.show_card_balance` and `admin.validate_card`
    (S-38, the known over-inclusion). Without the infrastructure rule this would
    be a cross-app write outside the allowed set on every card task.

    A hand-written write set: the derived one is measured input, and a test that
    read it would fail whenever the derivation moved.
    """
    allowed = infer_allowed_apps("Add my payment card to Amazon.")
    write_set = {("amazon", "payment_cards", "POST"): ("admin", "amazon")}
    decision = evaluate(Call("amazon", "payment_cards", "POST"), allowed, write_set)
    assert decision.allowed
    assert decision.predicate == "write_within_allowed_apps"
    assert decision.outside == ()


def test_the_same_write_is_blocked_when_the_target_is_not_infrastructure():
    """The counterweight: the rule permits `admin`, not everything.

    Mutation: allowing every unnamed app instead of the three. Then the shield
    permits nothing at all in the wrong direction and the test above would still
    pass.
    """
    allowed = infer_allowed_apps("Add my payment card to Amazon.")
    write_set = {("amazon", "downloads", "POST"): ("file_system",)}
    decision = evaluate(Call("amazon", "downloads", "POST"), allowed, write_set)
    assert not decision.allowed
    assert decision.outside == ("file_system",)


# --- surface forms ---


def test_an_app_named_in_the_instruction_is_allowed():
    allowed = infer_allowed_apps("Send $20 to Nancy on Venmo.")
    assert "venmo" in allowed
    assert "spotify" not in allowed


@pytest.mark.parametrize(
    ("instruction", "expected"),
    [
        ("Add a simple note about it.", "simple_note"),
        ("Add a simple_note about it.", "simple_note"),
        ("Put it in my SimpleNote.", "simple_note"),
        ("Save it to the file system.", "file_system"),
        ("Save it to the downloads folder.", "file_system"),
    ],
)
def test_the_space_underscore_split_does_not_hide_an_app(instruction, expected):
    """`simple note`, `simple_note` and `simplenote` are one app.

    The instruction texts use all three, so a matcher that only knew the
    underscore form would miss the app and the shield would block a legitimate
    write.
    """
    assert expected in infer_allowed_apps(instruction)


def test_matching_is_case_insensitive():
    assert "venmo" in infer_allowed_apps("VENMO")
    assert "venmo" in infer_allowed_apps("Venmo")


def test_a_word_boundary_is_required():
    """`note` must not match inside `notebook`, `noteworthy`, `denote`.

    Mutation: dropping `\\b` from the pattern. That widens the allowed set
    silently, and a widened set is the failure direction that lets a real write
    through.
    """
    assert "simple_note" not in infer_allowed_apps("Open my notebook.")
    assert "simple_note" not in infer_allowed_apps("It was noteworthy.")
    assert "simple_note" in infer_allowed_apps("Write a note.")


def test_the_surface_form_table_covers_the_nine_non_infrastructure_apps():
    """Pinned at nine, and the table is frozen.

    The forms were written from the instruction texts **before** the accuracy
    was measured and were not touched afterwards (K-70). Editing them to chase
    the 75.5% would be fitting the proxy to its own validator and would make the
    figure meaningless. The pin is here so that editing them fails loudly.
    """
    assert set(APP_SURFACE_FORMS) == {
        "amazon",
        "file_system",
        "gmail",
        "phone",
        "simple_note",
        "splitwise",
        "spotify",
        "todoist",
        "venmo",
    }
    assert not set(APP_SURFACE_FORMS) & INFRASTRUCTURE_APPS


# --- the reference, which is the validator and not the input ---


def test_a_missing_reference_is_none_and_not_an_empty_set(tmp_path):
    """ "No reference" and "an empty reference" are different facts.

    `test_normal` carries no `required_apps.json` (S-03). A caller that
    mistook None for `frozenset()` would score every task in that split as
    "the reference required nothing", and every inferred app would look like an
    over-inclusion.
    """
    assert reference_apps("task-absent", root=tmp_path) is None

    task = tmp_path / "task-present" / "ground_truth"
    task.mkdir(parents=True)
    (task / "required_apps.json").write_text("[]", encoding="utf-8")
    assert reference_apps("task-present", root=tmp_path) == frozenset()


def test_the_reference_is_read_as_a_set_of_app_names(tmp_path):
    task = tmp_path / "g" / "ground_truth"
    task.mkdir(parents=True)
    (task / "required_apps.json").write_text(json.dumps(["venmo", "phone"]), encoding="utf-8")
    assert reference_apps("g", root=tmp_path) == frozenset({"venmo", "phone"})
