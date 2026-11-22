"""The public build's rules: exclusions, data classes, the scanners, and determinism.

Most tests pin a pure rule from both sides: a scanner fires on its target and stays
silent on the complement. The instruction tests pin the two cases earlier scans missed,
a quotation that crosses a line break and one taken from the middle of an instruction.
The determinism test builds the tree twice from HEAD; it needs AppWorld's installed apps
and data, so it carries the `appworld` marker.

The build's private inputs, `scripts/public_templates/`, live only in the archive (K-205).
Nothing here loads them at import. The tests that need them skip with `NO_TEMPLATES` as
the reason when the directory is absent, which is the case in the public tree.
"""

from __future__ import annotations

import importlib.util
import io
import json
import pathlib
import re
import subprocess
import sys
import zipfile

import pytest

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPOSITORY / "scripts"
TEMPLATES = SCRIPTS / "public_templates"
NO_TEMPLATES = (
    "scripts/public_templates/ is absent; the public build's private inputs are kept only "
    "in the archive (K-205)"
)


def _load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


build = _load("build_public_tree", SCRIPTS / "build_public_tree.py")

NEVER = re.compile(r"(?!x)x")
INSTRUCTION = (
    "Book a table for two at the place my friend liked, then send her the address "
    "and the time by text message before noon."
)


def _detectors(**overrides):
    fields = {"routes": [NEVER, NEVER, NEVER], "apis": None, "windows": {}, "short": {}}
    fields.update(overrides)
    return build.Detectors(**fields)


def _instruction_detectors(instructions: dict[str, str]):
    windows, short = build.instruction_windows(instructions)
    return _detectors(windows=windows, short=short)


def test_fold_maps_turkish_letters_case_and_whitespace():
    assert build.fold("ÇĞİÖŞÜ  çğıöşü") == "cgiosu cgiosu"
    assert build.fold("A \n\t B") == "a b"


def test_names_match_whole_words_across_case_letters_and_paths(tmp_path):
    names_file = tmp_path / "names.txt"
    names_file.write_text("# comment\nZörbel Kanzu\nQıx\n", encoding="utf-8")
    names = build.load_names(names_file)
    files = {
        "a.md": b"visited ZORBEL\n  KANZU yesterday",
        "b.md": b"zorbelkanzu and qixel stay silent",
        "c.md": b"the Qix lab",
        "Qix/notes.txt": b"nothing here",
    }
    found = build.scan(files, names, _detectors())["names"]
    assert {(hit["path"], hit["in"]) for hit in found} == {
        ("a.md", "content"),
        ("c.md", "content"),
        ("Qix/notes.txt", "path"),
    }


def test_binary_files_are_scanned_as_bytes(tmp_path):
    names_file = tmp_path / "names.txt"
    names_file.write_text("Zörbel Kanzu\n", encoding="utf-8")
    found = build.scan(
        {"blob.png": b"\x80\x00ZORBEL KANZU\x00\x89"}, build.load_names(names_file), _detectors()
    )["names"]
    assert [hit["path"] for hit in found] == ["blob.png"]


def test_wheel_members_are_scanned_and_allowlisted_by_sha256(tmp_path):
    names_file = tmp_path / "names.txt"
    names_file.write_text("Zörbel Kanzu\n", encoding="utf-8")
    names = build.load_names(names_file)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("pkg/clean.py", "x = 1\n")
        archive.writestr("pkg/notes.txt", "written by Zorbel Kanzu\n")
    wheel = buffer.getvalue()
    hits = build.scan({"vendor/p.whl": wheel}, names, _detectors())["names"]
    assert [(h["path"], h["member"]) for h in hits] == [("vendor/p.whl", "pkg/notes.txt")]
    entry = {"path": "vendor/p.whl", "member": "pkg/notes.txt", "sha256": hits[0]["sha256"]}
    allowed, failing = build.split_allowed(hits, [entry])
    assert (len(allowed), len(failing)) == (1, 0)
    allowed, failing = build.split_allowed(hits, [{**entry, "sha256": "0" * 64}])
    assert (len(allowed), len(failing)) == (0, 1)
    top_level = [{**hits[0], "member": None}]
    assert build.split_allowed(top_level, [entry]) == ([], top_level)


