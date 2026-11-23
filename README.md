*[Türkçe](README.tr.md)*

# zihin

Yusuf Eren GEREK

A research harness for skill and failure memory experiments on AppWorld. *Zihin* is
Turkish for mind. This repository is the public mirror of a private archive, and
[PROVENANCE.md](PROVENANCE.md) records how it was built.

This is not a product repository. Extra abstraction, extra configuration and extra
layers of independence are deliberately absent.

## The question

Do compiled skills and an explicit failure index lower the number of model calls
needed to solve held-out tasks? This is the one confirmatory test, and it runs in a
single cell: the
mechanisms-on condition against the baseline, on the model-call metric, on the unseen
subset, two-sided, with `qwen2.5-coder:32b-instruct-q4_K_M` as the primary cell's
model since the addendum of 25 September 2026. A second, exploratory question asks
whether the effect systematically disappears within the model sizes examined. Both
are stated in [docs/02-research-question.en.md](docs/02-research-question.en.md), and
the design is in [docs/05-experiment-design.en.md](docs/05-experiment-design.en.md).

## Status

**The mechanisms are built.** The skill compiler, the failure index, the retriever,
the shield and the sandbox exist, run on the production path, and are measured in
`PILOT_REPORT.md` (in Turkish).

**The precondition gate fired on the original local axis.** Qwen2.5-Coder 1.5B, 3B
and 7B each solved 0 of the same thirty AppWorld tasks. The finding rests on three
runs, two of them ceiling-limited and one not in the record (S-63).

**A boundary control showed that the zeros come from the model, not from the
apparatus.** On the same thirty tasks DeepSeek V4 Flash 0731, run as
`openrouter/deepseek/deepseek-v4-flash-0731`, scored 20/30 on this pipeline.
The design declared that run with thinking off, but it was made with thinking on, so
the number belongs to a thinking model. It still answers the control's question,
whether any model can succeed on this pipeline (S-34).

**The primary cell moved to 32B.** `qwen2.5-coder:32b-instruct-q4_K_M`, served by
Ollama on a Colab A100 (preregistration A.2, addendum of 25 September 2026), solved
11/30. Twenty-five of the thirty tasks require changing the world, and on those it
solved 7/25. That is the band in which the mechanisms can be tested.

**The experiment is defined and has not run.** Its conditions are frozen in section
19.6 of the setup protocol and in the preregistration's addenda. The driver,
`scripts/run_experiment.py`, runs phase 1 slice by slice on the action stratum's 104
tasks: three conditions (`baseline`, `skills_failures` and `irrelevant_retrieval`) times
three seeds on the 103 covered tasks, and the baseline alone three times on `8ce6779_3`,
930 episodes in all.

**No experiment cell has completed.** The archive's 3 local record databases hold no episode under the experiment's run prefix, `dny`. They were counted when this tree's measurement was taken. No slice has run on Colab either.

**The end-to-end demo's behaviour claim was retracted.** The demo reported that the
carded arm reached a successful effect where the card-free arm did not. Run with three
repeats, eleven of the fifteen cells (five tasks, three arms) disagree across repeats,
and the card-free arm reaches the effect in six of its fifteen episodes (five tasks,
three repeats each). The entry claim, that the cards enter the
prompt byte for byte, is unaffected and stands. Detail in
`docs/reports/uc-kollu-kart-kosusu.md` (in Turkish).

**The mirror finding, and its bound.** The skill library and the failure index were
mined from two independent corpora and converged on the same mechanical bottleneck:
the library teaches how to get the authentication token, and the index forbids
calling without carrying it. Getting past that bottleneck is not enough, though. In
the three-arm run the token was obtained in each arm while completion was 0/45, so
the place the mechanisms converged on is not where the task gets solved (S-57).

The limits named here by number are in
[docs/09-limitations.en.md](docs/09-limitations.en.md).

## Method

The contribution beyond the mechanisms is how the measurements are kept honest. The
setup protocol names the faults that cut a measurement silently and turns each one
into a rule, together with the measured incident that produced it
([experiments/setup-protocol.en.md](experiments/setup-protocol.en.md), section 6 and
the rules after it). The rules are enforced by guards: the `check_*` scripts and the
`--check` modes of the scripts that generate a view, run in CI and by
`scripts/local_checks.sh`. A guard is accepted only after it has been seen to fire
on the fault it exists for: the fault is put back by a deliberate edit, a mutation,
and the guard has to refuse it (K-49). Limits and decisions are kept as dated
records: 83 limitations in
[docs/09-limitations.en.md](docs/09-limitations.en.md) and 207 decisions in
`docs/08-decisions.tr.md` (in Turkish).

The code was written with an AI coding agent under the author's direction. Every
change was reviewed by the author through pull requests, tests and guards.

## Reproduce

The full installation, with its prerequisites, Git LFS among them, is in
[REPRODUCE.md](REPRODUCE.md). The short form:

