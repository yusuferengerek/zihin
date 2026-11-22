"""Reads condition configurations and verifies they match the schema.

All six files under `config/` carry the same schema; only the field values
differ. This module's single job is to make that claim machine-checkable: a
missing field, an extra field or an undefined enum value does not pass
silently, it raises `ConfigError`.

The mechanisms themselves are not here. This file only reads which mechanism
is enabled under which condition.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, StrEnum
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """The configuration does not match the schema."""


class SkillSource(StrEnum):
    """Where the skill library comes from.

    none        — no skill cards.
    standard    — the library produced by the normal compiler.
    naive       — the library produced by the naive miner; compiler-quality control.
    irrelevant  — cards exist but their content is unrelated to the task;
                  context-volume control.
    """

    NONE = "none"
    STANDARD = "standard"
    NAIVE = "naive"
    IRRELEVANT = "irrelevant"


class FailureSource(StrEnum):
    """Where the failure library comes from.

    There is no counterpart to the skill side's `naive`: the naive compiler
    only produces skills, there is no such thing as a naive failure index. An
    unused enum value is deliberately not added — a value that just sits there
    is a value somebody will try to use.
    """

    NONE = "none"
    STANDARD = "standard"
    IRRELEVANT = "irrelevant"


class RetrievalMode(StrEnum):
    """How retrieval is done. It does not carry content relevance; that is
    carried by `skills.source` and `failures.source`.

    none      — no retrieval; baseline only.
    symbolic  — symbolic retrieval.

    If hybrid retrieval is tried, a third value goes here.
    """

    NONE = "none"
    SYMBOLIC = "symbolic"


@dataclass(frozen=True)
class ConditionConfig:
    """Configuration of a single experimental condition."""

    condition: str
    skills_source: SkillSource
    failures_source: FailureSource
    retrieval_mode: RetrievalMode
    # The smallest expected saving, in model calls, a skill card must carry to
    # reach the slot. Declared 1 on 25 September 2026 (K-175): the primary metric
    # is the model call, and a card that saves none cannot move it.
    min_expected_saving: int
    shield_enabled: bool
    fill_enabled: bool
    skill_slots: int
    failure_slots: int


# Schema: top-level key -> the fields under that key.
# All six files have to match this exactly.
_SCHEMA: dict[str, tuple[str, ...]] = {
    "condition": (),
    "skills": ("source",),
    "failures": ("source",),
    "retrieval": ("mode", "min_expected_saving"),
    "shield": ("enabled",),
    "fill": ("enabled",),
    "cards": ("skill_slots", "failure_slots"),
}


def _check_keys(actual: Any, expected: tuple[str, ...], where: str) -> None:
    if not isinstance(actual, dict):
        raise ConfigError(f"{where}: expected a mapping, got {type(actual).__name__}")
    missing = set(expected) - set(actual)
    extra = set(actual) - set(expected)
    if missing:
        raise ConfigError(f"{where}: missing field(s): {sorted(missing)}")
    if extra:
        raise ConfigError(f"{where}: unrecognised field(s): {sorted(extra)}")


def _as_bool(value: Any, where: str) -> bool:
    if not isinstance(value, bool):
        raise ConfigError(f"{where}: expected a boolean, got {value!r}")
    return value


def _as_slot_count(value: Any, where: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ConfigError(f"{where}: expected a non-negative integer, got {value!r}")
    return value


def _as_enum(enum_cls: type[Enum], value: Any, where: str) -> Any:
    try:
        return enum_cls(value)
    except ValueError:
        allowed = [member.value for member in enum_cls]
        raise ConfigError(f"{where}: {value!r} is invalid; allowed: {allowed}") from None


def parse_condition_config(raw: Any, source: str) -> ConditionConfig:
    """Validates a parsed YAML body and produces a `ConditionConfig`."""
    _check_keys(raw, tuple(_SCHEMA), source)

    for key, fields in _SCHEMA.items():
        if fields:
            _check_keys(raw[key], fields, f"{source}:{key}")

    condition = raw["condition"]
    if not isinstance(condition, str) or not condition:
        raise ConfigError(f"{source}:condition: expected non-empty text, got {condition!r}")

    return ConditionConfig(
        condition=condition,
        skills_source=_as_enum(SkillSource, raw["skills"]["source"], f"{source}:skills.source"),
        failures_source=_as_enum(
            FailureSource, raw["failures"]["source"], f"{source}:failures.source"
        ),
        retrieval_mode=_as_enum(
            RetrievalMode, raw["retrieval"]["mode"], f"{source}:retrieval.mode"
        ),
        min_expected_saving=_as_slot_count(
            raw["retrieval"]["min_expected_saving"], f"{source}:retrieval.min_expected_saving"
        ),
        shield_enabled=_as_bool(raw["shield"]["enabled"], f"{source}:shield.enabled"),
        fill_enabled=_as_bool(raw["fill"]["enabled"], f"{source}:fill.enabled"),
        skill_slots=_as_slot_count(raw["cards"]["skill_slots"], f"{source}:cards.skill_slots"),
        failure_slots=_as_slot_count(
            raw["cards"]["failure_slots"], f"{source}:cards.failure_slots"
        ),
    )


def load_condition_config(path: str | Path) -> ConditionConfig:
    """Reads and validates a condition configuration file."""
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return parse_condition_config(raw, path.name)