def test_ciphertext_is_not_word_scanned_and_every_other_binary_is(tmp_path):
    # A planted three-letter acronym, an assistant-like word and an instruction window,
    # the way random ciphertext bytes can spell them.
    names_file = tmp_path / "names.txt"
    names_file.write_text("QXV\n", encoding="utf-8")
    names = build.load_names(names_file)
    synthetic = re.compile(r"zorkbot", re.IGNORECASE)
    detectors = _instruction_detectors({"t_1": INSTRUCTION})
    planted = b"\x8f\x02\xa7 QXV \x91 zorkbot \x10" + INSTRUCTION.encode() + b"\xfe"
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("pkg/.source/apps.bundle", planted)
        archive.writestr("pkg/notes.bin", planted)
    files = {
        build.BUNDLE_PATH: planted,
        "vendor/other.bundle": planted,
        "assets/logo.png": planted,
        "vendor/p.whl": buffer.getvalue(),
    }
    found = build.scan(files, names, detectors, assistant=synthetic)
    scanned = [("assets/logo.png", None), ("vendor/p.whl", "pkg/notes.bin")]
    for key in ("names", "assistant", "instructions"):
        assert sorted((h["path"], h["member"]) for h in found[key]) == scanned, key
    assert sorted((h["path"], h["member"]) for h in found["ciphertext"]) == [
        (build.BUNDLE_PATH, None),
        ("vendor/other.bundle", None),
        ("vendor/p.whl", "pkg/.source/apps.bundle"),
    ]
    # The path of a ciphertext file is plain text and is still scanned.
    renamed = build.scan({"QXV/derived.bundle": planted}, names, detectors, assistant=synthetic)
    assert [(h["path"], h["in"]) for h in renamed["names"]] == [("QXV/derived.bundle", "path")]


def test_a_name_in_a_packed_input_fails_the_build_before_packing(tmp_path, monkeypatch):
    names_file = tmp_path / "names.txt"
    names_file.write_text("Zörbel Kanzu\n", encoding="utf-8")
    names = build.load_names(names_file)
    synthetic = re.compile(r"zorkbot", re.IGNORECASE)
    packed = []
    monkeypatch.setattr(build, "pack", lambda files, bundle: packed.append(sorted(files)) or [])
    bundle = tmp_path / "derived.bundle"
    clean = {"results/a.json": b'{"route": "/spotify/login"}'}
    for planted in (b'{"note": "ZORBEL KANZU"}', b'{"note": "ZorkBot wrote this"}'):
        with pytest.raises(build.BuildError, match="nothing was packed"):
            build.seal({**clean, "results/b.json": planted}, names, _detectors(), bundle, synthetic)
    assert packed == []
    # Task text is not a hit: carrying it encrypted is what the bundle is for.
    with_task = {**clean, "results/c.json": INSTRUCTION.encode()}
    build.seal(with_task, names, _instruction_detectors({"t_1": INSTRUCTION}), bundle, synthetic)
    assert packed == [sorted(with_task)]


def test_assistant_scan_fires_on_its_pattern_and_not_on_ordinary_words():
    synthetic = re.compile(r"zorkbot|co-zx-by", re.IGNORECASE)
    found = build.scan(
        {"a.md": b"Co-ZX-By: someone", "b.md": b"ZorkBot wrote", "c.md": b"plain text"},
        [],
        _detectors(),
        assistant=synthetic,
    )["assistant"]
    assert [hit["path"] for hit in found] == ["a.md", "b.md"]


def test_the_scanner_carries_no_assistant_name_in_plain_text():
    words = build.assistant_words()
    assert len(words) == len(build.ASSISTANT_ROT13) == 7
    assert build.ASSISTANT.pattern.count("|") == 6
    assert all(build.ASSISTANT.search(f"x {w.upper()} y") for w in words)
    for path in (SCRIPTS / "build_public_tree.py", pathlib.Path(__file__)):
        source = path.read_bytes().lower()
        assert not [w for w in words if w.encode() in source], path.name