```bash
git clone https://github.com/yusuferengerek/zihin.git zihin
cd zihin
uv sync --all-groups --frozen
uv run appworld install
uv run appworld download data
uv run python scripts/unpack_derived.py
uv run pytest -m "not model_server and not sandbox"
```

`scripts/unpack_derived.py` restores the AppWorld-derived data files from
`derived/appworld-derived.bundle` to their original paths and checks each one against
`derived/MANIFEST.json`.

### The record databases

The four record databases are not in the tree. They are published as encrypted assets
in this repository's [releases](https://github.com/yusuferengerek/zihin/releases), one
`.bundle` file per database. Download the four files into one directory and restore
them:

```bash
uv run python scripts/restore_records.py <directory with the downloaded assets>
```

The script opens each asset with the installed `appworld unpack`, checks the restored
file's size and sha256 against `records/MANIFEST.json`, and only then writes it under
`results/`. It refuses a path outside the repository and never overwrites a file whose
sha256 differs. It works with the git-pinned `appworld` 0.2.0.dev0 and with the PyPI
release 0.1.3.post1.

**What a correct run looks like.** Both outcomes below were measured on this tree.

Without the record databases, after the commands above: 815 tests are
collected, 797 pass, 18 are skipped and none fail. The 18 skips
are expected and fall into 4 groups:

| Group | Test | Reason |
|---|---|---|
| private templates | `tests/test_build_public_tree.py::test_the_colab_defaults_name_the_archive_here_and_this_repository_in_public` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| private templates | `tests/test_build_public_tree.py::test_the_experiment_status_comes_from_the_count` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| private templates | `tests/test_build_public_tree.py::test_the_public_ci_is_the_archives_with_its_patches` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| private templates | `tests/test_build_public_tree.py::test_the_readmes_render_every_count_and_the_method_sentence[en]` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| private templates | `tests/test_build_public_tree.py::test_the_readmes_render_every_count_and_the_method_sentence[tr]` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| private templates | `tests/test_build_public_tree.py::test_two_builds_of_one_commit_differ_only_in_the_bundle` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| private templates | `tests/test_build_public_tree.py::test_unpack_manifest_refuses_paths_outside_the_repository` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| record databases | `tests/test_experiment_sets.py::test_the_committed_sets_are_what_the_slots_give_today` | results/zihin-3.sqlite is absent: restore it with scripts/restore_records.py |
| record databases | `tests/test_library_source.py::test_the_guard_passes_on_the_declared_pair` | results/zihin-3.sqlite is absent: restore it with scripts/restore_records.py |
| record databases | `tests/test_library_source.py::test_the_guard_refuses_a_library_that_is_not_the_declared_one` | results/zihin-3.sqlite is absent: restore it with scripts/restore_records.py |
| record databases | `tests/test_library_source.py::test_the_library_is_where_the_constant_says_it_is` | results/zihin-3.sqlite is absent: restore it with scripts/restore_records.py |
| record databases | `tests/test_recorded_run.py::test_actions_carry_full_raw_parameters` | results/zihin.sqlite is absent: restore it with scripts/restore_records.py, or take a run with scripts/record_run.py |
| record databases | `tests/test_recorded_run.py::test_at_least_one_step_produced_multiple_actions` | results/zihin.sqlite is absent: restore it with scripts/restore_records.py, or take a run with scripts/record_run.py |
| record databases | `tests/test_recorded_run.py::test_episode_carries_load_state_and_sequence` | results/zihin.sqlite is absent: restore it with scripts/restore_records.py, or take a run with scripts/record_run.py |
| record databases | `tests/test_recorded_run.py::test_run_manifest_records_the_verified_context_window` | results/zihin.sqlite is absent: restore it with scripts/restore_records.py, or take a run with scripts/record_run.py |
| record databases | `tests/test_recorded_run.py::test_whole_episode_reads_back_in_order` | results/zihin.sqlite is absent: restore it with scripts/restore_records.py, or take a run with scripts/record_run.py |
| single-commit history | `tests/test_dates.py::test_a_correction_note_naming_the_right_commit_rescues` | no git history here: a shallow checkout, or the CI simulation's copy, which carries the tracked files without `.git`. The sweep reads the record and belongs to `local_checks.sh` for exactly this reason. |
| untracked AppWorld run outputs | `tests/test_api_routes.py::test_the_whole_local_corpus_resolves` | experiments/outputs holds no api_calls.jsonl log: the recorded AppWorld runs are untracked and are not in this checkout |

With the four record databases restored: 815 tests are collected,
806 pass, 9 are skipped and none fail. The
9 remaining skips fall into 3 groups:

