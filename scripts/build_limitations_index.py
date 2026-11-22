"""Builds the map at the top of the limitations document, and checks it stays true.

**Why a map.** The document carries 55 records over 1700 lines. A reader handed
it starts at S-01 and walks. Which limits are still open, which were closed, and
which claim each one bounds — none of that is visible without reading the whole
thing, and it is the document named in the delivery list.

**Why generated rather than written.** A hand-kept index is a second source of
truth, and this repository has measured what that costs: the decision CSV carried
"Karar." as thirty rationale summaries because a projection drifted from its
source and nothing objected (K-103). The map is derived from the document, and
`--check` fails when the two disagree.

**Three fields, all read from what is already written.**

*Status* comes from the heading: struck through, or carrying CLOSED/FIXED/SOLVED,
means closed. No new syntax enters the document.

*Axis* comes from the first blockquote under the heading — `> **İddiayı
sınırlıyor.** <claim>`, `> **Kapsam.** <what it records>`, or
`> **Sınıflandırılmadı.** <why>`. The operational test is that a record counts as
claim-limiting only when the claim it bounds is named; without a name it is scope
(K-107). A closed record's axis is not asked: a closed limitation bounds nothing,
so the column shows a dash rather than an omission.

*Closure class* comes from the second blockquote — `> **Kapanma sınıfı.**
<label> — <one line>` — and answers one question: whose hands is the work that
would close this record in. Upstream, hardware and the frozen scaffold are
`Dış olgu`; a measurement whose answer is the constraint itself is `Ölçüldü`; a
planned measurement or build of our own is `Sonraki tur`; an event in our own
history that no work undoes is `Kalıcı kayıt`. Only the third can close, so the
count of it is the share of the document that is provisional — the reason the
field is worth generating rather than leaving in a report that closes.

The first three labels were declared by a sweep over fifteen records. `Kalıcı
kayıt` appeared when the same test was applied to all thirty-nine and two of them
fit none of the three, which is the branch K-104 requires a pre-declared table to
carry.

**`(özgün metin)` is an appendix, not a record.** When a limitation is closed the
original text is kept below it under the same identifier rather than deleted. It
is folded into its record instead of being counted twice.

Usage:

    uv run python scripts/build_limitations_index.py           # writes the map
    uv run python scripts/build_limitations_index.py --check   # fails if stale
"""

from __future__ import annotations

import pathlib
import re
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
SOURCE = REPOSITORY / "docs/09-limitations.tr.md"
TRANSLATION = REPOSITORY / "docs/09-limitations.en.md"

EN_CLAIM = re.compile(r"^> \*\*Bounds a claim\.\*\* (.+)$", re.M)
STATUS_EN = {"açık": "open", "kapandı": "closed"}
AXIS_EN = {
    "sınırlıyor": "bounds",
    "kapsam": "scope",
    "sınıflandırılmadı": "unclassified",
    "işaretsiz": "unmarked",
    "—": "—",
}
CLOSURE_EN = {
    "Dış olgu": "External fact",
    "Ölçüldü": "Measured",
    "Sonraki tur": "Next round",
    "Kalıcı kayıt": "Permanent record",
    "işaretsiz": "unmarked",
    "—": "—",
}

BEGIN = "<!-- HARITA BASLANGIC: uretilmis, elle duzenlenmiyor -->"
END = "<!-- HARITA BITIS -->"
CLAIMS_BEGIN = "<!-- IDDIA HARITASI BASLANGIC: uretilmis, elle duzenlenmiyor -->"
CLAIMS_END = "<!-- IDDIA HARITASI BITIS -->"

HEADING = re.compile(r"^## (.+)$", re.M)
IDENTIFIER = re.compile(r"(S-\d+)")
AXIS = re.compile(r"^> \*\*(İddiayı sınırlıyor|Kapsam|Sınıflandırılmadı)\.\*\*", re.M)
CLAIM = re.compile(r"^> \*\*İddiayı sınırlıyor\.\*\* (.+)$", re.M)
AXIS_SHORT = {
    "İddiayı sınırlıyor": "sınırlıyor",
    "Kapsam": "kapsam",
    "Sınıflandırılmadı": "sınıflandırılmadı",
}
CLOSURE = re.compile(r"^> \*\*Kapanma sınıfı\.\*\* ([^—]+) —", re.M)
CLOSURE_LABELS = ("Dış olgu", "Ölçüldü", "Sonraki tur", "Kalıcı kayıt")
CLOSED_WORDS = ("KAPANDI", "DÜZELTİLDİ", "ÇÖZÜLDÜ", "KAPATILDI")