def test_kind_follows_suffix_and_place():
    assert build.kind_of("results/x.json") == "data"
    assert build.kind_of("config/a.yaml") == "data"
    assert build.kind_of(".github/workflows/ci.yml") == "code"
    assert build.kind_of("docs/a.md") == "doc"
    assert build.kind_of("src/zihin/schema.sql") == "code"
    assert build.kind_of("vendor/appworld/x.whl") == "binary"


def test_exclusions_report_every_rule_even_when_nothing_matched():
    entries = [
        build.Entry("docs/private.md", "100644", b""),
        build.Entry("results/a.sqlite", "100644", b""),
        build.Entry("scripts/public_templates/n.txt", "100644", b""),
        build.Entry("x/.cache/y", "100644", b""),
        build.Entry("ignored.log", "100644", b""),
        build.Entry("kept.py", "100644", b""),
    ]
    rules = {
        "paths": [{"path": "docs/private.md", "reason": "r"}],
        "suffixes": [{"suffix": ".sqlite", "reason": "r"}, {"suffix": ".nothing", "reason": "r"}],
        "prefixes": [{"prefix": "scripts/public_templates/", "reason": "r"}],
        "path_parts": [{"part": ".cache", "reason": "r"}],
    }
    kept, applied = build.apply_exclusions(entries, rules, {"ignored.log"})
    assert [e.path for e in kept] == ["kept.py"]
    matched = {row["rule"]: row["matched"] for row in applied}
    assert matched["suffix .nothing"] == []
    assert matched["the commit's .gitignore"] == ["ignored.log"]
    assert len(applied) == 6


def test_a_missing_patch_anchor_fails_the_build(tmp_path):
    (tmp_path / "a.py").write_text("keep = 1\n", encoding="utf-8")
    patches = [{"path": "a.py", "old": "drop = 2\n", "new": "", "reason": "r"}]
    with pytest.raises(build.BuildError, match="matched 0 times"):
        build.patch(tmp_path, patches)
    patches[0]["old"] = "keep = 1\n"
    applied = build.patch(tmp_path, patches)
    assert applied == [{"path": "a.py", "removed": ["keep = 1"], "added": 0, "reason": "r"}]


def test_a_patch_that_inserts_reports_what_it_added(tmp_path):
    (tmp_path / "a.md").write_text("intro\n\n## next\n", encoding="utf-8")
    patches = [{"path": "a.md", "old": "intro\n", "new": "intro\n\nmirror note\n", "reason": "r"}]
    assert build.patch(tmp_path, patches) == [
        {"path": "a.md", "removed": [], "added": 2, "reason": "r"}
    ]
    assert (tmp_path / "a.md").read_text(encoding="utf-8") == "intro\n\nmirror note\n\n## next\n"


def test_provenance_writes_one_line_in_the_singular_and_every_other_count_in_the_plural(
    tmp_path, monkeypatch
):
    # A stand-in template that carries only the patch list, so this runs without
    # scripts/public_templates/ as well.
    (tmp_path / "PROVENANCE.md").write_text("$patches\n", encoding="utf-8")
    monkeypatch.setattr(build, "TEMPLATES", tmp_path)
    context = {
        "commit": "c",
        "measured_commit": "m",
        "script_sha256": "s",
        "appworld": {"version": "v", "commit": "a"},
        "bundled_count": 0,
        "manifest_sha256": "h",
        "exclusions": [],
        "written": [],
        "allowlist": [],
        "patches": [
            {"path": "a.py", "removed": ["x"], "added": 0, "reason": "r."},
            {"path": "b.py", "removed": [], "added": 1, "reason": "r."},
            {"path": "c.py", "removed": ["x", "y"], "added": 11, "reason": "r."},
            {"path": "d.py", "removed": ["x"] * 11, "added": 2, "reason": "r."},
        ],
    }
    heads = [
        line for line in build.render_provenance(context).splitlines() if line.startswith("- `")
    ]
    assert heads == [
        "- `a.py`, 1 line removed, 0 lines added. r.",
        "- `b.py`, 0 lines removed, 1 line added. r.",
        "- `c.py`, 2 lines removed, 11 lines added. r.",
        "- `d.py`, 11 lines removed, 2 lines added. r.",
    ]


