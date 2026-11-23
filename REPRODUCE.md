# Reproduction

Turkish is the source: `REPRODUCE.tr.md`.

Instructions for setting up from scratch on a clean machine. Every step here was
run in Stage 1. No command that was not run has been written down.

## Prerequisites

| Prerequisite | Version or note |
|---|---|
| Ubuntu 24.04, on WSL2 or native | K-01 |
| Python 3.11 | `uv` installs it itself; `.python-version` is pinned |
| `uv` | 0.11.28 |
| Git LFS | Required, see below |
| GitHub CLI (`gh`) | Only for `scripts/local_checks.sh`; must be authenticated |

### Git LFS

AppWorld's `apps.bundle` and `tests.bundle` files are stored in the repository
with Git LFS, and `appworld install` unpacks them. Without the filter installed,
`uv` downloads these files as 131-byte pointers. The installation then fails with
this line:

```
Exception: File .../appworld/.source/apps.bundle is a Git LFS pointer and not a bundle file.
```

To install it:

```bash
sudo apt-get install git-lfs
git lfs install
```

The second command is required. Having the package installed is not enough; the
filter has to be written into `~/.gitconfig`. With the filter installed, the files
arrive at 193950 and 204426 bytes, identical byte for byte to a manual clone.

On the repository side, the counterpart is the `lfs = true` line in
`pyproject.toml`. CI has a `git lfs install` step too, so this prerequisite is
tested on every PR.

If upstream Git LFS stops serving the pinned commit's bundle objects, `uv sync` cannot
finish. That happened on 2026-08-20, with HTTP 403 and `This repository exceeded its LFS
budget`. The archive this repository is built from keeps a mirror of the two AppWorld
wheels, built from the pinned commit. This repository does not carry them; reviewers can
have them on request.

| | |
|---|---|
| Upstream source | `https://github.com/StonyBrookNLP/appworld.git` |
| Pinned commit | `a072b7a86e7c1d5b1d7175659d750ebb9b79f10a` |
| `appworld-0.2.0.dev0-py3-none-any.whl` | sha256 `13965100b4e6191e5503c06a24f9b9140b0f04a95a56c8394c29bc6f094c67e3` |
| `appworld_agents-0.1.0.dev0-py3-none-any.whl` | sha256 `32fcd23f68b86c08fdf357fe409a8823fdc7ae64582d784dcf046374cd739e73` |

`vendor/appworld/README.md` says how the mirror was built and how to rebuild it.

## If you use WSL: networking mode

The model server runs on the Windows side, the experiment inside WSL. In the
default NAT mode the Hyper-V firewall cuts connections from WSL to Windows,
because `DefaultInboundAction` is `Block`. As a result `127.0.0.1:11434` is
unreachable.

Add this to `~/.wslconfig`:

```ini
[wsl2]
networkingMode=mirrored
```

Then run `wsl --shutdown` and reopen the distribution. In mirrored mode WSL shares
the host's network namespace. `127.0.0.1` works in both directions, no firewall
rule is needed, and Ollama does not have to be bound to `0.0.0.0`. Because the
server does not listen on the LAN interface, it is not exposed to the outside.

The known risk of this mode is that it breaks outbound DNS. It was tested after the
switch: `pypi.org`, `github.com` and `registry.ollama.ai` resolved, HTTPS requests
returned, `uv lock --check` passed.

The alternative was a Hyper-V rule that opens only port 11434 to the WSL virtual
machine. That path needs administrator rights and requires the server to be bound
to `0.0.0.0`. Since mirrored works, it was not used.

## Installation

```bash
git clone <repository-url> zihin
cd zihin
uv sync --all-groups --frozen
uv run appworld install
uv run appworld download data
```

`--frozen` applies the lock as it is. If the lock and `pyproject.toml` have
diverged, it fails instead of updating silently.

`appworld download data` unpacks 198 MB of data under `data/`. The directory is
not tracked. The task data carries a canary marker and can always be regenerated
with the command.

### AppWorld-derived data

