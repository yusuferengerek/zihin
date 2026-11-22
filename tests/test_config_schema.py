"""Verifies that the six condition configurations carry the same schema.

One of stage 0's acceptance criteria: "every config file will carry the same
schema, only the field values will differ." The tests here make that sentence
checkable — is the key structure identical, do the values come from defined
enums, and is a malformed file really refused.
"""

from __future__ import annotations

from dataclasses import fields
from pathlib import Path

import pytest
import yaml

from zihin.config import (
    ConditionConfig,
    ConfigError,
    FailureSource,
    RetrievalMode,
    SkillSource,
    load_condition_config,
    parse_condition_config,
)

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"

EXPECTED_CONDITIONS = [
    "baseline",
    "failures",
    "irrelevant_retrieval",
    "naive_compiler",
    "skills",
    "skills_failures",
]

# The non-condition files under `config/`. The list is written out explicitly so
# that a new file is neither counted as a condition in silence nor ignored in
# silence. `sandbox` joined this list in item 8: the resource limits and the image
# digest are not a condition variable, they are the same under every condition.
# `analysis` joined it with the pre-registered analysis script: the bootstrap seed
# and iteration count are the same under every condition too, and they are here
# rather than in the script because a value that changes a reported number has no
# silent default (S-30).
NON_CONDITION_CONFIGS = ["analysis", "models", "recording", "sandbox", "scaffold"]


def _key_shape(data: object) -> object:
    """Drops the values and returns only the key tree."""
    if isinstance(data, dict):
        return {key: _key_shape(value) for key, value in sorted(data.items())}
    return None


def _valid_payload() -> dict[str, object]:
    """A minimal body that fits the schema. The tests probe by breaking it."""
    return {
        "condition": "trial",
        "skills": {"source": "none"},
        "failures": {"source": "none"},
        "retrieval": {"mode": "none", "min_expected_saving": 1},
        "shield": {"enabled": True},
        "fill": {"enabled": False},
        "cards": {"skill_slots": 0, "failure_slots": 0},
    }


def test_exactly_six_condition_files_exist() -> None:
    found = sorted(
        path.stem for path in CONFIG_DIR.glob("*.yaml") if path.stem not in NON_CONDITION_CONFIGS
    )
    assert found == EXPECTED_CONDITIONS


def test_config_directory_carries_no_unaccounted_file() -> None:
    """A new yaml is either a condition or on the list; there is no third state."""
    found = sorted(path.stem for path in CONFIG_DIR.glob("*.yaml"))
    assert found == sorted(EXPECTED_CONDITIONS + NON_CONDITION_CONFIGS)


@pytest.mark.parametrize("condition", EXPECTED_CONDITIONS)
def test_each_config_loads(condition: str) -> None:
    config = load_condition_config(CONFIG_DIR / f"{condition}.yaml")
    assert config.condition == condition


def test_all_six_share_one_key_shape() -> None:
    shapes = {}
    for condition in EXPECTED_CONDITIONS:
        raw = yaml.safe_load((CONFIG_DIR / f"{condition}.yaml").read_text(encoding="utf-8"))
        shapes[condition] = _key_shape(raw)

    reference = shapes[EXPECTED_CONDITIONS[0]]
    for condition, shape in shapes.items():
        assert shape == reference, f"{condition}.yaml has left the schema"


def test_shield_is_enabled_in_all_six() -> None:
    """The shield is on without exception — a design decision, not something to
    be switched off by accident."""
    for condition in EXPECTED_CONDITIONS:
        config = load_condition_config(CONFIG_DIR / f"{condition}.yaml")
        assert config.shield_enabled is True, f"{condition}: the shield is off"


def test_baseline_carries_no_cards() -> None:
    config = load_condition_config(CONFIG_DIR / "baseline.yaml")
    assert config.skills_source is SkillSource.NONE
    assert config.failures_source is FailureSource.NONE
    assert config.retrieval_mode is RetrievalMode.NONE
    assert config.fill_enabled is False
    assert config.skill_slots == 0
    assert config.failure_slots == 0


