"""Builds the coverage summary at the top of the presentation skeleton.

**Why generated.** The skeleton's whole method is a coverage test: every claim
carries an attribution slot, and the summary counts how many slots are full. A
hand-kept summary is a second source of truth over the same rows, and this one
drifted three times before anyone counted. It said 28 claims, 22 filled, 6 empty;
the rows said 35, 28 and 7. Section 2 gained a claim, section 4 gained a claim,
and section 5 — five claims — was never in the summary at all.

The drift mattered beyond arithmetic. The summary is the first table a reader
sees and the sentence under it reads "the causal layer is entirely empty".
That sentence stayed true, but the number that supports it was wrong, and a
coverage test whose own coverage number is stale is arguing against itself.

The rows are the source. `--check` fails when the summary disagrees with them.

Usage:

    uv run python scripts/build_skeleton_coverage.py           # writes the table
    uv run python scripts/build_skeleton_coverage.py --check   # fails if stale
"""

from __future__ import annotations

import pathlib
import re
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
SOURCE = REPOSITORY / "docs/reports/sunum-iskeleti.md"

BEGIN = "<!-- KAPSAMA BASLANGIC: uretilmis, elle duzenlenmiyor -->"
END = "<!-- KAPSAMA BITIS -->"

SECTION = re.compile(r"^(\d)\. (.+?)$")
CLAIM = re.compile(r"^\| ([1-6])\.(\d+) \| (.+?) \| (.+?) \| (.+?) \|$", re.M)


def layers(text: str) -> list[tuple[str, str, int, int]]:
    """(number, name, claims, empty) per section, counted from the claim rows.

    Rows are counted **inside their own section**, not swept from the whole
    file. Later sections of the skeleton discuss the same claims in tables of
    their own, and a claim row is only a claim row where the claims live. The
    numbering is checked against the section it sits in for the same reason: a
    `2.5` row under section 3 means one of the two is wrong, and counting it
    silently would hide that.
    """
    found = []
    for block in text.split("\n## ")[1:]:
        heading, _, body = block.partition("\n")
        match = SECTION.match(heading)
        if not match:
            continue
        number, name = match.group(1), match.group(2).split("—")[0].strip(" *")
        rows = CLAIM.findall(body)
        for section, item, _, _, _ in rows:
            if section != number:
                raise SystemExit(f"claim {section}.{item} sits under section {number}")
        found.append((number, name, len(rows), sum("BOŞ" in row[4] for row in rows)))
    return found


def table(found: list[tuple[str, str, int, int]]) -> str:
    total = sum(count for _, _, count, _ in found)
    empty = sum(blank for _, _, _, blank in found)
    lines = [
        BEGIN,
        "",
        "| Katman | İddia sayısı | Atfı olan | Boş |",
        "|---|---|---|---|",
    ]
    for _, name, count, blank in found:
        mark = "**" if blank else ""
        lines.append(
            f"| {mark}{name}{mark} | {mark}{count}{mark} | {count - blank} | {mark}{blank}{mark} |"
        )
    lines.append(f"| **Toplam** | **{total}** | **{total - empty}** | **{empty}** |")
    lines += [
        "",
        "Bu tablo üretiliyor; elle düzenlenen bir kopyası yok "
        "(`scripts/build_skeleton_coverage.py`). Sayılar aşağıdaki iddia "
        "satırlarından sayılıyor, ayrıca yazılmıyor.",
        "",
        END,
    ]
    return "\n".join(lines)


def rendered(text: str) -> str:
    new = table(layers(text))
    if BEGIN in text and END in text:
        head, _, rest = text.partition(BEGIN)
        _, _, tail = rest.partition(END)
        return head + new + tail
    marker = "| Katman | İddia sayısı | Atfı olan | Boş |"
    head, _, rest = text.partition(marker)
    _, _, tail = rest.partition("\n\n")
    return head + new + "\n\n" + tail


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    updated = rendered(text)
    found = layers(text)
    if "--check" in sys.argv:
        if updated != text:
            sys.exit(
                f"{SOURCE.relative_to(REPOSITORY)}: the coverage summary is stale. "
                "Run scripts/build_skeleton_coverage.py."
            )
        print(f"skeleton coverage: current, {sum(c for _, _, c, _ in found)} claims")
        return
    SOURCE.write_text(updated, encoding="utf-8")
    total = sum(count for _, _, count, _ in found)
    empty = sum(blank for _, _, _, blank in found)
    print(
        f"{SOURCE.relative_to(REPOSITORY)}: {total} claims, "
        f"{total - empty} attributed, {empty} empty"
    )


if __name__ == "__main__":
    main()
