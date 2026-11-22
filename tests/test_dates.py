"""Pins the shape of the date sweep over dated addenda.

The sweep's failure mode is silence: markers that stop matching examine nothing
and report that every date holds. That is the class K-103 recorded, and the
remedy is the same one — pin the shape, and prove the floor fires.

The second thing pinned here is the escape hatch. A corrected date can never
match its own commit, so the sweep accepts a mismatch when a correction note
names a commit dated as claimed. If that hatch widened to "a note is enough",
any wrong date could be silenced by writing the words next to it.
"""

from __future__ import annotations

import datetime
import importlib.util
import pathlib
import sys

import pytest

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]


def _module():
    path = REPOSITORY / "scripts/check_dates.py"
    spec = importlib.util.spec_from_file_location("check_dates", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_dates"] = module
    spec.loader.exec_module(module)
    return module


def test_a_turkish_addendum_dates_itself() -> None:
    module = _module()
    line = "### Ek — 25 Ağustos 2026: eksene beşinci nokta"
    assert module.SELF_DATING.match(line)
    assert module.parse(line) == datetime.date(2026, 8, 25)


def test_an_english_addendum_dates_itself_in_both_notations() -> None:
    module = _module()
    iso = "**Addendum, 2026-08-26 — a retroactive ceiling audit.** The rate"
    named = "**Closed, 18 August 2026.** The criterion was applied."
    assert module.SELF_DATING.match(iso) and module.parse(iso) == datetime.date(2026, 8, 26)
    assert module.SELF_DATING.match(named) and module.parse(named) == datetime.date(2026, 8, 18)


def test_an_event_date_is_not_a_self_dating_line() -> None:
    """ "The gate fired on 11 August" is written down later, by design."""
    module = _module()
    line = "**Bu kapı bir kez ateşledi: 11 Ağustos 2026.** Qwen2.5-Coder 1,5B"
    assert not module.SELF_DATING.match(line)


def test_a_correction_note_without_a_commit_rescues_nothing() -> None:
    module = _module()
    lines = [
        "### Ek — 25 Ağustos 2026: eksene beşinci nokta",
        "",
        "**Tarih düzeltmesi, 26 Ağustos 2026.** Bu ek önce başka türlü tarihlendi.",
    ]
    assert module.corrected_by(lines, 0, datetime.date(2026, 8, 25)) is None


def test_a_correction_note_naming_a_commit_of_another_date_rescues_nothing() -> None:
    """The named commit has to carry the claimed date; naming any commit is not enough."""
    module = _module()
    lines = [
        "### Ek — 25 Ağustos 2026: eksene beşinci nokta",
        "",
        "**Tarih düzeltmesi.** Bunu yazan commit `41f79ec`.",
    ]
    assert module.corrected_by(lines, 0, datetime.date(2026, 8, 25)) is None


def test_a_correction_note_naming_the_right_commit_rescues() -> None:
    module = _module()
    sha = "e2e40dd"
    claimed = module.commit_date(sha)
    if claimed is None:
        pytest.skip(
            "no git history here: a shallow checkout, or the CI simulation's copy, "
            "which carries the tracked files without `.git`. The sweep reads the "
            "record and belongs to `local_checks.sh` for exactly this reason."
        )
    lines = [
        f"### Ek — {claimed} : eksene beşinci nokta",
        "",
        f"**Tarih düzeltmesi.** Eki yazan commit `{sha}`.",
    ]
    assert module.corrected_by(lines, 0, claimed) == sha


def test_only_self_dating_lines_enter_the_pair_comparison() -> None:
    """Free prose differs in notation between the languages; that is not a defect."""
    module = _module()
    prose = "20 Ağustos 2026'da yayına girdi ve bu bir olay tarihi."
    addendum = "**Kapandı, 18 Ağustos 2026.** Ölçüt uygulandı."
    assert module.load_bearing_dates(prose) == []
    assert module.load_bearing_dates(addendum) == [datetime.date(2026, 8, 18)]


def test_the_floor_is_below_what_the_documents_carry() -> None:
    module = _module()
    assert 0 < module.FLOOR
    found = 0
    for path in REPOSITORY.rglob("*.md"):
        if any(part in (".git", "vendor", "node_modules", ".venv") for part in path.parts):
            continue
        if path.name.endswith(".en.md"):
            continue
        found += len(module.load_bearing_dates(path.read_text(encoding="utf-8")))
    assert found >= module.FLOOR, f"{found} self-dating lines found, floor is {module.FLOOR}"


def test_an_english_correction_dates_itself() -> None:
    """The English word for "Düzeltme" is a marker; it was missing once."""
    module = _module()
    line = "**Correction — 25 September 2026: this section's title was wrong.**"
    assert module.SELF_DATING.match(line)
    assert module.parse(line) == datetime.date(2026, 9, 25)


def test_every_marker_is_a_pair_and_both_halves_match() -> None:
    module = _module()
    for turkish, english in module.MARKERS:
        assert turkish and english
        assert module.SELF_DATING.match(f"**{turkish} — 1 Ocak 2026.** metin")
        plain = english.replace("(?:It )?", "").replace("[Hh]", "H")
        assert module.SELF_DATING.match(f"**{plain} — 1 January 2026.** text"), english
