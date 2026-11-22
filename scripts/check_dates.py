"""Does every dated addendum carry a date the git record can confirm?

**Why it exists.** A preregistration is worth what its dates are worth. "Declared
before the run" is a claim about time, and the only thing that can settle it is
the record: the commit that carried the declaration into the repository. A date
typed into a document is a claim; a commit date is evidence. When the two
disagree, the document is quietly stronger than the record supports — which is
exactly what happened once here, where an addendum dated itself four days before
the commit that wrote it, turning a four-hour lead over the run into a four-day
one.

**What it checks.** Only lines that date *themselves* — an addendum, a
correction, a closure: "Ek — 25 Ağustos 2026", "Kapandı, 18 Ağustos 2026",
"Date correction, 2026-08-26". Those say when the writing happened, so the
record can check them.

**The markers come in pairs, and that is the rule.** Each kind of self-dating line
has a Turkish word and an English word (`MARKERS`): Ek and Addendum, Düzeltme and
Correction, Tarih düzeltmesi and Date correction, Kapandı and Closed, and so on. A
translation may use the English word of the pair its source used; a new kind of
line enters as a pair or not at all.

**What it does not check.** Lines that record when an *event* happened ("the
gate fired on 11 August"). Those are written down later by design, and the date
belongs to the event, not to the sentence.

**Translations are checked differently.** An `.en.md` file is written after its
`.tr.md` source and carries the source's dates, so its own commit date proves
nothing. What matters there is that the translation did not *change* a date, so
the two halves of a bilingual pair are compared as multisets of dates instead —
the parity check's idea, applied to dates rather than to backticked spans.

**The escape hatch, and why it is narrow.** A corrected date can never match its
own commit: correcting the text creates a new commit today. So a mismatch is
also accepted when the surrounding paragraph carries a correction note naming a
commit **whose date is the written date**. Naming the commit is the whole point;
a note without one silences nothing.

**Where it runs.** In `local_checks.sh`, not in CI. It reads the whole history
with `git log --all -S`, and CI checks out one commit deep; asking a shallow
clone when a text was written gets no answer, and a check that cannot see its
subject must decline rather than pass.

Usage:

    uv run python scripts/check_dates.py
"""

from __future__ import annotations

import collections
import datetime
import functools
import pathlib
import re
import subprocess
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
# A shape change that stopped these patterns from matching would leave the check
# reporting "every date holds" over nothing at all.
FLOOR = 15

MONTHS = {
    "Ocak": 1,
    "Şubat": 2,
    "Mart": 3,
    "Nisan": 4,
    "Mayıs": 5,
    "Haziran": 6,
    "Temmuz": 7,
    "Ağustos": 8,
    "Eylül": 9,
    "Ekim": 10,
    "Kasım": 11,
    "Aralık": 12,
}
ENGLISH = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}
NAMED = dict(MONTHS, **ENGLISH)
NAMES = "|".join(NAMED)
TURKISH = re.compile(rf"\b(\d{{1,2}}) ({NAMES}) (\d{{4}})\b")
ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
# The markers of a line that dates itself, as pairs: the Turkish source's word and
# the English translation's word for the same kind of line. The pattern is built
# from the pairs, so a marker cannot enter in one language only. It did once:
# "Düzeltme" had no English counterpart, and the correct translation,
# "Correction", was invisible to the pair comparison below, which then reported
# the source's date as missing from the translation.
MARKERS = (
    ("Ek", "Addendum"),
    ("Düzeltme", "Correction"),
    ("Tarih düzeltmesi", "Date correction"),
    ("Kapandı", "Closed"),
    ("Gerçekleşti", "(?:It )?[Hh]appened"),
    ("Üçüncü örnek", "A third instance"),
    ("Sınanmamış izin", "An untested permission"),
)
SELF_DATING = re.compile(
    r"^#{0,4}\s*[*_]*\s*(?:" + "|".join(rf"{word}\b" for pair in MARKERS for word in pair) + ")"
)
COMMIT = re.compile(r"`([0-9a-f]{7,40})`")
CORRECTION = re.compile(r"Tarih düzeltmesi|Date correction")
LOOKAHEAD = 8


def parse(line: str) -> datetime.date | None:
    """The first date on a line, in either notation."""
    turkish = TURKISH.search(line)
    if turkish:
        day, month, year = turkish.groups()
        return datetime.date(int(year), NAMED[month], int(day))
    iso = ISO.search(line)
    if iso:
        year, month, day = (int(part) for part in iso.groups())
        try:
            return datetime.date(year, month, day)
        except ValueError:
            return None
    return None


