"""Pins the branch a Colab session clones, in one place.

The notebook defaulted to a feature branch. That branch merged, `main` moved on,
and the notebook kept cloning the old tip — so a clean Colab checkout came up
without files that were in `main`. The failure named itself wrongly: a
`FileNotFoundError` reads as "the file was never written", not "this copy is
stale".

What is pinned: the notebook's `ZIHIN_REF` default is the branch, the Colab
README names the same one, and neither drifts from the other.
"""

from __future__ import annotations

import json
import pathlib
import re

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
NOTEBOOK = REPOSITORY / "experiments/colab/zihin-colab.ipynb"
README = REPOSITORY / "experiments/colab/README.md"

DEFAULT = re.compile(r'os\.environ\.get\(\s*"ZIHIN_REF"\s*,\s*"([^"]+)"\s*\)')
# The branch name stops at the next slash: a greedy class would swallow the
# path that follows it and compare a path against a branch.
IN_LINK = re.compile(r"colab\.research\.google\.com/github/[\w-]+/[\w-]+/blob/([\w.-]+)/")
IN_PROSE = re.compile(r"dal: `([\w./-]+)`")


def notebook_ref() -> str:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    for cell in notebook["cells"]:
        found = DEFAULT.search("".join(cell.get("source", [])))
        if found:
            return found.group(1)
    raise AssertionError("the notebook has no ZIHIN_REF default; the parser no longer reads it")


def test_the_notebook_declares_a_branch() -> None:
    assert notebook_ref()


def test_the_branch_is_the_one_that_carries_merged_work() -> None:
    """A feature branch is a moment; `main` is where merged work lands."""
    assert notebook_ref() == "main"


def test_the_readme_names_the_same_branch() -> None:
    text = README.read_text(encoding="utf-8")
    named = IN_LINK.findall(text) + IN_PROSE.findall(text)
    assert len(named) >= 2, (
        f"only {len(named)} branch mention(s) were found in the Colab README; the "
        "document's shape changed and this test no longer reads it"
    )
    assert set(named) == {notebook_ref()}, (
        f"the README names {sorted(set(named))} and the notebook clones {notebook_ref()!r}"
    )


def test_no_stale_feature_branch_is_named_anywhere_in_the_colab_material() -> None:
    """The specific branch that caused this, by name, so it cannot come back."""
    for path in (NOTEBOOK, README):
        assert "protokol-cevirisi" not in path.read_text(encoding="utf-8"), (
            f"{path.name} names the branch that merged and went stale"
        )


def test_the_notebook_run_command_names_a_declared_prefix() -> None:
    """The caller is pinned, not only the capability.

    `check_prerequisites.py` learned to narrow its requirements by run prefix and
    the notebook was never taught to name one, so the capability sat unused and
    the preflight kept asking for a library the run does not read. The lookup used
    to search for one runner by name, so the day the notebook moved to another
    runner it silently found nothing (K-153).
    """
    from zihin.declared import declared_prefixes, run_command, run_prefix

    command = run_command()
    assert command, (
        "no shell line in the notebook names a prefix the protocol declares; "
        "the run cell and the protocol have drifted apart"
    )
    prefix = run_prefix()
    assert prefix in declared_prefixes(), (
        f"the notebook runs {prefix!r}, which the protocol declares no conditions section for"
    )


def test_the_notebook_runs_the_runner_its_conditions_section_declares() -> None:
    """The command in the cell and the command in the table are one command."""
    from zihin.declared import conditions, run_command, run_prefix

    prefix = run_prefix()
    _, table = conditions(prefix)
    declared = (table.get("komut") or table.get("command") or "").strip().strip("`*")
    if not declared:
        return  # a notebook-driven run may keep its command only in the cell
    assert " ".join(run_command()) == declared, (
        f"the notebook runs {' '.join(run_command())!r} but section for {prefix} "
        f"declares {declared!r}"
    )
