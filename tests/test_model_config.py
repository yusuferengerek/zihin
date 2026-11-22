"""Checks the rules the model-serving configuration carries.

These tests do not connect to the server; they inspect the configuration itself,
so they run in CI. Whether the server really runs with those settings is checked
in a separate test (`test_model_serving.py`).
"""

from __future__ import annotations

import pytest
import yaml

from zihin.records import RecordError, load_model_config

PATH = "config/models.yaml"


def _valid() -> dict:
    with open(PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _write(tmp_path, body: dict):
    path = tmp_path / "models.yaml"
    path.write_text(yaml.safe_dump(body, allow_unicode=True), encoding="utf-8")
    return path


def test_the_scale_axis_carries_its_declared_points() -> None:
    """The axis is a pre-registered object, so its members are pinned here.

    Five points since 2026-08-21. The fourth was added by a decision with a
    dated addendum to the pre-registration, not by editing a configuration line
    (K-133), and this test is the mechanical half of that: a point that appears
    or disappears without the record moving fails here.
    """
    config = load_model_config(PATH)
    assert config.models == (
        "qwen2.5-coder:1.5b-instruct-q4_K_M",
        "qwen2.5-coder:3b-instruct-q4_K_M",
        "qwen2.5-coder:7b-instruct-q4_K_M",
        "qwen2.5-coder:14b-instruct-q4_K_M",
        "qwen2.5-coder:32b-instruct-q4_K_M",
    )


def test_the_axis_varies_size_and_nothing_else() -> None:
    """One family, one quantisation. The axis measures size, not size and family.

    Written when 14B extended the axis: the extension opened the local-hardware
    lock and deliberately left the family lock closed, and a lock that is only
    written down in prose is a lock nobody enforces.
    """
    for tag in load_model_config(PATH).models:
        family, _, version = tag.partition(":")
        assert family == "qwen2.5-coder"
        assert version.endswith("-instruct-q4_K_M")


def test_model_tags_carry_size_and_quantisation() -> None:
    """A shortened tag erases which weights ran from the manifest."""
    for tag in load_model_config(PATH).models:
        assert ":" in tag
        assert "-q" in tag


def test_scale_axis_stays_within_one_family() -> None:
    """If families were mixed, two variables would change along the axis at once."""
    aileler = {tag.split(":")[0] for tag in load_model_config(PATH).models}
    assert aileler == {"qwen2.5-coder"}


def test_context_window_is_the_designed_value() -> None:
    assert load_model_config(PATH).num_ctx == 32768


def test_temperature_is_low_but_not_zero() -> None:
    """At zero temperature the seed becomes meaningless and the spread across seeds dies."""
    temperature = load_model_config(PATH).temperature
    assert 0 < temperature < 1
    assert temperature == 0.2


def test_seed_is_deterministic_for_the_same_pair() -> None:
    config = load_model_config(PATH)
    bir = config.seed_for("82e2fac_1", 0)
    two = config.seed_for("82e2fac_1", 0)
    assert bir == two


def test_seed_changes_with_task_and_with_index() -> None:
    """If the seed does not change when one of the two components does, the seed axis dies."""
    y = load_model_config(PATH)
    base = y.seed_for("82e2fac_1", 0)
    assert y.seed_for("82e2fac_2", 0) != base
    assert y.seed_for("82e2fac_1", 1) != base


def test_seed_signature_takes_only_task_and_index() -> None:
    """The seed must carry neither model nor condition.

    In a paired design the seed is a blocking factor: the same task and the same
    seed index must give the same seed under every model and every condition.
    Otherwise the model difference and the seed difference interleave.

    This test pins the signature. If model or condition comes back as a third
    argument, it fails here.
    """
    import inspect

    parametreler = list(inspect.signature(load_model_config(PATH).seed_for).parameters)
    assert parametreler == ["task_id", "seed_index"], (
        f"seed_for signature is {parametreler}. The seed must derive from the task id and "
        "the seed index alone."
    )


def test_seed_index_is_bounded(tmp_path) -> None:
    y = load_model_config(PATH)
    with pytest.raises(RecordError, match="seed_index"):
        y.seed_for("82e2fac_1", y.seed_count)


def test_unknown_field_is_rejected(tmp_path) -> None:
    body = _valid()
    body["fazla"] = 1
    with pytest.raises(RecordError, match="unrecognised field"):
        load_model_config(_write(tmp_path, body))


def test_missing_field_is_rejected(tmp_path) -> None:
    body = _valid()
    del body["num_ctx"]
    with pytest.raises(RecordError, match="missing field"):
        load_model_config(_write(tmp_path, body))


def test_two_point_axis_is_rejected(tmp_path) -> None:
    body = _valid()
    body["models"] = body["models"][:2]
    with pytest.raises(RecordError, match="three points"):
        load_model_config(_write(tmp_path, body))


def test_shortened_model_tag_is_rejected(tmp_path) -> None:
    body = _valid()
    body["models"][0] = "qwen2.5-coder:1.5b"
    with pytest.raises(RecordError, match="must be complete"):
        load_model_config(_write(tmp_path, body))


def test_zero_temperature_is_rejected(tmp_path) -> None:
    body = _valid()
    body["temperature"] = 0
    with pytest.raises(RecordError, match="temperature"):
        load_model_config(_write(tmp_path, body))
