"""Proves `scripts/check_colab_notebook.py` refuses each fault it was written for.

**Why every case puts the fault back rather than describing it.** A guard that
has only been run against a correct file has not been shown to do anything. The
twelve faults below are the ones a cell-by-cell audit found in the notebook and
the material it calls, each stated as the exact edit that reintroduces it. If a
rule stops working, the case for it fails here rather than in Colab.

**Why a scratch copy.** The check resolves the repository from its own location
and reads the protocol, the notebook, the README and every script the notebook
invokes, and its tracked-file rule asks git. So the module copies every tracked
file, as it stands in the working tree, into its own temporary directory, indexes
the copy with `git add`, and runs the copy's check. A test never writes into the
repository tree. Each case still restores its file in a `finally`, so the cases
stay independent, and the last test asserts the copy is clean again.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys

import pytest

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
GUARD = "scripts/check_colab_notebook.py"
NOTEBOOK = "experiments/colab/zihin-colab.ipynb"


@pytest.fixture(scope="module")
def copy(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    """The tracked tree, with working-tree contents, in this module's own directory."""
    root = tmp_path_factory.mktemp("colab-check") / "repository"
    listed = subprocess.run(
        ["git", "-C", str(REPOSITORY), "ls-files", "-z"], capture_output=True, check=True
    ).stdout.decode("utf-8")
    for relative in filter(None, listed.split("\0")):
        source = REPOSITORY / relative
        if not source.is_file():
            continue
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    return root


def run_guard(root: pathlib.Path) -> tuple[int, str]:
    done = subprocess.run(
        [sys.executable, str(root / GUARD)], capture_output=True, text=True, cwd=str(root)
    )
    return done.returncode, done.stdout + done.stderr


def edit_cell(root: pathlib.Path, index: int, old: str, new: str) -> None:
    notebook = root / NOTEBOOK
    data = json.loads(notebook.read_text(encoding="utf-8"))
    text = "".join(data["cells"][index]["source"])
    assert old in text, f"cell {index} no longer contains {old[:40]!r}"
    text = text.replace(old, new, 1)
    parts = text.split("\n")
    data["cells"][index]["source"] = [p + "\n" for p in parts[:-1]] + (
        [parts[-1]] if parts[-1] else []
    )
    notebook.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def edit_file(root: pathlib.Path, relative: str, old: str, new: str) -> None:
    path = root / relative
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{relative} no longer contains {old[:40]!r}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# (what the fault is, the file it lives in, the edit that puts it back, the
#  sentence the check must say about it)
FAULTS = [
    (
        "the reader is told to select a runtime the model does not fit",
        NOTEBOOK,
        lambda root: edit_cell(root, 0, "Çalışma zamanı → A100 GPU", "Çalışma zamanı → T4 GPU"),
        "select T4",
    ),
    (
        "the pull announces the previous model's size",
        "scripts/colab_bootstrap.sh",
        lambda root: edit_file(
            root, "scripts/colab_bootstrap.sh", "about ${MODEL_GB} GB", "about 8.99 GB"
        ),
        "states a size of '8.99'",
    ),
    (
        "the conditions are cited from another run's section",
        NOTEBOOK,
        lambda root: edit_cell(root, 8, "şartlar §19.6'da", "şartlar §15.2'de"),
        "cell 8 cites section 15.2",
    ),
    (
        "resumption is cited from another run's section",
        NOTEBOOK,
        lambda root: edit_cell(root, 8, "(§19.6,", "(§15.6,"),
        "cell 8 cites section 15.6",
    ),
    (
        "a section is cited that is neither this run's nor an allowed rule",
        NOTEBOOK,
        lambda root: edit_cell(root, 10, "(§15.7,", "(§15.4,"),
        "cell 10 cites section 15.4",
    ),
    (
        "the prose states an episode count the run does not declare",
        NOTEBOOK,
        lambda root: edit_cell(
            root, 0, "Dilim başlamadan", "**Otuz epizot** sürecek dilim başlamadan"
        ),
        "episode count of 'Otuz'",
    ),
    (
        "a refusal states the previous run's episode count",
        "scripts/setup/require_colab_environment.py",
        lambda root: edit_file(
            root,
            "scripts/setup/require_colab_environment.py",
            "No episode may start on an unmeasured runtime",
            "Thirty episodes must not start on an unmeasured runtime",
        ),
        "episode count of 'Thirty'",
    ),
    (
        "the README beside the notebook names a different runtime",
        "experiments/colab/README.md",
        lambda root: edit_file(
            root,
            "experiments/colab/README.md",
            "Çalışma zamanı türünü değiştir → A100 GPU",
            "Çalışma zamanı türünü değiştir → T4 GPU",
        ),
        "select T4",
    ),
    (
        "a cell sets a variable nothing it runs reads",
        NOTEBOOK,
        lambda root: edit_cell(
            root,
            9,
            "%cd $WORKDIR\n",
            "%cd $WORKDIR\n%env ZIHIN_SCAN=results/bant-taramasi-anahtar-gocu.json\n",
        ),
        "ZIHIN_SCAN is written in cell 9",
    ),
    (
        "a script reads a knob no cell writes",
        "scripts/colab_bootstrap.sh",
        lambda root: edit_file(
            root,
            "scripts/colab_bootstrap.sh",
            "check_prerequisites.py || fail",
            'check_prerequisites.py ${ZIHIN_PREFIX:+--prefix "$ZIHIN_PREFIX"} || fail',
        ),
        "reads ZIHIN_PREFIX with no default",
    ),
    (
        "a cell hard-codes the working directory the first cell lets you override",
        NOTEBOOK,
        lambda root: edit_cell(
            root,
            5,
            "!bash $WORKDIR/scripts/colab_bootstrap.sh",
            "!bash /content/zihin/scripts/colab_bootstrap.sh",
        ),
        "cell 5 hard-codes /content/zihin",
    ),
    (
        "the guard and the run are separate shell lines, so the guard does not guard",
        NOTEBOOK,
        lambda root: edit_cell(
            root,
            9,
            "require_colab_environment.py && uv run python scripts/run_experiment.py",
            "require_colab_environment.py\n!uv run python scripts/run_experiment.py",
        ),
        "not chained on one shell line",
    ),
]