def test_the_appworld_wheels_do_not_reach_the_public_tree():
    # The wheels come from the mirror's provenance file, which both trees carry, and from
    # what git tracks here: the archive tracks the wheels, the public tree does not.
    provenance = json.loads(
        (REPOSITORY / "vendor/appworld/PROVENANCE.json").read_text(encoding="utf-8")
    )
    named = {f"vendor/appworld/{wheel['file']}" for wheel in provenance["wheels"]}
    assert len(named) == 2
    listed = subprocess.run(
        ["git", "ls-files", "-z", "vendor/appworld/"],
        cwd=REPOSITORY,
        capture_output=True,
        check=True,
    ).stdout.decode()
    paths = sorted(named | {p for p in listed.split("\0") if p})
    entries = [build.Entry(p, "100644", b"") for p in paths]
    kept, _ = build.apply_exclusions(entries, build.EXCLUSIONS, set())
    assert {e.path for e in kept} == {
        "vendor/appworld/README.md",
        "vendor/appworld/PROVENANCE.json",
    }


def test_route_shapes_fire_and_their_complements_stay_silent():
    table = {"spotify": [(None, "/library/songs/{song_id}", None), (None, "/liked_songs", None)]}
    detectors = _detectors(routes=build.route_patterns(table))
    assert detectors.route_hits("DELETE /spotify/library/songs/101") == 1
    assert detectors.route_hits("spotify.library/songs/{song_id}") == 1
    assert detectors.route_hits("a bare library/songs/{song_id} template") == 1
    assert detectors.route_hits('"path": "/liked_songs"') == 1
    assert detectors.route_hits("liked_songs as a word") == 0
    assert detectors.route_hits("x/library/songs/{song_id}") == 0


def test_api_markers_need_a_pair_from_the_api_list():
    pattern = build.api_pattern({("spotify", "login"), ("api_docs", "show_api_doc")})
    detectors = _detectors(apis=pattern)
    assert detectors.api_hits("calls spotify.login once") == 1
    assert detectors.api_hits("apis.api_docs.show_api_doc(app_name='x')") == 1
    assert detectors.api_hits("xspotify.login and spotify.loginx") == 0
    # The case of results/sandbox-olcum.json: a Python attribute path, not an API.
    assert detectors.api_hits("apis.api_docs.requester") == 0


def test_instruction_quoted_from_the_middle_is_found():
    detectors = _instruction_detectors({"t_1": INSTRUCTION})
    middle = "the place my friend liked, then send her the address"
    assert len(build.words_only(middle)) >= build.WINDOW
    assert detectors.instruction_hits(f'She wrote: "{middle}" in the note.') == ["t_1"]
    assert detectors.instruction_hits("the place my friend liked, then") == []


def test_instruction_found_across_line_breaks_quotes_and_bold():
    detectors = _instruction_detectors({"t_1": INSTRUCTION})
    assert detectors.instruction_hits("Book a table for two\nat the place my friend said") == [
        "t_1"
    ]
    assert detectors.instruction_hits("> Book a table for two\n> at the place my friend") == ["t_1"]
    assert detectors.instruction_hits("Book a **table** for two, at the place my friend") == ["t_1"]
    assert detectors.instruction_hits("Book a chair for two at the place my friend") == []


def test_a_short_instruction_is_matched_whole():
    detectors = _instruction_detectors({"t_2": "How many songs are in my queue?"})
    assert detectors.short == {"how many songs are in my queue": ("t_2",)}
    assert detectors.instruction_hits("Q: how many songs are in my queue") == ["t_2"]
    assert detectors.instruction_hits("how many songs are in my library") == []


