"""Checks the Colab notebook against the repository it calls into.

**Why it exists.** Five faults in five rounds were all the same shape: a value
was updated in one place and the thing that carried a copy of it was not. Every
one was found by running, which costs a session and a share of the compute
budget. The notebook was the least-checked artefact in the repository - every
script has a guard, and the notebook had `tests/test_colab_ref.py`, which pins a
branch name and the run command and nothing else. A sweep of its twelve cells
then found eleven more faults of the same shape, none of which that test could
see.

**What it decides.**

1. Every repository path the notebook names exists and is tracked.
2. Every protocol section it cites belongs to the run it actually runs. This is
   the class an existence check cannot see: section 15.2 exists, and it is
   `b14`'s conditions table on a notebook that runs `bir1`.
3. Every environment variable a cell writes is read by something the notebook
   runs. `ZIHIN_SCAN` was set in the run cell and read by nothing there; its one
   reader had already run, one cell earlier.
4. The prose states the values the conditions table declares, and the line that
   tells the reader which runtime to select names the declared one. The notebook
   said T4 while the declared model's measured file is 19.851 GB.
5. No cell hard-codes the working directory the first cell lets the user
   override. Four of them did, so the override was honoured once and ignored
   four times.

**What it cannot decide** is `S-69`: whether the notebook that runs is this one.
A copy in someone's Drive is outside every check in this repository. That limit
is the reason this file is small and mechanical - it makes the repository's copy
correct, and correctness of the copy is a separate problem with a separate fix.

Usage:

    uv run python scripts/check_colab_notebook.py
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
NOTEBOOK = REPOSITORY / "experiments/colab/zihin-colab.ipynb"

sys.path.insert(0, str(REPOSITORY / "src"))

# Floors. A shape change that stopped these patterns from matching would report
# a clean notebook, which is the failure mode this whole file exists to prevent.
CELL_FLOOR = 8
PATH_FLOOR = 5
CITATION_FLOOR = 2

PATH = re.compile(
    r"(?<![\w/.\-])((?:scripts|src|tests|config|results|experiments|docs|prompts|data)/[\w./\-]+\.\w+)"
)
CITATION = re.compile(r"§\s*(\d+)(?:\.(\d+))?")
MAGIC_ENV = re.compile(r"^\s*%env\s+(\w+)=(.*)$", re.M)
PYTHON_ENV = re.compile(r"os\.environ\[\s*[\"'](\w+)[\"']\s*\]\s*=")
# Every script on the line, not the first. Chaining a guard to a run with `&&`
# put two scripts on one line and the non-greedy form found only one, which
# would have made a variable read solely by the second look unread.
# No lookbehind: the shell lines address the scripts through `$WORKDIR/`, so a
# rule that refused a preceding slash found the Python scripts and silently
# dropped both shell ones.
INVOKED = re.compile(r"((?:scripts)/[\w./\-]+\.(?:py|sh))")
SHELL_LINE = re.compile(r"^\s*!(.*)$", re.M)
WORKDIR_LITERAL = "/content/zihin"

# Sections a run-specific notebook may cite outside its own: each one states a
# rule that is not about this run, and names where the rule actually lives. An
# allowlist rather than a pattern, because an exception written down is visible
# where a silently permitted one is not.
CITATIONS_OUTSIDE_THE_RUN = {
    "15.3": (
        "the rule that no episode starts on an unmeasured runtime; it is stated "
        "once, in the 14B section"
    ),
    "15.7": (
        "the rule that results are pushed rather than pasted; the run's section has no "
        "push subsection"
    ),
}

# Variables a cell writes for a reader outside the notebook's own run path.
# Same rule: named, with the reader.
WRITTEN_FOR_OTHERS = {
    "GITHUB_TOKEN": "scripts/colab_publish_results.sh, three cells later",
    "GIT_ASKPASS": "every later subprocess, git's credential path (K-152)",
    "GIT_TERMINAL_PROMPT": "every later subprocess",
    "ZIHIN_WORKDIR": "colab_bootstrap.sh and colab_publish_results.sh, which both default to it",
    "UV_NO_SYNC": "every later uv invocation, in the kernel rather than one shell",
}

# Values the conditions table declares that the prose must also state.
DECLARED_IN_PROSE = (("episode_ceiling", "the ceiling the run stops at"),)

# The line that tells the reader which runtime to select, in both languages, in
# the notebook and in the README beside it. Only this line is compared: the
# prose around it must stay free to name a runtime in order to say why it is the
# wrong one, and a blanket ban on the word would forbid the explanation along
# with the mistake.
SELECTION = re.compile(r"^.*(?:Çalışma zamanı|Runtime)\s*(?:→|->).*$", re.M)
RUNTIMES = ("A100", "T4", "L4", "V100", "P100")
ALSO_SELECTS = ("experiments/colab/README.md",)

# An episode count stated in prose, in either language. Every one of them must be
# a number the conditions table declares: the notebook said "thirty episodes" and
# so did the guard's own refusal, both left over from `b14`, on a run whose first
# sweep is ninety and whose ceiling is 270.
COUNT = re.compile(
    r"(\w+\W+|^)"
    r"\b(\d{1,4}|otuz|doksan|thirty|ninety|iki y\u00fcz yetmi\u015f|two hundred and seventy)\b"
    r"[^.\n(),;=]{0,20}?\b(epizot|epizotluk|episode|episodes)\b",
    re.I | re.M,
)
# A count introduced by one of these is a rate, not a claim about how many
# episodes this run has.
CADENCE = ("every", "each", "per", "her", "beher")
WORDS = {
    "otuz": "30",
    "thirty": "30",
    "doksan": "90",
    "ninety": "90",
    "iki y\u00fcz yetmi\u015f": "270",
    "two hundred and seventy": "270",
}

# A size written as a literal. The bootstrap announced "about 8.99 GB" for a pull
# of a model whose measured file is 19.851 GB: the 14B's number, left behind when
# the declared model changed. A literal is allowed only when it equals the
# declared size - prose written for a person may state the number, and then this
# rule is what keeps the stated number and the declared one the same.
SIZE_LITERAL = re.compile(r"\b(\d+[.,]\d+)\s*GB\b")

# Only what the reader sees, which is every line that is not a comment. Reading
# whole files flagged the comment recording what a number USED to be and a
# comment about the experiment's total episode count - a rule that fires on the
# explanation of a fix pushes the explanation out of the file. Matching only the
# line that carries `print(` or `sys.exit(` was too narrow the other way: the
# refusal this rule exists for is a multi-line string, and the sentence with the
# count in it carries no call at all.
COMMENT = re.compile(r"^\s*(#|//)")

# A shell variable read with no default. `${ZIHIN_PREFIX:+--prefix ...}` was read
# by the bootstrap and written by no cell, so it expanded to nothing every time -
# a knob with no hand on it.
UNDEFAULTED = re.compile(r"\$\{(ZIHIN_[A-Z0-9_]+)(:[+])")


def cells() -> list[tuple[int, str, str]]:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    return [
        (index, cell["cell_type"], "".join(cell.get("source") or []))
        for index, cell in enumerate(notebook["cells"])
    ]


def _run_command() -> list[str]:
    from zihin.declared import run_command

    return run_command()


def tracked(path: str) -> bool:
    done = subprocess.run(
        ["git", "-C", str(REPOSITORY), "ls-files", "--error-unmatch", path],
        capture_output=True,
    )
    return done.returncode == 0


def main() -> int:
    from zihin.declared import Undeclared, conditions, declared_field, run_prefix

    body = cells()
    if len(body) < CELL_FLOOR:
        sys.exit(f"the notebook has {len(body)} cells and the floor is {CELL_FLOOR}")

    prefix = run_prefix()
    section, _ = conditions(prefix)
    top = section.split(".")[0]
    print(f"notebook runs {prefix!r}; its conditions are section {section}")
    print()

    problems: list[str] = []

    # ---------------------------------------------------------------- 1. paths
    named: dict[str, list[int]] = {}
    for index, _, text in body:
        for path in PATH.findall(text):
            named.setdefault(path, []).append(index)
        for path in re.findall(r"/content/zihin/((?:scripts)/[\w./\-]+\.\w+)", text):
            named.setdefault(path, []).append(index)
    if len(named) < PATH_FLOOR:
        sys.exit(f"only {len(named)} paths were found and the floor is {PATH_FLOOR}")
    print("paths")
    for path in sorted(named):
        ok = tracked(path)
        print(f"  {'ok ' if ok else 'GAP'}  {path}  (cells {named[path]})")
        if not ok:
            problems.append(f"{path} (cells {named[path]}) is not a tracked file")

    # ------------------------------------------------------------ 2. citations
    print()
    print("protocol citations")
    seen = 0
    for index, _, text in body:
        for whole, minor in CITATION.findall(text):
            seen += 1
            cited = f"{whole}.{minor}" if minor else whole
            if whole == top:
                print(f"  ok   cell {index:>2}  section {cited}  the run's own section")
            elif cited in CITATIONS_OUTSIDE_THE_RUN:
                print(
                    f"  ok   cell {index:>2}  section {cited}  allowed: "
                    f"{CITATIONS_OUTSIDE_THE_RUN[cited]}"
                )
            else:
                print(f"  GAP  cell {index:>2}  section {cited}  not section {top} and not allowed")
                problems.append(
                    f"cell {index} cites section {cited}; {prefix!r} declares section "
                    f"{section}. The cited section exists, which is why reading it "
                    "looked right."
                )
    if seen < CITATION_FLOOR:
        sys.exit(f"only {seen} citations were found and the floor is {CITATION_FLOOR}")

    # -------------------------------------------------------- 3. the environment
    print()
    print("environment chain")
    written: dict[str, int] = {}
    for index, _, text in body:
        for match in MAGIC_ENV.finditer(text):
            written.setdefault(match.group(1), index)
        for name in PYTHON_ENV.findall(text):
            written.setdefault(name, index)
    invoked = sorted(
        {
            script
            for _, _, text in body
            for line in SHELL_LINE.findall(text)
            for script in INVOKED.findall(line)
        }
    )
    readers = {}
    for script in invoked:
        path = REPOSITORY / script
        readers[script] = path.read_text(encoding="utf-8") if path.exists() else ""
    print(f"  (the notebook invokes: {', '.join(invoked) or 'nothing'})")
    for name, where in sorted(written.items()):
        who = [script for script, text in readers.items() if name in text]
        if who:
            print(f"  ok   {name}: written in cell {where}, read by {', '.join(who)}")
        elif name in WRITTEN_FOR_OTHERS:
            print(f"  ok   {name}: written in cell {where}, for {WRITTEN_FOR_OTHERS[name]}")
        else:
            print(f"  GAP  {name}: written in cell {where}, read by nothing the notebook runs")
            problems.append(
                f"{name} is written in cell {where} and no script the notebook invokes "
                "names it. A variable nobody reads is a setting that does nothing."
            )

    # ---------------------------------------------------------- 4. declared prose
    print()
    print("prose against the conditions table")
    prose = "\n".join(text for _, kind, text in body if kind == "markdown")
    for field, why in DECLARED_IN_PROSE:
        try:
            value = declared_field(field, prefix)
        except Undeclared as error:
            print(f"  ??   {field}: {error}")
            continue
        if value in prose:
            print(f"  ok   {field}={value!r} appears in the prose ({why})")
        else:
            print(f"  GAP  {field}={value!r} is declared and the prose does not state it")
            problems.append(f"the prose does not state the declared {field} ({value!r}): {why}")

    # --- the runtime, on the line that actually tells the reader what to select
    try:
        runtime = declared_field("runtime", prefix)
    except Undeclared as error:
        print(f"  ??   runtime: {error}")
        runtime = ""
    if runtime:
        sources = [("the notebook", prose)] + [
            (name, (REPOSITORY / name).read_text(encoding="utf-8")) for name in ALSO_SELECTS
        ]
        for name, text in sources:
            found = SELECTION.findall(text)
            if not found:
                print(f"  GAP  {name}: no runtime selection line found at all")
                problems.append(
                    f"{name} has no line telling the reader which runtime to select, "
                    f"so the declared {runtime!r} is stated nowhere the reader acts on"
                )
                continue
            for line in found:
                line = line.strip()
                wrong = [
                    other
                    for other in RUNTIMES
                    if other != runtime and re.search(r"\b" + re.escape(other) + r"\b", line)
                ]
                if runtime in line and not wrong:
                    print(f"  ok   {name}: selects {runtime}  |  {line[:62]}")
                else:
                    print(f"  GAP  {name}: {line[:70]}")
                    problems.append(
                        f"{name} tells the reader to select "
                        f"{(wrong or ['a runtime it does not name'])[0]} while the "
                        f"declared runtime is {runtime!r}"
                    )

    # ------------------------------------------------- 5. counts, sizes, knobs
    print()
    print("counts, sizes and knobs in the Colab material")
    # Totals only. A cadence - "every thirty episodes" - is checked by the words
    # around it instead, because the block size and `b14`'s whole run are both
    # thirty and no comparison of numbers can tell them apart. "Thirty episodes
    # must not start" states a total and is stale; "every thirty episodes
    # re-mines the library" states a cadence and is right.
    # Both from the table. The first sweep used to be counted by asking AppWorld
    # how many tasks the `train` split has, and AppWorld's data is absent in CI:
    # the same commit would have accepted "ninety episodes" here and refused it
    # there. K-117 says a check must not give a different answer in a different
    # environment, so the number is declared instead of discovered.
    declared_counts = set()
    for field in ("first_sweep", "episode_ceiling"):
        try:
            declared_counts.add(declared_field(field, prefix).replace(".", ""))
        except Undeclared:
            pass
    try:
        size = declared_field("model_file_gb", prefix)
    except Undeclared:
        size = ""
    print(f"  (declared counts: {sorted(declared_counts)}; declared size: {size or 'none'} GB)")

    # The notebook and the README are read whole: every word of them is addressed
    # to the reader. The scripts are read only where they speak.
    material = [("the notebook", "\n".join(text for _, _, text in body))]
    material += [(name, (REPOSITORY / name).read_text(encoding="utf-8")) for name in ALSO_SELECTS]
    material += [
        (name, "\n".join(line for line in text.splitlines() if not COMMENT.match(line)))
        for name, text in readers.items()
        if text
    ]
    # The knob rule reads the whole script, not only the lines that speak: a
    # variable spliced into a command is not printed anywhere. Narrowing the
    # count rule to what the reader sees had silently narrowed this one too.
    whole = [(name, text) for name, text in readers.items() if text]
    for name, text in whole:
        for knob, _ in UNDEFAULTED.findall(text):
            if knob in written:
                continue
            print(f"  GAP  {name}: reads {knob} with no default and no cell writes it")
            problems.append(
                f"{name} reads {knob} with no default and no notebook cell writes it, "
                "so the expansion is always empty"
            )
    for name, text in material:
        for before, number, _ in COUNT.findall(text):
            value = WORDS.get(number.lower(), number)
            if value in declared_counts:
                continue
            if before.strip().lower().rstrip(",") in CADENCE:
                continue
            print(f"  GAP  {name}: an episode count of {number!r} is stated and not declared")
            problems.append(
                f"{name} states an episode count of {number!r}; the conditions table "
                f"declares {sorted(declared_counts)}"
            )
        for literal in SIZE_LITERAL.findall(text):
            if size and literal.replace(",", ".") == size.replace(",", "."):
                continue
            print(f"  GAP  {name}: the size {literal!r} GB is not the declared {size!r}")
            problems.append(
                f"{name} states a size of {literal!r} GB; the conditions table declares "
                f"{size!r} GB for the model this run resolves"
            )
    if not [line for line in problems if "states an" in line or "reads ZIHIN" in line]:
        print("  ok   every stated count and size is declared, every knob is written")

    # --------------------------------------------- 6. the guard guards the run
    print()
    print("the guard and the run")
    command = " ".join(_run_command())
    chained = [
        line
        for _, _, text in body
        for line in SHELL_LINE.findall(text)
        if command in line and "require_colab_environment.py" in line
    ]
    if chained:
        print(f"  ok   the run is chained behind the guard: {chained[0].strip()[:80]}")
    else:
        print("  GAP  the run command is not on the guard's line")
        problems.append(
            "the run command and require_colab_environment.py are not chained on one "
            "shell line. A failing `!` line does not stop the next one and the cell "
            "still reports success, so the guard refuses and the run starts anyway."
        )

    # ------------------------------------------------------- 7. the working copy
    print()
    print("working directory")
    for index, kind, text in body:
        if kind != "code":
            continue
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith(("!", "%cd")):
                continue
            if WORKDIR_LITERAL in stripped:
                print(f"  GAP  cell {index:>2}  {stripped[:70]}")
                problems.append(
                    f"cell {index} hard-codes {WORKDIR_LITERAL}, so the ZIHIN_WORKDIR "
                    "override the first cell offers is ignored here"
                )
            else:
                print(f"  ok   cell {index:>2}  {stripped[:70]}")

    print()
    print(f"problems: {len(problems)}")
    for line in problems:
        print(f"  - {line}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