def load_bearing_dates(text: str) -> list[datetime.date]:
    """The dates on lines that date themselves, normalised.

    Free prose is not compared. Turkish writes "20 Ağustos'ta" where English
    writes "on 2026-08-20", and one of the two carries a year — a difference in
    notation, not in the record. Self-dating lines are marked in both languages
    and are the ones a claim rests on.
    """
    found = []
    for raw in text.splitlines():
        line = raw.strip()
        if not SELF_DATING.match(line):
            continue
        date = parse(line)
        if date is not None:
            found.append(date)
    return found


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPOSITORY), *args],
        capture_output=True,
        text=True,
        check=False,
    ).stdout


@functools.cache
def commit_date(revision: str) -> datetime.date | None:
    out = git("log", "-1", "--date=short", "--format=%ad", revision).strip()
    try:
        return datetime.date.fromisoformat(out)
    except ValueError:
        return None


def introducing(line: str) -> tuple[datetime.date, str] | None:
    """The oldest commit whose diff added this exact text, on any branch.

    Not restricted to the file's current path: a rename would otherwise date the
    text to the day the directory scheme changed.
    """
    out = git("log", "--all", "--reverse", "--date=short", "--format=%ad|%h", "-S", line)
    rows = [row for row in out.splitlines() if "|" in row]
    if not rows:
        return None
    written, sha = rows[0].split("|", 1)
    return datetime.date.fromisoformat(written), sha


def corrected_by(lines: list[str], index: int, claimed: datetime.date) -> str | None:
    """A correction note below this line naming a commit dated as claimed."""
    window = "\n".join(lines[index : index + LOOKAHEAD])
    if not CORRECTION.search(window):
        return None
    for sha in COMMIT.findall(window):
        if commit_date(sha) == claimed:
            return sha
    return None


def main() -> None:
    checked = 0
    accepted: list[str] = []
    problems: list[str] = []

    for path in sorted(REPOSITORY.rglob("*.md")):
        if any(part in (".git", "vendor", "node_modules", ".venv") for part in path.parts):
            continue
        relative = path.relative_to(REPOSITORY).as_posix()
        if git("ls-files", "--error-unmatch", relative).strip() == "":
            continue
        # A translation carries its source's dates; its own commit proves nothing.
        if relative.endswith(".en.md"):
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, raw in enumerate(lines):
            line = raw.strip()
            if not SELF_DATING.match(line):
                continue
            claimed = parse(line)
            if claimed is None:
                continue
            checked += 1
            origin = introducing(line)
            if origin is None:
                problems.append(
                    f"{relative}:{index + 1} no commit adds this line; it is uncommitted "
                    f"or was rewritten: {line[:60]}"
                )
                continue
            written, sha = origin
            if written == claimed:
                continue
            rescue = corrected_by(lines, index, claimed)
            if rescue:
                accepted.append(
                    f"{relative}:{index + 1} says {claimed}, commit {sha} is {written}, "
                    f"correction note names {rescue} ({claimed})"
                )
                continue
            problems.append(
                f"{relative}:{index + 1} says {claimed} but commit {sha} that wrote it "
                f"is dated {written} ({(written - claimed).days:+d} days): {line[:60]}"
            )

    # The second half: a translation may not change a date.
    pairs = 0
    for source in sorted(REPOSITORY.rglob("*.tr.md")):
        translation = source.with_name(source.name[: -len(".tr.md")] + ".en.md")
        if not translation.exists():
            continue
        pairs += 1
        left = collections.Counter(load_bearing_dates(source.read_text(encoding="utf-8")))
        right = collections.Counter(load_bearing_dates(translation.read_text(encoding="utf-8")))
        name = source.relative_to(REPOSITORY).as_posix()
        for date in sorted(set(left) | set(right)):
            if left[date] != right[date]:
                problems.append(
                    f"{name}: a dated addendum says {date} {left[date]} time(s) in the "
                    f"source and {right[date]} time(s) in the translation"
                )

    print(f"self-dating lines checked: {checked}")
    print(f"bilingual pairs compared by date: {pairs}")
    if accepted:
        print(f"corrected, and the correction names its commit: {len(accepted)}")
        for line in accepted:
            print(f"  - {line}")

    if checked < FLOOR:
        print()
        sys.exit(
            f"only {checked} self-dating line(s) were found and the floor is {FLOOR}. "
            "The documents' shape changed and this parser no longer reads them; it "
            "declines rather than reporting that every date holds."
        )

    print()
    if not problems:
        print(f"every dated addendum matches the commit that wrote it ({checked} checked)")
        return
    print(f"{len(problems)} DATE(S) THE RECORD DOES NOT CONFIRM, out of {checked}:")
    for line in problems:
        print(f"  - {line}")
    sys.exit(1)


if __name__ == "__main__":
    main()