def test_a_window_shared_by_two_tasks_reports_both():
    shared = "Book a table for two at the place my friend liked"
    detectors = _instruction_detectors(
        {"t_1": f"{shared}, then text her.", "t_2": f"{shared} and pay the deposit now."}
    )
    window = build.words_only(shared)[: build.WINDOW]
    assert detectors.windows[window] == ("t_1", "t_2")
    assert detectors.instruction_hits(f"She wrote: {shared}.") == ["t_1", "t_2"]
    assert detectors.instruction_hits("the place my friend liked and pay the deposit now") == [
        "t_2"
    ]
    assert detectors.instruction_hits("a chair for two at the place my friend liked") == []


def test_turkish_only_is_an_unpaired_markdown_file_in_turkish():
    turkish = "Bu belge yalnız Türkçe; ağaçtaki öbür belgelerle eşleşmiyor ve şöyle yazılmış."
    english = "This document is in English and has no counterpart in the other language."
    files = {
        "README.md": english.encode(),
        "README.tr.md": turkish.encode(),
        "REPRODUCE.md": english.encode(),
        "REPRODUCE.tr.md": turkish.encode(),
        "docs/01-a.tr.md": turkish.encode(),
        "docs/01-a.en.md": english.encode(),
        "docs/reports/report.md": turkish.encode(),
        "docs/08-decisions.tr.md": turkish.encode(),
        "PROVENANCE.md": (english * 20 + " ığş").encode(),
        "notes.md": english.encode(),
        "scripts/x.py": turkish.encode(),
    }
    assert build.turkish_only(files) == ["docs/08-decisions.tr.md", "docs/reports/report.md"]
    # The threshold, from both sides: 20 per mille is Turkish, 19 is not.
    at = "ğ" * 20 + "a" * 980
    below = "ğ" * 19 + "a" * 981
    assert build.turkish_only({"at.md": at.encode(), "below.md": below.encode()}) == ["at.md"]


def test_a_skip_belongs_to_one_of_four_groups_or_the_measurement_fails():
    reasons = [
        "scripts/public_templates/ is absent; kept only in the archive (K-205)",
        "results/zihin.sqlite is absent: restore it with scripts/restore_records.py, "
        "or take a run with scripts/record_run.py",
        "results/zihin-3.sqlite is absent: restore it with scripts/restore_records.py",
        "no git history here: a shallow checkout",
        "experiments/outputs holds no api_calls.jsonl log: the runs are untracked",
    ]
    assert [build.skip_group(reason) for reason in reasons] == [0, 1, 1, 2, 3]
    # A record skip that does not name the restore script is no longer an expected skip.
    for reason in (
        "podman is not installed",
        "the record is not tracked",
        "results/zihin-3.sqlite is not in this checkout",
        "results/zihin.sqlite is absent. Set MODEL_SERVER_URL and run "
        "`uv run python scripts/record_run.py` first.",
        "results/zihin-3.sqlite is absent: restore it with scripts/restore_records.py, or not",
    ):
        with pytest.raises(build.BuildError, match="none of the expected groups"):
            build.skip_group(reason)


def test_a_changed_file_makes_the_measurement_stale():
    files = {"src/a.py": b"x = 1\n", "README.md": b"rendered", build.BUNDLE_PATH: b"\x00"}
    measured = build.fingerprint(files)
    assert set(measured) == {"src/a.py"}
    rerendered = {**files, "README.md": b"rendered again", build.BUNDLE_PATH: b"\x01"}
    assert build.stale_paths(measured, build.fingerprint(rerendered)) == []
    changed = {**files, "src/a.py": b"x = 2\n", "tests/test_b.py": b""}
    assert build.stale_paths(measured, build.fingerprint(changed)) == [
        "src/a.py",
        "tests/test_b.py",
    ]


@pytest.mark.skipif(not TEMPLATES.is_dir(), reason=NO_TEMPLATES)
def test_the_experiment_status_comes_from_the_count():
    databases = [{"path": f"results/{n}.sqlite"} for n in ("a", "b", "c")]
    none = {"count": 0, "databases": databases, "conditions": [], "runs": 0, "tasks": 0}
    some = {**none, "count": 12, "runs": 2, "tasks": 6, "conditions": ["baseline"]}
    assert "No experiment cell has completed" in build.experiment_status(none, "en")
    for language in ("en", "tr"):
        opening = build.phrases(language)["status_none"].split("**")[1]
        assert opening in build.experiment_status(none, language)
        text = build.experiment_status(some, language)
        assert "12" in text and "`baseline`" in text and opening not in text