def test_the_material_as_it_stands_passes(copy: pathlib.Path) -> None:
    """Every case below rests on this: the fault put back is the only difference."""
    code, output = run_guard(copy)
    assert code == 0, output


@pytest.mark.parametrize(
    ("description", "path", "mutate", "expected"),
    FAULTS,
    ids=[fault[0][:44].replace(" ", "-") for fault in FAULTS],
)
def test_the_check_refuses_each_fault(copy, description, path, mutate, expected) -> None:
    target = copy / path
    saved = target.read_text(encoding="utf-8")
    try:
        mutate(copy)
        code, output = run_guard(copy)
    finally:
        target.write_text(saved, encoding="utf-8")
    assert code != 0, f"{description}: the check passed on it\n{output}"
    assert expected in output, f"{description}: refused, but not about this\n{output}"


def test_the_check_declines_rather_than_passing_when_it_cannot_read_the_notebook(
    copy: pathlib.Path,
) -> None:
    """A parser that stops matching must not report a clean notebook.

    This is the failure mode the floors exist for, and the one that makes a
    guard worse than no guard: it goes on answering after it has stopped
    looking.
    """
    notebook = copy / NOTEBOOK
    saved = notebook.read_text(encoding="utf-8")
    try:
        data = json.loads(saved)
        data["cells"] = data["cells"][:3]
        notebook.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        code, output = run_guard(copy)
    finally:
        notebook.write_text(saved, encoding="utf-8")
    assert code != 0, output
    assert "floor" in output, output


def test_the_copy_is_as_it_was(copy: pathlib.Path) -> None:
    """Every case restores its file in the copy; this says so out loud."""
    done = subprocess.run(
        ["git", "-C", str(copy), "diff", "--stat"], capture_output=True, text=True, check=True
    )
    assert done.stdout == "", f"a case left the copy changed:\n{done.stdout}"
    code, output = run_guard(copy)
    assert code == 0, f"the check no longer passes:\n{output}"