def bodies(text: str) -> dict[str, str]:
    """The text under each record's heading, keyed by identifier."""
    found: dict[str, str] = {}
    for block in text.split("\n## ")[1:]:
        heading = block.split("\n", 1)[0]
        if "(özgün metin)" in heading:
            continue
        match = IDENTIFIER.search(heading)
        if match:
            found.setdefault(match.group(1), block)
    return found


def records(text: str) -> list[tuple[str, str, str, str]]:
    """(identifier, title, status, axis, closure) per record, appendices folded in."""
    under = bodies(text)
    found = []
    seen = set()
    for heading in HEADING.findall(text):
        if "(özgün metin)" in heading:
            continue
        match = IDENTIFIER.search(heading)
        if not match:
            continue
        identifier = match.group(1)
        if identifier in seen:
            continue
        seen.add(identifier)
        struck = heading.startswith("~~") and heading.rstrip().endswith("~~")
        closed = struck or any(word in heading for word in CLOSED_WORDS)
        title = heading.strip("~").split("—", 1)[-1].strip()
        for word in CLOSED_WORDS:
            title = title.split(f"— {word}")[0].split(f"— {word.title()}")[0]
        title = title.strip(" ~—")
        if closed:
            axis = closure = "—"
        else:
            body = under.get(identifier, "")
            found_axis = AXIS.search(body)
            axis = AXIS_SHORT[found_axis.group(1)] if found_axis else "işaretsiz"
            found_closure = CLOSURE.search(body)
            closure = found_closure.group(1).strip() if found_closure else "işaretsiz"
            if closure not in CLOSURE_LABELS and closure != "işaretsiz":
                raise SystemExit(f"{identifier}: unknown closure class “{closure}”")
        found.append((identifier, title, "kapandı" if closed else "açık", axis, closure))
    return found


def table(found: list[tuple[str, str, str, str, str]]) -> str:
    open_count = sum(1 for r in found if r[2] == "açık")
    limiting = sum(1 for r in found if r[3] == "sınırlıyor")
    scope = sum(1 for r in found if r[3] == "kapsam")
    unclassified = sum(1 for r in found if r[3] == "sınıflandırılmadı")
    unmarked = sum(1 for r in found if r[3] == "işaretsiz")
    by_class = {label: sum(1 for r in found if r[4] == label) for label in CLOSURE_LABELS}
    unclassed = sum(1 for r in found if r[4] == "işaretsiz")
    provisional = by_class["Sonraki tur"]
    lines = [
        BEGIN,
        "",
        f"**{len(found)} sınırlama: {open_count} açık, {len(found) - open_count} "
        "kapandı.** Bu tablo üretiliyor; elle düzenlenen bir kopyası yok "
        "(`scripts/build_limitations_index.py`). Kayda gitmek için kimliği arayın.",
        "",
        f"**Açık maddelerin ekseni:** {limiting} bir iddiayı sınırlıyor, {scope} kapsam, "
        f"{unclassified} sınıflandırılmadı, {unmarked} henüz işaretsiz. Eksen her kaydın "
        "başlığının altındaki ilk alıntı satırından okunuyor; bir maddeyi "
        "“sınırlıyor” saymak için sınırladığı iddia adıyla yazılıyor (K-107).",
        "",
        f"**Açık maddelerin kapanma sınıfı:** {by_class['Dış olgu']} dış olgu, "
        f"{by_class['Ölçüldü']} ölçüldü ve kısıt gerçek çıktı, {provisional} sonraki tur, "
        f"{by_class['Kalıcı kayıt']} kalıcı kayıt, {unclassed} sınıfsız. Ölçüt tek soru: "
        "*bu kaydı kapatacak iş kimin elinde?* Yalnız üçüncü sınıf kapanabilir — yani "
        f"{open_count} açık maddenin {provisional} tanesi geçici, kalan "
        f"{open_count - provisional} tanesi belgede kalıcı.",
        "",
        "| | Sınırlama | Durum | Eksen | Kapanma |",
        "|---|---|---|---|---|",
    ]
    for identifier, title, status, axis, closure in sorted(
        found, key=lambda r: int(r[0].split("-")[1])
    ):
        mark = "" if status == "açık" else "~~"
        lines.append(f"| `{identifier}` | {mark}{title}{mark} | {status} | {axis} | {closure} |")
    lines += ["", END]
    return "\n".join(lines)