MEASURED = {
    "experiment_episodes": {
        "count": 0,
        "databases": [{"path": "results/zihin.sqlite"}],
        "conditions": [],
        "runs": 0,
        "tasks": 0,
    },
    "public_tests": {
        "commit": "a" * 40,
        "collected": 10,
        "passed": 6,
        "skipped": [
            {"test": "tests/t.py::a", "reason": "scripts/public_templates/ is absent"},
            {
                "test": "tests/t.py::b",
                "reason": "results/zihin.sqlite is absent: "
                "restore it with scripts/restore_records.py",
            },
            {"test": "tests/t.py::c", "reason": "no git history here"},
            {"test": "tests/t.py::d", "reason": "experiments/outputs holds no log"},
        ],
    },
    "public_tests_restored": {
        "commit": "a" * 40,
        "collected": 10,
        "passed": 9,
        "skipped": [
            {"test": "tests/t.py::a", "reason": "scripts/public_templates/ is absent"},
        ],
    },
}
# The owner's wording, kept as data: the Turkish half is document text, not code.
METHOD = json.loads(
    (REPOSITORY / "tests/data/readme-method-sentences.json").read_text(encoding="utf-8")
)


@pytest.mark.skipif(not TEMPLATES.is_dir(), reason=NO_TEMPLATES)
@pytest.mark.parametrize("language", ["en", "tr"])
def test_the_readmes_render_every_count_and_the_method_sentence(language):
    tests = MEASURED["public_tests"]
    values = {
        "experiment_status": build.experiment_status(MEASURED["experiment_episodes"], language),
        "limitations": 81,
        "decisions": 206,
        "tests_commit": tests["commit"][:7],
        **build.outcome_values(tests, language),
        **build.outcome_values(MEASURED["public_tests_restored"], language, "_restored"),
        "turkish_count": 2,
        "turkish_list": "- `a.md`\n- `b.md`",
    }
    text = build.render(f"README.{language}.md", values)
    flat = " ".join(text.split())
    assert METHOD[language] in flat
    for group in build.phrases(language)["groups"]:
        assert group in text
    assert " 81 " in flat and " 206 " in flat
    # Both outcomes: the as-built table lists four skips, the restored one only the first.
    assert " 6 " in flat and " 9 " in flat
    assert text.count("`tests/t.py::a`") == 2 and text.count("`tests/t.py::b`") == 1
    assert "uv run python scripts/restore_records.py <" in text
    assert "(https://github.com/yusuferengerek/zihin/releases)" in text
    # The measurement commit is in PROVENANCE, not in the sentence (owner, 15 Nov 2026).
    assert "aaaaaaa" not in text
    assert text.splitlines()[2] == "# zihin"
    clone = "git clone https://github.com/yusuferengerek/zihin.git zihin\ncd zihin\n"
    assert clone in text
    other = "README.tr.md" if language == "en" else "README.md"
    assert f"({other})" in text