def test_non_baseline_conditions_carry_equal_slots() -> None:
    """The volume control is only meaningful if the slot counts are equal."""
    for condition in EXPECTED_CONDITIONS:
        if condition == "baseline":
            continue
        config = load_condition_config(CONFIG_DIR / f"{condition}.yaml")
        assert config.skill_slots == 5, condition
        assert config.failure_slots == 5, condition
        assert config.fill_enabled is True, condition


def test_retrieval_mode_is_none_only_in_baseline() -> None:
    """`retrieval.mode` carries the retrieval method: off in the baseline,
    symbolic in the other five."""
    for condition in EXPECTED_CONDITIONS:
        config = load_condition_config(CONFIG_DIR / f"{condition}.yaml")
        expected = RetrievalMode.NONE if condition == "baseline" else RetrievalMode.SYMBOLIC
        assert config.retrieval_mode is expected, condition


def test_pure_content_contrast_differs_in_one_field_only() -> None:
    """`skills` and `irrelevant_retrieval` must differ in the skill source alone.

    This is the analysis plan's "pure content" contrast. If a second field differs
    too, the difference is no longer pure content and the contrast loses its
    meaning in silence.
    """
    skills = load_condition_config(CONFIG_DIR / "skills.yaml")
    irrelevant = load_condition_config(CONFIG_DIR / "irrelevant_retrieval.yaml")

    differing = [
        field.name
        for field in fields(ConditionConfig)
        if field.name != "condition"
        and getattr(skills, field.name) != getattr(irrelevant, field.name)
    ]
    assert differing == ["skills_source"], f"unexpected divergence: {differing}"


def test_pure_volume_contrast_carries_no_relevant_content() -> None:
    """The difference between `baseline` and `irrelevant_retrieval` is pure context volume.

    Neither may carry relevant content; if one starts carrying a real card the
    difference stops being volume.
    """
    relevant = {SkillSource.STANDARD, SkillSource.NAIVE, FailureSource.STANDARD}
    for condition in ("baseline", "irrelevant_retrieval"):
        config = load_condition_config(CONFIG_DIR / f"{condition}.yaml")
        assert config.skills_source not in relevant, condition
        assert config.failures_source not in relevant, condition


def test_missing_field_is_rejected() -> None:
    payload = _valid_payload()
    del payload["cards"]
    with pytest.raises(ConfigError, match="missing field"):
        parse_condition_config(payload, "trial.yaml")


def test_unknown_field_is_rejected() -> None:
    payload = _valid_payload()
    payload["compiler"] = {"mode": "naive"}
    with pytest.raises(ConfigError, match="unrecognised field"):
        parse_condition_config(payload, "trial.yaml")


def test_undefined_enum_value_is_rejected() -> None:
    payload = _valid_payload()
    payload["skills"] = {"source": "uydurma"}
    with pytest.raises(ConfigError, match="is invalid"):
        parse_condition_config(payload, "trial.yaml")


def test_slot_count_rejects_boolean() -> None:
    """In Python bool is a subtype of int; it must not pass in silence."""
    payload = _valid_payload()
    payload["cards"] = {"skill_slots": True, "failure_slots": 0}
    with pytest.raises(ConfigError, match="non-negative integer"):
        parse_condition_config(payload, "trial.yaml")


def test_every_condition_declares_the_same_saving_floor() -> None:
    """Declared once for the experiment (K-175): a floor that differed between two
    conditions would make their contrast carry a second field."""
    floors = {
        condition: load_condition_config(CONFIG_DIR / f"{condition}.yaml").min_expected_saving
        for condition in EXPECTED_CONDITIONS
    }
    assert set(floors.values()) == {1}, floors


def test_the_runner_reads_the_floor_from_the_configuration() -> None:
    """The selection lives in `zihin.slots` since K-181 and the runner calls it, so
    the floor is read there and neither file may carry a number of its own."""
    import re

    selection = (CONFIG_DIR.parent / "src/zihin/slots.py").read_text(encoding="utf-8")
    runner = (CONFIG_DIR.parent / "scripts/record_run.py").read_text(encoding="utf-8")
    assert "config.min_expected_saving" in selection
    assert "compose(" in runner
    # Neither spelling of a literal: a keyword argument or a dictionary entry.
    for source in (selection, runner):
        assert not re.search(r"""min_expected_saving["']?\s*[=:]\s*\d""", source)