def claims(text: str) -> dict[str, list[str]]:
    """Which limitations bound each claim: the map read the other way round.

    The limitation-keyed table answers "what does this record bound". A
    presentation needs the inverse: how many limitations stand under a claim. A
    claim carrying eight of them is barely a claim, and that is only visible from
    this side.

    The key is the text before the first em dash in the marker, so two records
    naming `K-51` land on the same claim whatever they say after it.
    """
    grouped: dict[str, list[str]] = {}
    for identifier, block in bodies(text).items():
        heading = block.split("\n", 1)[0]
        struck = heading.startswith("~~") and heading.rstrip().endswith("~~")
        if struck or any(word in heading for word in CLOSED_WORDS):
            continue
        match = CLAIM.search(block)
        if not match:
            continue
        key = match.group(1).split("—")[0].strip().rstrip(".,")
        grouped.setdefault(key, []).append(identifier)
    return {k: sorted(v, key=lambda s: int(s.split("-")[1])) for k, v in grouped.items()}


def claims_table(grouped: dict[str, list[str]]) -> str:
    total = sum(len(v) for v in grouped.values())
    lines = [
        CLAIMS_BEGIN,
        "",
        f"**{len(grouped)} iddia, {total} sınırlama.** Bu tablo yukarıdakinin ters "
        "yönü: her iddianın altında kaç sınırlama durduğu. Sekiz sınırlaması olan "
        "bir iddia zar zor iddiadır ve bu ancak buradan görünüyor. Üretiliyor; "
        "elle düzenlenen kopyası yok (K-107).",
        "",
        "| İddia | Sınırlama | Kimlikler |",
        "|---|---|---|",
    ]
    for key, identifiers in sorted(grouped.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        joined = ", ".join(f"`{i}`" for i in identifiers)
        lines.append(f"| {key} | {len(identifiers)} | {joined} |")
    lines += ["", CLAIMS_END]
    return "\n".join(lines)


def with_claims(text: str) -> str:
    """The claim-keyed table, written under the limitation-keyed one."""
    new = claims_table(claims(text))
    if CLAIMS_BEGIN in text and CLAIMS_END in text:
        head, _, rest = text.partition(CLAIMS_BEGIN)
        _, _, tail = rest.partition(CLAIMS_END)
        return head + new + tail
    head, separator, tail = text.partition(END)
    return head + separator + "\n\n" + new + tail


def english_titles(text: str) -> dict[str, str]:
    """Record titles as the translation words them, keyed by identifier.

    The map's structure is read from the Turkish source — it is the source, and
    parsing one document keeps one parser. Only the wording is taken from the
    translation, so the English map reads as English without a second parser
    drifting from the first.
    """
    found: dict[str, str] = {}
    for heading in HEADING.findall(text):
        if "(original text)" in heading:
            continue
        match = IDENTIFIER.search(heading)
        if not match or match.group(1) in found:
            continue
        title = heading.strip("~").split("—", 1)[-1].strip()
        for word in ("CLOSED", "FIXED", "SOLVED", *CLOSED_WORDS):
            title = title.split(f"— {word}")[0]
        found[match.group(1)] = title.strip(" ~—")
    return found


def english_claims(text: str, wanted: set[str]) -> dict[str, list[str]]:
    """The claim-keyed map in English, restricted to the records still open."""
    grouped: dict[str, list[str]] = {}
    for identifier, block in bodies(text).items():
        if identifier not in wanted:
            continue
        match = EN_CLAIM.search(block)
        if not match:
            continue
        key = match.group(1).split("—")[0].strip().rstrip(".,")
        grouped.setdefault(key, []).append(identifier)
    return {k: sorted(v, key=lambda s: int(s.split("-")[1])) for k, v in grouped.items()}


def english_table(found: list[tuple[str, str, str, str, str]], titles: dict[str, str]) -> str:
    open_count = sum(1 for r in found if r[2] == "açık")
    by_class = {label: sum(1 for r in found if r[4] == label) for label in CLOSURE_LABELS}
    provisional = by_class["Sonraki tur"]
    lines = [
        BEGIN,
        "",
        f"**{len(found)} limitations: {open_count} open, {len(found) - open_count} "
        "closed.** This table is generated; there is no hand-edited copy "
        "(`scripts/build_limitations_index.py`). Search the identifier to reach a record.",
        "",
        f"**Axis of the open items:** {sum(1 for r in found if r[3] == 'sınırlıyor')} bound a "
        f"claim, {sum(1 for r in found if r[3] == 'kapsam')} are scope. The axis is read from "
        "the first quoted line under each record's heading; calling an item “bounds” requires "
        "naming the claim it bounds (K-107).",
        "",
        f"**Closure class of the open items:** {by_class['Dış olgu']} external fact, "
        f"{by_class['Ölçüldü']} measured and the constraint is real, {provisional} next round, "
        f"{by_class['Kalıcı kayıt']} permanent record. The test is one question: *whose hands "
        "is the work that would close this record in?* Only the third class can close — so "
        f"{provisional} of the {open_count} open items are provisional and the remaining "
        f"{open_count - provisional} are permanent in this document.",
        "",
        "| | Limitation | Status | Axis | Closure |",
        "|---|---|---|---|---|",
    ]
    for identifier, _, status, axis, closure in sorted(
        found, key=lambda r: int(r[0].split("-")[1])
    ):
        title = titles.get(identifier)
        if title is None:
            raise SystemExit(f"{identifier}: present in the source, absent from the translation")
        mark = "" if status == "açık" else "~~"
        lines.append(
            f"| `{identifier}` | {mark}{title}{mark} | {STATUS_EN[status]} | "
            f"{AXIS_EN[axis]} | {CLOSURE_EN[closure]} |"
        )
    lines += ["", END]
    return "\n".join(lines)


def english_claims_table(grouped: dict[str, list[str]]) -> str:
    total = sum(len(v) for v in grouped.values())
    lines = [
        CLAIMS_BEGIN,
        "",
        f"**{len(grouped)} claims, {total} limitations.** This table is the reverse of the one "
        "above: how many limitations stand under each claim. A claim carrying eight of them is "
        "barely a claim, and that is only visible from this side. Generated; there is no "
        "hand-edited copy (K-107).",
        "",
        "| Claim | Limitations | Identifiers |",
        "|---|---|---|",
    ]
    for key, identifiers in sorted(grouped.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        joined = ", ".join(f"`{i}`" for i in identifiers)
        lines.append(f"| {key} | {len(identifiers)} | {joined} |")
    lines += ["", CLAIMS_END]
    return "\n".join(lines)


def between(text: str, begin: str, end: str, new: str) -> str:
    if begin not in text or end not in text:
        raise SystemExit(f"the translation has no {begin!r} markers")
    head, _, rest = text.partition(begin)
    _, _, tail = rest.partition(end)
    return head + new + tail


def rendered(text: str) -> str:
    """The document with the map in place, whether or not it had one."""
    new = table(records(text))
    if BEGIN in text and END in text:
        head, _, rest = text.partition(BEGIN)
        _, _, tail = rest.partition(END)
        return head + new + tail
    marker = "\n---\n"
    head, separator, tail = text.partition(marker)
    return head + "\n" + new + "\n" + separator + tail


def translated(text: str, source: str) -> str:
    """The English document with both generated blocks in place."""
    found = records(source)
    titles = english_titles(text)
    still_open = {r[0] for r in found if r[2] == "açık"}
    with_map = between(text, BEGIN, END, english_table(found, titles))
    return between(
        with_map, CLAIMS_BEGIN, CLAIMS_END, english_claims_table(english_claims(text, still_open))
    )


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    english = TRANSLATION.read_text(encoding="utf-8")
    updated = with_claims(rendered(text))
    updated_english = translated(english, text)
    found = records(text)
    if "--check" in sys.argv:
        if updated != text:
            sys.exit(
                f"{SOURCE.relative_to(REPOSITORY)}: the map is stale. "
                "Run scripts/build_limitations_index.py."
            )
        if updated_english != english:
            sys.exit(
                f"{TRANSLATION.relative_to(REPOSITORY)}: the map is stale. "
                "Run scripts/build_limitations_index.py."
            )
        print(f"limitations map: current in both languages, {len(found)} records")
        return
    SOURCE.write_text(updated, encoding="utf-8")
    TRANSLATION.write_text(updated_english, encoding="utf-8")
    open_count = sum(1 for r in found if r[2] == "açık")
    unmarked = sum(1 for r in found if r[3] == "işaretsiz")
    unclassed = sum(1 for r in found if r[4] == "işaretsiz")
    print(
        f"{SOURCE.relative_to(REPOSITORY)}: {len(found)} records, "
        f"{open_count} open, {unmarked} without an axis marker, "
        f"{unclassed} without a closure class"
    )


if __name__ == "__main__":
    main()