The data files derived from AppWorld (route lists, measurement outputs that carry
routes, a test fixture) ship encrypted in `derived/appworld-derived.bundle`, as
AppWorld's sharing terms ask. Restore them to their original paths before running the
tests or the guardians:

```bash
uv run python scripts/unpack_derived.py
```

The script opens the bundle with `appworld unpack` and checks every file against the
sha256 in `derived/MANIFEST.json` before writing it. The restored paths are listed in
`.gitignore`.

### Record databases

The four record databases are published as encrypted assets in this repository's
[releases](https://github.com/yusuferengerek/zihin/releases), one `.bundle` file per
database. Without them the tests that read the record are skipped and the guards that
read it cannot run. Download the four files into one directory and restore them:

```bash
uv run python scripts/restore_records.py <directory with the downloaded assets>
```

The script opens each asset with `appworld unpack` and checks the restored file's size
and sha256 against `records/MANIFEST.json` before writing it under `results/`. It never
overwrites a file whose sha256 differs. The test outcome without and with the databases
is in the README, under "What a correct run looks like".

## Model server

On the Windows side, with the project's script:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/serve_models.ps1
```

The script starts the server as a process independent of the session and passes
four settings to the server process: context window, KV cache type, flash
attention and `keep_alive`. It prints to its output that the settings were
actually applied. To stop it: `Stop-Process -Name ollama`.

Three models:

```powershell
ollama pull qwen2.5-coder:1.5b-instruct-q4_K_M
ollama pull qwen2.5-coder:3b-instruct-q4_K_M
ollama pull qwen2.5-coder:7b-instruct-q4_K_M
```

The tags are pinned in full in `config/models.yaml`, size and quantization
included. Shortened tags are not used, because then the manifest could no longer
tell which weights ran.

If `OLLAMA_CONTEXT_LENGTH` is not given, Ollama picks a context window of 4096 by
looking at VRAM. The line in the server log is:
`vram-based default context ... default_num_ctx=4096`. The instruction file alone
is 11350 bytes and the agent spends about 3800 input tokens per step, so in a 4096
window the prompt is truncated. Its measured effect is in the Stage 1 report.

Stage 4 will start this server from its own script and pass the KV cache type and
flash attention settings through environment variables. The current process does
not have those settings: `OLLAMA_KV_CACHE_TYPE` is empty, `OLLAMA_FLASH_ATTENTION`
false. No performance measurement taken from here is valid for Stage 4.

## How reproducible it is

This has to be said plainly, because the three models are not alike.

Episodes run in the cold regime: before every episode the model is unloaded from
memory, and the unload is verified by asking the server. When the same quadruple
of task, seed, condition and model is repeated:

| Model | Reproducibility |
|---|---|
| 1.5B | Exact. Ten runs, one trajectory |
| 3B | Exact. Ten runs, one trajectory |
| 7B | Within measured variance. Nine of ten runs one trajectory, one another |

7B's divergence is not a fault but a measured quantity. Determinism is not
assumed; the residual variance is measured per model and added to the noise floor
(K-51).

To repeat the measurement:

```bash
MODEL_SERVER_URL=http://127.0.0.1:11434 \
  ZIHIN_MODEL=7b ZIHIN_REPEATS=10 \
  uv run python scripts/check_cold_determinism.py
```

## Running a single task end to end

```bash
MODEL_SERVER_URL=http://127.0.0.1:11434 uv run python scripts/run_single_task.py
```

`MODEL_SERVER_URL` is the reference scaffold's own variable. It fills the template
in the `base_url` field.

The run writes under `experiments/outputs/asama-1-tek-gorev/`. The verifier's
verdict is in two places:

- `tasks/<task>/evaluation/report.md`, per-task detail
- `evaluations/on_only_<task>.txt` and `.json`, aggregate metrics

## The copy in your hands is not what the checks look at

The subject of every check in this repository is **the repository's tree**. The
copies you hold — a Colab notebook saved to Drive, a downloaded database, a clone
pulled a week ago — are outside those checks.

**The rule for the Colab notebook.** The notebook is opened **from the repository**
in every session; a copy saved to Drive is not used. A saved copy freezes the
moment it is saved, and no fix in the repository reaches it. It happened once: the
copy kept pulling a merged branch, the files added later were missing, and the
fault named itself "the file was never written".

**The rule for a clone.** Before a run, run the prerequisite check; its first line
says how many commits the working copy is behind `origin/main`:

```bash
uv run python scripts/setup/check_prerequisites.py --prefix bir1
```

`--prefix` names the run about to happen, and the check reads the requirements from
that run's declared conditions. Run without a prefix, it asks for every
requirement — including the skill library from a run that reads no cards
(`K-152`).

**What these rules do not close is written in `S-69`.** The staleness check runs
**after** cloning, that is, one round late, and there is no mechanism that checks
the copy in your hands before it is cloned.

## Verification

CI runs five jobs. Their local equivalents:

```bash
uv run ruff check .
uv run ruff format --check .
uv run python -c "import zihin"
uv build
uv run pytest -m "not model_server and not sandbox"
```

The test filter does **not** exclude the `appworld` marker: since K-100 CI runs
`appworld install` and installs the data, so those tests run in CI as well. The two
excluded markers run separately — `sandbox` in its own job, `model_server` only
locally.

The Lint job also checks five generated views; none of them needs data:

```bash
uv run python scripts/check_docs_parity.py
uv run python scripts/build_limitations_index.py --check
uv run python scripts/build_skeleton_coverage.py --check
uv run python scripts/build_decisions_csv.py --check
uv run python scripts/count_guards.py --check
```

## Local-only checks

Tests marked `appworld` need the downloaded 198 MB of data and do not run in CI.
Among them is one of the project's most important invariants: the per-episode
database reset. Because they are not under CI's protection, they are run by hand
before every stage merge.

**Correction, 13 October 2026: what CI runs today.** This paragraph describes the state
before K-100; the "Verification" section above is right. `.github/workflows/ci.yml`
runs this today:

- The tests job (`Testler`) runs `pytest -m "not model_server and not sandbox"` after
  `appworld install` and `appworld download data`; the `appworld`-marked tests are part
  of it. A step after it checks that no test was skipped for missing app modules and
  that the `appworld`-marked tests were actually collected.
- The sandbox job (`Sandbox`) runs `pytest -m sandbox` after the same installation.
- Tests marked `model_server` run in no CI job.

In the table below, `tests/test_appworld_reset.py` runs in CI;
`tests/test_recorded_run.py` is collected in CI but skipped there, because CI has no
`results/zihin.sqlite` (it runs once the record databases are restored); only
`tests/test_model_serving.py` stays outside CI.

```bash
bash scripts/local_checks.sh
```

The script runs the full test suite and prints the result with its date. Every
stage report writes when this output was last taken and with what result.

**Correction, 18 October 2026: what the script runs.** The "full test suite" is the
union of three selections: first `pytest -m "appworld or model_server"`, then
`scripts/ci_simulasyonu.sh` runs CI's two selections in a clean checkout,
`not model_server and not sandbox` and, if podman is present, `sandbox`. Without
podman the sandbox tests are skipped. Then the language check; the citation, date,
merged-PR artefact and Colab notebook checks; and the `--check` modes of the
touched-task list, the series merge and the experiment sets.

**On a fresh clone this script does not pass, and that is correct.** Two of its
steps rely on a working setup: the language check reads its comparison corpus from
under `results/` and from the record, and the merged-PR artifact check needs an
authenticated `gh`. Without the record the language check **refuses to answer** —
it fails rather than give a wrong answer. With the record databases restored it
answers, but on a clone it still fails, because part of its corpus is untracked run
output that exists only on the archive's machine. S-84 gives the measured numbers.

| Check | What it protects |
|---|---|
| `tests/test_appworld_reset.py` | No database leakage between episodes |
| `tests/test_recorded_run.py` | A real run is written to the record schema with all four levels |
| `tests/test_model_serving.py` | The effective context window on the server is 32768, all three models fully in VRAM, the seed controls the output |

The second check reads `results/zihin.sqlite`. Without the file the test is
skipped. Restore the record databases listed in `records/MANIFEST.json` with
`scripts/restore_records.py`, or take a run of your own:

```bash
MODEL_SERVER_URL=http://127.0.0.1:11434 uv run python scripts/record_run.py
```

## Public mirror

The public repository, yusuferengerek/zihin, is built from this archive's tree by
`scripts/build_public_tree.py` (K-205). A sync runs the same script against a newer
archive commit and applies the difference to the public repository as one commit:
`Sync with archive <hash>`. The test outcome and the experiment episode count that the
READMEs cite are measured again with `--measure` before a sync. If the tree changed
after the measurement, the build refuses to produce the public tree.

### Syncing

From 23 November 2026, `main` of the public repository is protected. It requires the five
jobs of `.github/workflows/ci.yml` as status checks. The branch must be up to date before it
moves, force pushes and deletion are blocked, and the rule applies to administrators. A sync
commit therefore reaches `main` only after the five checks have passed on that exact commit.

The input is `A`, the archive commit to mirror. It is on the archive's `main`, and
`uv run python scripts/build_public_tree.py --check --commit A` reports the measurement fresh
and the verification clean. Below, `<A7>` stands for the first seven characters of `A`.

1. Build the tree of `A` into an empty directory `<out>` outside the archive:

   ```bash
   uv run python scripts/build_public_tree.py --commit A --out <out> --report <report.json>
   ```

   The build refuses a stale measurement. The dry-run table must show the verification clean,
   gitleaks 0 and the measurement fresh.

2. In a fresh clone of the public repository, branch from `origin/main` and empty the tree:

   ```bash
   git switch -c sync/<A7> origin/main
   git rm -r -q .
   ```

   Copy the contents of `<out>` in, without any `.git` directory, and run `git add -A`. Commit
   once, with the owner as author and committer, the same identity as the earlier public
   commits. The subject is `Sync with archive <A>` (K-205). The last line of the body is
   `Archive: <A>`, with the full hash of `A`. Every public commit names the archive commit it
   mirrors in such a final line (PROVENANCE). No other trailer. Before pushing, `git ls-files`
   must equal the build's output list, and the diff against `origin/main` must be the change
   the build report describes.

3. Push the branch only and open a pull request from it to `main`:

   ```bash
   git push origin sync/<A7>
   ```

   CI runs on pull requests and on pushes to `main`, not on pushes to other branches, so the
   pull request is what starts the checks. Wait until all five have passed on the branch's
   head commit. If one fails, fix the cause in the archive, build again from the new archive
   commit and replace the branch. Nothing is fixed in the public repository itself.

4. When the five checks have passed and the branch is up to date with `main`, move `main` to
   that same commit with a fast-forward push:

   ```bash
   git push origin sync/<A7>:main
   ```

   This keeps the verified commit and its hash. A squash or rebase merge in the web interface
   would write a different commit, and a merge commit would add a second commit for every
   sync. GitHub marks the pull request merged once its head commit is on `main`.

5. Delete the sync branch if it is still there. The push to `main` starts CI and the Pages
   workflow. Confirm that both pass and that the site serves the new tree. Record the public
   commit's hash next to `A` in the archive.

The procedure does not cover three things:
- The record databases. A change to them needs new assets and a new release. That is decided
  separately and is not part of a tree sync.
- The status check names. They are the job names in `.github/workflows/ci.yml`. If a job is
  renamed in the archive, the branch protection must be updated to the new name before that
  sync, or `main` can never move.
- Dependabot pull requests. They change `uv.lock` in the public repository only. Merging one
  would make the public tree differ from the archive. The owner decides how they are handled.

Not yet verified: that the branch protection lets the fast-forward push of step 4 through
once the five checks have passed on that commit. No review requirement is set, so it is
expected to. It has not been tried. If GitHub refuses it, merge through the pull request
instead and record the choice.
