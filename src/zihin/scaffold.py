"""Adds a card slot to the reference scaffold's prompt.

The scaffold itself is untouched. Its logic, parser and loop stay the same.
The only change is in the prompt file, and that is in our own copy (K-23).

Substitution happens here, before the scaffold reads the file, so Jinja never
sees the marker. Using a Jinja variable would have meant relying on an
undefined variable rendering silently as empty — a dependency that can break
without a sound.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

SLOT_MARKER = "<<<ZIHIN_CARD_SLOT>>>"

PROMPT_DIR = Path("prompts/react_code_agent")
SLOTTED_PROMPT = PROMPT_DIR / "instructions.txt"
REFERENCE_PROMPT = PROMPT_DIR / "instructions.reference.txt"

VALID_SLOT_POSITIONS = ("before_user_task",)


class ScaffoldError(RuntimeError):
    """A scaffold-layer rule was violated."""


@dataclass(frozen=True)
class ScaffoldConfig:
    """Contents of `config/scaffold.yaml`."""

    slot_position: str
    empty_slot_renders_nothing: bool


def load_scaffold_config(path: str | Path) -> ScaffoldConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    expected = {"slot_position", "empty_slot_renders_nothing"}
    missing = expected - set(raw)
    unknown = set(raw) - expected
    if missing:
        raise ScaffoldError(f"missing field in scaffold config: {sorted(missing)}")
    if unknown:
        raise ScaffoldError(f"unrecognised field in scaffold config: {sorted(unknown)}")
    if raw["slot_position"] not in VALID_SLOT_POSITIONS:
        raise ScaffoldError(
            f"slot_position {raw['slot_position']!r} is invalid; "
            f"allowed: {list(VALID_SLOT_POSITIONS)}"
        )
    if raw["empty_slot_renders_nothing"] is not True:
        raise ScaffoldError(
            "empty_slot_renders_nothing can only be true. An empty slot must "
            "produce a byte-for-byte identical prompt (K-25)."
        )
    return ScaffoldConfig(**raw)


def render_prompt(card_block: str = "", template_path: str | Path = SLOTTED_PROMPT) -> str:
    """Places the card block into the slotted template.

    Given an empty block, the marker is removed without leaving a trace. A
    non-empty card block must carry its own trailing newline; none is added
    here, because adding one would make the empty and non-empty forms differ by
    more than the cards themselves.
    """
    text = Path(template_path).read_text(encoding="utf-8")
    if text.count(SLOT_MARKER) != 1:
        raise ScaffoldError(
            f"slot marker occurs {text.count(SLOT_MARKER)} times in the template, "
            "it must occur exactly once"
        )
    return text.replace(SLOT_MARKER, card_block)


def write_rendered_prompt(
    destination: str | Path,
    card_block: str = "",
    template_path: str | Path = SLOTTED_PROMPT,
) -> Path:
    """Writes the substituted prompt to disk and returns its path.

    The scaffold reads the file itself through `prompt_file_path`, so
    substitution is done at file level.
    """
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_prompt(card_block, template_path), encoding="utf-8", newline="\n")
    return path


def reference_prompt(path: str | Path = REFERENCE_PROMPT) -> str:
    """The unmodified reference prompt. Anchor for the byte comparison."""
    return Path(path).read_text(encoding="utf-8")


def episode_prompt_path(
    run_id: str, task_id: str, seed_index: int, root: str | Path = "results/prompts"
) -> Path:
    """Episode-specific prompt path.

    The prompt file is regenerated per episode, because the slot content will
    vary by episode. The path has to be episode-specific too: small models will
    run episodes concurrently, and a fixed path would mean two episodes
    overwriting each other's file. The overwrite would be silent, because both
    would read a valid prompt and carry on.
    """
    name = f"{run_id}__{task_id}__seed{seed_index}.txt"
    return Path(root) / name