| Group | Test | Reason |
|---|---|---|
| private templates | `tests/test_build_public_tree.py::test_the_colab_defaults_name_the_archive_here_and_this_repository_in_public` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| private templates | `tests/test_build_public_tree.py::test_the_experiment_status_comes_from_the_count` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| private templates | `tests/test_build_public_tree.py::test_the_public_ci_is_the_archives_with_its_patches` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| private templates | `tests/test_build_public_tree.py::test_the_readmes_render_every_count_and_the_method_sentence[en]` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| private templates | `tests/test_build_public_tree.py::test_the_readmes_render_every_count_and_the_method_sentence[tr]` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| private templates | `tests/test_build_public_tree.py::test_two_builds_of_one_commit_differ_only_in_the_bundle` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| private templates | `tests/test_build_public_tree.py::test_unpack_manifest_refuses_paths_outside_the_repository` | scripts/public_templates/ is absent; the public build's private inputs are kept only in the archive (K-205) |
| single-commit history | `tests/test_dates.py::test_a_correction_note_naming_the_right_commit_rescues` | no git history here: a shallow checkout, or the CI simulation's copy, which carries the tracked files without `.git`. The sweep reads the record and belongs to `local_checks.sh` for exactly this reason. |
| untracked AppWorld run outputs | `tests/test_api_routes.py::test_the_whole_local_corpus_resolves` | experiments/outputs holds no api_calls.jsonl log: the recorded AppWorld runs are untracked and are not in this checkout |

Any other skip, or any failure, means the run is not the expected one.

## AppWorld data

AppWorld's data license requires that any public redistribution of its protected
portion, or of derivatives of it, be encrypted. The data files derived from AppWorld
therefore ship in `derived/appworld-derived.bundle`, packed with AppWorld's own
`pack_bundle`, and the record databases are published only as encrypted release
assets, restored as described under "The record databases" above. Bundles produced by
the pinned version's `pack_bundle` open with both the PyPI release `appworld`
0.1.3.post1 and the git-pinned 0.2.0.dev0. This was verified on a harmless test bundle
and on the four record assets: every unpacked file matched its sha256.

The two AppWorld wheels that the archive keeps as an install fallback are not in this
repository. They are held in the private archive. Their source, the pinned commit and
each wheel's sha256 are in [vendor/appworld/README.md](vendor/appworld/README.md).

## Language

The CI job names, the container file and the comments in the configuration files
(`.github/workflows/ci.yml`, `Containerfile`, `config/*.yaml`) are in Turkish. Those
files are frozen until the experiment completes, and they will be translated in the
sync that follows it. The documents listed at the end of this page exist only in
Turkish.

## Provenance

This repository is built by a script from a private archive, which stays the system
of record. No history is carried over. [PROVENANCE.md](PROVENANCE.md) names the
archive commit, the build script and its hash, what was excluded and why, and every
edit and file made for this tree only. Each commit here names the archive commit it
mirrors. The `code_commit` keys inside the record databases refer to the archive, and
the archive is available to reviewers on request.

## Turkish-only documents

These 40 documents exist only in Turkish. The list is generated from the
tree: a Markdown file with no English counterpart whose text is Turkish.

- `CHANGELOG.md`
- `PILOT_REPORT.md`
- `PROJECT_STATUS.md`
- `PULL_REQUESTS.md`
- `docs/08-decisions.tr.md`
- `docs/10-external-review.tr.md`
- `docs/11-falsification.tr.md`
- `docs/appworld-facts.tr.md`
- `docs/reports/asama-0.md`
- `docs/reports/asama-1.md`
- `docs/reports/asama-2.md`
- `docs/reports/asama-3.md`
- `docs/reports/asama-4.md`
- `docs/reports/asama-5.md`
- `docs/reports/b32-olcumu.md`
- `docs/reports/bant-taramasi.md`
- `docs/reports/bant3-taramasi.md`
- `docs/reports/bosluk-raporu.md`
- `docs/reports/denetim-bosluk-raporu.md`
- `docs/reports/hizalama-denetimi.md`
- `docs/reports/izinli-uygulama-vekili.md`
- `docs/reports/kapanis-raporu.md`
- `docs/reports/kurulum-sonrasi-1.md`
- `docs/reports/kurulum-sonrasi-2.md`
- `docs/reports/kurulum-sonrasi-3.md`
- `docs/reports/kurulum-sonrasi-4.md`
- `docs/reports/mekanizma-kapanis-notlari.md`
- `docs/reports/model-ailesi-taramasi.md`
- `docs/reports/sinir-kontrolu.md`
- `docs/reports/sunum-iskeleti.md`
- `docs/reports/teknik-olgular.md`
- `docs/reports/teshis.md`
- `docs/reports/uc-kollu-kart-kosusu.md`
- `docs/reports/uctan-uca-demo.md`
- `experiments/colab/README.md`
- `experiments/pilot-plan.md`
- `experiments/preregistration.md`
- `inputs/README.md`
- `scripts/setup/README.md`
- `vendor/appworld/README.md`

## License

Apache 2.0. See [LICENSE](LICENSE).