@pytest.mark.skipif(not TEMPLATES.is_dir(), reason=NO_TEMPLATES)
def test_the_public_ci_is_the_archives_with_its_patches(tmp_path):
    import yaml

    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        (REPOSITORY / ".github/workflows/ci.yml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    patches = json.loads((TEMPLATES / "patches.json").read_text(encoding="utf-8"))["patches"]
    build.patch(tmp_path, [p for p in patches if p["path"] == ".github/workflows/ci.yml"])
    ci = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    assert ci["permissions"] == {"contents": "read"}
    assert len(ci["jobs"]) == 5
    names = {job: [s.get("name", "") for s in ci["jobs"][job]["steps"]] for job in ci["jobs"]}
    runs = [s.get("run", "") for job in ci["jobs"].values() for s in job["steps"]]
    assert not any("build_public_tree" in run for run in runs)
    assert "Public build gates" not in sum(names.values(), [])
    test = names["test"]
    unpack = "Unpack the AppWorld-derived data"
    assert test.index(unpack) < test.index("pytest")
    assert test.index("Install gitleaks") < test.index("Scan the repository with gitleaks")
    scan = ci["jobs"]["test"]["steps"][test.index("Scan the repository with gitleaks")]["run"]
    assert scan.startswith("gitleaks git ") and "--exit-code 1" in scan
    assert ci["jobs"]["test"]["steps"][0]["with"] == {"fetch-depth": 0}
    sandbox = names["sandbox"]
    assert sandbox.index(unpack) < sandbox.index("Güvenlik testleri")


# Where each Colab file states the repository it clones or pushes to by default.
COLAB_DEFAULTS = {
    "experiments/colab/zihin-colab.ipynb": re.compile(
        r'os\.environ\.get\(\s*"ZIHIN_REPO_SLUG"\s*,\s*"([^"]+)"\s*\)'
    ),
    "scripts/colab_publish_results.sh": re.compile(r"\$\{ZIHIN_REPO_SLUG:-([^}]+)\}"),
}


def _code(path: str, text: str) -> str:
    if path.endswith(".ipynb"):
        return "".join("".join(cell["source"]) for cell in json.loads(text)["cells"])
    return text


@pytest.mark.skipif(not TEMPLATES.is_dir(), reason=NO_TEMPLATES)
def test_the_colab_defaults_name_the_archive_here_and_this_repository_in_public(tmp_path):
    # After the owner renames the archive, yusuferengerek/zihin is the public repository,
    # so the archive's defaults name zihin-archive and the build turns them back (K-205).
    patches = json.loads((TEMPLATES / "patches.json").read_text(encoding="utf-8"))["patches"]
    for path, default in COLAB_DEFAULTS.items():
        archive = (REPOSITORY / path).read_text(encoding="utf-8")
        assert default.findall(_code(path, archive)) == ["yusuferengerek/zihin-archive"], path
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(archive, encoding="utf-8")
        build.patch(tmp_path, [p for p in patches if p["path"] == path])
        public = target.read_text(encoding="utf-8")
        assert default.findall(_code(path, public)) == ["yusuferengerek/zihin"], path


@pytest.mark.skipif(not TEMPLATES.is_dir(), reason=NO_TEMPLATES)
def test_unpack_manifest_refuses_paths_outside_the_repository(tmp_path):
    unpack = _load("unpack_derived_template", TEMPLATES / "unpack_derived.py")
    manifest = tmp_path / "MANIFEST.json"
    manifest.write_text(json.dumps({"files": [{"path": "../x", "sha256": "0"}]}))
    with pytest.raises(unpack.RestoreError, match="escapes"):
        unpack.read_manifest(manifest)
    manifest.write_text(json.dumps({"files": [{"path": "a"}]}))
    with pytest.raises(unpack.RestoreError, match="malformed"):
        unpack.read_manifest(manifest)


@pytest.mark.appworld
@pytest.mark.skipif(not TEMPLATES.is_dir(), reason=NO_TEMPLATES)
def test_two_builds_of_one_commit_differ_only_in_the_bundle(tmp_path):
    data = REPOSITORY / "data"
    if not (data / "datasets").is_dir():
        pytest.skip("AppWorld data is not downloaded")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPOSITORY, capture_output=True, text=True, check=True
    ).stdout.strip()
    detectors = build.build_detectors(data)
    trees = []
    for name in ("first", "second"):
        out = tmp_path / name
        build.produce(commit, out, detectors)
        trees.append(
            {
                p.relative_to(out).as_posix(): (p.read_bytes(), p.stat().st_mode)
                for p in sorted(out.rglob("*"))
                if p.is_file()
            }
        )
    first, second = trees
    assert set(first) == set(second)
    different = sorted(path for path in first if first[path] != second[path])
    assert different in ([], [build.BUNDLE_PATH])
