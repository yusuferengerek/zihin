# Limitations

Turkish is the source: `09-limitations.tr.md`.

The constraints we know about. The unmeasured ones get a number here as they are
measured. The closable ones get struck through when they close.

<!-- HARITA BASLANGIC: uretilmis, elle duzenlenmiyor -->

**82 limitations: 64 open, 18 closed.** This table is generated; there is no hand-edited copy (`scripts/build_limitations_index.py`). Search the identifier to reach a record.

**Axis of the open items:** 53 bound a claim, 11 are scope. The axis is read from the first quoted line under each record's heading; calling an item “bounds” requires naming the claim it bounds (K-107).

**Closure class of the open items:** 11 external fact, 11 measured and the constraint is real, 29 next round, 13 permanent record. The test is one question: *whose hands is the work that would close this record in?* Only the third class can close — so 29 of the 64 open items are provisional and the remaining 35 are permanent in this document.

| | Limitation | Status | Axis | Closure |
|---|---|---|---|---|
| `S-01` | AppWorld is pinned to a moving branch, not a published release | open | bounds | External fact |
| `S-02` | Reference solutions exist only in train and dev | open | scope | External fact |
| `S-03` | The per-task app list is absent from the test splits | open | bounds | External fact |
| `S-04` | The two components of the verifier verdict may not be separable | open | bounds | Next round |
| `S-05` | No response body at the action level, and no status code either | open | bounds | External fact |
| `S-06` | One server process holds one world at a time | open | scope | External fact |
| `S-07` | The scaffold has truncation logic of its own | open | scope | External fact |
| `S-08` | Three models do not fit in 8 GB of VRAM at once | open | scope | External fact |
| `S-09` | The WSL memory limit is host-wide | open | scope | External fact |
| `S-10` | ~~Reaching Ollama on the Windows host from inside WSL is unsolved~~ | closed | — | — |
| `S-11` | ~~Agent behaviour is unstable even at the same seed~~ | closed | — | — |
| `S-12` | ~~The reset test is not under CI protection~~ | closed | — | — |
| `S-13` | There is one more server-side state we do not see | open | bounds | Next round |
| `S-14` | The smallest point of the scale axis is stuck to a floor effect | open | bounds | Next round |
| `S-15` | The list of write-performing GET endpoints is a lower bound | open | bounds | Next round |
| `S-16` | Action-level response instrumentation does not exist yet | open | bounds | Next round |
| `S-17` | The step ceiling and the anchor are in different units | open | bounds | Next round |
| `S-18` | The cold regime is not uniform at 7B | open | bounds | Measured |
| `S-19` | 3B's zero calls is not a capability floor but a systematic error | open | bounds | Next round |
| `S-20` | A single well-formed example could close the small models' dominant error | open | scope | Next round |
| `S-21` | Residual variance gets an upper bound, not a point estimate | open | bounds | Measured |
| `S-22` | The censoring rate rests on five tasks and one episode per model | open | bounds | Next round |
| `S-23` | The published baseline rates for this model class were not consulted before the design | open | bounds | Permanent record |
| `S-24` | The external review did not ask the precondition question | open | bounds | Permanent record |
| `S-25` | ~~The stopping rule counts a successful read as progress~~ | closed | — | — |
| `S-26` | The same output budget does not mean the same condition across model families | open | bounds | Measured |
| `S-27` | The band sweep ran under the old stopping rule, and the precondition gate rests on it | open | bounds | Next round |
| `S-28` | ~~A manifest field was written at the wrong call site, thirty episodes fell, and the guard did not fire~~ | closed | — | — |
| `S-29` | ~~The machine side of the manifest contract only holds on a database built from scratch~~ | closed | — | — |
| `S-30` | ~~The output budget was read from the environment and its silent default started the wrong run~~ | closed | — | — |
| `S-31` | ~~The resume logic could silently merge two different measurement conditions~~ | closed | — | — |
| `S-32` | The stopping rule's endpoint criterion had never been in force | open | bounds | Next round |
| `S-33` | The machine-readable decision record is produced by parsing prose | open | bounds | Next round |
| `S-34` | The boundary control did not run in the declared condition: thinking was on | open | bounds | Next round |
| `S-35` | ~~The two sources of the write set disagreed on one endpoint~~ | closed | — | — |
| `S-36` | ~~Two route templates match the same path, and the resolver gave the wrong answer~~ | closed | — | — |
| `S-37` | ~~`update` is not a model verb, and it made two pure reads into writers~~ | closed | — | — |
| `S-38` | ~~The write-set derivation took the `@app.delete` decorator for a write call~~ | closed | — | — |
| `S-40` | Bound-argument detection is limited to what the agent printed | open | bounds | Next round |
| `S-41` | Most postconditions are empty in v0, because attribution needs isolation | open | bounds | Measured |
| `S-42` | ~~Boundness was searched across the episode, not within the body~~ | closed | — | — |
| `S-43` | The 409 class is outside the scope of the v0 index | open | bounds | Measured |
| `S-44` | `actions.error_class` is single-valued, the signal is in the status code | open | bounds | Measured |
| `S-45` | The index cards' condition can separate by accident, and the card carries this on its face | open | bounds | Measured |
| `S-46` | ~~The fixed block's share in the architecture document was unmeasured and wrong~~ | closed | — | — |
| `S-47` | The binding context limit is not the token window but the scaffold's character ceiling | open | bounds | External fact |
| `S-48` | The index's most frequent pattern is retrievable by no task | open | bounds | Measured |
| `S-49` | ~~Forty-five tests had never run in CI, and two environment differences were invisible locally~~ | closed | — | — |
| `S-50` | Not all admin routes can be cut: eleven are needed to build the world | open | bounds | Measured |
| `S-51` | The container's environment server is in the same process as the agent's code | open | bounds | External fact |
| `S-52` | The proxy cannot fill the `error_class` field, because there is no exception on the wire | open | bounds | Next round |
| `S-53` | ~~The recorder's mount point did not fire in remote mode, and it was silent~~ | closed | — | — |
| `S-54` | The state probe's blind spot closed, but **only going forward** | open | bounds | Next round |
| `S-56` | The noise floor is not zero: the upper bound on every claim readable from one episode | open | bounds | Measured |
| `S-57` | Getting past the authentication barrier is necessary but not sufficient | open | bounds | Next round |
| `S-58` | The 32B measurement ran with two declared conditions drifted | open | bounds | Next round |
| `S-59` | The 32B result was read from an incomplete set and under a binding ceiling | open | bounds | Next round |
| `S-60` | A reproducibility verification belongs to a moment; an outside service can invalidate it retroactively | open | bounds | Permanent record |
| `S-61` | The scale axis's points were measured on three different cards | open | bounds | Permanent record |
| `S-62` | The band label describes the reference solution's path, not the difficulty | open | bounds | External fact |
| `S-63` | Two of the three runs the precondition rests on are ceiling-limited, and one is not in the record | open | bounds | Permanent record |
| `S-64` | Unmerged work is the subject of no check | open | bounds | Next round |
| `S-65` | The failure index is behind the corpus: fifteen cards in the record, twenty from today's corpus | open | bounds | Next round |
| `S-66` | The interval-width sweep's noise model comes from two cells | open | bounds | Next round |
| `S-67` | The memorisation gate is a distinction the design cannot carry | open | bounds | Next round |
| `S-68` | The derived pass-rate threshold is two and a half times the measured one: the design is underpowered | open | bounds | Next round |
| `S-69` | The checks' subject is the repository; the copies in the user's hands are outside | open | bounds | Permanent record |
| `S-70` | Two of the notebook check's rules read prose by pattern | open | bounds | Next round |
| `S-71` | A resumed episode's manifest describes the machine of the first attempt | open | bounds | Next round |
| `S-72` | The miner reads the whole file, not the run's episodes | open | bounds | Next round |
| `S-73` | Branch A has no observation for the run's first 188 episodes | open | bounds | Permanent record |
| `S-74` | Series 3 has been in two files since 26 August; from 13 to 25 September half of it was missing from the repository's record | open | bounds | Next round |
| `S-75` | The threshold derivation's artefact was produced with an undeclared argument | open | bounds | Permanent record |
| `S-76` | The language check scans Python files only | open | bounds | Next round |
| `S-77` | A.5's example of inaction is a single episode, and it did not come back | open | bounds | Permanent record |
| `S-78` | A test task's instruction was taken out of an artefact; the original text is in this repository's history | open | scope | Permanent record |
| `S-79` | Three train tasks' instructions were taken out of the documents; the original texts are in this repository's history | open | scope | Permanent record |
| `S-80` | ~~The route test's sample log now comes from a train task, and is still an AppWorld derivative~~ | closed | — | — |
| `S-81` | ~~`SKILL_SPEC.tr.md` and the `skills` table differ in nine fields, and the decisions record has no decision~~ | closed | — | — |
| `S-82` | Earlier scans did not normalize whitespace; a quote of a train instruction stayed in two places | open | scope | Permanent record |
| `S-83` | A test's AppWorld outputs entered the shadow-mode corpus; one of the blocks was the test's own call | open | scope | Permanent record |
| `S-84` | The language check cannot pass in a public clone, even with the record databases restored | open | scope | Measured |

<!-- HARITA BITIS -->

**Addendum — 15 November 2026: S-39 and S-55 were never assigned.** The counter
skipped S-39 when S-40 was written on 15 August 2026 (`7266048`) directly after S-38,
and skipped S-55 when S-56 was written on 18 August 2026 (`4c573ce`) directly after
S-54. No entry was lost. The map's 81 is the number of entries.

<!-- IDDIA HARITASI BASLANGIC: uretilmis, elle duzenlenmiyor -->

**40 claims, 53 limitations.** This table is the reverse of the one above: how many limitations stand under each claim. A claim carrying eight of them is barely a claim, and that is only visible from this side. Generated; there is no hand-edited copy (K-107).

| Claim | Limitations | Identifiers |
|---|---|---|
| 07-failure-taxonomy | 4 | `S-05`, `S-16`, `S-43`, `S-44` |
| K-58 | 4 | `S-19`, `S-23`, `S-27`, `S-63` |
| 05-experiment-design | 3 | `S-04`, `S-17`, `S-32` |
| 04-threat-model | 2 | `S-15`, `S-51` |
| K-51 | 2 | `S-18`, `S-21` |
| REPRODUCE.md | 2 | `S-01`, `S-60` |
| docs/reports/b32-olcumu.md | 2 | `S-58`, `S-59` |
| the boundary control | 2 | `S-26`, `S-34` |
| 02-research-question second question | 1 | `S-14` |
| 02-research-question, the second question | 1 | `S-61` |
| 03-architecture | 1 | `S-47` |
| 06-skill-language | 1 | `S-40` |
| 10-external-review | 1 | `S-24` |
| A.1 | 1 | `S-68` |
| A.5 | 1 | `S-77` |
| DATA_MODEL.md | 1 | `S-52` |
| Every check in this repository | 1 | `S-69` |
| Every per-band result reported | 1 | `S-62` |
| K-21 | 1 | `S-13` |
| K-53 | 1 | `S-22` |
| K-85 | 1 | `S-45` |
| K-93 | 1 | `S-54` |
| K-95 | 1 | `S-50` |
| PILOT_REPORT.md | 1 | `S-48` |
| PILOT_REPORT.md and the end-to-end demo | 1 | `S-56` |
| PILOT_REPORT.md mirror finding | 1 | `S-57` |
| PILOT_REPORT.md shield section | 1 | `S-03` |
| SKILL_SPEC.md | 1 | `S-41` |
| The retriever's coverage and discriminativeness numbers | 1 | `S-65` |
| Y-2 | 1 | `S-67` |
| `K-139` | 1 | `S-74` |
| `K-77` | 1 | `S-76` |
| `results/interval-width.json` | 1 | `S-66` |
| `results/pass-threshold.json` | 1 | `S-75` |
| `run_manifests.boot_id` and `created_at` | 1 | `S-71` |
| `scripts/check_colab_notebook.py` | 1 | `S-70` |
| `scripts/check_merged_artefacts.py` | 1 | `S-64` |
| experiments/decisions.csv | 1 | `S-33` |
| §18.1 | 1 | `S-72` |
| §18.3 branch A | 1 | `S-73` |

<!-- IDDIA HARITASI BITIS -->

---

## S-84 — The language check cannot pass in a public clone, even with the record databases restored

> **Scope.** `scripts/check_language.py` in a clone of the public repository, with the guard unchanged

> **Closure class.** Measured — with the four record databases restored, the corpus still lacks run outputs that exist only on the archive's machine

**What was measured.** On 22 November 2026 the public tree of archive commit `41be190`
was built and made a one-commit repository, and the four record databases were restored
into it from their assets with `scripts/restore_records.py`. There
`scripts/check_language.py` exits 1 with 58 Turkish strings left: 36 distinct strings in
13 files. In the archive, at the same commit and on the same day, it exits 0. Both scan
the same 160 files.

| | Public clone, databases restored | Archive |
|---|---|---|
| Data strings in the corpus | 20 215 | 22 519 |
| Of them from the record | 17 929 | 17 915 |
| Turkish strings left | 58 | 0 |

The clone's record share is larger because the clone also holds
`results/zihin-3-colab.sqlite`, which the archive keeps only in its history.

**Why.** The guard's corpus is every key and identifier-shaped value in the record and
under `results/` and `experiments/`, and every file name there. In the archive, 34
entries under `results/` besides the record databases, and the 437 entries under
`experiments/outputs` (1.9 GB), are run outputs that git does not track. Neither the
public tree nor the record assets carry them. Copied into throwaway copies of the clone,
they account for the whole difference:

| Added to the clone | Turkish strings left |
|---|---|
| nothing | 58 |
| the 34 untracked `results/` entries | 2 |
| `experiments/outputs` | 56 |
| both | 0 |

**What it does not mean.** The strings the guard reports are names those untracked
outputs define, not Turkish prose. The guard still runs in the archive through
`scripts/local_checks.sh`, and it passes there. CI does not run it. Passing in a public
clone would take either shipping those outputs or changing the guard, and neither is
done here.

## S-83 — A test's AppWorld outputs entered the shadow-mode corpus; one of the blocks was the test's own call

> **Scope.** corrects the blocking numbers cited from `results/shadow-mode.json`; the results file is not rewritten

> **Closure class.** Permanent record — the numbers were corrected with dated corrections where they are cited

**What happened.** From `e26e09c`, where it was added (10 August 2026), until `a995af7`
(14 November 2026), `tests/test_appworld_reset.py` wrote two AppWorld runs into the
working directory, under `experiments/outputs/reset-check-1` and `reset-check-2`.
`scripts/setup/measure_shadow_mode.py` counts every `api_calls.jsonl` in that directory
as a recorded episode. The input listing of `results/shadow-mode.json` itself
(`per_experiment`), committed with `d76d932` on 28 August, carries both directories: 2
episodes, 9 calls, 1 block. The blocked call is the note the test opens in
`simple_note`. The allowed apps inferred from the instruction of `82e2fac_1` do not
include `simple_note`.

**How it was found.** In the public tree the corpus test was skipped on a first run and
passed on a second, because the first run wrote these two directories. The user asked
for every script that reads `experiments/outputs` to be checked for whether these two
directories were in its input.

**Readers.** The only measurement script that sweeps the whole directory is
`measure_shadow_mode.py`. The other scripts read only the experiments they name, and no
`reset-check-*` name matches any of their prefixes. `scripts/check_language.py` also
reads `experiments/**/*.json`, but it is a guardian and produces no recorded number.

**Recomputation.** The script was run in a temporary directory over the experiments in
the record's input listing, with and without the two directories. The results file was
not touched. Every row of the 243 experiments still on disk came out identical to the
record. The only difference from the record is three `durum-sondasi` directories deleted
later, and their share was taken from the record's own rows.

| Number | In the record | Without the test outputs |
|---|---|---|
| Episodes | 258 | 256 |
| Calls | 9154 | 9145 |
| Blocked calls | 6 = 0.07% | 5 = 0.05% |
| Blocked episodes | 6 = 2.33% | 5 = 1.95% |
| Blocked tasks | 1/58 = 1.72% | 1/58 = 1.72% |
| Read / allowed write / disallowed write | 8631 / 517 / 6 | 8623 / 517 / 5 |
| First shadow run, before S-37 | 8/9154 = 0.09% | 7/9145 = 0.08% |

The last row could not be rerun, because that day's write set never entered the
repository. It was derived: according to S-37 that set differed from today's only by the
two endpoints of the `update` verb, and the test calls neither.

**What could not be determined.** `src/zihin/api_routes.py`, `tests/test_api_routes.py`
and S-36 say that 7138 of the 7138 calls in 239 recorded episodes resolve (`fd28a43`, 14
August). That measurement has no input listing. It could not be rebuilt from log
timestamps either: the logs written before that hour give 235 episodes and 7121 calls
today, and no combination of the two test directories and the three deleted
`durum-sondasi` directories gives exactly 239/7138. If the test outputs were in it, the
number would be 7129/7129 in 237 episodes. The claim that every call resolves holds
either way.

**Closed, 15 November 2026: the probe runs stay in the corpus.** The user decided this.
The corpus definition does not change. The two `reset-check` directories were removed
because a defect put them there, not because of their content: the test wrote into the
repository, and `a995af7` fixed that. The probe runs were deliberate runs and fall within
the script's definition: every run under `experiments/outputs` except those starting
with `legacy_`. Narrowing that definition after seeing the result is not allowed. As
measured, all five remaining blocks come from probe runs (`durum-sondasi-2`,
`durum-sondasi-3`, `notlar`, `sifirlama2-1`, `sifirlama3-1`) and none comes from a model
episode. `sifirlama3-1` repeats the call sequence of `reset-check-1` exactly. This
matches the internship report's statement that the shield blocks nothing in model
trajectories. A model-only figure stays an open possibility, not a task. It would need
its rule written first as a dated addendum, applied to every experiment, and reported
next to the existing number, never in its place.

**What was done.** The test now moves AppWorld's root to its own temporary directory
(`a995af7`). The numbers were corrected with dated corrections where they are cited:
`PILOT_REPORT.md`, `PROJECT_STATUS.md`, K-72, `docs/reports/kapanis-raporu.md`,
`docs/reports/mekanizma-kapanis-notlari.md`, `experiments/setup-protocol.tr.md` and
`experiments/setup-protocol.en.md`, S-37 and the internship report. `PULL_REQUESTS.md` did
not change, because it carries pull request bodies as they were written, and this record
is their correction. `results/shadow-mode.json` was not rewritten.

## S-82 — Earlier scans did not normalize whitespace; a quote of a train instruction stayed in two places

> **Scope.** records where a quote of an instruction stayed and which scans missed it; it changes no measured result

> **Closure class.** Permanent record — commit messages are not rewritten; the correction is this record and the redaction

