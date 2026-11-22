"""Does an empty slot produce a byte-identical prompt?

Stage 5's acceptance criterion has two layers. The first is at prompt level: the
text rendered with an empty slot must be identical to the unmodified reference.
The second is at behaviour level and lives in `test_slot_trajectory.py`; that one
needs a model.

The first layer runs in CI, because it is only a file comparison.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from zihin.scaffold import (
    REFERENCE_PROMPT,
    SLOT_MARKER,
    SLOTTED_PROMPT,
    ScaffoldError,
    load_scaffold_config,
    reference_prompt,
    render_prompt,
    write_rendered_prompt,
)

CONFIG = "config/scaffold.yaml"


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_repo_carries_its_own_copy_of_the_prompt() -> None:
    """K-23: the file inside site-packages is untouched, the copy is in the repository."""
    assert Path(SLOTTED_PROMPT).exists()
    assert Path(REFERENCE_PROMPT).exists()


def test_empty_slot_renders_byte_identical_prompt() -> None:
    """K-25. The first layer of the acceptance criterion."""
    uretilen = render_prompt("")
    reference = reference_prompt()
    assert _digest(uretilen) == _digest(reference), (
        "the empty-slot prompt diverges from the reference. "
        f"produced {len(uretilen)} bytes, reference {len(reference)} bytes"
    )
    assert uretilen == reference


def test_marker_is_absent_from_the_rendered_prompt() -> None:
    """If the marker leaks into the prompt the model sees it as text."""
    assert SLOT_MARKER not in render_prompt("")
    assert SLOT_MARKER not in render_prompt("card text\n")


def test_slot_is_the_only_difference_from_the_reference() -> None:
    """The marker must be the only difference between the template and the reference."""
    template = Path(SLOTTED_PROMPT).read_text(encoding="utf-8")
    assert template.replace(SLOT_MARKER, "") == reference_prompt()


def test_slot_sits_before_the_task_block() -> None:
    """K-24: after the instructions, before the task statement."""
    template = Path(SLOTTED_PROMPT).read_text(encoding="utf-8")
    isaret = template.index(SLOT_MARKER)
    task_block = template.index("USER:\nUsing these APIs, now generate code")
    assert isaret < task_block
    assert template[isaret + len(SLOT_MARKER) :].startswith("USER:")


def test_card_block_lands_in_the_slot() -> None:
    card = "### Skill cards\n- sample\n\n"
    uretilen = render_prompt(card)
    assert card in uretilen
    assert uretilen.index(card) < uretilen.index("USER:\nUsing these APIs")
    assert len(uretilen) == len(reference_prompt()) + len(card)


def test_template_with_two_markers_is_rejected(tmp_path) -> None:
    bozuk = tmp_path / "instructions.txt"
    bozuk.write_text(f"a{SLOT_MARKER}b{SLOT_MARKER}c", encoding="utf-8")
    with pytest.raises(ScaffoldError, match="exactly once"):
        render_prompt("", bozuk)


def test_template_without_marker_is_rejected(tmp_path) -> None:
    bozuk = tmp_path / "instructions.txt"
    bozuk.write_text("text without a marker", encoding="utf-8")
    with pytest.raises(ScaffoldError, match="exactly once"):
        render_prompt("", bozuk)


def test_written_prompt_matches_rendered_text(tmp_path) -> None:
    path = write_rendered_prompt(tmp_path / "alt" / "instructions.txt", "")
    assert path.read_text(encoding="utf-8") == reference_prompt()


def test_episode_prompt_paths_do_not_collide() -> None:
    """Concurrent episodes must not overwrite one another's prompt file.

    The overwrite would be silent: both episodes would read a valid prompt and
    carry on, and the difference would show only in the results.
    """
    from zihin.scaffold import episode_prompt_path

    paths = {
        episode_prompt_path("run-1", "82e2fac_1", 0),
        episode_prompt_path("run-1", "82e2fac_1", 1),
        episode_prompt_path("run-1", "82e2fac_2", 0),
        episode_prompt_path("run-2", "82e2fac_1", 0),
    }
    assert len(paths) == 4


def test_scaffold_config_loads() -> None:
    config = load_scaffold_config(CONFIG)
    assert config.slot_position == "before_user_task"
    assert config.empty_slot_renders_nothing is True


def test_unknown_slot_position_is_rejected(tmp_path) -> None:
    path = tmp_path / "scaffold.yaml"
    path.write_text("slot_position: ortaya\nempty_slot_renders_nothing: true\n", encoding="utf-8")
    with pytest.raises(ScaffoldError, match="is invalid"):
        load_scaffold_config(path)


def test_disabling_the_empty_slot_rule_is_rejected(tmp_path) -> None:
    """If the rule could be switched off, the criterion could break in silence."""
    path = tmp_path / "scaffold.yaml"
    path.write_text(
        "slot_position: before_user_task\nempty_slot_renders_nothing: false\n",
        encoding="utf-8",
    )
    with pytest.raises(ScaffoldError, match="can only be true"):
        load_scaffold_config(path)