**What happened.** 77 of the 129 characters of the instruction of `train` task `692c77d_1`
stood verbatim in two places: `docs/reports/asama-2.md` (lines 131–132, entered with
`ddcc320` in #5) and the copy of that report's pull request body in `PULL_REQUESTS.md`. The
quote crossed a line break. D5's scan and the scans after it searched without normalizing
whitespace, so they did not see a quote that crossed a line break.

**The statement that was wrong.** The commit message of `71be1ca` says of
`PULL_REQUESTS.md` that the assistant-name and task-instruction scans were clean. For this
quote it was wrong. The message of `239be07` speaks only of the assistant-name scan; it
makes no claim about task instructions. The messages are not rewritten; the correction is
this record.

**What was done.** The quote in the report took the D5 form: the task id and the sha256 of
the original instruction. The tool that writes `PULL_REQUESTS.md` puts a placeholder of the
same form wherever a pull request body carries task text, and the file's header says so.
The public build searches every normalized 40-character window of every instruction in
every split; a line break, a blockquote marker or bold markers do not get past it.

**What remains.** The original text stays in this repository's history: in the versions of
`asama-2.md` from `ddcc320` on, and in the versions of `PULL_REQUESTS.md` from `71be1ca`
and `239be07`.

## ~~S-81 — `SKILL_SPEC.tr.md` and the `skills` table differ in nine fields, and the decisions record has no decision~~ — CLOSED: the specification was corrected; the table defines what was measured (K-202)

> **Scope.** records the differences between the specification's fields and the table the compiler writes; it does not rule on which one is authoritative

> **Closure class.** Next round — whether the specification or the code is corrected is the repository owner's decision

**Closed, 18 October 2026.** A decision was made: the specification was corrected and
the code was not touched (`K-202`).

**Evidence.** `SKILL_SPEC.tr.md` and `SKILL_SPEC.md` now take the table, in a dated
correction, as the authoritative description of what was measured, and list the nine
fields as designed and not implemented in that form. `src/zihin/schema.sql` did not
change.

**What did not close.** Six fields have no implementation, because skills are not
invoked. The specification's sections on the attribution of blame and the demotion
rule therefore remain design and describe nothing that was measured.

**What was measured.** The specification entered on 15 August 2026 (`51f3e0d`), the
`skills` table a day later (`142662f`). The table keeps nine of the specification's
fields under another name, with other content, or not at all:

| Field in the specification | In the `skills` table |
|---|---|
| *signature* | under another name: `free_parameters` |
| *calls* | under another name: `body`, its length `body_length` |
| *effect_suffix* | same name, other content: the specification asks for the indices of the writing calls, the table holds the suffix's calls |
| *precondition* | absent |
| *invocations*, *blamed_failures*, *postcondition_misses*, *model_failures_gate_1*, *model_failures_gate_2* | absent |

**What the decisions record says.** There is no recorded decision to rename or drop
these fields, and the record does not say the specification was frozen either.
`PROJECT_STATUS.md` shows the three gates of the attribution of blame as "designed":
the skills were given to episodes as cards and never invoked, so no event has occurred
that would fill the track-record counters.

**What was not touched.** Neither the specification nor the code changed. *kind* is not
on this list: K-75 writes that only skills enter the library, the table follows it, and
the specification was corrected at that point with a dated correction.

## ~~S-80 — The route test's sample log now comes from a train task, and is still an AppWorld derivative~~ — CLOSED: the sample log is synthetic and carries no AppWorld output

> **Scope.** records the source and the license status of the sample log `tests/test_api_routes.py` reads; we make no claim that rests on it

> **Closure class.** Next round — whether it is encrypted or left out of the public copy is the repository owner's decision

**Closed, 13 October 2026.** The sample log became synthetic.

**Evidence.** `scripts/build_api_calls_fixture.py` writes
`tests/data/api_calls-synthetic.jsonl`: 22 calls over ten routes, two templates reached
through more than one invented id, every call's `data` empty. No task text, no model
output, no trajectory. `tests/data/api_calls-229360a_2.jsonl` left the tree. In the test,
the file path, the comment on line 42 and the module's description changed; the test
logic is the same. Each of the five conditions was tested by mutation, and every mutation
failed the test it targets.

**Why these ten routes.** They are the old sample's routes, so the pinned count of ten
endpoints does not move. AppWorld's public API Explorer
(https://appworld.dev/appworld/api-explorer) shows all ten with app, API name, method and
path.

**What did not close.**
- The route names are derived from AppWorld's bundles. The site shows them to every
  visitor, but it sends the documentation encrypted, decrypts it in the browser and puts a
  canary string on every record; AppWorld's README also asks that data derived from the
  bundles not be posted online in plain text. Most of the same routes stand elsewhere in
  the tree too (`inputs/write-set-static.json`, the tests). That is a question for the
  public repository's design.
- A synthetic log cannot notice a change in the production shape. That check is the local
  corpus measurement: when `experiments/outputs` exists, every recorded call is checked for
  the same three keys.
- The two old samples stay in this repository's history.

**What changed.** The route test's sample log came from a `test_normal` task:
`tests/data/api_calls-32616b5_1.jsonl`, the 55 calls of the `sinir3` run on task
`32616b5_1`. The file left the tree; it stays in this repository's history (it entered
with `fd28a43`). In its place is `tests/data/api_calls-229360a_2.jsonl`: `train` task
`229360a_2`, 43 calls, 10 endpoints. Only the test's file path line changed, and the test
passes.

**Why the source is not our own run.** The test asks for exactly 10 distinct endpoints, at
least 20 calls and identities that merge. The 132 `train` logs on disk were measured. All
six that pass the test unchanged come from AppWorld's published gpt-4o run
(`legacy_react_code_agent/openai/gpt-4o-2024-05-13/train`); no `train` log of our own runs
met those conditions. It was cleaned as the old sample was: emails to aliases, password and
token fields to a fixed string.

**What does not close.** The new file is an AppWorld experiment output and a derivative
too. The license's condition of encrypted distribution does not separate `train` from
`test`, and AppWorld's leaderboard instructions ask that experiment outputs not be
published unencrypted. The change removes the contamination of the test split; it does not
remove the license question.

**Two stale places.** The module's description and the comment on line 42 still describe
the old sample (`sinir3-32616b5_1`, 55 calls). This change was allowed to alter only the
file path line.

## S-79 — Three train tasks' instructions were taken out of the documents; the original texts are in this repository's history

> **Scope.** records what replaced the quotations in two documents; what the documents argue does not change

> **Closure class.** Permanent record — history is not rewritten in this repository; the public copy is built from a filtered history

**What changed.** Three quotations were the instructions of AppWorld `train` tasks. In
their place are the task id and the sha256 of the original instruction text. The digest is
of the UTF-8 bytes of the `instruction` field in `data/tasks/<task_id>/specs.json`:

| Where | Task | sha256 |
|---|---|---|
| `docs/reports/izinli-uygulama-vekili.md`, lines 66–67 | `2a163ab_1` | `sha256:8171d51f01bd488de4138feca6b3ffb19c89efb3b854da8f3e2729b19e156ca2` |
| `docs/reports/izinli-uygulama-vekili.md`, lines 69–70 | `afc0fce_1` | `sha256:2b1127911151dd1e34ed76e403c1109b09a26be2a41769650c880141d85e2166` |
| `docs/appworld-facts.tr.md`, lines 340–341 | `692c77d_1` | `sha256:a950a91993090db7f485be0426584f1860ec42f296285eec93e92d53eb7bc1cf` |

**Why.** AppWorld's data license asks that public redistribution of task data and its
derivatives be done in an encrypted format (`data/LICENSE`). The condition does not
separate `train` from `test`.

**What remains.** What the documents argue is the same. The proxy report still names the
relationship words the instructions carry ("roommates", "siblings", "coworkers"). The
original texts stay in this repository's history: in the versions that entered with
`04c488a` and `b863acf`.

## S-78 — A test task's instruction was taken out of an artefact; the original text is in this repository's history

> **Scope.** records what one field of `results/demo-eklenti.json` holds; the numbers read from the file do not change

> **Closure class.** Permanent record — history is not rewritten in this repository; the public copy is built from a filtered history

**What changed.** `results/demo-eklenti.json`, line 71, field "gorev_metni", carried the
instruction of `test_normal` task `0de03ea_1` word for word. In its place are the task id
and the sha256 of the original instruction text:
`sha256:97d2ae07f37901ada1385075a28412fa3799f9bdd7c13a40e16853aefb0fdcbb`. The digest is of the
UTF-8 bytes of the `instruction` field in `data/tasks/0de03ea_1/specs.json`.

**Why.** AppWorld's data license asks that public redistribution of task data and its
derivatives be done in an encrypted format (`data/LICENSE`). This is a test task; an
instruction on the open web is where future training crawls can collect it.

**What remains.** The file's other fields and the numbers cited from it are the same. The
original text stays in this repository's history: in the file's versions from `93889e5`
up to this change.

## S-77 — A.5's example of inaction is a single episode, and it did not come back

> **Bounds a claim.** A.5 — "that inaction can be rewarded was measured"

> **Closing class.** Permanent record — an example observed once cannot be multiplied after the fact

Preregistration A.5 explains why the graded score is a diagnostic through
`0de03ea_1`: the carded arm acted, failed a test that a do-nothing agent passes,
and lost a free pass; corrected against the no-op baseline, 2/3 against 0/3. That
observation comes from **one episode**: the carded episode of the `demo` run.

**Measured** (`results/no-op-example.json`, with `zihin.verification.graded_detail`).
The same task ran twelve times in the record. Of the five carded episodes:

| Episode | Meaningful tests | Free tests lost |
|---|---|---|
| `demo` carded — A.5's citation | 2/3 | **1** |
| comparability run, carded | 0/3 | 0 |
| three-arm run, carded arm, three repeats | 0/3, 0/3, 0/3 | 0, 0, 0 |

In **none** of the four later carded episodes did the arm lose a free test, and
none passed any meaningful test. The example did not come back; it is in the class
of `S-56`: an arm comparison read off a single episode is below the noise floor.

**It does not bind A.5's rule.** The graded score being a diagnostic, and the raw
pass count not being primary, rest on the structure of the test file: there is a
`no_op_pass` test an acting agent can fail, and that is the same in every episode.
What is bound is the **observation** offered as the rule's reason: not "measured",
but "observed once". The task is no longer in the evaluation sample either
(`K-166`).

## S-76 — The language check scans Python files only

> **Bounds a claim.** `K-77` — "comments and runtime text in English"

> **Closing class.** Next round — closes if the check's scope is widened and the files it then covers are translated

`scripts/check_language.py` looks for Turkish, but only in the `.py` files under
`src/`, `tests/` and `scripts/`. "Turkish left: 0" is true of that scope; it is
not true of the whole code side.

**Measured, 25 September 2026.** Outside that scope, **20 tracked files** carry
Turkish prose. The largest:

| File | Lines with Turkish letters |
|---|---|
| `config/recording.yaml` | 72 |
| `.github/workflows/ci.yml` | 70 |
| `experiments/colab/zihin-colab.ipynb` | 57 |
| `config/sandbox.yaml` | 56 |
| `scripts/ci_simulasyonu.sh` | 44 |
| `pyproject.toml` | 42 |
| `scripts/local_checks.sh` | 37 |
| `config/models.yaml` | 35 |

The other twelve: `.gitignore`, `Containerfile`, `scripts/serve_models.ps1`,
`scripts/colab_publish_results.sh`, `.gitattributes`, and seven more
configuration files under `config/`. The count looks at letters particular to Turkish, so Turkish
lines without diacritics are not in it; the numbers are a lower bound. One file
name is outside the rule as well: `scripts/ci_simulasyonu.sh`.

**Turkish that breaks no rule is separate.** `experiments/decisions.csv` is
generated from the Turkish decision record, and a few result artefacts carry
Turkish data strings from the record; that is the language of their source, and
the data rule of `scripts/check_language.py` already sets them apart.

**Why it stayed invisible.** The language migration went through the Python tree
and the check was written for that tree. Configuration comments, CI steps and
shell scripts were never the subject of any check.

## S-75 — The threshold derivation's artefact was produced with an undeclared argument

> **Bounds a claim.** `results/pass-threshold.json` — "the threshold was derived from the preregistration"

> **Closing class.** Permanent record — the command an artefact was produced with cannot be declared after the fact

`results/pass-threshold.json`, committed on 28 August, carries `replicates: 9`.
The default of `scripts/setup/derive_pass_threshold.py` was 8, and the documented
command — the call with no argument — did not produce that artefact. Nothing said
"it was run with 9".

**Measured.** With the same list and the same record (the merged series 3 of 28
August), running with the default of 8 gave 236 leaves different from the
artefact; `--replicates 9` gave none. The script is deterministic: two runs with
the same argument are identical.

**What was hidden and what was not.** The number was not hidden: the artefact
carried its own replicate count. What was hidden was the command that produced it,
and an artefact that cannot be reproduced cannot be checked. `K-146`, `S-68` and
`K-148` rest on this artefact.

**The threshold itself is not affected.** With 8 and with 9 the derived threshold
is the same: 0.85 at an expected effect of 0.2, 0.75 at 0.3 and 0.5. What differs
is some of the readable rates per distinction.

**From here on.** The default is 9 (`K-167`); the command with no argument
produces the artefact committed today.

## S-74 — Series 3 has been in two files since 26 August; from 13 to 25 September half of it was missing from the repository's record

> **Bounds a claim.** `K-139` — "a measurement series may run on two machines, but it cannot stay in two files"

> **Closing class.** Next round — replacing the copy on Drive with the merged file, and a check that asks whether the series is split

`K-139` merged series 3 on 26 August and wrote the rule. The rule was a
**procedure**: the merge is done by `scripts/merge_series.py`, run by hand, and
nothing asks whether two files carry the same series. The split came back in
two stages.

| Date | What happened | Source |
|---|---|---|
| 26 August, 14:58 | The series was merged locally: 182 episodes. The copy on Drive stayed at the Colab half: 62 episodes (`b14`, `b32c`) | commit `1023098`; file dates |
| 2 September, 17:58 UTC | The first `bir1` episode was written **to the copy on Drive**. From then on each file carries rows the other does not | `run_manifests.wall_clock_utc` |
| 3 September | `S-72` counted six prefixes in the local file; an hour later the addendum to §18.1 measured the Colab file and counted three (`b14`, `b32c`, `bir1`). The two descriptions sat side by side in the same repository | commit `92396ea`, `fc83a92` |
| 13 September, 20:59 | `results/zihin-3.sqlite` was **overwritten** with the Colab record (269 episodes). The local half — `b3l`, `b7l`, `b15l`, `b32`, 120 episodes — left the repository's record; it survived only in backups in the home directory | file dates; `sha256` match |
| 25 September | The local half was put back: 389 episodes | `results/series-3-merge.json` |

**Why it was not noticed.** Four reasons, all four measured.

1. `ACTIVE_SERIES` is a **path**, not an identity. When the file at that path is
   replaced wholesale, every reader still "reads series 3".
2. The record is not in git (`*.sqlite` is ignored). The overwrite produced no
   diff, no commit and no review.
3. Four scan artefacts (`results/b3l-taramasi.json`, `results/b7l-taramasi.json`,
   `results/b15l-taramasi.json`, `results/b32-taramasi.json`) say
   `results/zihin-3.sqlite` in their `database` field. From 13 September that file
   held not one row of those prefixes, and no check read the claim.
4. Two contradicting descriptions of the same series entered the repository on
   the same day, an hour apart, and nothing compares prose with the record. That
   is also why the sentence in `S-72` — "on Colab these twenty are mined in the
   same corpus as the sixty of `bir1`" — was wrong: the Colab file did not hold the
   six passes of `b32`.

**What was produced from the half record.** On Colab, between 2 and 10
September, every block mining and preflight of the accumulation run — including
the delivered `v0-gap2-sup3-0c3f4ac` and `v0-sup1-0c3f4ac`. Locally, after 13
September, `results/accumulation-closure.json`. **Their measured effect is zero:**
the corpus rule (`K-159`: the declared model **and** `train`) selected 207
episodes before the merge and 207 after. No episode of the lost half enters that
rule — all four prefixes are in `test_normal` and all four carry another model
tag. The five outputs of the four scripts that read the list and their successor
(`results/task-types.json` and those after it) were produced from the full file on
28 August; re-run against that file, all five came out identical leaf for leaf.

**How the merge was tested.** `scripts/merge_series.py`: counts, the foreign-key
check, episodes per run. Asked to merge the local half into a file that already
held it, it **refused** with 120 collisions. `scripts/verify_series_merge.py`:
every run of both halves is identical **in content** in the merged file, the
prefix of each of the four scan artefacts is in place, and the corpus rule did not
move; run against the unmerged file, it refused with six problems.
`scripts/verify_carried_record.py`: the manifests of `b3l`, `b7l`, `b15l`,
`b32c` and `bir1` agree with the declared conditions. The three differences of
`b14` are not new: they are the third example in `S-58`.

**What stays open.** The copy on Drive is still the 269-episode half file. If the
next Colab run writes to it the split starts a third time; replacing that file
with the merged one is work for whoever has access to Colab. And there is no
standing check that asks whether the series is split:
`scripts/verify_series_merge.py` ran once.

**Addendum — 25 September 2026.** One of the two open items is closed: the standing
check that asks whether the series is split now exists (`K-172`) and is part of
the local checks. The other — replacing the copy on Drive — is on the Colab side.

## S-73 — Branch A has no observation for the run's first 188 episodes

> **Bounds a claim.** §18.3 branch A — "the run stops when two consecutive blocks add no new skill"

> **Closing class.** Permanent record — an observation that was never made cannot be reconstructed

The ledger was lost with the session (`K-162`), so at every block boundary the
runner read an empty ledger and counted every skill it found as **new**. In all
seven mining events `new_skills` came out greater than zero; the criterion "two
consecutive quiet blocks" was never once evaluated.

**It cannot be reconstructed, and the reason was measured.** The library id has
the form `v0-gap{gap}-sup{support}-{commit}` and every mining in a session ran at
the same commit, so all of them took the **same id**; `replace_library` deleted
the previous one each time. A change of commit makes a new id, so what remains is
one snapshot per session - two of them in the fresh copy, for seven minings
(`K-163`). Which skills were
found in which block is written nowhere, so "did block 4 add a skill block 3 did
not" cannot be answered today.

**What it does not bound.** Not the episodes, the passes or the final library:
those are in the record, and the corpus filter (`K-159`) was in force throughout,
so every mining ran on the right corpus. What is bounded is the **yield** branch's
verdict on this run's first 188 episodes. Branch B is unaffected; that count
comes from the record (`K-160`).

**What follows is not bounded.** `run_ledger` is in the record now; every block
boundary from here leaves a durable row and branch A can be evaluated across
sessions. If the run continues, branch A's observations accumulate **from episode
188 onwards**; for what came before, the report says "not evaluated", not "did
not fire".

**Addendum — 25 September 2026.** The sentence above, "`run_ledger` is in the
record now", was not true that day: the table had entered the code, not the real
record. It was absent from the record until 25 September, so the next run could
not have evaluated branch A either. The table was created that day and the
prerequisite check now asks for it (`K-171`).

## S-72 — The miner reads the whole file, not the run's episodes

> **Bounds a claim.** §18.1 — "the corpus comes from the evaluated model's own episodes"

> **Closing class.** Next round — the runner passing the builder a filter, and a decision on the filter's criterion

`passing_sequences` reads **every** passing episode in the database; there is
no prefix, condition or model filter. The failure index's `observed_episodes`
does the same, without even requiring a pass. The accumulation run writes into
`results/zihin-3.sqlite`, and that file carries 182 episodes from six prefixes
before `bir1`: `b14` (14B), `b15l`, `b3l`, `b7l`, `b32` (OpenRouter, quantisation
unknown, `S-58`), `b32c`.

**Measured.** In this repository's copy of that file the set the miner sees is
20 passing episodes, 13 tasks, 540 calls: `b14` 3, `b32` 6, `b32c` 11 (`K-158`).
On Colab those twenty are mined **in the same corpus** as `bir1`'s sixty.

**What it breaks.** The declaration says "the model's own episodes". `b32c` is
the same model tag; `b14` and `b32` are not. Every pattern that can enter the
library can gather support from all three sources, so the sentence "mined from
the 32B's own episodes" is not true of today's file. The corpus the thresholds
were calibrated on (`zihin-2`, `sinir3`) is not in this file either, so
calibration and production do not use the same selection rule.

**Why it was not closed here.** The filter's criterion is a decision: by
**prefix** (`bir1`, this run only) or by **model tag** (32B q4_K_M, which lets
`b32c`'s 11 passes in). The declaration says "model", not "run"; the two give
different corpora and different libraries. That is the user's call and wants a
dated addendum; changing the miner's selection rule mid-run changes the
measurement.

**What it does not bound.** Not the record itself: every episode sits under its
own prefix and `model_ref`, the filter can be applied after the fact, and the
library is a derived projection that can be rebuilt (`03-architecture.tr.md`).

## S-71 — A resumed episode's manifest describes the machine of the first attempt

> **Bounds a claim.** `run_manifests.boot_id` and `created_at` — "the manifest describes the machine and the moment the episode under it ran on"

> **Closing class.** Next round — recording the attempt as a row of its own

The manifest write became resume-aware (`K-155`): when the same `run_id` arrives
a second time the conditions are compared and, if identical, nothing is written.
So the manifest that survives is the one of the attempt that **first claimed**
that id.

**Right for the conditions, not for two fields.** All of
`MANIFEST_CONDITION_FIELDS` is compared, and a `code_commit` difference escalates
to a refusal when a measurement-defining path changed. The two that are not
compared are attempt-specific: `boot_id` and `created_at`. After a Colab timeout
the new session is a new machine, so an episode running on boot B carries a
manifest naming boot A.

**What that breaks.** `boot_id` exists to catch a machine restarting mid-run. For
a resumed episode it answers that question **wrongly**: manifest and episode
belong to different boots and the manifest does not say so. `created_at` is
`uptime:`-relative, so it is relative to the first attempt's clock.

**Why it was not overwritten.** Overwriting means changing the row under a
partly-written episode (manifest and episode present, verdict absent), and that
episode belongs to the first attempt. Making one row right by making another
wrong.

**Closing it.** Recording the attempt in its own row: not one manifest per
`run_id` but one row per attempt, with a link saying which one an episode belongs
to. That is a schema change and it is not being made before the run.

**What it does not bound.** Not the consistency of the conditions: had two
attempts differed in condition the second would have been refused, and that is
proven field by field for nine fields in `tests/test_resumption.py`.

## S-70 — Two of the notebook check's rules read prose by pattern

> **Bounds a claim.** `scripts/check_colab_notebook.py` — "if the check passes, the notebook's prose matches what is declared"

> **Closing class.** Next round — anchoring the rules to declared fields

Five of the check's seven rules are structural: does a path exist, who reads a
variable, is a path hard-coded, is the run command on the guard's line. Those do
not depend on prose. Two do, and their limit belongs in writing.

**One. The list of run-independent citations is keyed to absolute section
numbers.** `15.3` and `15.7` are on it with their reasons: one is the rule that
no episode starts on an unmeasured runtime, the other that results are pushed
rather than pasted, and neither belongs to `bir1`'s section because neither rule
belongs to any run. Renumber the protocol and the list silently permits
different sections. Closing it means moving the rules themselves into a
run-independent section, after which the list is not needed.

**Two. A cadence is separated from a total by a word.** "Every thirty episodes"
is a rate, "Thirty episodes must not start" is a claim, and the number separates
neither - thirty is both the block size and the whole of `b14`'s run. The check
looks at the word **before** the number: `every`, `each`, `per`, `her`, `beher`.
A construction outside that list - "in blocks of thirty" - reads as a total and
fires wrongly; a total phrased with a cadence word escapes. Measured: the rule
in its first form flagged the comment recording what a number USED to be and the
word `episodes` inside a SQL string, and it was narrowed twice.

**What it does not bound.** None of the twelve faults the audit found rested on
these two rules alone: all twelve are put back in `tests/test_colab_notebook.py`
and all twelve are caught. What is bounded is the assumption that a **future**
fault will fall into the same pattern.

**And this is not `S-69`.** That one covers whether the copy that runs is this
file. This one covers how much of the file the check can read when the file
itself is right.

## S-69 — The checks' subject is the repository; the copies in the user's hands are outside

> **Bounds a claim.** Every check in this repository — "if the check passed, the artefact that ran is right"

> **Closure class.** Permanent record — a check inside the repository cannot be the subject of a copy outside it

A check speaks about the tree it reads. `tests/test_colab_ref.py` verifies the
repository's `experiments/colab/zihin-colab.ipynb`, and verifies it correctly —
but if the artefact that runs is not that file, the check has asked the right
question about the **wrong subject**.

**As measured.** The notebook in the repository was corrected to clone `main` and
the test pinned it. The user was running their own copy saved to Drive; that copy
still clones a branch that has merged, and the correction never reached it. The
test was green and the running artefact was stale.

**This class appeared three times this round.** In K-138 a check ran correctly
and answered about the wrong model; in K-142 the right question was asked over
the wrong set; here the right file was verified while a different file ran. What
they share is that the check does not **choose its own subject**.

**Why a mechanism placed inside the notebook does not close it.** A notebook that
checks itself carries the check inside it — so a saved **stale** copy carries a
**stale check**. A check cannot catch a version of itself that predates it. A
self-check added today helps copies saved from tomorrow, not the one in hand.

**The staleness check is one round late.** `scripts/setup/check_prerequisites.py`
reports how far behind the working copy is (`K-151`), but it runs **after** the
clone. If the artefact doing the cloning is itself stale, its cloning of the wrong
branch is already over before the check speaks.

**The limit's own limit: this is not about the notebook.** Every copy in the
user's hands is in the same position — the database on Drive, a downloaded scan,
a clone pulled a week ago, a hand-carried record. K-139 made verifying a
hand-carried record a rule; this record generalises why that rule was needed.

**What it does not bind.** The claim that the repository is internally consistent
stands: 90 citations resolve, 1059 anchors match, the date check is 26 of 26.
What is bound is the claim that this consistency **travels to a copy outside it**.

**A mitigation, not a closure.** The rule is written down: the notebook is opened
from the repository every session (`experiments/colab/README.md` and
`REPRODUCE.md`). A rule is not a check; nothing shows it was followed.

## S-68 — The derived pass-rate threshold is two and a half times the measured one: the design is underpowered

> **Bounds a claim.** A.1 — that the first research question can be answered confirmatorily

> **Closure class.** Next round — a higher pass rate, a larger sample or a design asking for fewer distinctions closes it

The threshold derived from the preregistration (K-146) is between **0.75 and
0.85**, depending on the effect size expected. The pass rate measured on the
primary stratum is **0.280**. The gap is more than two and a half fold.

**What it means.** If every distinction the preregistration declares is to be
readable at once, this model and this sample do not reach that readability.
Results can still be produced, but some of the declarations will come out unable
to return a verdict.

**The direction is known.** The threshold is on the optimistic side because of
`S-66`: if the noise is larger than measured, the threshold rises, it does not
fall.

**Three things could close it and all three are design decisions, not
measurements.** A model with a higher pass rate; a larger sample (the stratum is
105 tasks and the memorisation gate reads half of it); or narrowing which
distinctions count as confirmatory. This record does not say which.

**Two of them were priced, 2026-08-28 (K-147).** The first is **closed**: the
highest point this project has measured, DeepSeek V4 Flash, gives 15/25 =
**0.600** on the action stratum, below the threshold; gpt-4o gives 10/25 = 0.400.
The second asks for **500 action tasks** — on top of today's 105, nearly all of
`test_challenge` — which means changing the definition of the held-out set.

**Addendum — 25 September 2026.** "500 action tasks" is the median of seven
replicates; per replicate the range is 400–557 and some replicates do not reach it
at all (`K-168`). The stratum is now 104.

## S-67 — The memorisation gate is a distinction the design cannot carry

> **Bounds a claim.** Y-2 — the claim that the gain does not come from memorisation

> **Closure class.** Next round — enlarging the subgroup, or demoting the gate to a descriptive statistic, closes it

Y-2 says memorisation is confirmed if the unseen gain falls below **half** the
seen gain. Telling half from none needs an interval narrower than half the
effect, and because the gate reads **half** the sample that interval is 1.42
times the primary one. The requirement lands at **0.35** of the primary width —
the strictest of the six requirements swept.

**What was measured.** If the effect expected is 10%, the requirement is met at
no rate up to the highest one swept (0.85). At 20% it needs 0.85, at 30% and 50%
it needs 0.75.

**This is a finding, not a defect.** The gate was written before the measurement
and it was written correctly; what cannot carry it is not the gate but the size
of the subgroup it reads. The action stratum is 105 tasks and half of it is
about 52.

**What it does not bind.** The gate's **direction** can still be reported: the
seen and unseen gains can be written separately. What cannot be done is to
return a **verdict** on whether the ratio sits below one half.

## S-66 — The interval-width sweep's noise model comes from two cells

> **Bounds a claim.** `results/interval-width.json` — the confidence-interval widths reported by pass rate

> **Closure class.** Next round — re-measuring it once repeated passing episodes exist closes it

The sweep applies a multiplicative per-episode noise whose coefficient was
measured from the record: **two** repeated passing cells. Two episodes in one cell
means seeing a point of the distribution, not its shape.

**The direction is known.** If the real within-episode variability is larger than
what was measured, the intervals are **wider** than reported. Every width in the
table is therefore a **lower bound**, and any row read as "this rate is enough"
sits on the optimistic side.

**What it does not affect.** The table's **shape** comes from censoring, not from
noise: a passing episode costs twelve calls, a censored one twenty to a hundred
and fifty. That gap is an order of magnitude above the noise, so grid B coming
out far wider than grid A does not depend on this limitation.

**It is cheap to close.** Once the accumulation run puts several seeds on the same
task, the coefficient can be re-measured from a real distribution and the sweep
re-run.

**Addendum — 25 September 2026.** The sweep was re-run on the action stratum
(`results/interval-width-action.json`, `K-174`); it uses the same noise model, so
this limitation binds the new table too. The statement above, grid B coming out
far wider than grid A, holds on the action stratum as well: 8.2 times at the
median.

## S-65 — The failure index is behind the corpus: fifteen cards in the record, twenty from today's corpus

> **Bounds a claim.** The retriever's coverage and discriminativeness numbers — all read from the stored index

> **Closure class.** Next round — re-mining the index closes it, but that is an experiment design decision

The stored index `v0-sup1-4bb340a` carries fifteen cards. The same miner at the
same `min_support`, run over today's corpus, produces **twenty**. The difference
is the corpus growing: the forty-five episodes of the three-arm run, prefixed
`uckol`, entered `results/zihin-2.sqlite` after the index was built and were
never mined.

**The skill side has no such gap, but the ratio is severe.** The passing episodes
did not change; the miner still finds a hundred and five patterns today and the
library carries four skills. What takes a hundred and five down to four is the
merging and filtering chain, and that ratio had never been reported.

**What it bounds.** The retriever's coverage and discriminativeness measurements
were all read from the stored index, that is, from an **incomplete** mining of
the present corpus. The direction is known: more cards, more coverage — so
today's coverage numbers are a **lower bound**.

**Re-mining is a decision, not a measurement.** Refreshing the index changes the
retriever's input, and when that happens belongs to the experiment design. This
record only measures the gap; it does not close it. The curve is in
`results/accumulation.json`, the miner in
`scripts/setup/build_failure_index.py`.

## S-64 — Unmerged work is the subject of no check

> **Bounds a claim.** `scripts/check_merged_artefacts.py` — "every artefact named in a report is in the repository"

> **Closure class.** Next round — a check that measures unmerged work closes it

`scripts/check_merged_artefacts.py` calls `gh pr list --state merged --limit 6`
and asks whether the files named in those pull request bodies are in
`origin/main`'s tree. The risk it catches is narrow and deliberately so: the last
commit of a branch is not pushed, the earlier pushes keep CI green, the pull
request merges, and everything in that commit is gone while the report says it
landed (`K-116`).

**The blind spot is inside the definition.** Its subject is *merged* pull
requests; work that never merged does not exist for it. From the nineteenth to
the twenty-sixth of August thirty-five commits sat on a single branch
(`protokol-cevirisi`) and `main` did not move. The check said nothing for that
week, because the question it asks is "are the merged artefacts in place", not
"is there unmerged work". `--limit 6` is a second narrowing: an artefact from an
older pull request is never asked about.

**What showed this was not a check but a hand look.** The same look showed a
second thing: the branch `origin/colab-sonuclari` carries two artefacts of the
14B point (`results/b14-taramasi.json`, `results/colab-ortam.json`) and is the
ancestor of no branch. `scripts/analyze_passes.py` names the first of them in its
usage example, and the file is not in the working tree.

**Addendum, 2026-08-28 — the command it named is now asked.** This record wrote
down that "how many commits are there between the branch and `origin/main`" was
being asked by nothing, and the question bit: the Colab notebook kept cloning a
branch that had merged, the files added after it were absent in a clean checkout,
and the fault named itself a `FileNotFoundError` — which reads as "never
written". The preflight now refreshes `origin`, counts the difference, and fails
when the copy is behind (K-151). **The other half of this record stays open:**
work that never merged is still the subject of no check.

**What is not measured is mechanical.** "How many commits are there between the
branch and `origin/main`" is a single command, and no check asks it today.

## S-63 — Two of the three runs the precondition rests on are ceiling-limited, and one is not in the record

> **Bounds a claim.** K-58 — the precondition finding, "there is no band on the declared axis"

> **Closure class.** Permanent record — the runs were made at the ceiling they were made at; loosening it afterwards would be re-running them

K-60 requires that, before a zero is interpreted, every parameter that could bind
is shown not to bind, and the threshold for the ceiling-hit rate is **10%**. The
three runs the precondition finding rests on had never been measured against it.
They have been now:

| Run | Episodes | Ceiling hits | State |
|---|---|---|---|
| `bant2` | 30 (in the JSON) | **not in the record** | the termination reason was never written, and no episode with that prefix exists in any series |
| `bant3` | 30 | **0.0%** | below the threshold; this zero is not ceiling-limited |
| `bant3-kapali` | 26 | **96.2%** | far above it |

**For `bant3-kapali` this is no surprise, but the note was needed.** In that run
the stopping rule was **entirely off**, so the only thing that could end an
episode was the ceiling. Being high by design does not mean the result is not
ceiling-limited: on the contrary, that zero is a **lower bound** and should have
been reported as one.

**For `bant2` the answer is not "zero" but "undetermined".** In its JSON the
`termination` field is empty for all thirty episodes, and no series database
holds an episode with that prefix. Counting an empty field as 0% would be turning
an absence into a negative (K-131). That run says **nothing** about the ceiling.

**What changes and what does not.** The precondition finding itself stands: all
three gave zero, and a ceiling cannot manufacture a zero, only hide one. What
changes is the finding's **strength**: "there is no band on the declared axis"
rests not on three independent clean measurements but on one clean measurement
(`bant3`), one lower bound (`bant3-kapali`) and one undetermined (`bant2`).

**The audit is itself a finding.** The rule (K-60) existed, the threshold (10%)
existed, and the three runs had never been measured against it. A rule being
written down does not mean it was applied; what shows it was applied is a
measurement.

## S-62 — The band label describes the reference solution's path, not the difficulty

> **Bounds a claim.** Every per-band result reported — the band scan's `1-10`, `90+` labels

> **Closure class.** External fact — `num_api_calls` is AppWorld's field and its definition is not ours

The step ceiling is derived from the anchor and the band label comes from the
anchor. The anchor (`num_api_calls`) counts how many API calls **the reference
solution** made, not what the task requires.

**Measured.** In the 14B run `09b0ee6_1` carries an anchor of **102**, which puts
it in the `90+` band, and it was passed in **six steps**. The task text asks for
six artist names — an **answer task**; `ground_truth/evaluation.py` carries two
tests and only one is `no_op_fail`, a string equality. `09b0ee6_2` is the same
shape: anchor 97, six steps.

**The effect runs both ways.** Per-band rates cannot be read as "it passed in the
hard band too"; and the ceiling formula gives these tasks a ceiling far above
what they need, so the ceiling-hit rate looks low on them.

**Mitigation.** When a per-band result is reported, what the label measures is
written next to it. `meaningful_total` is already in the record as well: how many
of a task's tests would eliminate an agent that does nothing is measured, and the
weight of a pass can be read from it.

## S-61 — The scale axis's points were measured on three different cards

> **Bounds a claim.** 02-research-question, the second question — how the effect changes with model size

> **Closure class.** Permanent record — the measurements were taken on the hardware they were taken on; moving them to one card later would be re-running them

1.5B, 3B and 7B on the local **RTX 4070** (Ada, compute 8.9), 14B on Colab's
**L4** (Ada, 8.9), 32B on Colab's **A100** (**Ampere, 8.0**). Ampere is a
different generation, and its support for flash attention and a `q8_0` KV cache
may not be the same.

**Why this is a limitation.** The axis is supposed to be a size axis. Changing
the card introduces a second variable: the same request can land on a different
kernel, and if the KV cache type is unsupported it silently falls back to `f16` —
twice the memory, a different computation.

**The mitigation, and why it is not enough.** `runtime_facts` reads the
**requested** and the **effective** value separately out of the server's own log:
how many layers are on the GPU, whether flash attention is effective, what the KV
cache's real type is. The `comparability` verdict is printed before the run, and
if it is not `COMPARABLE` the result is labelled not comparable with the local
measurement. It was read on the L4 and it held (49/49, enabled, q8_0). But that
verdict compares **the three things it measures**; every difference between the
cards that we do not measure stays open.

## S-58 — The 32B measurement ran with two declared conditions drifted

> **Bounds a claim.** docs/reports/b32-olcumu.md — the comparability of the 32B result with the boundary control

> **Closure class.** Next round — re-running the measurement in the declared condition closes it

Protocol §14.2 said "the stopping rule, the threshold and the shield mode are the
same as the boundary control". The manifests were compared: `no_progress_limit`
is 15 in `sinir3` and **40** in `b32`; `shield_mode` is `off` in `sinir3` and
**shadow** in `b32`.

**The cause is not in the runner but in how the condition was written.** The
runner read the current value in `config/recording.yaml`, and the configuration
has moved from 15 to 40 since the boundary control. The condition was written
**relatively** ("the same as the boundary control") and the thing it referred to
shifted underneath it.

**The direction of the effect is measurable and it does not destroy the
finding.** A looser threshold runs episodes longer, which makes passing easier,
not harder; the six passes are not an artefact of a tight rule. What is destroyed
is the **direct comparison** with `sinir3`'s 20/30.

**What did not drift.** The model tag, the output budget (4000), the temperature,
the base seed, the task set and the split are the same; that the task set is
identical to `sinir3`'s was verified separately.

**A third instance, 2026-08-25, by a different mechanism.** *(Date correction,
2026-08-26: this paragraph was first dated 2026-08-20. That is the day section 15's
conditions were declared, not the day of the finding. The run it describes is
`b14`, whose first episode is stamped `2026-08-25 08:51` UTC, and the commit that
wrote the finding is `f01132e`, at `10:55` UTC the same day.)* In the first two the
condition was written *relatively* ("the same as the boundary control") and the
value underneath moved. This time it was written *absolutely* - protocol section
15.2 says `max_output_tokens: 400` and `no_progress_limit: 15` - and it still did
not hold. The cause was measured:

- `max_output_tokens`: the protocol says 400, `config/recording.yaml` carries
  4000, and the runner reads the configuration. 400 was never in the
  configuration; it was copied into the protocol from a `bant3` manifest, and
  `bant3` took that value **before the configuration had the key at all**
  (commit `fc9101a`).
- `no_progress_limit`: the notebook passed `--stop-threshold 15`, but
  `measure_band.py` had no such flag; it scanned `sys.argv` for
  `--allow-dirty-tree` alone and **dropped the rest in silence**. The runner read
  the configuration's 40.
- `shield_mode`: the protocol says `off`, the runner records `shadow`.
  `ShieldMode` has no `off` member at all; `off` exists only in manifests from
  runs made before the shield was mounted. So this field cannot be repaired by a
  flag - it is waiting on a measurement decision.

**The lesson is not absoluteness but a single source.** Writing the number down
is not enough: the place it is written and the place it is read have to be the
same. The repair is in K-136, and a check now compares the two
(`scripts/check_declared_conditions.py`).

## S-59 — The 32B result was read from an incomplete set and under a binding ceiling

> **Bounds a claim.** docs/reports/b32-olcumu.md — the number of passes measured at 32B

> **Closure class.** Next round — re-running with a higher cost ceiling and a higher step ceiling closes it

Two separate gaps bound the same number.

**The set is incomplete.** 27 of the thirty tasks were written; the cost ceiling
(3.00 dollars) stopped the run and two episodes could not be written. §6 forbids
quoting an incomplete episode set.

**The ceiling was binding.** The ceiling-hit rate is **22.2 per cent** (6/27) and
K-60 wants it below 10. Any result under a binding ceiling is a lower bound.

**The incompleteness is asymmetric.** Episodes that did not run can hide a pass;
they cannot manufacture an observed one. So the **existence claim** ("there is a
band") stands and the **rate claim** ("this many passed") does not. No rate was
written in the report.

## S-60 — A reproducibility verification belongs to a moment; an outside service can invalidate it retroactively

> **Bounds a claim.** REPRODUCE.md — "it installs from scratch from a clean clone"

> **Closure class.** Permanent record — the outer links of the chain are not ours; upstream recovering does not change that the verification belonged to a moment

REPRODUCE.md was executed from a clean clone and it passed. That execution
happened while the upstream AppWorld repository's Git LFS objects were **still
being served**. On 2026-08-20 they stopped: GitHub answers 403 with `This
repository exceeded its LFS budget`. The same answer came from a Colab runtime
and from the development machine, so it is a fact about upstream and not about
either network.

**What was verified was a chain, and its links are not ours.** "It installs on a
clean machine" looks like one claim but rests on at least four outside services:
GitHub's git access, GitHub's LFS storage and its **budget**, PyPI, and
AppWorld's data download. When one of them closes, the claim is falsified without
us changing anything. A green verification does not say "this installs"; it says
"this installed, that day, with those services".

**Only a fresh install is blocked.** The installation on the development machine
is untouched: the objects were already fetched and `.venv` is in place. The
measurements, the reports and the record database are untouched too. The only
thing broken is that someone without an existing installation cannot build one
today — which is exactly what the reproducibility claim asserts.

**S-01 wrote this class down in advance, but with a different mechanism.** There
the risk is told as "the branch is rewritten or the commit becomes unreachable".
That is not what happened: the commit is reachable, the tree is in place, only
the LFS objects are not served. The reachability of what was pinned and the
reachability of **the objects it depends on** are two different things, and
pinning does not protect the second.

**The mitigation, and its limit.** Under `vendor/appworld/` there is a mirror
built from the pinned commit; the bootstrap tries upstream first and falls back
only when LFS refuses. When the mirror is used the manifest carries
`appworld: mirror a072b7a86 (2026-08-20)`, so the source of a measurement is not
hidden. This does not **rescue** reproducibility, it moves it: whoever uses the
mirror is now trusting us rather than upstream. Because a bundle's sha256 equals
its LFS object id the sameness can be measured; but that the object id is the
right id rests on our record until upstream returns.

## S-01 — AppWorld is pinned to a moving branch, not a published release

> **Bounds a claim.** REPRODUCE.md — "can be installed from scratch on a clean machine"

> **Closure class.** External fact — the upstream branch is not ours; closing it depends on AppWorld publishing a release

The `main` branch carries version `0.2.0.dev0`, an unpublished development
branch. Reproducibility rests entirely on commit pinning. If upstream rewrites
the branch or the commit becomes unreachable, the installation cannot be
reproduced.

**Impact.** Medium. **Mitigation.** The commit hash goes into the manifest. In
the long run we may need to keep our own copy of the repository.

**It happened on 2026-08-20, but not by the mechanism written here.** The branch
was not rewritten and the commit did not become unreachable; upstream's Git LFS
budget ran out and the `.bundle` objects the commit depends on stopped being
served. The copy called "may be needed in the long run" was needed that day and
was taken (`vendor/appworld/`). The detail and its general form are in S-60.

## S-02 — Reference solutions exist only in train and dev

> **Scope.** records which splits carry reference solutions; we make no claim that rests on it

> **Closure class.** External fact — which split publishes reference solutions is upstream's decision

~~`appworld download data` downloads in `minimal` mode by default and reference
solutions may never reach us.~~

**Measured in stage 2, partly refuted.** The default download brings 147 tasks
in `full` mode: 90 from train and 57 from dev. The `mode` field in
`metadata.json` says so explicitly. Those tasks all carry `solution.py`,
`compiled_solution.py`, `api_calls.json`, `required_apps.json`,
`required_apis.json` and `generator.py`. The remaining 585 tasks are in
`minimal` mode and carry none of them.

**Residual impact.** Medium. The test splits have no reference solution, so the
step ceiling for tasks there cannot be tied to a reference length. But the API
call count per task is readable through `metadata.num_api_calls` for all 732
tasks, and that field agrees exactly with `api_calls.json` on the 147.

## S-03 — The per-task app list is absent from the test splits

> **Bounds a claim.** PILOT_REPORT.md shield section — that the permitted app set is task-specific

> **Closure class.** External fact — the shape of `allowed_apps` and the distribution of `required_apps.json` are upstream

`world.task.allowed_apps` returns every app for every task; it gives no
task-specific list. The task-specific list lives in
`ground_truth/required_apps.json` and exists only in train and dev. For the test
splits we have counts: `metadata["num_apps"]` and `metadata["num_apis"]`, both
present for all 732 tasks.

**How it was worked around in stage 2.** A proxy that extracts app names from
the task instruction was written and tested on the 147 tasks that have a
reference list. On 111 of the 147 the set matched exactly, 75.5 per cent.
Jaccard similarity 0.878.

**Residual impact.** Medium. App names in the test splits come from a proxy
measurement and one task in four does not match exactly. The proxy's error
profile is known: it over-counts `simple_note` and misses `phone` and `venmo`.
It never over-counted for `amazon`, `splitwise` or `todoist`, so it is reliable
whenever it sees those three in the difficulty split.

**14 August addendum: the proxy is the shield's specification, and its accuracy
is the shield's limit.**

The shield's permitted app set is derived from the task text; deriving it from
ground truth would hand the shield an oracle it will not have outside the
benchmark. So the proxy is not an approximation but the definition itself — and
its accuracy is directly the shield's accuracy.

The proxy went into the repository (`src/zihin/allowed_apps.py`) and onto the
`MEASUREMENT_DEFINING_PATHS` list. Before that its code was outside version
control and lived only in the stage 2 report; a component that affects the
measurement sitting outside version control was a gap by itself.

Measured again (`scripts/setup/measure_app_proxy.py`, 147 tasks, train + dev):
exact match 75.5 per cent, mean Jaccard 0.857. Misses were `phone` 30, `venmo`
6, `file_system` 3; over-counts `simple_note` 6. All 36 non-matching tasks have
at least one miss, so the shield's **false positive upper bound today is 24.5
per cent**.

**Most of the misses are a real limit, not a defect of the proxy.** In all
thirty `phone` misses the instruction says "roommates", "siblings",
"coworkers"; the relationship lives in the `phone` app but the text never names
the app. No text-based proxy can rescue that.

This is not an experimental artefact but **a real property of the
distribution**: in real use, too, all you have is the user's sentence. Detail in
`docs/reports/izinli-uygulama-vekili.md`.

## S-04 — The two components of the verifier verdict may not be separable

> **Bounds a claim.** 05-experiment-design — the episode-level "unexpected side effect" label

> **Closure class.** Next round — extraction from the `requirement` texts was never attempted; attempting it closes this or settles it

AppWorld's `TestTracker` class gives `passes` and `failures` lists. It may not
give the paper's two distinctions — whether the expected changes are complete,
and whether any unexpected change is present — as two separate booleans.

**Impact.** Low. **Mitigation.** The two relevant columns stay in the
`verifier_results` table. If they cannot be extracted they stay `NULL`.

**Where we looked.** The evaluation JSON carries a `requirement` text and a
`label` per test. Across eight evaluations only two labels appeared,
`no_op_pass` and `no_op_fail`; but the agent did nothing in that sample, so the
label set is not representative. The two components do separate in the
`requirement` texts — "assert model changes match ..." tests the expected
change, "assert no new ... was added" tests the unexpected one. That is the
starting point if extraction is attempted; for now both columns are written
`NULL` (`src/zihin/verification.py`).

## S-05 — No response body at the action level, and no status code either

> **Bounds a claim.** 07-failure-taxonomy — action-level failure classes

> **Closure class.** External fact — the three fields of `api_calls.jsonl` are AppWorld's log format; measured and confirmed

**Measured and confirmed in stage 3, and it came out narrower than expected.**
`logs/api_calls.jsonl` carries only three fields per record: `method`, `url` and
`data`. No response body, and no status code.

**Impact.** Medium. The `actions.result_status` and `actions.error_class`
columns cannot be filled from this source and stay `NULL` for now. Whether a
step succeeded is readable only from the observation text, not per individual
call.

**Mitigation.** The columns stay. Filling them requires our own measurement
layer to wrap the call; that is out of scope for now.

## S-16 — Action-level response instrumentation does not exist yet

> **Bounds a claim.** 07-failure-taxonomy — action-level failure classes (three-gate blame attribution rests on the same response data)

> **Closure class.** Next round — the API client will be wrapped and the response and status code recorded; the transport layer is outside K-19

`api_calls.jsonl` carries neither a response body nor a status code (S-05).
Three things rest on this data: the action-level failure taxonomy, failure index
mining, and three-gate blame attribution.

**Impact.** High, and it has a deadline. Accumulation happens once and cannot be
back-filled. If the instrumentation is not built before accumulation starts,
then when the gap is noticed the whole corpus has to be re-run.

**Order of preference.** First the API client gets wrapped and the response and
status code recorded; this transport layer is outside the scope of the scaffold
constraint (K-19). Failing that, we fall back to parsing the step output, but
its brittleness and the cases where it misses will be measured. There is no
third option: continuing without action-level status kills half of the failure
index mechanism.

**Closed.** `src/zihin/api_capture.py` wraps the `Requester._get`, `_post`,
`_patch`, `_delete` and `_put` methods; response body and status code are
captured, 401 included. The recorder now writes actions from here and the
`actions.result_status` and `error_class` columns are populated.

The capture point is before the `raise_if_failure` call and a separate test in
`tests/test_api_capture.py` pins that. If the order breaks, exactly the cases we
care about are missed and the measurement looks green: in the first probe seven
of seven calls were reported 200, when two of them had failed.

Both sources are kept side by side. The call count seen by the capture layer is
compared per step against the count from the `api_calls.jsonl` delta; any
divergence is recorded and goes into the report.

## S-18 — The cold regime is not uniform at 7B

> **Bounds a claim.** K-51 — that residual variance is measured per model

> **Closure class.** Measured — ten cold episodes were run and 7B did not come out uniform; the answer itself is the constraint

Ten cold episodes were run per model. 1.5B and 3B gave the same trajectory ten
times out of ten. Nine of 7B's runs gave one trajectory and one gave another;
the diverging run finished in 6 steps instead of 12. Unloading was verified
before every episode, so the cause is not regime mixing.

**Impact.** High. K-21 chose the cold regime because it was the only option with
measured uniformity; at 7B that reason does not hold.

**Mitigation.** K-48 takes over: the determinism goal is dropped and load state
becomes a recorded covariate. Whether the rule applies per model or to all three
points at once is not written in K-48 and has to be decided.

## S-19 — 3B's zero calls is not a capability floor but a systematic error

> **Bounds a claim.** K-58 — reading the precondition gate as "the model is not capable"

> **Closure class.** Next round — fixing the source of the systematic error and re-running 3B changes the floor reading

S-14 was opened for the smallest point of the scale axis. All ten episodes run
with 3B produced zero API calls and all of them hit the twenty-step ceiling. On
first reading this looked like a second floor effect.

**Classification says otherwise.** All 200 steps of the ten episodes fall into
K-36's fourth category: code was produced, it parsed, and it raised an execution
error without producing any action. And all with the same error:

```
NameError: name 'playlists' is not defined
```

**The mechanism is in the prompt.** The reference instruction's example solution
defines `playlists = []` and fills it page by page. The models copy the later
part of the example (`for playlist in playlists:`) but do not carry the
definition over. The same error appeared in stage 2 in 1.5B's "empty success"
episode.

**Impact and direction.** The diagnosis is not "the model is weak" but "the
model makes a specific error systematically on this scaffold". If it were a
capability floor, 3B would not be expected to do worse than 1.5B; yet 1.5B makes
19 calls on the same task.

**This has a twofold consequence and the second one is a validity risk.** On one
hand there is a band to measure, because the error is a fixable error. On the
other hand, if the mechanism fixes this error, the effect we measure may not be
"the contribution of accumulated experience" but "the closing of a single
prompt-copying error". If the effect comes out large it will have to be
separated.

**What will not be done.** The prompt is not fixed. The reference scaffold is
taken unchanged (K-23, K-26) and this error is the scaffold's own behaviour.
Fixing it will be the mechanism's job, not ours.

**Three models, three different failure shapes.** Step categories on the same
task:

| Model | Action-producing steps | Dominant failure | Call status |
|---|---|---|---|
| 1.5B | 190/200 | Login loop with the wrong password | 19/19 calls 401 |
| 3B | 0/200 | `NameError`, undefined variable | no calls |
| 7B | 40/120 | Silent empty success (60/120) | 5/5 calls 200 |

None of them solves the task, but their reasons differ, so the three cannot be
collected under one floor-effect heading. 1.5B's loop is the behaviour K-20
predicted: under a fixed temperature and seed the agent repeats the failing
call.

**Its limit.** One task. Generalising the pattern needs the pilot.

## S-17 — The step ceiling and the anchor are in different units

> **Bounds a claim.** 05-experiment-design — that the ceiling-hit rate is kept under 10 per cent

> **Closure class.** Next round — the conversion factor will be measured in the pilot, not assumed (K-43)

The ceiling is in units of model calls, the anchor (`metadata.num_api_calls`) in
units of API calls. The conversion between them is unknown.

**Impact.** High. A wrong conversion factor shifts every ceiling and directly
affects the censoring rate. **Mitigation.** The conversion will be measured in
the pilot, not assumed (K-43). In stage 3 one episode fitted nineteen actions
into twenty steps, but a ratio cannot be derived from one task.

## S-15 — The list of write-performing GET endpoints is a lower bound

> **Bounds a claim.** 04-threat-model — that the shield's write set is complete

> **Closure class.** Next round — the list will be widened by runtime measurement; it may stop being a lower bound

The shield's read/write predicate will rest on the `method` field. A static scan
showed fifteen GET endpoints containing a write call (K-41). But the scan only
sees direct calls in the handler body: of the 302 non-GET endpoints, writes were
found in 211, and the remaining 91 delegate the work to a helper function.

**Impact.** High. A missed write endpoint is exactly the case the shield has to
stop. **Mitigation.** The list will be widened by runtime measurement before
stage 4: GET endpoints get called and the database digest is checked for change.

## S-06 — One server process holds one world at a time

> **Scope.** records that the AppWorld engine holds one world per process; an operational constraint

> **Closure class.** External fact — one world per process is the AppWorld engine's design

The AppWorld engine can run in a separate process, but starting a second world
inside one process returns HTTP 400. The reason is freezegun faking time
process-wide, and avoiding database connection leaks.

**Impact.** High. Parallel episodes need a separate server process per port.
That is directly a memory and core budget problem.

## S-07 — The scaffold has truncation logic of its own

> **Scope.** records the scaffold's own truncation logic; with no assembler written it bounds no claim today

> **Closure class.** External fact — the truncation logic is inside the reference scaffold and the scaffold is frozen by K-19

The reference scaffold replaces older observations with `[NOT SHOWN FOR
BREVITY]`. When our context assembler arrives the two mechanisms will collide.

**Impact.** High for the next task, zero now. **Current state.** Untouched.

## S-08 — Three models do not fit in 8 GB of VRAM at once

> **Scope.** records that three models do not fit in 8 GB of VRAM; a hardware constraint

> **Closure class.** External fact — a hardware constraint; 8 GB of VRAM is outside the measurement design

Roughly 1.1, 2.0 and 4.7 GB, plus the KV cache for a 32k context. Switching
models requires an explicit unload, which inserts a reload delay between
episodes.

**Impact.** Medium. **Measurement.** Real numbers land in stage 4.

## S-09 — The WSL memory limit is host-wide

> **Scope.** records that the WSL memory limit is host-wide; an operational constraint

> **Closure class.** External fact — `.wslconfig` is host-wide; a constraint of the operating environment

`.wslconfig` applies to every distribution, docker-desktop included. The 8 GB
limit binds all of them, not just ours.

**Impact.** Low.

## ~~S-10 — Reaching Ollama on the Windows host from inside WSL is unsolved~~

~~The network mode was left at the default NAT. Reaching the host from WSL needs
either switching to mirrored mode or finding the host IP dynamically and opening
a firewall rule.~~

**Closed, stage 1.** `networkingMode=mirrored` solved it. The server stays bound
to `127.0.0.1` and WSL reaches it. No firewall rule was needed (K-34).

## ~~S-11 — Agent behaviour is unstable even at the same seed~~

~~Three episodes run with the same task, same model, same seed and same
temperature made 19, 1 and 19 API calls respectively.~~

**Closed, stage 2.** The source of the instability was not randomness but
whether the model was loaded in memory. litellm passes the seed correctly. The
first inference after a cold load differs from the warm one but is stable in
itself. At the episode level two cold runs gave exactly the same trajectory (19
calls) and two warm runs gave exactly the same trajectory (1 call). The full
measurement is in `docs/appworld-facts.tr.md`. Continued in S-13.

## S-13 — There is one more server-side state we do not see

> **Bounds a claim.** K-21 — that the cold regime is uniform

> **Closure class.** Next round — the per-episode unload protocol will be measured and settled under K-21

An uncertainty remained when S-11 closed. "Warm" is not a single state. The same
task gave 1 API call with a warm model in one run, and 0 with a warm model again
in a twelve-episode measurement batch. The difference is which requests the model
had seen before. We do not see that state from the client.

**Impact.** Medium. Reproducibility only holds if the server's state is
controlled. **Mitigation.** The only reliable protocol measured is unloading the
model before every episode. Stage 4 will decide, under K-21.

## S-14 — The smallest point of the scale axis is stuck to a floor effect

> **Bounds a claim.** 02-research-question second question — the three points of the scale axis

> **Closure class.** Next round — if the precondition gate lifts, the smallest point of the scale axis gets measured again

In eleven of the twelve episodes run with
`qwen2.5-coder:1.5b-instruct-q4_K_M` the agent hit the twenty-step ceiling
without calling any API. Across 223 model turns there was 1 API call in total,
0.0045 per turn.

**Impact.** High. There is no band to measure at this point, so the smallest end
of the scale axis cannot show the mechanism's contribution.

**Stage 4 warning.** The same task was also run with 3B and 7B and all three hit
the twenty-step ceiling; none finished the task. This suggests the floor-effect
worry may cover the axis rather than just 1.5B. But the measurement is one task
and one seed per model; the seeds derive from `run_id`, so they are not
comparable across models. The scope was therefore not widened, only the warning
added.

**Mitigation.** The decision belongs to the pilot. The rule was declared before
the pilot: if 1.5B produces no solution in the baseline condition, the axis
drops to 3B and 7B, two points remain, and the scale question narrows further
into an exploratory one. There is no upward compensation because 14B does not
fit in 8 GB.

**Addendum, 2026-08-20.** The last sentence no longer holds, and it is not
deleted: the obstacle was the hardware, and the hardware changed. 14B runs on
Colab's GPU and entered the axis as a fourth point (K-133), with a dated
addendum to pre-registration A.11. There **is** upward compensation; there was
none *on the local machine*.

## ~~S-12 — The reset test is not under CI protection~~ — CLOSED: K-100 put the data into CI

**Closed, 18 August 2026.** The criterion was applied, not asserted.

**Closure criterion: it was a design gap and the gap was filled.** K-100 added
the `appworld install` and `appworld download data` steps to CI, and the
`pytest` filter became `-m "not model_server and not sandbox"` — so the
`appworld` marker is no longer filtered out.

**Evidence, two pieces.** The test lives in `tests/test_appworld_reset.py` and
carries `pytestmark = pytest.mark.appworld`. Collection was run with the filter
CI uses: in the output of `pytest -m "not model_server and not sandbox"
--collect-only`, `test_appworld_reset` appears **once**, so the test really is
collected in CI.

**What did not close.** The test was shown to run in CI; whether the test
measures the right thing is a separate question and this record never asked it.

The per-episode database reset is one of the project's most important
invariants. But its test is marked `appworld`, meaning it wants the 198 MB of
downloaded data, and it does not run in CI.

**Impact.** Medium. **Mitigation.** The local-only checks were listed and are run
before every stage merge. The result goes into the stage report with its date
(K-35).

## S-20 — A single well-formed example could close the small models' dominant error

> **Scope.** records that an untried fix might work; work not done

> **Closure class.** Next round — an untried fix; trying it closes this or refutes it

The most common termination in 3B's episodes is code referring to an undefined
variable. Instead of writing a call through `apis` the agent refers to a name
never assigned, and the step ends without producing any API call.

The limit is not specific to 3B. In a sweep across five tasks, 90 of 1.5B's 144
steps fell into the same category (62.5 per cent), and in three of the five
tasks every step in the episode was in that category. The measurement was taken
with the stopping rule on, so the ratio is conditional on the threshold; even so
the category's dominance points the same way in both models.

This error is about the instruction itself. The scaffold's instruction contains
an example showing correct usage, but not enough for the model to imitate it. A
single well-formed example added to the instruction could largely close this
error.

**Measurement made the limit harder still: the example itself does not work.**
Line 153 of `prompts/react_code_agent/instructions.reference.txt` is this:

```text
spotify_password = [account_password["account_name"] == "spotify" for account_password in passwords][0]["password"]
```

The line is left unformatted because it is a quotation; this is how it stands in
the instruction. The list comprehension produces booleans, `[0]` gives a boolean,
and `["password"]` then raises `TypeError: 'bool' object is not subscriptable`.
The instruction shows a successful login output after this line, that is, it
presents a line that does not work as though it had worked. A second gap:
`print(login_result)` prints the dictionary but the `login_result["access_token"]`
extraction is never shown, and in measurement the model passes the whole
dictionary to the `access_token` parameter and gets a 401.

Across 45 episodes the broken pattern was written 34 times (in 13 episodes) and
produced that `TypeError` 11 times. In the same episodes the correct filter
appears 488 times, so the model mostly corrects it: the defect is real but not
the dominant cause on its own.

The instruction is still not changed (K-19, K-23). Changing it would lose
comparison with AppWorld's published baseline numbers, and those baselines ran
with the same defective instruction.

**The defect is not a confounder, but it may explain part of the effect.** The
broken example is identical in all six conditions; it does not enter the
difference between the baseline and the mechanism conditions. So it is not a
confounder in the technical sense but a scope item that pulls the baseline down.

The risky side is in the interpretation. This defect is the mechanism's **most
visible target**: a compiled skill card or a failure index entry will carry a
well-formed example showing the right password selection and the
`login_result["access_token"]` extraction. Part of the gain we measure would then
mean not "the mechanism uses accumulated experience" but **"our cards repair the
benchmark's broken example"**.

The two cannot be separated by looking at the same number. What separates them is
K-59's contrast: because the repair is structural, an irrelevant card does the
same job. If the irrelevant retrieval condition also gains, the interpretation
goes to the first branch, the verdict "the value is in the structural template".

**Impact.** High, and on the interpretation rather than the result.
**Mitigation.** K-56's mandatory condition, K-59's interpretation written in
advance, and this item being written into the paper as scope.

**Impact.** High, but on the interpretation rather than the result. If the
mechanism shows a gain at 3B, how much of that gain comes from skill knowledge
and how much from merely seeing a well-formed example cannot be told apart.

**Mitigation.** The instruction is not changed. Changing it would break K-19 and
lose comparison with AppWorld's published baseline numbers. Two things are done
instead: this limit stands written here, and the separation is left to the
`irrelevant_retrieval` condition — that condition keeps the card's form and
breaks its content, so it separates the contribution of "seeing an example" from
content (K-56).

## S-21 — Residual variance gets an upper bound, not a point estimate

> **Bounds a claim.** K-51 — the upper bound written for residual variance

> **Closure class.** Measured — zero divergence over thirty episodes; more episodes narrow the bound, they do not take it to zero

The first measurement used one task with the stopping rule off: one of twenty
episodes at 7B gave a different trajectory, and ten episodes each at 1.5B and 3B
came out uniform.

The measurement was spread over one task from each of five scenarios, six cold
episodes per model per task, stopping rule on. At 1.5B and 7B all thirty
episodes came out identical within a task; there is no deviation in the
twenty-step episodes that hit the ceiling either.

**Zero divergence does not mean a zero rate.** Seeing no divergence in thirty
episodes shows the rate is small, not that it is zero. The number that goes into
the pre-registration is therefore an upper bound. Clopper-Pearson one-sided 95
per cent upper bounds:

| Measurement | Regime | Divergence | Upper bound |
|---|---|---|---|
| 1.5B, five tasks | rule on | 0/30 | 9.5% |
| 7B, five tasks | rule on | 0/30 | 9.5% |
| The two pooled | rule on | 0/60 | 4.9% |
| 1.5B, one task | rule off | 0/10 | 25.9% |
| 3B, one task | rule off | 0/10 | 25.9% |
| 7B, one task | rule off | 1/20 | 21.6% |

The number entering the noise floor is **9.5 per cent** per model, and the regime
it was measured in is written next to it: stopping rule on, that is, the regime
the experiment will run in. The pooled 4.9 per cent holds only under the
assumption that the two models share a rate; because K-51 wants the rate per
model, the floor is taken per model.

**An axis the measurement did not see got tested by accident.** The sweep had
run inside a single Ollama process. The server later died and was restarted from
the script; the censoring measurement ran in that new process and with a
different runner script. The five tasks of the two models, that is ten
configurations, repeated the sweep's step and call counts exactly — including
7B's two ceiling-hitting episodes (20 steps, 19 and 20 calls). The match is at
the step and call level, not at the trajectory-summary level: the recording
script does not compute that summary. Even so, a server restart enters the
tested sources of residual variance only to that extent.

**Residual limit.** Bringing the upper bound down to 2 per cent needs 149
episodes with zero divergence; we have thirty per model. Narrowing it depends on
the pilot's repeat runs. The two regimes cannot be pooled: with the rule on the
episodes get shorter and the opportunity to deviate shrinks, so the two
measurements do not measure the same quantity. The 1/20 of the first measurement
is not refuted, it belongs to a different regime.

**Impact.** Low. The noise floor no longer rests on one task and is in a state
where it can go into the pre-registration. 3B's residual variance was not swept
in the rule-on regime; because whether it stays on the scale axis depends on
K-53, its sweep was left until after that decision.

## S-22 — The censoring rate rests on five tasks and one episode per model

> **Bounds a claim.** K-53 — that the censoring rate is a result

> **Closure class.** Next round — five tasks and one episode per model; the bound narrows as repeats increase

K-53's criterion was rejected on all three models: fifteen of fifteen episodes
failed the verifier, and the 95 per cent lower bound per model is 54.9 per cent.
The result itself is strong but the sample it rests on is narrow.

The five tasks were not chosen at random. They came from the residual variance
sweep, and that sweep had chosen them for a different purpose, one task per
scenario. There is no evidence that they represent the difficulty distribution of
the train split. There is also one episode per model; the rate measures a model's
behaviour on those five tasks, not in general.

**Impact.** Medium, and not one-sided. If the five tasks are harder than average
the real censoring rate is lower; if easier, it is higher still. The second
possibility threatens the whole scale axis, because 7B does not meet the
criterion either.

**A second limit: the ceiling was fixed.** All fifteen of the fifteen episodes
ran with a fixed 20-step ceiling, whereas K-43 ties the ceiling to
`k × num_api_calls`. The five tasks' anchors are 10, 29, 71, 145 and 195. So on
`6104387_1` the reference solution needs 195 calls while the agent was given 20
model calls; that episode's failure may be a result of the ceiling rather than
the model. Only `29caf6f_1` (anchor 10) ran with a ceiling consistent with its
anchor. The conclusion "the criterion is not met" stands, but how much of the
cause comes from the model does not follow from this measurement.

**Mitigation.** What goes into the pre-registration is the rule, not the number.
But the rule's first wording was also wrong: it said "the censoring rate must be
below 10 per cent" and merged the two quantities K-53 separates. The correct form
is this — the ten per cent rule belongs to the **ceiling-hit rate**, while the
censoring rate is a result and is not bound by that rule. The threshold of the
stay-on-the-axis criterion comes from the requirements of the matched design; its
exact number comes from the pilot.

The rate will be measured again on the pilot's own sample and with a per-task
ceiling. The function of the fifteen episodes here is to leave the assumption
"7B is not a problem" without support.

## S-27 — The band sweep ran under the old stopping rule, and the precondition gate rests on it

> **Bounds a claim.** K-58 — the band sweep the precondition gate rests on

> **Closure class.** Next round — re-running the band sweep under today's stopping rule changes what it rests on

The band sweep's thirty episodes ran under the old rule that said "a successful
call is progress", with a four-step threshold. That rule was later measured to be
wrong (S-25) and fixed.

**Measured contamination:**

| Termination | Episodes |
|---|---|
| `no_progress` | 16/30 (53%) |
| `step_ceiling` | 9/30 |
| `agent_finished` | 5/30 |

Of the sixteen episodes that closed with `no_progress`, **fifteen would not have
been cut by the corrected rule**: their endpoint-based stalls run between 2 and
6, and the new threshold is 15. Six of them closed at four steps.

**Impact.** High. Half of the thirty episodes may never have had a chance to
succeed, and **the 0/30 result is not a clean measurement.** The precondition
gate fired on 11 August 2026 on the strength of that result; the reopening of the
model family question depends on it too.

**Counter-evidence, weakening but not closing.** The old rule did not cut every
episode at four: in the diagnostics, 45 episodes ran 958 steps, a mean of 21, and
two episodes went 150 and 92 steps. The fault was asymmetric — it let
call-producing episodes run forever and cut the ones producing no calls at four.
The side that matters for the gate's firing is exactly the second.

**Mitigation.** The sweep is being repeated under the corrected rule (`bant2`
prefix). If its result comes out zero, the gate's firing will have rested on
clean data and everything downstream stands. If it comes out other than zero, the
gate fired on contaminated data and the family decision will be reopened.

## ~~S-28 — A manifest field was written at the wrong call site, thirty episodes fell, and the guard did not fire~~ — CLOSED: a pre-K-100 fault; the preflight guard was built

**Closed, 18 August 2026.** The criterion was applied.

**Closure criterion: it was a design gap and the gap was filled.** The record
said "a guard that depends on being remembered is not a guard"; what was missing
was the sweep's own preflight.

**Evidence.** `scripts/setup/measure_band.py` and
`scripts/setup/measure_boundary_control.py` each contain a `def preflight`
definition, and both run the write path with a single episode before the thirty
start: the manifest row and the episode row are looked for, and if the model call
count is zero the run does not start.

**What did not close.** The preflight shows that the write path runs; it does not
show that the values written are correct. The content of the manifest fields is
the subject of a separate contract (S-29).

While `max_output_tokens` was being added to the manifest for K-60 (637c825) it
was written into the `RecordingAgent` constructor instead of
`insert_run_manifest`. The scaffold does not know that keyword; all thirty
episodes of the `bant2` sweep fell with
`TypeError: Agent.__init__() got an unexpected keyword argument 'max_output_tokens'`
while the agent was being constructed, and the sweep produced no data at all.

**Why it was not noticed.** That commit says "152 tests passed, none skipped" and
it says so truthfully. Despite its name, `tests/test_recorded_run.py` does not run
`scripts/record_run.py`; it reads the **old** rows in the database. However badly
the runner breaks, that test passes as long as good rows from a past run remain.

**The part a unit test could not close.** The agent constructor can be called
without a server (`Agent.__init__` only stores configuration), but `record_run.py`
reads the effective context window from the server before reaching the
constructor (the K-37 gate), so a serverless subprocess test never reaches the
constructor. Because the keywords going to the constructor are written inline in
`main()`, a separate test copying them would not have helped either: the copied
call site is exactly the thing that can drift.

**Mitigation.** The smoke test became the measurement script's preflight and runs
automatically (`scripts/setup/measure_band.py`, `preflight`). Leaving it as a tool
to be run by hand would not have been enough: the tool existed that day too and
was not run. A guard that depends on being remembered is not a guard.

**Impact.** None on the measurement: the failed run wrote no data and episode
atomicity held. The impact is in time, one sweep wasted.

## ~~S-29 — The machine side of the manifest contract only holds on a database built from scratch~~ — CLOSED: the runners check the manifest constraints before starting

**Closed, 18 August 2026.** The criterion was applied.

**Closure criterion: it was a design gap and the gap was filled.** That `ALTER
TABLE` carries no constraints is an unchanging fact about SQLite; the closure
does not close that fact but its silence.

**Evidence.** `missing_manifest_constraints` is called in all three runners —
`measure_band.py`, `measure_boundary_control.py`, `measure_rule_off.py` — and if a
constraint is missing the run **does not start**; it exits without spending an
episode.

**What did not close.** An existing database still carries unconstrained columns.
What closed is running a new measurement on top of that database.

The schema is only applied to a new file; missing columns are added to an existing
file with `ALTER TABLE ADD COLUMN`. SQLite's ALTER TABLE carries no constraints,
and this was measured:

| Attempted | Result |
|---|---|
| `ADD COLUMN ... NOT NULL DEFAULT CURRENT_TIMESTAMP` | rejected, non-constant default |
| `ADD COLUMN ... NOT NULL` (no default) | rejected, a NOT NULL column cannot be added with a NULL default |
| `ADD COLUMN ... NOT NULL DEFAULT '' CHECK (...)` | rejected, CHECK fails on existing rows |
| `ADD CONSTRAINT` | does not exist, syntax error |
| `ADD COLUMN ... NOT NULL DEFAULT <constant>` | passed |

The result: the `serving_mode` column was added to `results/zihin.sqlite`, and the
two CHECKs that came with it were not. The live file's schema was read and it
carries no more than three old CHECKs. On top of that, `num_ctx_requested` is
still `NOT NULL` there, so the gap the hosted mode leaves is rejected at the
schema level: **PR #18's contract does not operate at all in the live database.**

Why this went unnoticed is visible too: all sixty-two manifest rows are `local`
and the model labels are only the three `qwen2.5-coder` sizes. The boundary
control's thirty episodes were never written into this store —
`scripts/setup/measure_boundary_control.py` only produces JSON and does not use
the record layer. Because the hosted mode was never tried, the constraint was
never tested either.

**Impact.** None on written data: the difference is in constraints, not values,
and the Python layer was in force in every run. The impact is forward-looking —
the claim "the contract is held by machine, not by interpretation" is true only
for files built from scratch.

## ~~S-30 — The output budget was read from the environment and its silent default started the wrong run~~ — CLOSED: the output budget moved into configuration

**Closed, 18 August 2026.** The criterion was applied.

**Closure criterion: it was a design gap and the gap was filled.** The rule was
written — everything that affects the measurement lives in configuration — and it
had not been applied to this parameter.

**Evidence, two pieces.** `max_output_tokens` is now defined in
`config/recording.yaml`, and the `ZIHIN_MAX_TOKENS` environment variable **does
not appear at all** in `scripts/record_run.py` (searched, zero matches). The value
is written into the manifest too.

**What did not close.** That the same budget is not the same condition across
model families is a separate limitation and stays open (S-26).

`max_output_tokens` affects the measurement directly: on the same model and the
same thirty tasks, 6/30 at 400 and 20/30 at 4000 (S-26). So it is not a plumbing
parameter but part of the measurement's definition.

Despite that it was read from an environment variable, and its silent default was
400. This was a violation of our own rule — everything that affects the
measurement lives in configuration, the environment only for secrets and values
read back from the server. The rule was written and had not been applied to this
parameter.

The consequence is concrete: the boundary control was started by accident on 13
August with a budget of 400 and was stopped after two episodes had been written.
Because they are not comparable, that prefix was abandoned.

**Fix.** The value lives in `config/recording.yaml` and has no silent default; if
it is not given, the run falls.

## ~~S-31 — The resume logic could silently merge two different measurement conditions~~ — CLOSED: the resume guard compares the condition of what was written

**Closed, 18 August 2026.** The criterion was applied.

**Closure criterion: it was a design gap and the gap was filled.** The skipping
existed, the condition comparison did not.

**Evidence.** `resume_check` is defined in `src/zihin/records.py` and called in
two runners (`measure_rule_off.py`, `measure_boundary_control.py`). If the
condition of the written episodes does not match the current one the run stops,
and the message asks for a new prefix.

**What did not close.** The guard is limited to the fields it compares. A
condition difference the manifest does not carry is still invisible.

When resuming an interrupted run, completed episodes are skipped. Skipping alone
was not enough: the **condition** of the written episodes was not compared against
the new run's.

The scenario S-30 exposed is concrete. Had a resume with 4000 been run on top of
two episodes whose budget was 400, the set of thirty would have been a mixture of
two at 400 and twenty-eight at 4000. The manifest records this but does not by
itself prevent it.

In the main run the same fault would throw away a forty-hour set, and the
difference would only be noticed afterwards.

**Fix.** The resume check compares the condition fields and rejects the run if
they do not match: model, serving mode, temperature, base seed, output budget,
stopping threshold, context window, KV cache type, flash attention, AppWorld
commit, instruction digest, library identifier, working tree, condition, split
and step ceiling.

Three fields are in a separate class.

`code_commit` is not rejected: resuming under a different commit can be legitimate
and was deliberately done that way on 13 August. But the difference between the
two commits is listed, and if one of the paths that **determine what happens
inside an episode** appears in that difference, the warning is raised to a
rejection. That separates "a different commit" from "a different commit that
changes the measurement", and the decision happens by machine.

`working_tree` is rejected. A different commit can be identified, a dirty tree
cannot: if the first half runs clean and the second half runs dirty with an
override, which code the second half ran under stays undefined.

`model_server_env` is not rejected; the differing keys are listed. Most of its
components are already rejected individually; the remainder gives visibility for
a setting the provider added that has no named field of ours.

**Residual coarseness.** The list of measurement-defining paths is at file level
and `src/zihin/records.py` is not on the list. The file carries both the
recorder's write path and the run orchestration helpers; 13 August's legitimate
resume change was in the second. Protecting the write path too would require
splitting the module.

**Two gaps in the list, found while the dirty-tree gate was being narrowed to it
(K-76).** `src/zihin/retriever.py` and `src/zihin/cards.py` were not on the list:
the first chooses which card goes to which task, the second determines what the
model reads. While the gate looked at the whole tree the omission only weakened
the resume check; once the gate was narrowed to the list it turned into **a gate
that does not close**, because a run could then be started with a dirty retriever.
Both were added and two tests nail them down. What the narrowing found was the
narrowing's own risk: the list is now the single line of defence, and the price of
a missing entry went up.

**Two gaps in the record were closed.** The step ceiling was written nowhere —
`termination_reason` said the ceiling was hit but not what the ceiling was;
`episodes.step_ceiling` was added. `library_id` was added to the manifest and is
NULL until the skill library arrives.

## S-56 — The noise floor is not zero: the upper bound on every claim readable from one episode

> **Bounds a claim.** PILOT_REPORT.md and the end-to-end demo — every arm comparison read from a single episode

> **Closure class.** Measured — eleven of fifteen cells diverged across three repeats; the noise floor is the finding itself

Fixed seed, temperature 0.2, same prompt, same cold regime — and **eleven of
fifteen cells diverge across three repeats.** The measurement is the three-arm
card run: 3 arms × 5 tasks × 3 repeats, all at one commit
(`docs/reports/uc-kollu-kart-kosusu.md`, `results/card-arms.json`).

This is not a defect but a magnitude. K-51 had turned determinism from an
assumption into a measured quantity; this is that quantity's value at 7B on this
task set.

**Its scope.** The noise floor invalidates every measurement that compares two
arms with a single episode. In this setup the only casualty was the end-to-end
demo, because it was the only measurement comparing two arms with one episode
(below).

**What it does not cover.** The zeros are unaffected. `bant2`, `bant3` and
`bant3-kapali` are three independent runs and all three gave zero; noise cannot
manufacture a zero. The precondition finding (K-58) stands.

**Addendum, 2026-08-26 — a retroactive ceiling audit.** The ceiling-hit rate of
these three runs was measured from the record afterwards, and the three do not
stand in the same place: `bant3` 0.0%, `bant3-kapali` **96.2%**, and `bant2` is
not in the record at all. The noise argument is unchanged — noise cannot
manufacture a zero — but that two of the zeros are **lower bounds** was not
written here. It is in S-63.

**Its application.** From here on, no result comparing two arms is read from a
single episode. The repeat count per cell is part of the measurement's definition
and will be written in the report.

---

## S-57 — Getting past the authentication barrier is necessary but not sufficient

> **Bounds a claim.** PILOT_REPORT.md mirror finding — the convergence of two mechanisms on the same bottleneck

> **Closure class.** Next round — what is needed after the barrier is the next measurement round's question

In the three-arm run, the login effect (`POST <app>.auth/token`, 2xx) was reached
in **each of the three arms**, in between three and seven of the fifteen cells.
Completion, however, was **0/45**.

So getting the token did not make a single task solvable in this sample. The
bottleneck measured is not the token; the token is the door onto the bottleneck
behind it.

**Consequence for the mirror finding.** The library teaches how to get the token,
the index forbids failing to carry it — two independent corpora converged on the
same mechanical bottleneck, and that convergence is real. But getting past that
bottleneck is not enough to solve the task. The narrative force of the mirror
finding is bounded by this measurement, and the two have to be written together:
the mechanisms converged on the same place, **and** that place is not where the
task gets solved.

---

## S-54 — The state probe's blind spot closed, but **only going forward**

> **Bounds a claim.** K-93 — that the state probe sees changes

> **Closure class.** Next round — re-running the old episodes, or accepting the forward-only scope, closes it

The digest-based probe in the served mode sees a `PATCH` that does not change the
row count (K-93, measured with `set_volume`). The blind spot written in the old
probe's own documentation closes on this axis.

**The closure holds only for runs from here on.** The existing skill library and
failure index were mined **with the old probe**: `state_change` carries a row
count difference and does not see calls that only update. This has consequences in
three places and none of them closed:

- **The empirical write set** (K-41) rests on row counts. A write that does not
  change the row count is not in that set.
- **The discriminating conditions of the failure cards** were searched using
  signals derived from that set; if the corpus is re-mined the conditions may
  change.
- **The stopping rule's calibration** was done under the old probe. Because its
  weight in the record is zero (0 in 4102 steps) the calibration is not expected
  to change, but it was not tested.

**Not deleted, kept with the distinction:** the blind spot is absent from new runs
and present in the old derived projections. If re-mining happens, the difference
between the two should be measured and reported; if it does not, the library
should be read as the product of the world the old probe saw.

## S-53 — The recorder's mount point did not fire in remote mode, and it was silent — FIXED

> **Unclassified.** same class

The first sandbox episode ran, produced a 32 KB trajectory and wrote **zero
steps** to the record. The episode row was still written, the verifier still
returned a verdict; no alarm appeared anywhere.

**Cause.** The reference agent calls `world.batch_execute`, not `world.execute`.
In the in-process mode `batch_execute` calls `self.execute` for each piece of
code, so wrapping `execute` was enough — the recording has worked by this
coincidence until now. In remote environment mode `batch_execute` diverts
straight to an HTTP call and `self.execute` is never called.

**Second layer.** After the mount was fixed the steps arrived but **the actions
stayed at zero**. `_action_rows` compares the lengths of two sources, and the
second source (`api_calls.jsonl`) does not exist on the host side in sandbox mode.
Its absence was read as "zero calls". The presence of the source is now an
explicit flag; its absence also disables the count comparison, because there is no
second number to compare against.

**Remaining protection.** If the proxy saw an app call and yet zero steps were
recorded, the run falls without writing the episode row (K-98). That would have
caught both of these faults.

## S-52 — The proxy cannot fill the `error_class` field, because there is no exception on the wire

> **Bounds a claim.** DATA_MODEL.md — that the `actions.error_class` field is populated in every episode

> **Closure class.** Next round — if the capture point or the data model changes, the field fills again

Today's record carries in `actions.error_class` the class name of the exception
`Requester` throws. The proxy never sees that exception: the exception is inside
the container and occurs after the call returns. In sandboxed episodes the field
stays `NULL`.

**No information is lost, but the column's meaning changes per mode.** Measured:
the field is empty in 4489 of 5261 actions and `"Exception"` in 772, and those 772
are exactly the sum of the non-200 status codes (401 503 + 422 235 + 409 34 =
772). So the field is derivable one-to-one from the status code and says nothing
extra in any action.

It would have been possible for the proxy to invent a value it does not see —
writing `"Exception"` whenever the status is not 200 — and it was not done. An
invented value becomes indistinguishable from a measured one.

## S-51 — The container's environment server is in the same process as the agent's code

> **Bounds a claim.** 04-threat-model — that the container isolates the agent's code

> **Closure class.** External fact — the embedded IPython shell is AppWorld's architecture; isolation is sought at the container boundary

The environment server executes the agent's code in an embedded IPython shell, so
the agent's code can do everything that process can do: it can change the world's
local time, corrupt the server's in-memory state, and affect the text `execute`
returns.

**This is a direct consequence of K-B and it is unavoidable.** If the container is
to hold the full `appworld` package, then the thing executing the code is that
package. A thin RPC client would have closed this surface but would have changed
the interface the agent sees (K-19).

**What is protected is the host, not the inside of the container.** All three are
outside: the record database, the verifier, and the API server's admin surface.
Every change the agent makes to the world has to go through the API server, and
that path goes through the proxy, so it is recorded. The verdict is on the host
side too, produced from databases the host writes.

**The one place that does not close is `DELETE /date_time`.** The proxy's field
criterion settles there for "non-empty text", because the value is a UUID produced
inside the container and the host cannot know it in advance. The agent can call
that route with an identifier of its own; what it achieves is lifting the
container's own time freeze. The world's clock is on the API server and
`POST /date_time` is bound to an exact match, so the world's clock does not change
this way.

## S-50 — Not all admin routes can be cut: eleven are needed to build the world

> **Bounds a claim.** K-95 — that twenty-one admin routes are cut at the proxy

> **Closure class.** Measured — eleven of K-95's twenty-one routes turned out to be needed to build the world

The scope document's K-95 decision said "twenty-one admin routes shall be cut
structurally at the proxy". Measurement showed this cannot be applied literally:
the environment server **itself** makes eleven admin calls to build the world —
eight at setup, one `POST /dbs/save` after every step, two at shutdown. Once the
environment server moves into the container, those calls come from the container
too.

The per-step `POST /dbs/save` also arrives **after the agent's code**, so a phase
gate of the form "setup is done, admin is closed from here" does not work either:
the call is inside `execute`, right after the agent's code.

**The form applied: the body's fields instead of the route name.** Every field of
the eleven permitted calls is bound either to its exact value or to a measured
pattern. Where the escape path stops is `to_db_home_path`: because it requires an
exact match, the agent cannot change where the host writes. Measured — 11 of the
real traffic passes, 12 of 12 tampered attempts are cut, and in the test's
unprotected arm the file really is written to the host.

**The residual limit was measured and largely closed.** Three separate
measurements:

1. **An agent-triggered `/dbs/save` does not consume the changes the probe would
   see.** A change that does not alter the row count was made, the probe saw it
   (`{"spotify": {"MusicPlayer": 1}}`), a permitted `/dbs/save` was sent, the probe
   was run again and the change was still there. A further change made afterwards
   also showed up (`MusicPlayer: 2`), so the probe stays live. The call is an
   idempotent write; the record is not blinded.
2. **Separating them with `SO_PEERCRED` is impossible, and the reason is
   two-layered.** In the container the agent's code is **pid 1**, that is, the same
   process as the environment server; and what connects to the proxy is the bridge,
   which is a thread of the same process. The unix socket carries this information
   but there are no two sides to separate. The same information served another
   purpose: confirming the container's identity (K-98).
3. **No path runnable from the agent's code was found.** AppWorld's own
   SafetyGuard cuts `requests`, `socket`, `subprocess` and
   `urllib.request.urlopen`; the requester object is not reachable through `apis`.
   Five paths were tried and all five are closed.

The third is **not proof that no path exists**, it is the result of five attempts.
The proxy's field criterion is not built on that assurance: if the reference's own
protection loosens one day, the filter stays in place.

## S-49 — Forty-five tests had never run in CI, and two environment differences were invisible locally — FIXED, AND THE COVERAGE WAS CLOSED LATER

> **Unclassified.** same class

**Note added later.** The fix below marked the tests and filtered them out in CI:
the requirement became visible but the tests still did not run. The coverage closed
with K-100 — CI now installs `appworld install` and the data. Measured difference:
tests run went from 365 to 446, skipped from 47 to 7; the cost is 26 seconds of
wall clock (`results/ci-kapsam.json`). The remaining seven skips are structural:
they depend on generated artefacts under `results/` and that directory is
deliberately gitignored.

The PR flow stopped after #19 and seven roadmap items accumulated on one branch as
52 commits. Because the branch was not pushed, **the four CI checks saw none of
those commits**. When it was pushed two separate faults appeared and neither was
visible in a local run.

**First difference: the app modules.** `route_table()` builds endpoint resolution
from AppWorld's app modules (`appworld.apps.venmo` and its siblings). Those modules
come with `appworld install`, not with the package — the package only has
`appworld.apps.lib`. CI installs the package and does not run `appworld install`
(K-32). Because the relevant tests did not carry the `appworld` marker,
`-m "not appworld"` did not filter them out. Measured: **45 tests** across four
modules — `test_api_routes` 16, `test_stopping_rule` 16, `test_shield_mount` 10,
`test_compiler` 3.

**Second difference: the invocation form.** `tests/test_shield_mount.py` takes the
fake requester through `tests.test_api_capture`. When the repository root is not on
sys.path the import fails, and whether the root is there depends on the invocation
form: `python -m pytest` adds the working directory, the `pytest` script does not.
The local run used the first, CI the second.

**Neither was caught by a local preflight, because the preflight used the same
concealing form.** Reproducing the first difference needed a hook rejecting the
`appworld.apps.<app>` import, and the second needed invocation in script form; once
both were built, all eight PRs were verified green locally in advance.

**Fixes.** If the app modules are absent, a test that needs resolution is now
**skipped**: the patch goes onto AppWorld's own `import_apis_module`, because the
tests import `route_table` directly and patching a module attribute does not change
the name in the caller's hand. A hand-kept marker list was not used; which module
touches resolution changes over time and a list goes stale silently. For the second
difference, `pythonpath = ["."]` in `pyproject.toml`: the same suite giving
different results under two invocation forms is a defect of the configuration, not
of the test.

**Residual limit.** Those 45 tests still do not run in CI, they are now skipped. So
the correctness of endpoint resolution is tested only locally; what CI sees is the
information "this test cannot run in this environment". The path to closure is
running `appworld install` in CI, and its price is downloading 198 MB of data.

## S-48 — The index's most frequent pattern is retrievable by no task

> **Bounds a claim.** PILOT_REPORT.md — the retriever's coverage rate

> **Closure class.** Measured — the most frequent pattern reaches no task; the cause is the structure of the symbol space

`GET api_docs.api_descriptions` (422, **150 failures**) is the highest-count
pattern in the index. The retriever gives it to no task: the symbol is on the app
and `api_docs` infrastructure list, and infrastructure falls out in the retriever
(K-86). Measured: it is retrieved in none of 315 tasks, and 14 of the 15 patterns
are retrievable (`results/card-tokens.json`, `unreachable_rows`).

**For this pattern specifically, that is good news.** The card resting on an
accidental condition in S-45 is exactly this card: its single separating condition
belongs to another app and does not state the real cause. So the suspect card
structurally cannot reach the model.

**But as a rule it is a loss.** If there really is learnable failure information in
the infrastructure apps, it cannot reach either, and the index's size therefore
looks larger than the size the retriever can reach. The abandonment criterion says
"the index is at the declared minimum size" (`05-experiment-design.tr.md`); the
correct reading is the number of **retrievable** patterns, not the index's row
count.

**There are two paths to closure and both need a decision**: giving infrastructure
cards to every task unconditionally (which breaks the discrimination measurement),
or a condition form able to express the real cause of the `api_docs` 422s (tied to
S-40, needs the response body).

## S-47 — The binding context limit is not the token window but the scaffold's character ceiling

> **Bounds a claim.** 03-architecture — that the context budget is 32K tokens

> **Closure class.** External fact — the 50000-character ceiling is inside the reference scaffold and K-19 froze it

The context budget is discussed as 32K tokens, but the reference scaffold cuts the
context **by characters**: `max_prompt_length` is 50000 and the truncation is
inside the scaffold itself (S-07). The two limits are in different units and which
one binds had never been measured.

**Measured** (`results/context-cost.json`): on real record content, 50000
characters is **12799 tokens**, that is 3.91 characters per token and **39 per
cent** of the 32K window. The fixed block together with cards is ~3400 tokens, 10
per cent. The difference is left to history, but history itself hits the character
ceiling: the window never fills.

**There are two consequences.** Context overflow (K-36's third category) cannot
come from the token window in this configuration; seeing zero context overflows in
the record is consistent with that. And when the context assembler arrives it will
have to write its budget in characters rather than tokens, or disable the
scaffold's truncation logic — the collision K-26 left open is exactly here.

**The ceiling bound, and this was measured.** Of the 105 recorded episodes, **31**
went past 50000 characters; the earliest at step 9, and in the truncated episodes
the median was step 19. The truncation drops the **head** of the history (the
instruction block is kept, the tail is kept), so in a third of the corpus the agent
stopped seeing its own early steps past some point. The measurement is a lower
bound: message frames (role lines, code block markers) were not counted, so the
real prompt is somewhat longer and truncation started somewhat earlier.

**The library and the index are unaffected by this**, because both were mined from
the record, not from the prompt. What is affected is the trajectories themselves.

**The value is ours, not the reference's.** The ceiling is a constructor parameter
of the agent, and the value the reference gives for this agent is `null`, meaning
no truncation: all 108 of the published `simplified_react_code_agent`
configurations are like that. The 50000 comes from the legacy `plan_execute` family
and entered the runner on 10 August with no decision record. It is now in
`config/recording.yaml`, in the manifest, and on the resume check's reject list
(K-90).

**The measurement's own limit.** The 3.91 characters-per-token ratio comes from the
code and observation text in the record. A different content distribution — more
JSON, more English prose — gives a different ratio; the number is specific to this
corpus.

## S-46 — The fixed block's share in the architecture document was unmeasured and wrong — FIXED

> **Unclassified.** same class

`03-architecture.tr.md` said this: "About 5958 input tokens per step. The fixed
block is roughly a fifth of the 32K budget, a quarter together with the cards."

**The second sentence was wrong.** Measured: the fixed block has a median of
**3172–3185 tokens**, that is **9.7 per cent** of the window; with cards, 10.1–10.5
per cent. A tenth instead of a fifth, and again a tenth instead of a quarter.

**The source of the error is a unit confusion, not a bad guess.** The number 5958
was measured in stage 2 and is **input tokens per step**, so it includes the
accumulated conversation history. The fixed block is a quantity independent of that
and had never been measured separately; the difference between the two numbers is
the history itself.

**How it was caught.** We wanted to measure the base the cards would sit on top of,
and when the base was measured it did not agree with the claim. So what caught it
was asking what the cards cost — not re-reading the document.

**Fixed.** The sentence in the document was replaced with measured numbers and the
source of the measurement was written down. Decision record K-88.

## S-45 — The index cards' condition can separate by accident, and the card carries this on its face

> **Bounds a claim.** K-85 — that the index cards' condition is discriminating

> **Closure class.** Measured — that discrimination can be accidental was shown on this corpus; the card carries it on its face

The condition is chosen as a predicate that holds in every failure and in no
success. The candidate space is the presence and absence of every call in the
alphabet — **92 candidates** on this corpus. If the failure group is small, a
predicate can separate **by accident**.

**Measured.** In 12 of the 13 cards carrying a condition, the separating condition
belongs to the call's own app, so it can be read causally ("log in first"). In one
(`GET api_docs.api_descriptions`, 422, 150 failures) the only separating condition
belongs to **another app**: "that `simple_note.profile` was called first". That is
a correlation, not a cause. The real cause of those 422s is the **value** of the
`app_name` argument, and by K-83 values do not enter the pattern.

**A number correction.** When this paragraph was first written it said "in 14 of 15
cards", and in that form it belonged to the state before K-85: in the same commit,
the condition was removed from two patterns that had no contrasting success, so the
number of conditioned cards is 13, not 15. The denominator changed, the numerator
did not. The correct figure is above and its source is
`results/pilot-dataset.json` → `failure_patterns`.

**A second trap: discriminating on patterns with no contrasting success is an empty
claim.** With no success to compare against, every eligible condition separates
trivially. On the `POST splitwise.auth/logout` card, **59** conditions separate; the
choice is entirely arbitrary.

**The remedy is not deletion but marking.** The card carries two diagnostic fields:
`discriminating_count` (how many conditions separated) and `own_app_condition`
(whether the chosen condition belongs to the call's own app). Both follow the same
pattern as `body_write`: over-inclusion appears inside the product rather than
inside the report, and can be interrogated.

**Why no "same app" rule was imposed.** It could have been, and it would have
dropped two suspect cards. But a causality constraint is not part of the condition
language, and a constraint added to the language silently weakens K-83's closure
rationale. No decision was made; the measurement and the marking went into the
record.

## S-44 — `actions.error_class` is single-valued, the signal is in the status code

> **Bounds a claim.** 07-failure-taxonomy — that the `error_class` field carries an action-level signal

> **Closure class.** Measured — the same value in 767 of 767 failed actions; the field carries no action-level signal

In **767** of 767 failed actions the `error_class` value is `Exception`. AppWorld
throws an exception on every failed response and the HTTP code is parsed out of the
exception text and written into the `result_status` column.

So the column is not discriminating. The taxonomy's action-level labels
(`07-failure-taxonomy.tr.md`) are read from **`result_status`**: 401 → authorisation
refused, 422 → invalid parameter, 409 → unsuitable state.

The `error_class` column was not removed, because it carries non-zero information:
the distinction between a call returning through an exception and one returning
through faulty code may mean something later in a different transport layer. But
today nothing can be built on it, and anything built on it separates nothing,
silently.

## S-43 — The 409 class is outside the scope of the v0 index

> **Bounds a claim.** 07-failure-taxonomy — that the condition language can express the failure classes

> **Closure class.** Measured — all 34 `409`s are on one endpoint and the cause is object state; the condition language cannot express it

All 34 recorded `409` errors are on one endpoint: `POST venmo.transactions`. The
cause is object state — a conflict such as insufficient balance — and the condition
language's forms for expressing that (object existence, object field value) are
**not observable**, because the call's response body is not written into the record
(S-40).

The v0 index covers the `401` and `422` classes. Even if the card produced for 409
finds a condition belonging to its own app, it does not state the real cause;
S-45's markings make it visible.

The path to closure is the same as S-40's: make the response body durable and
re-run. It cannot be applied to this corpus (S-16).

## S-42 — Boundness was searched across the episode, not within the body — FIXED

> **Unclassified.** same class

`06-skill-language.tr.md` defines a bound argument as one whose "value appears
**within the sequence** in the output of an earlier call", and the sequence is the
skill's own body. The first implementation searched the earlier observations of the
whole episode.

**Its consequence was measured and it is serious.** At gap 2 / support 3 the
highest-support skill was this:

    GET api_docs.api_doc
    POST venmo.auth/token

`supervisor.account_passwords` is **not** in the body. Despite that, `password`,
`username`, `app_name` and `api_name` were all four counted as bound, because the
values had been printed at an earlier step of the episode. The compiled skill would
come out with no parameters and at run time could obtain none of those values: the
body runs atomically, and the calls the gap skips never run at all.

**This is the second face of the skipped-call question.** The same measurement
produced both: a skill cannot depend on anything produced by the calls it skips.

**Fixed.** Boundness is searched only in the output of **the occurrence's own
steps**. The numbers: bound arguments from 22 to 13, free parameters from 5 to 14.
Skills now declare in their signatures what they need. The Venmo login skill asks
for credentials as parameters; the Spotify skill carries the `account_passwords`
call in its body, so its password stays bound and only the username is free.

**Residual contamination.** If a step carries both a body call and another call,
its observation contains the output of both. This is the same class as the
contamination in postcondition attribution (K-79) and will close in the same place.

## S-41 — Most postconditions are empty in v0, because attribution needs isolation

> **Bounds a claim.** SKILL_SPEC.md — that skills carry postconditions

> **Closure class.** Measured — K-79 limits attribution to single-call steps; empty postconditions are the known price of that decision

A postcondition is the shape intersection of the state differences observed in the
supporting episodes (`SKILL_SPEC.md`). Attribution is read only from **steps that
made a single call** (K-79): in a multi-call step it cannot be known which call the
difference came from.

**Measured base.** There are 454 steps across the 22 recorded passing episodes; 16
carry a state difference and **8 are single-call**. So the number of attributable
observations is limited to eight steps.

**Measured result.** Of the 40 skills mined in the gap 2 / support 3 configuration,
**39 have an empty postcondition** and one is populated
(`{venmo.PaymentRequest: +, venmo.Notification: +}`).

**The emptiness has two different causes and they must not be conflated.**

1. **The login family genuinely does not change state.** The `auth/token` call
   produced zero difference across 213 single-call steps. This is not a measurement
   gap but a fact: login produces a token, not rows. The effect suffix is populated,
   the postcondition is empty, and the specification allows that.
2. **Row counting does not see updates.** A skill that writes only at field level
   will produce an empty postcondition. This is the same blind spot that limits the
   write set, and the two close together with the `model_hashes.json` layer.

**Its effect.** In skills with an empty postcondition the post-execution
verification branch does not run, there is no relevance contribution in retrieval,
and the second counter of the demotion rule (`postcondition_misses`) never
increments. So all three uses of the postcondition mechanism are dead in those
skills.

**What has to change.** Calls per step is the scaffold's behaviour and we do not
change it (K-19). The path to closure is the same as for the empirical write set:
model hashing at episode close. If the corpus grows, the number of single-call
steps grows too, but the ratio does not change.

## S-40 — Bound-argument detection is limited to what the agent printed

> **Bounds a claim.** 06-skill-language — that bound-argument detection is done by structural path matching

> **Closure class.** Next round — if S-16's response instrumentation lands, the detection surface widens

The specification defines a bound argument as one whose "value appears within the
sequence in an earlier call's output, detected by structural path matching"
(`06-skill-language.tr.md`). **The call's response body is not written to the
database.** `ApiCapture` catches it at run time but `write_steps` stores only the
status code and the error class; S-05 fixed the status code, not the body.

**v0 uses the observation text.** Because the scaffold's pattern is
`print(apis.<app>.<api>(...))`, the values the agent uses later appear in the
observation. Detection is done by text containment, not by structural path
matching.

**The error is one-directional.** A value used without being printed **looks free**.
So the classification under-detects rather than over-detects. The direction
matters: over-detection buries a non-bound argument in the body and breaks the
skill; under-detection only lengthens the signature needlessly.

There is a lower bound for short values (three characters), because `1` and `on`
appear in every observation. That too works in the under-detection direction.

**Measured.** At gap 2 / support 3, 270 of the 40 skills' arguments were classified
as bound and 50 as free parameters. In the login skills `password`, `username`,
`app_name` and `api_name` come out bound — the expected result, since all of them
come from the output of an earlier `api_docs` or `supervisor` call.

**The v1 path.** Make the response body durable and re-run. It cannot be applied to
this corpus: collection is one-shot (S-16) and re-running changes the corpus. The
decision was made because not looking for boundness at all was not an option — the
specification warns about exactly this: if bound arguments are taken for
parameters, the caller has to know half the job already and the skill loses its
value.

## S-38 — The write-set derivation took the `@app.delete` decorator for a write call — SOLVED, and it left a known over-inclusion

> **Unclassified.** same class

**The defect.** The derivation walks every endpoint's body with `ast.walk` looking
for a call of the form `.delete(...)`. `ast.walk` also walks a `FunctionDef`'s
**decorator list**, and every DELETE endpoint is decorated with
`@app.delete("/path")`. So every DELETE endpoint counted as a writer, whatever was
in its body.

**Measured: nine endpoints are in the set only thanks to this accident.**

    amazon.delete_account        gmail.delete_account       splitwise.delete_account
    phone.delete_account         simple_note.delete_account spotify.delete_account
    file_system.delete_account   todoist.delete_account     venmo.delete_account

Their bodies contain no write verb, because all of them delegate to a shared helper
called `_delete_account(...)` and that helper is not in `apis.py`.

**The answer is right, the reason is wrong.** Deleting an account is of course a
write. But the reason they are in the set is not evidence in their bodies, it is
the route decorator. If the decorator leak is fixed on its own, these nine
endpoints **drop out** of the set and the shield passes the most destructive
operation on the whole surface unconditionally.

**Tracing in-module helpers does not rescue it, measured.** Tracing at one and at
three levels was tried too; all nine still drop, because `_delete_account` is not
in the module. Tracing does, on the other hand, **add** seven endpoints
(`file_system.move_file`, `move_directory`, `gmail.reply_to_email`,
`splitwise.settle_up`, and three `todoist.show_*`), and the last three need
separate examination.

**Why it was left open.** The correct form of the fix changes the derivation's
method: scan the shared library too, or fix the decorator leak and add the DELETE
method as a separate rule, or pin the nine by hand. The three produce different
sets. Nothing was touched before the decision.

**Today's state is on the safe side.** The set contains nine destructive
endpoints. The risk is in half-fixing it.

### The proposed fourth path was measured: it cannot be adopted as is

The proposal was: close the leak, and make HTTP method semantics an explicit rule —
POST, PUT, PATCH, DELETE count as writers, and the body scan runs only for GET.

The rule's rationale is sound: a DELETE endpoint changing state is not an accident
but the meaning of the protocol, and getting that right answer today through a
decorator leak is reaching a right conclusion by a wrong road. But two measurements
argue against fixing the rule as it stands.

**First measurement.** After the leak is closed, the number of non-GET endpoints
with no write in their body is **82** out of 302. That is not small. It includes
endpoints that *read* over POST: `admin.show_card_balance` and `admin.validate_card`
do a `find_one` in their bodies and return a value.

**Second measurement, arithmetic.** Today's figure of 242 is **not** "non-GET plus
12 GET writers":

| | |
|---|---|
| Named APIs | 478 |
| GET only | 176 |
| Non-GET | 302 |
| Writers today | 242 = 230 non-GET + 12 GET |
| What the rule would produce | 314 = 302 + 12 |

So the rule adds 72 endpoints and drops none. Not a no-op correction of the
rationale but a change that grows the set by 30 per cent.

**And the blocker: the false positive rate goes from 4.1 per cent to 24.5 per
cent.**

| Set | Writing key | False positive |
|---|---|---|
| Today | 242 | 6/147 = 4.1% |
| Fourth path | 314 | 36/147 = **24.5%** |
| Fourth path minus `login`/`logout` | 296 | 6/147 = 4.1% |

The cause is a single endpoint. `phone` goes from 0 misses to 30 and all thirty are
the same call: `POST auth/token`, that is **login**. The agent has to log in before
it can *read* from an app, and login is a POST. If the rule is adopted as is, login
counts as a write, login to a missed app is blocked, and reading is cut off
indirectly. K-69 — "reading is unconditionally free" — would be wrong in practice:
reading turns conditional behind a login gate. The measurement returns to exactly
24.5 per cent, the app-set error rate K-72 identified.

If `login` and `logout` are excluded the rule works and the false positive rate
stays at 4.1 per cent.

### The rule as applied

**Non-GET methods are writers, session endpoints excepted, and the body scan runs
only for GET.** The cross-boundary helper scan runs on every endpoint regardless of
method.

**The exception's rationale derives from K-69, not from the measurement.** K-69
leaves reading unconditionally free. Login is a precondition of reading: the agent
cannot read from an app it has not authenticated to. So if login counts as a write,
login to an app the inference missed is blocked, the reading behind it dies with
it, and K-69 becomes inapplicable. The exception comes from that derivation. The
number **confirms** the derivation, it does not produce it. `logout` is login's
counterpart: it drops a session token, does not touch user data, and blocking it
would leave sessions open while protecting nothing.

**The rationale for accepting it is the direction of error.** In a security
mechanism the two error directions are not symmetric. Counting a reader as a writer
blocks a legitimate read, and the marginal cost of that was **measured: zero** —
the false positive rate stayed at 4.1 per cent. Counting a writer as a reader lets
a real write through unchecked. Over-inclusion is the safe direction.

### The known over-inclusion

**64** of the 284 non-GET endpoints have no write call at all in their bodies and
all of them are in the set. Two are confirmed readers:

| Endpoint | Method | Body |
|---|---|---|
| `admin.show_card_balance` | POST | `_validate_card`, `PaymentCard.find_one`, returns a balance |
| `admin.validate_card` | POST | `_validate_card`, returns a boolean |

Both stay in the set and the `body_write: false` field records this per endpoint, so
the over-inclusion appears inside the product rather than inside the report.

The remaining 62 are mostly account lifecycle (`signup`, `verify_account`,
`reset_password`, `send_verification_code`, `update_account_name`) and endpoints
delegating to a shared helper; those really do write, the static scan simply cannot
see it.

### The gain

The nine `delete_account` endpoints are now in the set by a declared rule rather
than by accident. `file_system.move_file`, `file_system.move_directory`,
`gmail.reply_to_email`, `splitwise.settle_up` and all the account POSTs also
entered: 242 → **296** writers.

**Cross-boundary writers went from 16 to 19, and the three new members are a
consequence of this over-inclusion.** The new ones are `amazon.add_payment_card`,
`spotify.add_payment_card`, `venmo.add_payment_card`; all three count as writing to
`admin`. The cause is two readers at the head of the chain: the card helpers
`request_payment_card_balance` and `request_payment_card_validation` call the
`admin.show_card_balance` and `admin.validate_card` endpoints, those two count as
writers by the method rule because they are POSTs, and once the target counts as a
writer the helper counts as a cross-boundary write.

So these three members are not new evidence of a write but one step beyond the known
over-inclusion. **Their practical effect is zero**: `admin` is an infrastructure app
(`INFRASTRUCTURE_APPS`) and is always in the permitted set, so these three endpoints
are blocked on no task.

And the brittle half of the derivation — verb-name matching and delegation
blindness, the things that bit twice in this session — now applies only to the 176
GET endpoints.

## ~~S-37 — `update` is not a model verb, and it made two pure reads into writers~~ — CLOSED: `update` was removed from the write-verb set

**Closed, 18 August 2026.** The criterion was applied.

**Closure criterion: it was measured and an answer came back.** The record already
carried the measurement: `update` appears twice on the whole surface, both are pure
reads, and no model class defines it.

**Evidence.** `update` is **not** in the `WRITE_METHODS` set in
`scripts/setup/derive_write_set.py` (searched, zero matches).

**What did not close.** The real usage of each of the remaining eight verbs was not
verified individually; this record measured only one of them.

`update` was in the `WRITE_METHODS` set. The derivation does not know the receiver's
type, it only looks at the attribute name, and `update` is both a Python
`set`/`dict` method and a plausible model verb.

**The measurement is decisive.** `update` appears twice on the whole surface:

    phone.show_contact_relationships   relationships.update(...)   -> a set
    todoist.show_projects              project_dict.update(...)    -> a dict

No model class defines `update` and `callers.py` never calls it. So one of the nine
verbs had **zero** real usages and was producing two false positives. The remaining
eight names have no such collision: Python containers have no `save`, `create`,
`delete_all` or `create_save`.

**Its effect was seen in shadow mode.** Both are pure reads, and
`phone.show_contact_relationships` produced two of the shadow run's eight blocks —
exactly what the shield must not do, cutting a read.

**How it was found.** After running shadow mode, the blocked calls were examined one
by one. It would not have been visible by looking at the number: the 0.09 per cent
block rate was already small, and "small" does not mean "right".

**Correction, 15 November 2026.** One of the eight blocks was a note opened by a test
itself (S-83). Without it the first run is 7 blocks in 9145 calls, 0.08 per cent. The
finding of the two pure reads does not change.

**Fixed.** `update` was removed from the set, the writer endpoint count went from
244 to 242 and GET writers from 14 to 12. The `download_*` count stayed at nine —
K-41's load-bearing half did not move.

## ~~S-36 — Two route templates match the same path, and the resolver gave the wrong answer~~ — CLOSED: route resolution is method-aware

**Closed, 18 August 2026.** The criterion was applied.

**Closure criterion: it was measured and an answer came back.** The resolver was
looking only at the path; it now takes the HTTP method too.

**Evidence.** `src/zihin/api_routes.py` carries the method field inside resolution,
and `scripts/setup/verify_wire_identity.py` takes every action in the record through
the wire and reconstructs it — the signed arm's match measures the correctness of
this resolution, and the unsigned control arm shows the measurement is not vacuous.

**What did not close.** The measurement is over the actions in the record. A
path/method pair never seen in the record was not tested.

The `phone` app carries two pairs of templates and each pair's regexes match **the
same string**:

    GET, DELETE  /messages/text/{text_message_id}
    POST         /messages/text/{phone_number}

and the same for voice messages. `route_template()` looked only at the path and
returned the first match, so `POST /phone/messages/text/3155673041` — a phone number
— resolved to the `{text_message_id}` template.

**How it was found.** While measuring the shield's fail-open branch. The write set
covered 478 of the 478 named APIs, so no call should have fallen through to an
unknown endpoint; yet 26 of 5213 recorded calls did. The contradiction pointed at
the resolver.

**Its effect was measured and is latent on this corpus.** After the fix all 26 of
the 26 calls moved into the `write_within_allowed_apps` class, so **the shield's
decision does not change**: permitted either way. The defect produced no active
wrong decision on this corpus.

Its importance is in the general case. That endpoint writes to `phone`; on a task
where `phone` is not permitted the right decision would be **reject**, and the
unknown-endpoint branch would have let the call through. That combination did not
occur on this corpus, but the hole in the shield's coverage is real.

**The fix.** Resolution takes the method too. Because the pairs' methods are
disjoint, the distinction is exact. If the path matches and no route accepts that
method, the answer is None: that is a 405, not "an endpoint we could not find".

After the fix, unknown endpoints went from 26 to **zero** and the 26 calls moved to
the correct class (`write_within_allowed_apps`); the read and cross-boundary write
counts did not change.

**The blast radius was swept.** Only `endpoint_identity` uses the resolver, and only
the `episodes.distinct_endpoints` diagnostic column feeds it. The stopping rule's
PATH+PARAM identity and `distinct_resources` do **not** go through the resolver;
both use the concrete path from `split_endpoint`. No recorded number was affected:
no episode has been run since the column was added.

**Its class is a relative of S-32's.** The resolver was silently giving a wrong
answer and nothing objected. What caught it was two independent numbers
contradicting each other.

## S-35 — The two sources of the write set disagreed on one endpoint — CLOSED: K-41 over-counted

The static half of the write set was re-derived
(`scripts/setup/derive_write_set.py`, output `inputs/write-set-static.json`) and
agreed with K-41's recorded finding to within **one endpoint**.

| Measure | K-41 | Re-derivation |
|---|---|---|
| Writing GET endpoints | 15 | 14 → **12** |
| Of those, `download_*` | 9 | **9** |
| Derived-field group | 2 | **2** → 0 |
| Lazy-initialisation group | 4 | 3 |

The disagreeing endpoint: `splitwise.show_group_balance`.

**The two arrowed rows were corrected later and the difference is explained.** S-37
removed the `update` verb from the set; the two endpoints that dropped were
`phone.show_contact_relationships` and `todoist.show_projects`, that is, the whole
"derived field" group. Both are pure reads. So **two** of the three endpoints
between K-41's 15 and today's 12 are explained: they never wrote at all. One
uncertain endpoint remains, `splitwise.show_group_balance` below.

**The re-derivation exposed two errors of mine and they were fixed.** The first was
keying on the path: `splitwise`'s receipt-download endpoint shares its path with a
DELETE, so a "GET only" filter was eliminating a GET writer. AppWorld's unit is the
named API, and so is the shield's. The second was counting every call crossing an
app boundary as a write: `does_file_exist` and `enlist_files` also cross the
boundary but they read.

**The static view.** `show_group_balance` has no write call in its body; the only
local function it calls is `check_authorization_to_group` and that does not write
either. All of its calls are reads: `find_all`, `by_ids`, `by_id_or_raise`.

**The live probe.** The endpoint was called three times — twice with a group, once
without — and the per-model row count did not change in any of the three. That the
calls really ran was verified separately; on the first attempt the login had failed
silently and the probe said "unchanged", so a zero difference is not evidence by
itself.

**The uncertainty can be narrowed by one step, and it was.** K-41 put this endpoint
in the "lazy initialisation" group. Lazy initialisation means **creating rows**, and
the probe sees row creation. Since it did not see any, two possibilities remain: the
endpoint does not write at all, or it updates.

**K-41's classification is wrong either way.** So the only thing that is uncertain
is "does it not write, or does it update"; the question "is it lazy initialisation"
is closed.

The result: the lazy-initialisation group drops from four to **three plus one
uncertain**. The three certain endpoints are `spotify.show_current_song`,
`show_song_queue` and `show_volume`; the uncertain one is
`splitwise.show_group_balance`.

**Its effect on the shield is low.** Even if that endpoint writes, it writes to
`splitwise`, so it does not cross an app boundary; the shield's first-stage
predicate looks at cross-boundary writes. All nine of the nine `download_*`
endpoints matched exactly, and that group is the shield's reason for existing.

### Verdict: K-41 over-counted. The item closes.

Three pieces of evidence point the same way and none rests on another:

1. **The live probe saw no row change.** The endpoint was called three times, the
   per-model row count stayed the same all three times, and that the calls really ran
   was verified separately.
2. **There is no write verb in the body's 149 lines.** The full text was read. A
   `defaultdict` accumulation, `find_all`, `by_ids`, `by_id_or_raise`, dictionary item
   assignment. There is not even a `.update`, so the collision S-37 fixed does not
   touch this at all.
3. **K-41's classification was wrong in any case.** It put the endpoint in the "lazy
   initialisation" group; lazy initialisation means creating rows and the probe sees
   row creation. Since it did not see any, that label was already falling.

The three have one common explanation: the endpoint does not write and K-41
over-counted.

**The residual uncertainty and where it will close.** One possibility remains: an
ORM update invisible to both the body reading and the row counting — a field-level
write that does not change the row count. Static scanning and the row probe are
blind at exactly this point, and because both are blind neither can produce
evidence. The empirical half (K-41) catches it, because what it measures is not row
counts.

The item is not left pending indefinitely. The verdict was given, the residual
uncertainty was written down, and where it will close is known.

**Its effect on the shield was zero anyway.** Even if the endpoint writes, it writes
to `splitwise`, so it does not cross an app boundary, and the shield's first-stage
predicate looks at cross-boundary writes.

## S-34 — The boundary control did not run in the declared condition: thinking was on

> **Bounds a claim.** the boundary control — the "thinking off" declaration

> **Closure class.** Next round — re-running the boundary control in the declared condition closes it

The design declares the boundary control in `docs/05-experiment-design.tr.md` and
K-58 as: "DeepSeek V4 Flash 0731, over the API, **thinking off**." The run was made
with thinking on.

**Mechanism.** Nothing in the request parameters turns thinking off. The fields sent
are: `name`, `temperature`, `seed`, `max_tokens`, `stop`, `use_cache`,
`retry_after_n_seconds`, `max_retries`, `cost_per_token`, `api_key`. No `reasoning`,
no `thinking`. The scaffold **reads** `reasoning_content` from the response but
never turns it off anywhere, so the provider default applied. Measured live: 146
reasoning tokens on a default call, a field of 466 characters.

**The connection to S-26 was made afterwards.** S-26 had measured that four hundred
tokens was binding and had written the reason as "reasoning eats from the same
budget". That sentence was evidence that the declared condition had been violated,
but it was not connected at the time. So the reason the budget was binding is in
fact this violation.

**What stands.** The apparatus check stands: its question is "can any model succeed
on this line" and the answer is yes, 20/30. It stands because the question is
independent of the condition.

**What cannot be built.** The sentence "DeepSeek V4 Flash 0731, thinking off, 20/30"
cannot be built. The number belongs to a thinking model.

**The fix and its cost.** The model meets the requirement:
`reasoning={"enabled": False}` gives zero reasoning tokens and an empty field,
consistently across three separate questions. The parameter passes through the
scaffold's call path — `non_cached_lm_call` carries `reasoning` as a first-class
parameter — and no line in the scaffold has to change; putting a value in the
`generation_kwargs` dictionary is enough.

**The verification criterion, determined by measurement: zero tokens AND an empty
field, both together.** A zero-token report alone is not enough; on one call in
default mode `reasoning_tokens=0` came back while the field was 280 characters.

The thinking-off repeat of the boundary control was left until after the family
sweep: the sweep runs with the local `serving_mode` and never uses the hosted
branch.

## S-33 — The machine-readable decision record is produced by parsing prose

> **Bounds a claim.** experiments/decisions.csv — the machine-readable projection of the decision record

> **Closure class.** Next round — making the source structured closes the parsing brittleness

`experiments/decisions.csv` is a projection and its source is
`docs/08-decisions.tr.md`. Its production rests on prose patterns: section headings
(`### K-63 — ...`), supersession phrases (`Cevaplandı, K-28`,
`karar K-34'e taşındı`) and the rationale separator (`**Gerekçe.**`).

**Structural brittleness.** An ordinary prose edit can break the parsing. Changing a
heading level, rewriting a phrase or removing the separator leads to record loss.
The patterns are also **tied to Turkish**; when the English version of the documents
appears, the parser has to stay on the Turkish source or the CSV silently empties.

The fault happened once: the CSV had dropped to its header row, 68 decision rows had
been lost, and noticing it cost a round.

**It is not being restructured at this stage.** Producing the decisions from a
structured source (YAML front matter or separate records) is the right solution but
it is not the work to do now.

**Mitigation: a completeness check.** Every `[KA]-\d+` identifier in the source has
to be found in the CSV; if one is not, the script falls **without writing** the CSV.
It is stronger than a lower bound, because it catches partial loss and not only
total failure: when half the headings were corrupted, 35 missing identifiers were
reported. It is also self-maintaining; no threshold needs updating as the number of
decisions grows.

The check's pattern (`\b[KA]-\d+\b`) is deliberately independent of Turkish words, so
**the protection is less brittle than the thing it protects.** The lower bound did
not have that distinction.

## S-32 — The stopping rule's endpoint criterion had never been in force

> **Bounds a claim.** 05-experiment-design — that the stopping rule ran on two criteria

> **Closure class.** Next round — the rule was fixed; closure depends on re-running the affected measurements

The rule was built from two criteria: a step either changes verifiable state or
reaches a previously untouched API endpoint, and if neither holds it is
progress-free. The second criterion never worked.

**Mechanism.** The rule read the `app` and `api` keys from the step's actions. The
actions come from the `logs/api_calls.jsonl` delta and those rows' keys are `method`,
`url`, `data` — there is no `app` or `api` field. `.get()` returned None for both,
and every call mapped to a single constant identity (`None.None`). After the first
step with a call, that identity enters the "seen" set, so **every subsequent step**
counted as stalled. In practice the rule had degraded to "state has not changed for
N steps in a row".

This happened despite the fact written in `api_capture.py`'s own module docstring:
"`logs/api_calls.jsonl` carries only `method`, `url` and `data`" (S-05). The
information was standing in the document, the code assumed something else.

**The evidence is in the cut points.** Fifteen of the sixteen cut episodes of the
boundary control were cut at exactly the sixteenth step: one progressing step, then
fifteen stalled, threshold fifteen.

**Measured result.** The `sinir3` run gave 13/30; the same model and the same thirty
tasks gave 20/30 without the rule. The broken rule cut eight episodes that had passed
with `agent_finished`: `024c982_3`, `2d9f728_1`, `3b8fb7a_1`, `b6d1104_3`,
`3d9a636_3`, `0de03ea_3`, `8ce6779_1`, `8ce6779_2`. The graded score fell from
95/152 to 40/152.

**What stood, and why.** The band sweep's 0/30 stands. The reason is procedural: the
twenty-six cut episodes had been re-run with the rule off, and those control
endpoints read **from the database**, not from the log. The `app`/`api` in the
database are written through the capture layer and are correct. After the cut, 1603
steps produced zero new endpoints and zero state changes — and at the concrete path
level at that, that is, under the most generous definition. The rule-off control had
been put in as a procedural requirement; it rescued a measurement.

**What fell.** `sinir3` is invalid. The threshold calibration is invalid too: the
computation had been built from the log with a regex and was measuring the
**intended** rule, not the implemented one. It was not meaningless, it had been
applied to the wrong rule.

**That the criterion is load-bearing was measured by this very fault.** With the
endpoint criterion disabled, the broken rule cut forty per cent of the episodes that
would have passed. So without that criterion the state criterion cannot carry success
on its own. S-25's original rationale was weak — what actually caught that episode
was the state criterion — but the criterion itself now has its own independent
rationale.

**The fix.** The endpoint identity comes from AppWorld's own route table: the URL is
matched against compiled route patterns and the template becomes the endpoint
identity (`notes/{note_id}`). The identity is type-independent —
`friends/{user_email}` carries an email and a heuristic dropping numeric segments
would not have caught it. List and detail stay as separate endpoints. All 7138 of the
7138 calls in the 239 recorded episodes resolve.

**Correction, 15 November 2026: 239 episodes, 7138 calls.** This figure has no input
listing and cannot be reconstructed, so whether two outputs of a test were inside the
measurement cannot be known (S-83). The claim that every call resolves holds either way.

The method is not part of the identity: `GET /transactions` and `POST /transactions`
map to the same endpoint. A writing call passes the first criterion because it
changes state; a failed write really is stalling.

**Its class and its guards** are in section 6 of `experiments/setup-protocol.tr.md`.

## S-23 — The published baseline rates for this model class were not consulted before the design

> **Bounds a claim.** K-58 — that the precondition gate was foreseeable before the design

> **Closure class.** Permanent record — not having looked before the design cannot be undone; a new measurement does not change it

While the scale axis was being built on three local quantised models, AppWorld's
published baseline success rates for this model class were never consulted. It was
assumed, and not verified, that a quantised local 7B would sit in a measurable band.
It was the question that should have been asked at the very start of the design.

The numbers were looked at afterwards. `test_normal`, pass@1:

| Model | Task completion |
|---|---|
| Mistral 7B | 0.0% |
| Qwen3-8B, AWQ 4-bit, 32K context | 3.0% |
| Qwen3-8B, FP16, 12K context | 5.4% |
| DeepSeek-Coder 33B Instruct | 7.1% |
| LLaMA-3-70B-Instruct | 20.8% |
| GPT-4o | 48.8% |

Sources: <https://arxiv.org/abs/2407.18901> and
<https://arxiv.org/html/2604.11465v2>.

Our primary model is `qwen2.5-coder:7b-instruct-q4_K_M`, that is 7B and quantised
to four bits. The two nearest published points are 0.0 and 3.0 per cent. The
expected baseline rate is between zero and a few per cent, and the design was built
on top of that.

**Impact.** High, and it touches the body of the design. If the baseline rate is
around 2 per cent, measuring a mechanism effect through binary success needs a very
large sample; this justifies K-55's decision to compute power over an extracted
quantity, but may not be enough on its own.

**Mitigation.** The band sweep and K-57's three paths. The limit goes into the
pre-registration in this form: the published baselines were consulted after the
design, they did not influence the design decisions, and if the sampling rule was
rewritten accordingly that too is written here.

## S-24 — The external review did not ask the precondition question

> **Bounds a claim.** 10-external-review — that the external review audited the design

> **Closure class.** Permanent record — the review happened and did not ask that question; a later review does not undo it

The design went through two rounds of simulated peer review: five models, four juror
roles. None of them asked "can these models solve anything on this benchmark". The
missed question was the design's bottom assumption, and it turned out to be wrong.

The limit is in the review itself. Reviewer simulation audits the design's internal
consistency: is the estimand defined, does the censoring rule produce a confounder,
is the power calculation on the right quantity. All of those are questions inside
the design. The precondition outside the design — whether the thing the apparatus
tries to measure exists at all — stayed in the review form's blind spot.

**Impact.** High, and forward-looking rather than retrospective. In this study the
precondition has now been measured. The permanent side of the limit is this: a design
that passes an internal-consistency review still comes out empty if the thing it
measures is not there.

**Mitigation.** K-58's precondition gate. The gate does not leave the repetition of
the same error in the next design to review; it writes it into the run order.

## S-26 — The same output budget does not mean the same condition across model families

> **Bounds a claim.** the boundary control — that the same budget is the same condition

> **Closure class.** Measured — the same number gave a different condition in the boundary control; the fact is a property of model families

`max_tokens` is 400 on the local model. The same number was given in the boundary
control and the result was misleading: DeepSeek V4 Flash produces reasoning,
`reasoning_content` and `content` eat from the same budget, and as the context grows
the reasoning takes the whole budget and leaves the content empty.

The measured difference:

| | 400 tokens | 4000 tokens |
|---|---|---|
| Tasks passed | 6/30 | 20/30 |
| Code-free steps | 125/501 = 25.0% | 62/902 = 6.9% |
| Closed with `no_progress` | 21 | 4 |

Same model, same tasks, same scaffold; the only thing that changed was the output
budget. The number was equal while the conditions were not.

**The local measurements are unaffected.** qwen2.5-coder produces no reasoning and
the count of code-free steps in the band sweep's 958 steps is zero, so 400 was never
binding there. 7B's 0/30 stands.

**Impact.** High, and not only for this run but for the method. Every measurement
comparing across model families carries the same trap.

**Mitigation and rule.** What has to be equalised is not the number but the budget
not being binding. The audit indicator is the code-free step rate; if it is not near
zero the budget is binding and the result is a lower bound. Because the rate at 4000
tokens is 6.9 per cent, 66.7 per cent is also written down as a lower bound.

**And a method lesson.** I noticed this trap before running and "measured" it with a
single task: fourteen of sixteen steps produced an action, so I wrote that the budget
was sufficient. It was an inadequate check, because the problem does not appear in
the first steps but as the context grows. The right check was not the first steps of
one episode but the code-free step rate across the whole run.

## ~~S-25 — The stopping rule counts a successful read as progress~~

**Closed.** The rule was rebuilt over the endpoint set: a step is progress-free if it
did not change verifiable state and did not reach a previously untouched API
endpoint. A successful call alone does not count as progress.

The rule was measured on its own motivating cases before it was written. In
`09b0ee6_2` the endpoint set saturates at three endpoints on the fourth step and 146
stalled steps follow; in `c77c005_3` it saturates at four endpoints on the fifth
step, followed by 87 stalled steps. The rule fires in both.

The threshold was raised from 4 to **15** and calibrated on both sides.

The false negative side was measured on the local sweep's 62 episodes; all of them
fail and the shortest stall among the pathological ones is 13. But that set only
showed that it separates failures, **it did not show that it spares success.**

The false positive side was measured on the boundary control's 20 passing episodes.
The longest stall is 12 (`b6d1104_3`): a capable model can read the same endpoints for
twelve steps while thinking about what to do. **The value of 10 first proposed would
have cut two of the passing episodes.**

15 cuts none of the passing episodes, cuts 7/10 of the rest, and sits three steps
above the highest observed successful stall. There is a plateau giving the same
result between 13 and 17.

**The measurement's own limit.** Because the boundary control's episodes were written
to JSON, step-level endpoints were reconstructed from the episode log. The method was
compared against the database: step counts are identical across 30 episodes, and the
largest difference in stall length is 4. The direction of the deviation is known — in
call-heavy episodes the log method cannot see the state change and so overstates the
stall, meaning 12 is an upper bound.

**The cost on the false negative side, for the record.** On the local 62 episodes
N=13 caught eighteen episodes, N=15 catches seventeen. The single escaping episode is
`13547f5_2`: 20 steps, stall 13.

The second and larger cost: the old threshold was 4 and 44 of the 62 episodes have a
stall below 15, most of them exactly 4. Those were cut at four under the old rule and
will run to their ceilings under the new one. The sweep will slow down noticeably.

The priority order is deliberate: **first do not cut a passing episode, then catch
the pathology.** A cut success does not come back and its reason is not known either;
an episode running for nothing costs only time.

The value is still provisional; the exact number will come out of the threshold
sweep.

The original text below stays so that it remains on the record.

## S-25 (original text) — The stopping rule counts a successful read as progress

`_made_no_progress` counts a step as having progressed if either of two conditions
holds: the state difference is non-empty, or at least one of its calls succeeded. The
second condition carries a blind spot.

The measured example is `09b0ee6_2`: 150 steps, 736 API calls, 736 of the 736 are
200, and `state_change` is empty in all 150 of the 150 steps. At every step the agent
logs in again and re-pages the same playlist library. The rule never fired once,
because there was a successful read at every step.

The blind spot is not "purposeless state change" but purposeless **successful
reading**. The distinction determines the fix.

**Impact.** Medium. This episode ran to the ceiling and spent fifteen minutes. At
experiment scale the same pattern breaks both the budget and the step ceiling
calibration.

**No mitigation was attempted, because the easy fix is wrong.** Tightening the rule to
"state must change" wrongly cuts read-only research phases and answer tasks whose
verifier is "assert no model changes". The right fix goes through catching repetition:
the same call sequence repeated with the same response. The threshold sweep should
measure that too.

**The centrality of the repetition label was measured.** The same pattern appeared in
two independent places: `09b0ee6_2` re-runs the same login and paging sequence at
every step (150 steps, 736 calls, zero state changes), and `c77c005_3` repeats the
same wrong Venmo login 88 times. In the first the calls succeed, in the second they
fail; the only thing in common is repetition. The step taxonomy (K-36) does not carry
this axis at all, so repetition appears today in neither the stopping rule nor the
taxonomy.
