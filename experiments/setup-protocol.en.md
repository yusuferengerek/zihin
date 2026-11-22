# Setup protocol

Turkish is the source: `setup-protocol.tr.md`.

**This document freezes now.** The experiment pre-registration
(`preregistration.md`) is separate and will freeze after setup finishes, before
the pilot.

## Why the split

Family selection is a measurement, so by K-62 its interpretation rule has to be
written before the run. But the pre-registration's numbers cannot be known until
the family is selected: which family, which sizes, what the noise floor is. Had
it been one document, a list of amendments would have accumulated before the
experiment even started.

The split is also honest. In the setup phase, choosing a parameter by looking at
the data is legitimate; it has to be ruled. In one document it would be unclear
which decision was taken under which regime.

**Everything in this document belongs to the setup regime.** No number that comes
out of it carries a result claim.

## 1. The family selection criterion

The main axis requirements are in K-61: one family, at least three dense sizes
all of which fit in 8 GB under Q4_K_M with a 32K context and q8_0 KV, no
reasoning mode or one that can be turned off entirely, available in Ollama and
instruct-tuned.

The weight ceiling is roughly 5–6 GiB. Measured reference: `qwen2.5-coder:7b`
Q4_K_M is 5.16 GiB on the card, and a 32K q8_0 KV slot is about 0.9 GiB.

**Decision rule.** It is not enough for the family's largest fitting size to pass
the precondition. **At least two sizes have to pass**, otherwise the scale axis
does not live and the second research question dies.

**A rough threshold for eliminating families: baseline success above 25 per
cent.** The exact number will come from the pilot; this threshold is only for
eliminating candidates.

### The two criteria are not conflated

**Main axis requirement:** that at least three dense sizes **exist and fit**.
This is a fact about the family and has nothing to do with measurement.

**Selection criterion:** that at least **two** of those sizes pass the
precondition. This is a measurement result.

If they are conflated, a sweep is spent on a two-size family and even if it wins
the shape of the scale cannot be answered.

Fitting size counts measured from the Ollama registry server (weight ≤ 6 GiB):

| Family | Dense sizes that fit | Requirement 2 | Note |
|---|---|---|---|
| `falcon3` | 1b, 3b, 7b, 10b | **✓ 4** | Dense, no reasoning mode |
| `qwen2.5-coder` | 0.5b, 1.5b, 3b, 7b | ✓ 4 | The current family, failed the precondition |
| `qwen2.5` | 0.5b, 1.5b, 3b, 7b | ✓ 4 | Not a code specialist |
| `qwen3` | 0.6b, 1.7b, 4b, 8b | ✓ 4 | Hybrid thinking; can be turned off, requirement 3 debatable |
| `qwen3.5` | 0.8b, 2b, 4b | ✓ 3 | Its own page says "sparse MoE", which conflicts with the dense part of requirement 2 |
| `deepseek-r1` | 1.5b, 7b, 8b | ✓ 3 | Reasoning cannot be turned off, **eliminated** |
| `granite3.3`, `granite3.2`, `granite4`, `granite-code` | two each | ✗ 2 | Also in the family-control role |
| `gemma3`, `gemma2`, `codegemma`, `starcoder2`, `yi-coder`, `llama3.2`, `hermes3`, `opencoder`, `cogito` | two each | ✗ 2 | — |

**The only clean candidate meeting the requirement is `falcon3`.** Four of its
sizes fit, it is dense, it has no reasoning mode, it is instruct-tuned and it is
not Granite.

**Families with two fitting sizes are not eliminated automatically** but are
**swept last**. If one of them wins, the fact that the shape of the scale cannot
be answered goes into the limitations: two points do not give the direction of a
curve.

### Granite is kept separate

`granite3.3`, `granite3.2`, `granite4` and `granite-code` are different lines but
the same organisation. If Granite goes onto the main axis, the family control has
to come from **another organisation**, otherwise the "different family" control
weakens.

No decision is needed now: none of the four meets requirement 2, so they are not
candidates for the main axis and stay free for the family-control role. The
candidate list contains at least one non-Granite family (`falcon3`).

### Sweep order: by probability of passing, not by purity

The cost is asymmetric: a failed sweep costs one run, while a sweep that passes
at the price of purity costs a run **plus a design concession**. If the clean
candidate has a reasonable chance it goes first; if it is clearly weak the order
changes.

The evidence collected:

| Candidate | Release | Published AppWorld number | Note |
|---|---|---|---|
| `qwen3.5` | February 2026 | none | The newest generation |
| `qwen3` | April 2025 | **8B AWQ 4-bit 3.0%**, FP16 5.4% | `test_normal`, pass@1 |
| `falcon3` | **December 2024** | none | Same generation as Qwen2.5-Coder, not a code specialist |

Source: <https://arxiv.org/html/2604.11465v2>.

**Falcon 3 is the clean candidate but it is clearly weak.** It was released on 17
December 2024, so it is contemporary with the Qwen2.5-Coder that failed the
precondition, and it is not a code specialist either. Our reason for reopening
the family was "a 2026 family may be better than a 2024 family"; putting a
contemporary family first would probably waste a run.

**Order:** `qwen3.5` → `qwen3` → `falcon3` → the two-size families.

Qwen3's published number carries a warning too: the four-bit quantised form of
its 8B gets 3.0 per cent on `test_normal` while our elimination threshold is 25
per cent. It joins the queue but the expectation is low.

**The only family of the 2026 generation that fits is `qwen3.5`.** In the Ollama
library the smallest `gemma4` does not fit at 6.9 GiB; `qwen3.6`, `qwen3.7`,
`qwen3.8`, `llama5` and `phi5` do not exist.

### Two conditional candidates

**`qwen3` — whether thinking can be turned off is verified before the run, not
during it.**

For **each size to be used separately**, this test is run: a prompt that triggers
thinking in the open mode is chosen, and **zero thinking tokens** is shown in the
closed mode. The result goes into the manifest.

If one size does not pass, the family is eliminated. The test is written before
the run, because writing it afterwards falls into the same trap: seeing that
something works does not show it works for the right reason (K-49).

**`qwen3.5` — the axis is defined by the active parameter count.**

The reason for the density requirement was that the scale axis rests on one clear
number. In an MoE the total and the active parameters diverge and the axis
becomes ambiguous.

The rule: **the axis is the active parameter count**, because that determines the
unit cost and the project's cost story is that too. The total parameter count is
recorded beside it. Both are declared before the sweep.

**Dense and MoE families are not mixed on one axis.** The axis is either entirely
dense or entirely MoE.

### The rule for the three outcomes, written before the sweep (K-62)

**If it passes the threshold** the family is selected.

**If it falls between the usable power floor and 25 per cent**, it is compensated
by lowering the threshold and enlarging the evaluation sample. `test_normal` has
123 tasks left, and 10 per cent success on 123 tasks gives the same number of
jointly-solved tasks as 25 per cent on 50. The price is run time.

**If it falls below the power floor as well**, the local path closes and the
choice is between changing the benchmark and upgrading the model layer.

**The strongest local-class data point we have is 5.4 per cent** (Qwen3-8B,
FP16). Its four-bit form is 3.0 per cent, so the cost of quantisation is almost
half. Moving to FP16 is not a solution: it does not fit anything above 3B and
leaves two weak points on the axis.

The meaning is plain: **if `qwen3.5` does not pass, no local family passes on this
benchmark.**

### The elimination design

Each candidate's largest fitting size, on the twelve most discriminating tasks of
the band sweep: six from reference-length band 1–10 and six from 11–20. In the
boundary control DeepSeek got 4/6 and 6/6 on those two bands, and qwen2.5-coder
7B got 0/6 on both.

If a candidate scores zero here it cannot pass the 25 per cent threshold on
thirty tasks and a full run is wasted. Candidates scoring other than zero are run
on all thirty tasks.

**Budgets are set and reported so that they are not binding** (K-60). For each
candidate the code-free step rate and the unparseable step rate are given
separately.

**The number of fitting sizes is verified by measurement, not from the manifest
size.** `qwen3.5:9b` is 6.6 GiB and above the ceiling; whether it actually sits
on the card is measured by loading it. If it overflows we drop one size down,
**and in that case whether the number of fitting sizes falls below three is
checked again** — if it does, the family loses requirement 2.

**The family control is chosen separately**, after the main axis is fixed: a
different family, in the band of the main axis's largest point, one point, having
passed the precondition.

## 2. The tuning budget

**Rule.** How many parameter revisions are permitted after seeing the setup data
is written in advance. Once the budget is spent, a negative result is a
conclusion about **the design**, not about the parameters.

**Four revisions spent so far:**

| # | Revision | What changed |
|---|---|---|
| 1 | The ceiling anchor | From reference solution length to the call count the verifier expects, then to `metadata.num_api_calls` (K-11, K-44) |
| 2 | The cold regime | Because the warm regime was not uniform, we moved to unloading before each episode (K-21) |
| 3 | The precondition threshold | From a "is this a floor effect" diagnosis to a censoring/success-based criterion (K-53, K-58) |
| 4 | The model family | Qwen2.5-Coder failed the precondition, the family is being reselected (A-06, K-61) |

**The budget's number was not written and that is a gap.** The number has to be
set as this document freezes; without it the rule does not operate, because the
verdict "spent" cannot be given.

## 3. Tasks touched during setup

**Rule.** Tasks touched during setup are **removed from the evaluation sample**.
They may stay in the accumulation pool.

As measured (`results/touched-tasks.json`):

| Split | Touched | Total | Remaining |
|---|---|---|---|
| train | 13 | 90 | accumulation pool, no constraint |
| dev | 0 | 57 | accumulation pool, no constraint |
| test_normal | 45 | 168 | **123 tasks remain for evaluation** |
| test_challenge | 0 | 417 | **untouched**, the difficulty split is clean |

The forty-five task identifiers removed from `test_normal`:

```
024c982_1  024c982_3  042a9fc_1  09b0ee6_1  09b0ee6_2  09b0ee6_3
0de03ea_3  1150ed6_1  1150ed6_2  13547f5_2  166f4ff_1  21abae1_1
29a7b7e_1  29a7b7e_2  2d9f728_1  31dc501_2  32616b5_1  32616b5_3
3b8fb7a_1  3b8fb7a_2  3d9a636_3  59fae45_2  5a83b05_2  5a83b05_3
652485c_2  652485c_3  7847649_1  83a7951_2  8ce6779_1  8ce6779_2
9016950_3  986aa4e_2  9dabbc9_2  a30375d_1  afc4005_1  afc4005_3
b6d1104_3  b9c5c9a_3  c77c005_1  c77c005_3  d194965_2  dac78d9_1
f3f60f0_2  ff58e36_3  ffe6d5e_1
```

The reason for removal is not leakage but **having been seen**. On these tasks we
saw which is hard and which is easy, and we examined the per-task results of the
published gpt-4o run. A scope restriction derived from a seen result would be
cherry-picking.

The family sweep continues to run on these forty-five tasks; they are already out
of the evaluation.

**Addendum — 25 September 2026: the list is generated from the record.** The
table and the forty-five identifiers above are the state measured on 28 August;
they are not deleted. The list had been written by hand and had fallen four tasks
behind the record. `scripts/setup/build_touched_tasks.py` now generates it from
the record, and the four readers read it only through `zihin.touched`
(`K-166`). Today's numbers:

| Split | Touched | Total | Remaining |
|---|---|---|---|
| train | **90** | 90 | accumulation pool, no constraint |
| dev | 0 | 57 | accumulation pool, no constraint |
| test_normal | **49** | 168 | **119 tasks remain for evaluation** |
| test_challenge | 0 | 417 | **untouched** |

The four `test_normal` tasks added: `0a9d82a_1`, `0a9d82a_2`, `0a9d82a_3`,
`0de03ea_1`. `train` rising to 90 does not affect the accumulation; it takes the
split's share of the expansion pool from 65 to 0 (the addendum to preregistration
A.10).

## 4. Parameters to sweep during setup, and their decision rules

| Parameter | Decision rule | State |
|---|---|---|
| Step ceiling multiplier `k` | Swept at three values; chosen so the **ceiling-hit rate** stays below 10 per cent in every condition (K-43) | not swept |
| Stopping rule threshold | Ceiling-hit and category 4 rates at different thresholds; recovery with the rule off is also measured | provisional value **15**, with the endpoint-set criterion, calibrated on both sides (section 6) |
| Precondition threshold | The minimum success rate declared for the baseline condition. A rough threshold of 25 per cent for family elimination | rough threshold written, exact number from the pilot |
| Model family | Section 1 | running |
| Family control point | After the main axis is chosen: different family, in the largest point's band, one point, having passed the precondition | not chosen |
| Skill compiler value threshold | The main filter; the lowest value producing a meaningful difference against a naive compiler | no compiler |
| Constant-declaration threshold | In how many different tasks the same value has to be seen. Conservative against wrong freezing, given the cost asymmetry | no compiler |
| Size of the gap constraint | The gap permitted in pattern mining | no compiler |
| Minimum size of the failure index | What the abandonment criterion rests on; below this number no "no effect" verdict can be given | no index |
| Noise floor | The upper bound on residual variance, per model, with the regime it was measured in stated | measured: ≤9.5% per model in the rule-on regime (S-21) |

## 5. Definitions of the diagnostic metrics

All of them belong to the setup regime. **None of them enters the primary metric
or the falsification gates.**

### The mandatory diagnostic metric

**Model calls per successful API call.** Its interpretation is in the
pre-registration: if the ratio does not move, the gain comes from packaging; if
it moves, the gain also comes from less waste.

### Bindingness indicators (K-60)

| Parameter | Indicator |
|---|---|
| Output budget | code-free step rate |
| Context window | truncated observation rate, `was_truncated` |
| Step ceiling | ceiling-hit rate |
| Stopping rule | rate of episodes closed with `no_progress` |

If the indicator is not near zero the result is a **lower bound** and is written
as one.

### The category 4 rate

K-36's fourth category: the code ran and produced no API call at all. Reported
per condition (K-54).

**The two regimes are not mixed.** In the main experiment the rate is measured
with the stopping rule on. The rule-off measurement serves only threshold
selection. The paper states which rate comes from which regime.

### The graded score

**Definition (written before the family sweep).** AppWorld's verifier labels
every requirement: `no_op_fail` is a test that an agent doing nothing fails,
`no_op_pass` is a test that passes even if it does nothing.

**Graded score = the ratio of passed `no_op_fail` tests to total `no_op_fail`
tests.** The `no_op_pass` tests are not counted, because they pass when the agent
does nothing too and are not evidence of progress.

**Its status is a diagnostic metric.** Not a secondary outcome. It never enters
the primary metric or the falsification gates.

**It was born after seeing the data** and that is written plainly: in the setup
phase it was derived as the only quantity with discriminating power while binary
success was zero everywhere.

**It was declared in advance for this use:** comparing candidates in the family
sweep, and seeing whether there is a difference between the baseline and a
candidate when binary success is zero.

### The ceiling-hit rate and the censoring rate

**Two separate quantities, and they are not conflated.**

The ceiling-hit rate is a **measurement artefact**: it has to stay below 10 per
cent and the ceiling multiplier is chosen accordingly.

The censoring rate rests on the verifier's verdict and is a **result**. The ten
per cent rule does not apply to it; if it did, we would have imposed a 90 per cent
success requirement on the baseline.

Censoring is counted by verdict, not by termination reason: whether the episode
hit the ceiling, closed under the stopping rule, or the agent reported completion.
The termination reason is a separate diagnostic field.

## 6. Things that silently cut the measurement

This section was added after the document froze and it keeps growing. The reason
for each addition goes on the record: behind every item there is a measured fault
and all of them are of one family — something going missing without anyone
noticing. Sometimes what goes missing is an episode, sometimes a whole set,
sometimes a criterion itself.

### Every parameter that can terminate an episode is a measuring instrument, not plumbing

**Rule.** It gets calibrated before any measurement it affects is quoted.

The rationale is measured. The stopping rule's threshold was treated as plumbing
and its provisional value was four. In nine of the boundary control's twenty
successful episodes the stall reached four or more, so the old threshold could
have cut about half of the successes. Sixteen of the band sweep's thirty episodes
closed with `no_progress` — fifty-three per cent — and fifteen of those sixteen
would not have been cut by the corrected rule. The precondition gate had fired on
the strength of a sweep that had been cut.

Both sides of the calibration are needed: the threshold has to cut the pointless
step and not cut the episode that could have succeeded. Looking at one side
produced a second error; when the threshold was written as ten the false positive
side had not been measured, and that is why it went up to fifteen.

**Parameters in scope:** the stopping rule threshold, the step ceiling and its
multiplier, the output token budget, the context window. K-60 already requires
their bindingness to be shown; the additional requirement here is that the
calibration happens **before** the measurement.

### An incomplete episode set is never quoted

**Rule.** Either the set is completed or the run is thrown away. One rule, two
applications.

**Rationale: length bias.** An interruption is more likely to hit a long episode
than a short one. If the survivors are kept, the missing ones are systematically
the hard tasks and the success rate comes out biased upwards. "We have this much,
let us use it" is therefore not valid: the missingness is not random.

**Setup and calibration runs: repeat from scratch, with a new prefix.** An
interrupted sweep is abandoned, its prefix is never used again, and nothing is
added to that set. The code already forces this: the run identity is the
manifest's primary key and `scripts/setup/measure_band.py` takes the prefix from
the command line.

**The main run: resume at episode level.** Repeating from scratch is not
applicable there. If the time between interruptions is shorter than the run time,
the probability of completion goes to zero and the rule would have forbidden the
measurement; caution that prevents measurement is not caution. Resuming is
legitimate under three conditions: the set of completed episodes is read from the
database and not from the file system, the opening identity goes into the
manifest, and the post-interruption integrity check is run.

The guarantee is the same in both applications. There is no relaxed rule for the
main run, only a different route to completion.

### Why an episode is atomic

All of an episode's rows are written at the end in a single transaction
(`scripts/record_run.py`). An interrupted episode does not leave half a row, it
leaves no row. The band2 attempt is the proof: all thirty episodes fell and not a
single row entered the database.

Episodes are independent of one another. The seed derives from the task and the
model, not from the position in the queue; the model is unloaded before each
episode and the unloading is verified; the effective context window is verified
again in every episode; the manifest is written per episode and reads the server
settings at that moment. So if conditions changed after an interruption, that
enters the data rather than disappearing silently.

### The post-interruption integrity check

Before appending to a database left open to an interruption, four things are
measured:

| What | Expected | Measured (13 August 2026) |
|---|---|---|
| `PRAGMA integrity_check` | `ok` | `ok` |
| `PRAGMA synchronous` | 1, 2 or 3; **0 (OFF) is not accepted** | 2 (FULL) |
| `PRAGMA journal_mode` | anything other than `off` and `memory` | `delete` |
| The last episode's row set | episode + step + action + observation + verifier verdict | not measured |

If `synchronous` is OFF, even a committed transaction can be lost in a hard
interruption; the missingness would then be biased by length and the rule above
would be violated. The last two pragmas go into the manifest and the schema's
CHECK rejects a non-durable setting: a manifest cannot be written to a non-durable
store.

The first three are one command:

```bash
uv run python -c "
from zihin.records import open_database, storage_durability
b = open_database('results/zihin.sqlite')
print(b.execute('PRAGMA integrity_check').fetchone()[0], storage_durability(b))"
```

The fourth, the completeness of the last episode's row set:

```bash
uv run python -c "
from zihin.records import open_database
b = open_database('results/zihin.sqlite')
print(dict(b.execute('''
  SELECT e.episode_id, e.termination_reason,
         (SELECT COUNT(*) FROM steps WHERE episode_id = e.episode_id) steps,
         (SELECT COUNT(*) FROM verifier_results WHERE episode_id = e.episode_id) verdicts
  FROM episodes e ORDER BY e.episode_id DESC LIMIT 1''').fetchone()))"
```

If `steps` is zero or `verdicts` is zero the episode was written half-way and it
falls out of the set — but because an episode is written in a single transaction
this is not expected. The reason for measuring the unexpected is K-49: seeing that
something works does not show it works for the right reason.

### The rule-off run: the trigger and the interpretation of the three outcomes

**This section was written while the `bant3` sweep was running, before its result
was seen (K-62).**

**Trigger.** If the sweep comes out zero, the episodes **cut by the stopping rule**
are re-run with the rule off. Only the cut ones; not those that ended with
`agent_finished`.

**There is no share threshold and its absence is deliberate.** When the result is
zero, every cut episode is in principle a candidate for "the one that could have
succeeded". Whether the share is ten per cent or eighty, the same question is
asked. Setting a threshold would tie the answer to the size of the share; the
issue is not the size of the share but the cleanliness of the zero.

**Why it cannot be settled at the desk.** The case for "the rule did not spoil the
result" is strong: the threshold was calibrated on both sides, the stall in the
boundary control's passing episodes reached at most twelve, and the threshold is
fifteen. The case for "it did spoil it" is strong too: that calibration came from
**another model's** successful episodes. Because the local model has never had a
successful episode, direct calibration is impossible. The rule-off run is the only
measurement that closes this gap.

**The cost is accepted.** Episodes run to their ceilings, probably a few hours.
The whole direction of the project depends on this zero.

| Outcome | Interpretation |
|---|---|
| Zero with the rule off as well | The stopping rule is not the cause. The 0/30 is clean, the precondition gate rested on sound data, and we move to the family sweep. |
| Other than zero | The threshold is wrong for this model class. We now have successful episodes from this model; the threshold is recalibrated with them, the sweep is repeated, and the family decision is reopened. |
| Zero but the graded score rises markedly | The rule is cutting progress, not success. It does not change the gate; it goes on the record and loosening the threshold in the main run is discussed. |

### A diagnosis independent of the outcome: this model class's dominant failure is stalling, not budget

The class of termination reason changed places between the old rule and the new:

| Termination | Old rule (band, 30 episodes) | New rule (bant3) |
|---|---|---|
| `no_progress` | 16 | being measured |
| `step_ceiling` | 9 | being measured |
| `agent_finished` | 5 | being measured |

Under the old rule nine episodes hit the ceiling. The new rule catches exactly the
class that "looks productive and gets nowhere": no new endpoint in fifteen
consecutive steps and no state change.

**This is a finding to be reported whatever the outcome.** The model loses not by
exhausting its budget but by entering a loop. Raising the step ceiling gains this
class nothing.

### The source a running measurement imports is not edited during the run

**Rule.** While a sweep is running, `src/zihin/**` and `scripts/record_run.py` are
not edited. The sweep runs episodes as subprocesses and each subprocess reads the
source from disk again; an edit made midway runs half the episode set under
different code.

**The manifest could not catch this before.** `code_commit` records HEAD, not the
working tree; an uncommitted change appeared under the same `code_commit` in every
episode.

**Closed.** A dirty working tree now blocks a measurement run. Overriding it takes
an explicit flag and the flag goes into the manifest (`working_tree`). So
`code_commit` really means something: in a clean run HEAD is the whole of the code,
and in a dirty run the manifest says so. Setup exploration is not blocked, it is
marked.

If git cannot be read the value is `unknown` and the run is still blocked: a tree
that cannot be verified clean is not treated as clean.

This rule was violated on 13 August 2026 while the `bant3` sweep was running, and
the violation was measured to be inert: the constant and function added to
`records.py` are not imported by `record_run.py`, no line in the file was deleted
or changed (`git diff --numstat` shows zero deletions), and no episode fell in the
sweep. Being inert does not make the rule unnecessary; next time it may not be.

### A resumed run does not continue without verifying the condition is the same

**Rule.** When resuming an interrupted run, the condition of the written episodes
is compared against the one about to run. If they do not match the run is refused
and the set is run from scratch under a new prefix.

Skipping alone is not enough: a completely written episode is skipped, but if
nobody asks under which condition it was written, the set becomes a mixture of two
different measurements. The manifest records this and **does not prevent it**
(S-31).

The condition-defining fields: model, serving mode, temperature, base seed, output
budget, stopping threshold, context window, KV cache type, flash attention,
AppWorld commit, instruction digest, library identifier, working tree,
**condition**, **split** and **step ceiling**.

Having the condition on the list is critical in the main run: episodes from the
baseline condition and the mechanism condition merging into one set is exactly
what we want to prevent.

`code_commit` is not refused, but the file difference between the two commits is
listed, and if one of the paths that determine what happens inside an episode
appears in that difference, the warning is raised to a refusal. The code that
determines which episode runs is outside the list.

### No parameter that affects the measurement is read from the environment

**Rule.** The environment carries only secrets and values read back from the
server. Every parameter that affects the measurement lives in configuration and
**has no silent default**; if it is not given, the run falls.

The rule was written and had not been applied to `max_output_tokens`. Its silent
default was 400 and one boundary control run started with the wrong budget (S-30).
The same model on the same thirty tasks gives 6/30 at 400 and 20/30 at 4000.

**A fix that prevents is worth more than one that detects.** The resume check
catches this mixture; moving it into configuration stops it happening in the first
place. Both were done.

### A constraint standing where it is written does not mean it is in force

**Rule.** The place where the constraint is **enforced** gets measured, not the
place where it is written.

The rationale is S-29. The machine side of the manifest contract was written into
`schema.sql`, two tests exercised it at schema level and the tests passed — but the
schema is only applied to a file built from scratch, and SQLite's `ALTER TABLE`
carries no constraints. In the live database the machine side of the contract had
never come into force. The tests could not see this because they build a fresh
file; the PR was approved in that state.

Concretely: when a constraint is added, its existence is read **in the file used by
the run**. Reading the schema is not enough; the actual definition in
`sqlite_master` gets read.

### The measurement series are separate, and every number travels with its series

There are two series and both are live:

| Series | File | What is there and what is not |
|---|---|---|
| 1 | `results/zihin.sqlite` | Old stopping rule (threshold 4), no machine side of the manifest contract. 62 manifests, all `local`, only three `qwen2.5-coder` sizes. **Read, not written.** |
| 2 | `results/zihin-2.sqlite` | Corrected stopping rule (threshold 15), the full manifest contract, opening identity and wall clock. |
| 3 | `results/zihin-3.sqlite` | The shield mode constraint is in force too. It could not be added to series 2 because `ALTER TABLE` carries no constraints (S-29); the guard refused the 32B measurement for exactly that reason and the series was opened. |

**Series 1 is not an archive but a live reference.** The two surviving diagnoses
feed from it.

**Series 2 is not an archive either.** The band sweeps, the boundary control and the card run live there; no new measurement is written to it, but it is read and quoted.

**Rule.** Every report quoting a number states which series it came from.
Otherwise someone querying one file later takes it for the whole.

### A field that must exist is not read with `.get()`

**Rule.** A mandatory field is indexed directly and raises if absent; or the schema
is validated once at entry. `.get()` returns None silently.

The rationale is S-32 and, more generally, this repository's whole fault history:
every one of the faults came out of a silent None. The stopping rule read the `app`
and `api` keys — which do not exist in `api_calls.jsonl` rows — with `.get()`,
every call became `None.None`, and the endpoint criterion never worked. Had the
error raised an exception it would have been seen in the first episode.

### The data entering a rule and the data entering the record come by the same route

**Rule.** A criterion and its record are not fed from two separate sources. If they
must be, the difference between them gets measured and reported.

The rationale is S-32 again. The endpoints written to the database came from the
capture layer and were correct; the endpoints the rule read came from the log and
none of them resolved. This difference between the two routes was visible nowhere,
because nothing compared them. Count divergence within the same file was already
being measured — format divergence was not.

### A health criterion: has the criterion degenerated on its own input

**Rule.** That the criterion's input has degenerated will be tested by a number
readable from the measurement itself, and that test will run inside the
measurement run, automatically.

Concretely: if the **distinct endpoint count** the stopping rule sees in a
multi-call episode drops to one, the resolution has collapsed. `record_run.py
--health-check` tests this at the end of a run, and the band sweep's preflight
passes the flag by itself. The boundary control checks the same number after the
first episode, because every episode there costs money.

This criterion would have caught the fault on day one: the broken rule saw exactly
one endpoint in every episode.

### A test's fake data comes from the shape of the real producer

**Rule.** The fake record a unit test builds is nailed to the shape of whatever
really produces that record.

The rationale is S-32's deepest layer: all twelve unit tests of the stopping rule
passed and every one of them used the same invented shape. The test repeated the
shape the code assumed, not the shape it produced. When the two diverged, both were
wrong together.

Concretely: a log from a real run sits under `tests/data/`, the tests build steps
from that shape, and the key set is tested separately.

### The exit status of every command chained before a gate is bound to the gate

**Rule.** The exit status of every command running in front of a gate will be bound
so that it actually stops the gate, and the binding will be tested **by deliberately
failing the command**.

> A check running does not mean its result prevents anything.

Rationale: the same specific thing happened twice.

The first was the verification tool. It called subprocesses without `check=True`; a
crashed calibration left the previous output in place, the tool read the **stale
file** and said "identical", and a commit was reported as verified when it was not.

The second was the test suite. The `pytest` command ran in front of the commit but
its exit status was not bound with `&&`; the suite fell while the commit went
through.

In both cases the check ran, I saw its output, and it prevented nothing.

Concretely: after building the chain, fail the command once on purpose and see the
gate close. The binding is itself an interface, and an untested interface counts as
not working.

### Having been measured against a verifier does not replace branch tests

**Rule.** That a module has been measured against a verifier does not count as
having been tested. Both are needed, separately.

The distinction is this. **Measurement** says how far the output agrees with the
verifier on a sample. **A test** says whether the logic does what it claims in its
branches. The first is a number, the second is a behavioural claim, and neither
proves the other.

The rationale is measured. `allowed_apps.py` was measured against 147 tasks on
train + dev, gave 75.5 per cent exact match and 0.857 Jaccard, went into the
report, was mounted onto the shield — and had **not one line of test**. The rule
that infrastructure apps are unconditionally permitted existed in the code but was
nailed down nowhere; had it fallen, every task using a card would have been wrongly
blocked, and 75.5 per cent would not have seen it, because that number measures the
app set, not whether the rule is in force.

**What is dangerous is precisely the agreement.** The 75.5 per cent made the module
look verified and removed the felt need to write a test. A high number is the best
cover a uncovered branch can have.

### Every roadmap item closes with a closing note

**Rule.** When an item closes, a short note goes into
`docs/reports/mekanizma-kapanis-notlari.md`: what was built, what was measured,
which of the seven done-conditions were met.

**Rationale.** Without it, every number gets re-derived while the pilot report is
being written and the measurements scatter across reports. In this repository the
write set changed twice in one day; the same measurement gave two different numbers
and the only thing saying which was taken under which configuration was the record
itself.

If a condition was not met it is written **with its reason**. Leaving it blank reads
as met.

### Every roadmap item closes with its own PR

**The rule, in four parts.** Every roadmap item closes with its own PR. The item's
closing note goes into the PR description. No PR is opened before the item is
finished, and no next item is started before the PR is opened. The branch name
carries the item being worked on (like `madde-3-derleyici`), not a name that says
nothing about its content.

**The rationale is measured, and the price was counted.** In the setup phase there
was a "one PR per stage" rule; it was not carried over to the mechanism roadmap and
the flow stopped after PR #19. All seven items accumulated on one branch as 52
commits.

The price came from two places. First: **CI saw none of those commits.** Because the
branch was not pushed, that day's four checks did not run, and when it was pushed 45
tests came out red — because of two separate environment differences, both invisible
locally (S-49). Second: splitting retroactively produced unnatural boundaries — one
commit turned out to belong to two items and could not be split, because splitting
would mean rewriting history.

**Splitting is not forced.** If the commits do not sit on a natural boundary they are
grouped as far as they can be and the reason goes into the PR description. Work that
is not a roadmap item also gets its own PR, labelled "not an item".

**All five of the five CI jobs are green on every PR.** A red check starts the fixing
work, not the merge decision.

**The PR report carries a list of new names** (K-102). The report counts, in a
separate section, the module file names added in that PR and the new public
identifiers; if there are none it writes "none". The reason is measured: the language
rule wanted identifiers in English and the rule was set before the renaming round,
but it was not applied going forward — item 8 produced names like `kayit_vekili.py`,
`konteyner_girisi.py`, `soket_koprusu.py` and `SahteDunya`. Review happens through the
report rather than the diff, so the report is the only place the rule can live. An
ASCII check does not catch this: `kayit_vekili` is already ASCII.

### The minimum index size is the number of retrievable patterns, not index rows

**Rule.** The "the index is at the declared minimum size" condition that the per
mechanism abandonment criterion rests on is measured by the number of patterns the
retriever **can reach**. The index's row count is not a valid number for this
condition.

**The rationale is measured.** The most frequent pattern in the index — `GET
api_docs.api_descriptions`, 150 failures — is retrievable by no task: the symbol app
and the infrastructure apps fall out in the retriever (K-86, S-48). So the
retrievable size of a 15-row index is 14, and the difference does not have to stay
this small.

An index full of unreachable rows **looks sufficient** and unfairly acquits the
mechanism: the abandonment criterion says "the index was big enough, so the mechanism
was tried", whereas a pattern that never reaches the model has not been tried. The
same rule

applies to skills too: library size is the number of retrievable skills.

### A report does not copy numbers, it refers to the dataset

**Rule.** The numbers a report rests on live in one machine-readable data file.
The report states headline numbers in prose but does not copy tables, grids or
distributions; it points at the file and the path within it. The data file writes
a digest (sha256) of each of its inputs.

**Rationale.** A copied number ages independently of its source. In this
repository the write set changed twice in one day and the same measurement gave
two different numbers; in a table carried by hand from eight separate outputs, it
is invisible which number came from which configuration.

**The dataset checks the consistency of its own entries.** Do different
measurements come from the same library — if `library_id` and `index_id` diverge,
the build stops. Numbers from two libraries would read as one result and the
difference would be visible nowhere. Concretely,
`scripts/setup/build_pilot_dataset.py`.

### A measurement calls the production implementation of what it measures

**Rule.** A measurement script does not reimplement the logic it measures, it
calls the production implementation. A reimplementation produces two different
right answers and there is nothing to tell which is right.

The rationale is measured, and the rule caught its own violation in the same
session. To measure the shield's false positive rate with a new write set,
`writes_of` was rewritten and gave **zero**; the production path's answer on the
same input was six. The difference was in the URL parsing. Two implementations
produced two numbers and looking at the numbers could not show which was broken —
only a known reference value failing to hold gave it away. Without that reference
value the measurement would have been silently wrong.

Concretely: load the production module with `importlib` and call its function. Let
the thing you want to change be the input, not the code.

### Being small is not being right

**Rule.** When a rate comes out small, the individual cases get examined.
Smallness does not count as evidence of correctness.

The rationale is measured. Shadow mode's first run gave a 0.09 per cent block rate
— 8 out of 9154 calls. It was possible to look at that number and move on. Looking
at each of the eight calls showed that two of them were
`phone.show_contact_relationships`, that it is a pure read, and that it had entered
the write set through a Python `set` method (S-37). Zero point nine per cent never
announces itself.

**Correction, 15 November 2026.** One of the eight blocks was a note opened by
`tests/test_appworld_reset.py` itself: the test wrote its output into the corpus (S-83).
Without it the first run is 7 blocks in 9145 calls, 0.08 per cent. The rule's rationale
stands: the two pure reads were still there.

The same is not needed at large rates, because a large rate is already examined.
What is dangerous is the small rate: it stays quiet and looks correct.

### When a function's behaviour changes, that the caller runs the corrected path is verified separately

**Rule.** A fix is not made only in the definition. That the callers really run the
corrected path is shown by measurement.

The rationale is measured. A method parameter was added to the route resolver and
the distinction was verified, but the measurement script kept calling the resolver
without a method. The function was fixed, the caller was not, and the fix never
appeared in the measurement.

**A static signature check does not catch this class.** That check sees a missing
or extra keyword; **it cannot see a caller that omits a parameter with a default**,
because such a call is valid. Giving a new parameter a default provides backward
compatibility and that is exactly why it stays silent.

Concretely: the same measurement is run before and after the fix and the number is
shown to change. If it does not change, either the fix is inert or the caller is on
the old path.

### Verification is a property of a tree state, not of a task

**Rule.** Saying "verified" is always bound to a commit. A baseline comparison
records which commit it was taken against, a comparison records which commit it ran
at, and **if the tree is dirty, verification is not declared.** If the tree changes,
verification is run again.

This is the same discipline as `code_commit` in the manifest, applied to
verification instead of measurement. The rationale is measured: a commit was closed
as "verified", then a single keyword was fixed and the verification was not
repeated; that fix carried an error that brought the script down.

**A second condition: the tool itself must not give a false positive.** The
comparison script did not check the exit code of its subprocesses. The calibration
fell, wrote no file, and the comparison read the files left from a previous run and
said "identical". A comparison running on a stale file reports sameness **always**,
so the tool is silently green for ever.

**The consequence is retrospective.** No verification made with the old tool is
evidence — including the verification of the identifier renaming. The only valid
verification is the one taken at commit `09cbde6`, on a clean tree and with a
stamped baseline.

### Every parsed string is an interface

**Rule.** A string that is matched, compared or parsed is not prose but an
interface. In a language migration it is identified first; then it is either left
as it is, or changed **in the same commit** as the code that matches it.

Scope: `pytest.raises(match=)`, `in` and `startswith` checks, regular expressions,
equality comparisons, parsing delimiters. If they are translated, the matching code
either breaks silently or silently always returns true.

In the language migration 169 interface strings were found, 20 of them were Turkish
and they fell into three classes: tests bound to an exception message (changed in
the same commit as the message), test data (changed consistently within the file),
and **parsers bound to a source document** (untouched, see S-33).

### A guard has to be less brittle than what it guards

**Rule.** A check guarding a production that rests on a pattern must rest on
something more durable than that pattern.

Concretely, in S-33: the decisions CSV is produced with Turkish prose patterns, but
the completeness check looks at the `\b[KA]-\d+\b` identifier pattern — bound to no
Turkish word. The check stays standing when the parser it guards breaks.

A lower-bound check did not have this property, and it also failed to catch partial
loss: if forty of seventy records disappear, the threshold is either far too loose or
far too tight. The completeness check is also self-maintaining; no threshold needs
updating as the number of records grows.

### Uptime alone is not enough

`created_at` comes from `/proc/uptime` and is precise within a boot, but it resets on
a restart: the start of the episode after an interruption comes out smaller than the
previous one and the ordering breaks silently. That this is not rare was measured —
the WSL virtual machine shuts down when idle, so uptime resets independently of any
power cut.

Two fields went into the manifest. `boot_id` makes the seam visible: two manifests
with different values ran in separate boots. `wall_clock_utc` restores the ordering
across boots, because boot_id is a random UUID and gives no order by itself; its value
comes from SQLite's `CURRENT_TIMESTAMP`, since a time computed inside the process may
be frozen by AppWorld's use of freezegun. The uptime field stays for within-boot
precision.

### A test's markers are determined by its dependencies, not by its subject

**Rule.** A test is marked by looking at what it needs, not at what it is about.
Being "about the sandbox" requires the `sandbox` marker; reading task data
additionally requires the `appworld` marker.

**The rationale was measured twice, both times in the same place.** In S-49
forty-five tests were left unmarked by subject alone and broke in CI because there
was no `appworld install`. In item 8 the same thing recurred: two sandbox tests read
`specs.json` and wanted the app modules, but because they were "about the sandbox"
they carried only the `sandbox` marker. The fifth CI check went red.

A marker is not a label but a contract: "this test cannot run without that". A subject
label does not state that contract.

### A check set up once is a check not set up

**Rule.** A check built to catch a fault goes into the repository and is called from
the standard preflight. A check built temporarily and deleted counts as not built.

**The rationale is measured.** In S-49 a simulation reproducing the CI environment
locally was built by hand, caught both faults, and was deleted when the job was done.
In item 8 a fault of the same class appeared in CI again — had the simulation existed
it would have been seen locally. The simulation is now `scripts/ci_simulasyonu.sh` and
`scripts/local_checks.sh` calls it.

**The check itself was accepted only after being seen to fire.** Its first form built
a temporary worktree from `HEAD`, so it never saw an uncommitted change: when I
removed the marker and ran it, it went green. Built from the working tree, the same
experiment goes red. A check going green does not mean it went green while looking at
the right thing (K-49).

## 7. Where this document is deliberately silent

The hypothesis, the primary cell, the estimand, the analysis plan, the gates, the
form of the noise floor that enters the pre-registration and the power rule are not
here. All of them belong to the experiment pre-registration and will freeze after
setup finishes, before the pilot.

## 8. The one field awaiting a decision

**The number of the tuning budget.** Four revisions have been spent; the permitted
total was never written. This document is not fully frozen until that number is set.

## 12. The three-arm card run: its limit and its interpretation, before the result

This section was written **before** the run. Its purpose is to remove the
possibility of choosing an interpretation after seeing the number.

### 12.1 The setup

Three arms × five tasks × three repeats = 45 episodes, all at the same commit.

| arm | what goes into the slot |
|---|---|
| `cards` | the cards the retriever found for that task |
| `baseline` | nothing; the prompt is byte-identical to the reference (K-25) |
| `irrelevant` | a **non-matching** card from the library, no new mining |

The repeats are `seed_index` 0, 1, 2 — the existing seed derivation mechanism, no
new machinery. A separate run prefix. The original demo result is not deleted from
the record; it stays labelled as a measurement from an older commit.

### 12.2 The limit of the irrelevant arm — measured, not asserted

The library `v0-gap2-sup3-142662f` carries four skills and **all four have an
`auth/token` POST as their effect suffix**:

| skill | length | support | effect suffix |
|---|---|---|---|
| `134ca318…` | 2 | 8 | `POST venmo.auth/token` |
| `9bb946ad…` | 3 | 7 | `POST spotify.auth/token` |
| `65861cf8…` | 7 | 5 | `POST simple_note.auth/token` |
| `3ef8565f…` | 5 | 5 | `POST phone.auth/token` |

The bodies carry the same skeleton too: read the docs, read the supervisor
passwords, get the token. The only app-specific thing is which app's `auth/token`
endpoint is called; **the sequence itself is structural.**

The consequence is this: a card from another app teaches the same lesson — "get the
token, carry it". So **in this library the irrelevant control cannot separate
CONTENT from TEMPLATE.** The only thing it can separate is "card-shaped text" from
"text that is not card-shaped".

This is not a defect but a measured property of this library. Content attribution
needs a library carrying skills that are structurally different from one another,
and this corpus did not produce one.

### 12.3 The interpretation declared in advance

**Stability.** If the three repeats agree on all five tasks the result is stable and
the comparison is meaningful. If they diverge on some tasks the noise floor is not
zero and the comparison is written as a **ratio** rather than a number. If they
diverge on most, the demo's claim of "2 pairs with cards, 0 without" is not
supported and it is **retracted**.

**Arm comparison.**

| observation | interpretation |
|---|---|
| the irrelevant arm close to the carded one | the effect comes from volume and form; content attribution cannot be made in this library |
| the irrelevant arm close to the cardless one | the effect comes from content |
| the irrelevant arm in between | not interpretable at n=5, and reported as such |
| **fits none of them** | **the table was wrong; the result is reported without interpretation and what the table missed is written down** |

The last row really did fire in this run: the irrelevant arm fitted none of the
three predictions and came out **below** both. The detail is in
`docs/reports/uc-kollu-kart-kosusu.md` §4.

**Label.** The result is **demonstrative**, not statistical. Five tasks and three
repeats give no discriminating power and this run carries no gain claim.

**The expected result, written in advance.** The irrelevant arm is expected to
succeed as well, because the homogeneity in 12.2 leads us to expect it. If it comes
out that way, the finding is "the library is too homogeneous for content
attribution" — that is a measured result, not a failure.

### 12.4 What goes into the report

Per task, per arm, per repeat: the result, the step count, the termination reason.
Then the stability analysis, then the arm comparison against the table in 12.3, then
whether the original demo claim survives.


## 13. The pre-declaration rule: every table has a fourth branch

**Rule.** Every interpretation table written before the result carries an explicit
"if it fits none of these" branch. That branch's content is fixed: **the table was
wrong, the result is reported without interpretation, and what the table missed is
written down.**

**The rationale is measured.** The three-arm run's table carried three rows — the
irrelevant arm close to the carded one, close to the cardless one, or in between.
The pattern that came out was a fourth: the irrelevant arm below both. Writing three
rows means assuming the outcome space is covered; and when it is not, the gap that
appears invites forcing the result into one of the rows. No forcing happened, but
the invitation was real, and the invitation itself is a design fault.

**Why a ban on interpretation rather than a new row.** Adding a fourth row to the
table after seeing the result destroys the function of pre-registration: at that
point the interpretation has been chosen by looking at the data. That is why the
fourth branch produces no interpretation — it stops interpretation.

**Its limit.** This branch does not make it possible to see before the run that the
table is incomplete; it prevents the result from being quietly fitted into a row
when it turns out to be. Writing the table completely is still the writer's job.

## 14. The 32B measurement: conditions and interpretation, before the result

**This section was written before the run** (K-62). Its purpose is to remove the
possibility of choosing an interpretation after seeing the number.

### 14.1 What the question is, and what it is not

**The question:** does the precondition gate depend on model size?

The family does not change — `qwen2.5-coder`. The only thing that changes is the
"local, fits in 8 GB" constraint. A decision already locked in the design says the
smallest point of the axis moves up a size if it is pinned to the floor (S-14's
mitigation). Right now **all three points** are pinned, and this run tries one step
above that.

**The question is not:** "does the axis open a band at 32B". 32B is outside the
local constraint and cannot enter the axis; this measurement does not widen the
axis, it narrows the **cause** of the precondition finding.

### 14.2 Mandatory conditions

| Condition | Why |
|---|---|
| The provider will be **pinned** (`provider.only`, `allow_fallbacks: false`) | OpenRouter routes the same tag to several providers and **quantisation is the provider's choice**. Unpinned, the run is not one condition |
| The provider's name goes into the manifest | Which side the condition ran on has to be readable from the manifest |
| Declared quantisation and maximum context go into the manifest **as a declaration** | In hosted mode we cannot verify; the `context_verified = 1` ban stands and is enforced at schema level |
| The output budget is the **same** as the corrected boundary control (4000) and goes into the manifest | 6/30 at 400 tokens and 20/30 at 4000 (S-26). A wrong budget manufactures a **false zero** |
| The ceiling-hit rate will be reported | A zero cannot be interpreted before the budget is shown not to be binding (K-60) |
| Task set, stopping rule, threshold, seed derivation, shield mode: the same as the boundary control | So the only thing that changes is the model tag and the provider |
| The preflight will run | The write path is exercised before thirty episodes start (S-28) |

### 14.3 The pin sits in the transport layer, for a measured reason

**Provider pinning cannot pass through the scaffold's call path, and this was
measured.** OpenRouter reads the routing from the `provider` field in the request
body. The scaffold's `LanguageModel` filters generation kwargs against
`litellm.completion`'s signature; `extra_body` is **not** in that signature, so it
is rejected at construction. `non_cached_lm_call` also rejects any key not in its
own signature, by **raising** through `**kwargs`. Neither is a silent drop, which
is good; but the result is the same: the field does not reach the wire.

**The answer is not to change the scaffold** (K-19). The field is added to the body
in a thin local layer that forwards the request — where the recording proxy and
`api_capture` already sit, and which the scope of K-19 leaves out.

**The arrangement verifies itself:** the pin is read not from the body we send but
from **the provider's response**. OpenRouter reports the serving provider in the
response; that is the value that goes into the manifest. So "we pinned it" becomes
an observation rather than a declaration.

### 14.4 The interpretation, declared in advance — and asymmetric

| Observation | Interpretation |
|---|---|
| **Zero** | A 32B at the provider's precision solves nothing in this environment. The ceiling does not come from our quantisation and the precondition finding **strengthens markedly**; the "you picked a small model" objection closes |
| **Greater than zero** | There is a band. But **we do not know at what precision**: Cloudflare, the only provider, declares the quantisation as `unknown` (measured before the run). It cannot be claimed that the local Q4_K_M equivalent behaves the same — quantisation is the provider's choice, unnamed at that, and the model does not fit in 8 GB anyway. The widest form the finding can take: **"there is a band at 32B as Cloudflare serves it"** |
| **Fits none of these** | **The table was wrong; the result is reported without interpretation and what the table missed is written down** (K-104) |

**The asymmetry is deliberate.** Zero strengthens an existing finding and builds no
new claim. Greater than zero builds a new claim, and that claim's scope is written
already narrowed by two confounders — quantisation and hardware.

### 14.5 Cost

The ceiling is **3.00 dollars**, and the number was set by measurement rather than
by estimate.

The first ceiling written was 1.50 dollars and it rested on the assumption "the
boundary control cost 0.62 dollars, so this run should be comparable". **The
assumption was refuted by measurement.** Real usage read from `sinir3`'s forty-six
episodes is ~100,893 input and ~14,858 output tokens per episode; at Cloudflare's
prices (0.66 $/M input, 1.00 $/M output) thirty episodes come to **~2.44 dollars**.
A 1.50 ceiling would have stopped the run at about 61 per cent.

**And this is not a money question but a §6 question.** An incomplete episode set is
never quoted: because interruptions land on long episodes more often, the survivors
are systematically the easy tasks. Running at 1.50 would have produced a set that was
uncitable the moment it was produced.

The new ceiling adds 20 per cent on top of the measured 2.44. It is still binding:
the runner accumulates spending per episode and **stops** when it is passed, and how
much ran together with the real cost is reported. Passing the ceiling is a result,
not a fault.

**The estimate's own uncertainty.** The number is scaled from DeepSeek V4 Flash's
token usage; a 32B may write more or less. The direction is unknown, so the margin
was set wide enough for either, and the real cost will be reported separately.

Passing the ceiling is not a fault but a result: a run being more expensive than
predicted is also a measured fact and is written as one.

## 15. The 14B measurement on Colab: conditions in absolute values, interpretation before the result

**This section was written before the run** (K-62). The conditions are written as
**numbers**, not as a reference to another run — that is S-58's lesson.

### 15.1 Why 14B and not 32B

14B is the axis's missing point. It keeps the quantisation uniform (`q4_K_M`), it
fits a free T4, and it answers directly the question "is the barrier size, at our
quantisation". 32B was already measured on OpenRouter and there the **precision
was unknown** (`declared_quantisation: unknown`, S-58/S-59); because quantisation
is confounded with size, that measurement cannot separate the size question.
Colab holds quantisation fixed and changes only size.

### 15.2 The conditions, in absolute values (`b14`)

The values below were read from `bant3`'s manifests — the run that produced the
local 0/30 — and written here as numbers. The run will use these; it will not say
"the same as".

| Field | Value | Source |
|---|---|---|
| `model_tag` | `qwen2.5-coder:14b-instruct-q4_K_M` | the axis's missing point |
| `serving_mode` | `local` | Ollama, on the Colab GPU |
| `max_output_tokens` | **400** | `bant3` manifest |
| `no_progress_limit` | **15** | `bant3` manifest |
| `shield_mode` | **`off`** | `bant3` manifest |
| `temperature` | **0.2** | `bant3` manifest |
| `base_seed` | **123** | `bant3` manifest; the seed derives through `seed_for(task_id, seed_index)` with model and condition deliberately out (K-20) |
| `num_ctx_requested` | **32768** | `bant3` manifest |
| `kv_cache_type` | **`q8_0`** | `bant3` manifest |
| `flash_attention` | **1** | `bant3` manifest |
| Step ceiling | multiplier `k = 2`, floor 20, cap 150 | the band sweep's formula: `min(max(2 × anchor, 20), 150)` |
| Task set | the same thirty tasks | before the run it will be **compared exactly** against `bant3`'s task set, as was done for `b32` |

**The 400 tokens carry a condition of their own.** S-26 measured that four hundred
tokens was not binding locally — `qwen2.5-coder` produces no reasoning and the
count of code-free steps in the band sweep's 958 steps is zero. But that was
measured **for 7B**, not for 14B. So the run will **report the code-free step
rate**; if it is not near zero the budget is binding and the result is a lower
bound (K-60).

### 15.3 What gets measured before the run

`scripts/setup/measure_colab_environment.py`, and all three are properties of the
machine:

**The GPU and its VRAM.** The model name and total memory the driver reports.

**Whether the model sits entirely in VRAM.** Locally all three sizes were measured
fully resident (29/29 layers at 7B). A partially offloaded model runs a different
computation at a different speed, and a step ceiling calibrated on a resident model
would then be measuring the disk. **If it is not fully resident the run does not
start** — the script exits 1.

**Model load time.** K-21's cold regime rests on the locally measured 2.72 / 3.01 /
3.55 seconds. Colab's disk is not that disk. If loading costs ten times more, the
regime's price changes and that has to be written **before** the run.

**Whether the server actually ran the configuration it was given.** A fourth
measurement, and a separate question. `server_settings` reads what was
*requested*: `OLLAMA_FLASH_ATTENTION`, `OLLAMA_KV_CACHE_TYPE`. Whether the
hardware *honoured* it is another matter. On a GPU that does not support a q8_0
KV cache the request is accepted silently and the cache is kept in f16: twice the
memory, and section 15.8's arithmetic no longer holds. A configuration requested
but not applied means the environment is running **a different measurement**, not
a slower one, and in that case the Colab result cannot be compared with the local
one.

So it is read from the server's own log rather than asked of the setting:

| What is read | The line it comes from |
|---|---|
| Layers offloaded to the GPU | `offloaded 29/29 layers to GPU` |
| Flash attention as **effective** | `llama_context: flash_attn = enabled` |
| The KV cache's **effective** type | `K (q8_0): ..., V (q8_0): ...` |
| The KV cache's size | `llama_kv_cache: size = 952.00 MiB` |
| The **requested** values | `--cache-type-k q8_0 --flash-attn on` |

The parser was written and tested against a real load log locally: at 7B,
**29/29 layers, flash attention enabled, KV q8_0, 952 MiB** — which confirms
section 15.8's line about 0.9 GiB measured at 7B. The same lines will be read on
Colab, and requested and effective reported separately.

### 15.4 Colab is the third environment

Third after WSL and CI. Three guards in this repository turned out to be
environment-dependent and the clean-clone run found a fourth; K-117 holds in a new
environment too. The bootstrap script **runs every guard once** and reports which
one disagrees here. The sweep reports rather than stops — the point is not to judge
the environment but to see what diverges.

### 15.5 The interpretation, declared in advance

| Observation | Interpretation |
|---|---|
| **Greater than zero** | The band exists **at our quantisation and at 14B**, so the barrier was size. The scale axis's second point comes back |
| **Zero** | The difference between 7B and 32B may come from **precision** rather than size. The next measurement is then a hosted 7B, because that is the control which holds size fixed and changes precision |
| **Fits neither** | **The table was wrong; the result is reported without interpretation and what the table missed is written down** (K-104) |

**The result will be labelled exploratory.** The axis point was chosen **after**
the zeros were seen; this is not a pre-registered cell but a diagnostic measurement
that narrows the cause of the precondition finding. However well it comes out, it
does not count as confirmatory.

### 15.6 The session budget and its branch

On Colab's free tier the session length and the GPU quota are limited, and the cut
comes without warning. This is the time counterpart of §14.5's money ceiling.

**Budget: three sessions.** If thirty episodes are not finished in three sessions
the run stops and the **incomplete set is reported without interpretation**; §6
already forbids quoting an incomplete episode set, and this branch extends that to
the interpretation side.

**A session limit does not block the run, because the resume logic skips what is
complete** — and that claim is tested: `tests/test_resumption.py` nails down that
skipping only removes elements and does not change how a remaining episode runs
(neither the sequence number nor the seed is affected by skipping). So a set left
half-finished at the end of a session is completed from where it stopped in the
next one, and completed episodes are not re-run.

**Results are pushed to the repository at the end of every session** (§15.7). When
the session disappears the data does not: the database is linked to Drive and the
results are committed.

**The number is declared, not estimated.** How many sessions were spent and how
many episodes ran in each will be reported. Exceeding three sessions is a result
rather than a fault: that this measurement cannot be run on the free tier is also
a measured fact.

### 15.7 Results are not pasted by hand, they are pushed to the repository

**Rule.** The Colab run's outputs are not pasted into a chat; the notebook pushes
them into the repository and they are read from git.

**Two candidates were weighed and one was chosen.**

*Writing to Drive and reading it from WSL through `/mnt/c`.* Needs no token. But it
creates a second copy that can drift, and the deciding reason is this: **a file on
Drive has no commit identity.** This repository's whole discipline is that every
number travels with the commit that produced it — the manifest carries
`code_commit`, the reports name a series, and `check_merged_artefacts.py` can only
verify what is in git. A number read off Drive cannot be bound to any tree state,
which is exactly what K-116 was written about.

*The notebook pushing to the repository.* Costs a token and gives the result a
**commit identity**. This is the one chosen.

**Safety conditions, written into the script.** It never pushes to `main` and never
force-pushes: results land on the `colab-sonuclari` branch and a person merges
them, so an automated push can add to history but never rewrite it. Only files
under `results/` are pushed — no source change comes this way, because the code
that ran has to be the code that was reviewed.

**The token.** It lives in Colab Secrets and the notebook reads it with
`google.colab.userdata`; `~/.zihin-env` is a WSL arrangement and does not apply
there. The token is written to no file, printed nowhere and never committed. **It
does not enter the command line either:** git reads it from the environment
through `GIT_ASKPASS`, and it is not carried inside the address. That is not
caution but a measured lesson — the first form put the token in the clone URL,
the clone failed, and because Python's `CalledProcessError` prints
`process.args` the secret left the runtime inside a traceback and had to be
revoked (K-124). Its remaining limit: for the length of the session the token
sits in the process environment and in `/tmp/zihin-askpass.sh`, and a process of
the same user can read both — accepted because a Colab runtime is a single-user
virtual machine.

**The push is verified, not assumed.** After pushing, the script compares the
remote branch's SHA with the local one and exits 1 if they differ (K-116).

### 15.8 Whether 14B fits on the T4: the estimate and the measurement that binds it

The T4 was measured: **15360 MiB total, 14913 MiB free**, 12 GiB RAM, 66 GB free
disk.

The estimate was derived from measured numbers already in the repository:

| | |
|---|---|
| 7B weights, **measured** | 5.160 GiB |
| 14B weights, estimated | ~9.98 GiB (from the per-parameter ratio) |
| 32K q8_0 KV, **measured at 7B** | 0.9 GiB |
| 32K q8_0 KV, estimated at 14B | ~1.54 GiB (layers 28 → 48) |
| **Total estimate** | **~11.5 GiB (11800 MiB)** |
| Free VRAM | 14.56 GiB (14913 MiB) |
| Margin | ~3.0 GiB |

**This is an estimate, not a measurement, and it does not decide.**
`measure_colab_environment.py` asks the server whether the model really is entirely
in VRAM and measures it; if it is not fully resident the exit code is 1 and the run
does not start. The estimate only answers "is it worth trying".

### 15.9 What the Colab image carries and what it does not

Environment facts, measured. None of them are our choices; they are properties of
the image we run on, and each is recorded because each cost a round.

| Fact | Consequence |
|---|---|
| GPU: Tesla T4, 15360 MiB total, 14913 MiB free | 14B fits (section 15.8) |
| RAM 12 GiB, the `/content` disk 113 GB (66 GB free) | the 9 GB model pull fits |
| Drive is a FUSE mount | the model cache is **not** on Drive; it is on `/content` |
| **no `zstd`** | the Ollama installer unpacks a zstd bundle and fails |
| `UV_SYSTEM_PYTHON=1` is set | a `uv pip install` without a named target installs into the system Python (K-129) |
| every cell is its own shell | a variable `export`ed in one cell does not reach the next |
| no `gh` | the merged-PR artefact check declines to answer, with its reason |

The absence of `zstd` alone cost a round, and the cost per round comes from the
user being in the loop. That is why the check in section 15.10 was written: ask
everything up front instead of discovering one item at a time.

### 15.10 Prerequisites are checked up front, and all together

**Rule.** Before the Ollama install starts, the prerequisites of every remaining
step are checked, and **every missing one** is reported at once.

**The reason, as a number.** The Colab bootstrap failed in five rounds on five
different missing preconditions: the tokenless clone, the upstream LFS budget,
the empty data cache, the wrong Python environment, `zstd`. Each round revealed
the next. In an N-step chain, asking the preconditions up front turns N rounds
into one.

**What is checked.** The binaries (`curl`, `tar`, `git`, `zstd`, `nvidia-smi`),
the project environment's three imports, the GPU's VRAM, the model's real size
**asked of the registry** (8.99 GB), disk space at three paths, writability at
three paths, and the state of the server port.

**No check stops another.** A first missing item that hides a second one is the
shape of the problem, not a detail of it.

**What can be installed is not a failure.** If `zstd` is absent and `apt-get` is
present, the check reports it as "will install"; the failure is both being
absent.

---

## 16. Colab 32B — on an A100, with our own quantisation

### 16.1 Why this point

Four points of the `qwen2.5-coder` axis have been measured: 1.5B, 3B and 7B at
zero locally; 14B at 3/30 on Colab's L4. The fifth point is 32B, and it **opens
no new lock** — the local-hardware lock was already opened by 14B (K-133). The
only thing it extends is scale: 32B fits comfortably on an 80 GB A100.

**The 32B on OpenRouter is not this point.** That measurement was made on a
hosted server, with weights of unknown quantisation, over an incomplete set
(27/30) (S-58, S-59). This point uses our own quantisation: `q4_K_M`, measured
file size **19.851 GB**.

### 16.2 Conditions (`b32c`), in absolute values

| Field | Value | From |
|---|---|---|
| `model_tag` | `qwen2.5-coder:32b-instruct-q4_K_M` | the axis's fifth point |
| `serving_mode` | `local` | Ollama, on Colab's A100 |
| `max_output_tokens` | **4000** | `config/recording.yaml` |
| `no_progress_limit` | **40** | `config/recording.yaml` |
| `shield_mode` | **`shadow`** | the runner's mount default |
| `temperature` | **0.2** | `config/models.yaml` |
| `base_seed` | **123** | `config/models.yaml` |
| `num_ctx_requested` | **32768** | `config/models.yaml` |
| `kv_cache_type` | **`q8_0`** | `config/models.yaml` |
| `flash_attention` | **1** | `config/models.yaml` |
| Step ceiling | `min(max(2 × anchor, 20), 150)` | the band scan's own formula |
| Task set | the same thirty | compared one-to-one against `bant3` |

### 16.3 Why these values, written down because conditions must not look chosen from the result

**`max_output_tokens` is 4000, and 400 was an accident rather than a design.**
Section 15.2 read four hundred off a `bant3` manifest. Measured: `bant3` took
that value while `config/recording.yaml` had **no `max_output_tokens` key at
all** (commit `fc9101a`). So 400 was not a chosen budget but the residue of a
default. 4000 was written into the configuration later and **deliberately**.
S-26 measured that four hundred does not bind at 7B, but it was seen to bind on
a capable model; choosing four hundred for 32B would tie the result to the
budget.

**`no_progress_limit` is 40.** From the same record: at `bant3`'s time the
configuration carried 15 and it later became 40. In the 14B run eleven episodes
stopped under this rule; tightening it now would cut the run earlier and make
the two runs incomparable.

**`shield_mode` is `shadow`, because `off` is UNREACHABLE.** `ShieldMode` carries
only `shadow` and `enforce`; there is **no** `off` member. The `off` in section
15.2 was copied from manifests made before the shield was mounted. Shadow mode
does not block, it only observes — the trajectory is unaffected.

**These three values are the ones the 14B run used, and that coincidence is not
hidden.** The 14B run happened **before** this declaration, and it did **not**
run with the 400/15/off that section 15.2 declares; it ran with 4000/40/shadow,
because the place of declaration and the place of reading were different (S-58's
third instance, K-136). So the two runs agreeing on conditions is the outcome of
an accident, not of a design. The agreement makes the comparison possible; but
"it ran under the same conditions as 14B" became true **afterwards**, not by
having been declared in advance.

### 16.4 The architecture difference will be read, not assumed

The axis's points are measured on **three different cards**: the local RTX 4070
(Ada, 8.9), Colab's L4 (Ada, 8.9), Colab's A100 (**Ampere, 8.0**). Ampere is a
different generation and its support for flash attention and a `q8_0` KV cache
may not be the same.

This will be **measured, not guessed**. `runtime_facts` reads the requested and
the effective value out of the server's own log, and the `comparability` verdict
is printed before the run. If it is not `COMPARABLE` the run still happens and
the result is labelled **"not comparable with the local measurement"**. The
limitation is S-61.

### 16.5 The interpretation, declared in advance

| Observed | Interpretation |
|---|---|
| **Greater than zero** | The band exists at 32B under our own quantisation too. The OpenRouter probe's quantisation confounder falls away and the axis reaches four measurable points. |
| **Zero** | This is the more interesting one, because 14B gave 3/30. It would mean there is no monotone relation between size and success, and the reason is then looked for — quantisation, architecture, or the task set itself. |
| **Neither** | The table was wrong. The result is reported without interpretation and what the table missed is written down (K-104). |

**The result is exploratory.** The fifth point was also chosen after the zeros
were seen.

### 16.6 The nearest comparison available

The OpenRouter 32B run also ran with **4000 / 40 / shadow**. So the difference
between Colab 32B `q4_K_M` and OpenRouter 32B is largely **quantisation**. The
provider and `serving_mode` change too, which is a confounder; but this is the
nearest comparison available.

**Existence, not rate.** The OpenRouter set is incomplete (27/30, S-59) and
section 6 forbids quoting a rate from an incomplete set. The direction of the
incompleteness is asymmetric: unrun episodes can hide a pass, not manufacture
one.

### 16.7 The anchor warning, carried here because it is the same thirty tasks

The step ceiling is derived from the anchor, and the anchor (`num_api_calls`)
measures **the reference solution's path**, not what the task requires. Measured
in the 14B run: `09b0ee6_1` carries an anchor of 102 and was passed in six steps;
the task text asks for six artist names — an **answer task** — and its only
meaningful test is a string equality. So the `90+` band label describes the
length of the reference path for that task, not its difficulty.

Because the same thirty tasks are run, the warning applies here too: **per-band
results will be reported with the band label, and with what the label measures
written next to it**. The limitation is S-62.

---

## 17. The local axis, re-run at four thousand tokens

### 17.1 Why it is re-run, and why 4000

The axis's three local points — 1.5B, 3B, 7B — were run with a **400-token**
output budget and all three gave zero. The Colab points ran at 4000: 14B 3/30,
32B 11/30.

**400 was an accident rather than a design.** Written down with the measurement
in section 16.3: `bant3` took that value while `config/recording.yaml` had no
such key at all (commit `fc9101a`). Not a chosen budget but the residue of a
default. 4000 was written into the configuration later and deliberately.

**That the budget binds was measured.** S-26 measured that four hundred does not
bind at 7B, but that measurement was about the **share of steps without code**,
and while the band was at zero the binding could not show. It was seen to bind on
a capable model.

**Every point of the axis has to sit at the same budget.** Otherwise the axis is
not an axis but two separate measurements at two budgets, placed side by side. A
size axis has to measure size; if the output budget moves too, it carries two
variables at once.

**This re-run is NOT CONFIRMATORY.** The budget was changed after the results
were seen. A result above zero could be read as "it was the budget", but that is
a discovery, not a pre-declared test. The record carries it as such.

**The interpretation, declared in advance.** If all three stay at zero: the
budget is not the explanation, and the cause of the local zeros is elsewhere. If
at least one comes out above zero: 400 was binding and the three old zeros were a
**lower bound**, not a measurement — and S-14's "floor effect" reading is then
re-examined. If neither, K-104.

### 17.2 Conditions (`b15l`), in absolute values

| Field | Value | From |
|---|---|---|
| `model_tag` | `qwen2.5-coder:1.5b-instruct-q4_K_M` | the axis's point |
| `serving_mode` | `local` | Ollama, on the development machine |
| `max_output_tokens` | **4000** | given explicitly in the run command |
| `no_progress_limit` | **40** | given explicitly in the run command |
| `shield_mode` | **`shadow`** | the runner's mount default |
| `temperature` | **0.2** | `config/models.yaml` |
| `base_seed` | **123** | `config/models.yaml` |
| `num_ctx_requested` | **32768** | `config/models.yaml` |
| `kv_cache_type` | **`q8_0`** | `config/models.yaml` |
| `flash_attention` | **1** | `config/models.yaml` |
| Step ceiling | `min(max(2 × anchor, 20), 150)` | the band scan's own formula |
| Command | `uv run python scripts/setup/measure_band.py b15l --stop-threshold 40 --max-output-tokens 4000` | the one line that starts the run |

### 17.3 Conditions (`b3l`), in absolute values

| Field | Value | From |
|---|---|---|
| `model_tag` | `qwen2.5-coder:3b-instruct-q4_K_M` | the axis's point |
| `serving_mode` | `local` | Ollama, on the development machine |
| `max_output_tokens` | **4000** | given explicitly in the run command |
| `no_progress_limit` | **40** | given explicitly in the run command |
| `shield_mode` | **`shadow`** | the runner's mount default |
| `temperature` | **0.2** | `config/models.yaml` |
| `base_seed` | **123** | `config/models.yaml` |
| `num_ctx_requested` | **32768** | `config/models.yaml` |
| `kv_cache_type` | **`q8_0`** | `config/models.yaml` |
| `flash_attention` | **1** | `config/models.yaml` |
| Step ceiling | `min(max(2 × anchor, 20), 150)` | the band scan's own formula |
| Command | `uv run python scripts/setup/measure_band.py b3l --stop-threshold 40 --max-output-tokens 4000` | the one line that starts the run |

### 17.4 Conditions (`b7l`), in absolute values

| Field | Value | From |
|---|---|---|
| `model_tag` | `qwen2.5-coder:7b-instruct-q4_K_M` | the axis's point |
| `serving_mode` | `local` | Ollama, on the development machine |
| `max_output_tokens` | **4000** | given explicitly in the run command |
| `no_progress_limit` | **40** | given explicitly in the run command |
| `shield_mode` | **`shadow`** | the runner's mount default |
| `temperature` | **0.2** | `config/models.yaml` |
| `base_seed` | **123** | `config/models.yaml` |
| `num_ctx_requested` | **32768** | `config/models.yaml` |
| `kv_cache_type` | **`q8_0`** | `config/models.yaml` |
| `flash_attention` | **1** | `config/models.yaml` |
| Step ceiling | `min(max(2 × anchor, 20), 150)` | the band scan's own formula |
| Command | `uv run python scripts/setup/measure_band.py b7l --stop-threshold 40 --max-output-tokens 4000` | the one line that starts the run |

### 17.5 How the run is arranged

The three models run **in sequence**, thirty tasks each. The server is started
with the project's settings (`scripts/serve_models.ps1`), so `num_ctx`,
`kv_cache_type` and `flash_attention` reach the server process and go into the
manifest from there (K-22).

**The model name is not written a second time anywhere.** Each run carries its
own prefix, the prefix names its own conditions section, and the model is
resolved from that section (K-138). Three models running one after another is
exactly where that gets tested.

**Resumption.** If the machine goes down, completed episodes are skipped
(`tests/test_resumption.py`), so the run continues where it stopped.

**A separate report per model**: the band distribution, the termination reasons,
the ceiling-hit rate, the step counts of the passing episodes, and the graded
score.

## 18. The accumulation run: a corpus from the evaluated model's own episodes

### 18.1 Why now, and what it closes

The "accumulate, mine, evaluate" loop that is the heart of the design has never
run. Today's library was mined from the boundary control's episodes, that is,
from **another model's** successes; the model to be evaluated has never
accumulated any experience of its own.

**What it does not close.** This run does not answer the primary question. It
produces a corpus, and measures how much that corpus grows the library.

**Addendum — 3 September 2026, after block 1's mining stopped at a guard.** With
this addendum the corpus is defined as **model tag AND split**: the library and
the index are mined from episodes whose `model_ref` equals the declared model
**and** whose `split` is `train`; both builders take the rule as a required
argument and the runner passes it.

**This is a correction, not a deviation.** The sentence above said "the corpus
comes from the evaluated model's own episodes"; the miner, however, read every
passing episode in the file, with no prefix, condition or model filter. The
file on Colab was measured: `b14` (14B, 31 episodes, 3 passes), `b32c` (32B,
`test_normal`, 31 episodes, 11 passes) and `bir1` (32B, `train`, 64 episodes,
17 passes). The twelve-call sequence the guard bound on was `GET
spotify.songs/{song_id}` repeated, supported by two `b32c` episodes and one
`bir1`. A corpus that did not match the declaration is being returned to the
one declared.

**Two reasons.** The first is the declaration itself: `b14` is another model,
`b32` another run with unknown quantisation (`S-58`). The second is
**leakage**: `b32c` is the same model but ran on `test_normal`, and the
evaluation is on `test_normal`. A skill mined from `b32c`'s passes encodes an
evaluation task's call sequence; measuring on that set afterwards would be
training on the test set.

**The rule is written as model plus split, not as a prefix.** Today that equals
`bir1`'s seventeen passes; when a second `train` run comes it joins, and a
sibling of the same model on `test_normal` stays out. A prefix could say
neither.

**What the filtered corpus gave.** Seventeen episodes, seventeen tasks, 490
calls, an alphabet of 35; at gap 2 / support 3 **18 closed patterns, 9 with an
effect, 4 skills**, and the guard does not bind — the same 18 patterns at caps
of 12, 24 and 48. The calibration corpus gave 4 skills from 105 patterns; here 4
from 18. Recorded in `K-159`.

### 18.2 Conditions (`bir1`), in absolute values

| Field | Value | From |
|---|---|---|
| `model_tag` | `qwen2.5-coder:32b-instruct-q4_K_M` | the experiment's declared model |
| `serving_mode` | `local` | Ollama |
| `max_output_tokens` | **4000** | `config/recording.yaml` |
| `no_progress_limit` | **40** | `config/recording.yaml` |
| `shield_mode` | **`shadow`** | the runner's mount default |
| `temperature` | **0.2** | `config/models.yaml` |
| `base_seed` | **123** | `config/models.yaml` |
| `num_ctx_requested` | **32768** | `config/models.yaml` |
| `kv_cache_type` | **`q8_0`** | `config/models.yaml` |
| `flash_attention` | **1** | `config/models.yaml` |
| Step ceiling | `min(max(2 × anchor, 20), 150)` | the band scan's own formula |
| Task set | all ninety tasks of the `train` split | the accumulation pool |
| Seed | one, `seed_index` 0 | support is counted by distinct task |
| Condition | **`baseline`** | no cards: the corpus must not be contaminated by the mechanism under test |
| `runtime` | **A100** | the 32B's measured file is 19.851 GB; it does not fit a T4's 15360 MiB (§16.1) |
| `model_file_gb` | **19.851** | the measured file size of this tag in §16.1 |
| `block_size` | **30** | `scripts/setup/run_accumulation.py` |
| `episode_ceiling` | **270** | §18.3, branch B |
| `first_sweep` | **90** | the number of tasks in the `train` split; the first sweep runs all of them |
| `library_max_gap` | **2** | `results/accumulation.json`; the library in the record is `v0-gap2-sup3-142662f` |
| `library_min_support` | **3** | the same measurement, the same id |
| `index_min_support` | **1** | `results/accumulation.json` (`failure_index.min_support`); the index in the record is `v0-sup1-4bb340a` |
| `library_max_length` | **256** | a budget, not a threshold: 64 binds, 128/256/512 give the same 68 patterns and the same 9 skills (`K-161`) |
| `delivered_library_id` | `v0-gap2-sup3-0c3f4ac` | the library the run delivered; 11 skills, 45 supporting episodes |
| `delivered_index_id` | `v0-sup1-0c3f4ac` | the index mined in the same block; 29 cards |
| Command | `uv run python scripts/setup/run_accumulation.py bir1` | the single line that starts the run |

**Addendum — 13 September 2026, at the accumulation's closure.** The last two
rows are not a condition but the run's **output**: the identities of the library
and the index it delivered. They are written here because they must not change.
The library will be the experiment's input and `latest_library_and_index` picks
by row count, so a library mined later could silently take its place. The
preflight now compares the identity it resolves against these rows and
**refuses** if they differ. Both were mined at commit `0c3f4ac`, at gap 2 /
support 3 / constant threshold 3 (`K-164`).

**Addendum — 3 September 2026, after block 1's mining failed.** Three more rows
for the same reason: no value changed, it turned out a value had never been
declared. The **rule** for the mining thresholds was preregistered (`K-50`:
"chosen so, according to this measurement"), their **numbers** belonged to the
setup phase and the setup had long since filled them in — but they were in no
machine-readable place. The runner called `build_skill_library.py` with no
arguments and that script does not start without `--max-gap` and `--min-support`;
it failed at the block boundary after sixty episodes had been written. The
numbers were already written into the ids of the library and the index in the
record, just not anywhere that could be read.

**Addendum — 3 September 2026, after block 3's mining stopped at the depth cap.**
The `library_max_length` row went in. It is a **budget**, not a declared
threshold: the miner still names itself if it binds. The value was chosen as
"non-binding", not as "completing": on the fresh record (29 passes, 1102 calls)
64 binds — the longest pattern is 70 — while 128, 256 and 512 do not, and all
three give the same pattern set (68) and the same library (9 skills). 256 is
twice the first non-binding value, three and a half times the longest pattern,
and above the longest episode in the record (159 calls); a pattern can be no
longer than the shortest episode supporting it.


**Addendum — 31 August 2026, before the run.** These four rows went in that
day, and a fifth (`first_sweep`) was added the same day. No condition
changed; it turned out a condition had never been declared. The notebook was
telling the user to pick a T4 and there was nowhere else for it to say
otherwise: §18 named no runtime at all, so the value the notebook carried was
not a copy but the **only source**, and it was left over from the `b14` era.
Removing a copy of a value presupposes there is an original to read.

**This run does not read the library, and must not.** The condition is
`baseline`, so no card enters the prompt. Had it run carded, the corpus it
produces would be contaminated by the mechanism under test, and a library mined
from that corpus would be **circular**: feeding the mechanism from episodes the
mechanism produced. The preflight is therefore run with `--prefix bir1`; it reads
the declared condition and does **not** require the library for this run (K-152).

**One seed, and the reason is a measured fact.** Support is counted by distinct
task, so a second seed on a task that already passed adds nothing to the library.
Breadth before depth.

### 18.3 The stopping criterion: two branches, whichever fires first

**Branch A — yield.** At the end of every block of thirty episodes the library
**and** the index are re-mined with the real builders. **If two consecutive
blocks add zero new skills, the run stops.** It reads skills rather than
patterns, because the filtering chain that takes a hundred and five patterns down
to four skills was measured not to track the pattern count. Two blocks rule out
one block's coincidence.

**Branch B — a cap.** Two hundred and seventy episodes. If A has not fired the
run **stops anyway** and the report reads "the library had not saturated at 270
episodes". That is a result, not a failure.

**What runs after the first ninety.** The first sweep is all ninety tasks at seed
zero. If neither A nor B has fired, the second sweep re-runs only the **failed**
tasks at the next seed; a second seed cannot add support on a task that already
passed, but it can on one that failed.

### 18.4 The index is mined in the same block as the library

`S-65` happened once: the corpus grew, the index was not re-mined, and the
fifteen cards in the record fell behind the twenty today's corpus yields. In this
run the index is re-mined in **every block** where the library is. The two
builders are `scripts/setup/build_skill_library.py` and
`scripts/setup/build_failure_index.py`, and the block ledger
`results/accumulation-ledger.json` keeps both counts side by side.

### 18.5 The interpretation, declared in advance, in three branches

Today's ratio: four skills out of a hundred and five patterns. When the corpus
triples:

| Observation | Interpretation |
|---|---|
| The ratio **holds** | The skill count grows linearly with the corpus. |
| The ratio **falls** | The filtering chain is the bottleneck; the chain is examined. |
| The ratio **rises** | The corpus has become more varied; that is a finding too. |

**If none of them fits**, the table was wrong: the result is reported without
interpretation and what the table missed is written down (`K-104`).

### 18.6 How the run is arranged

**The model's name is not written a second time.** The prefix names its own
conditions section and the model is resolved from there (`K-138`).

**Resumption.** Completed episodes are skipped, so if a session is cut the run
carries on from where it stopped.

**What is written at a block boundary.** Every block appends a row to the ledger:
which block, how many episodes so far, how many distinct tasks have passed, the
library id and its skill count, the index id and its card count, and how many new
skills that block added. The stopping decision is made by reading that ledger,
not from memory.

## 19. The experiment: prefix and boundary

This section declares the boundary that separates the experiment's runs from the
rest of the record. The experiment's conditions, task order and slices come in
separate subsections.

### 19.1 The prefix

Every run of the experiment carries the prefix `dny`: the first segment of its
run id is `dny`. No other run in the record carries it. The value lives in one
place in the code, `zihin.declared`, and a test pins it to this section.

### 19.2 Why a prefix and not a commit

The experiment will last several sessions and the code can change in that time:
a fix that touches a measurement-defining path stops a run, and the run resumes
at a later commit (the 25 September addendum to A.9). A boundary tied to a commit
would move at that moment. The prefix does not.

### 19.3 The boundary's two sides

**The touched-task rule does not count `dny`.** The rule said "every run before
the experiment" and knew no boundary; the experiment's first episode on an
evaluation task would have made the list refuse. From here on the rule is
"every run but `dny`" (the addendum to preregistration A.10, `K-178`).

**`dny` episodes are held to two conditions**, because nothing else sees them
once they are outside the list:

1. The task is in the evaluation sample: `test_normal` with the touched tasks
   removed. A `dny` episode from the train, dev or challenge split is refused.
2. The run is not a preflight. Every runner in this repository wrote its health
   check under its own prefix, with the suffix `-onkontrol`: the record holds thirteen
   such episodes under seven prefixes. Under `dny` the same name would be a health
   check inside the boundary, and it is refused.

### 19.4 Runs that are not the experiment: `dnyk`

Runs that belong to the experiment but measure nothing — a preflight, a health
check, a smoke run — take the prefix `dnyk`. The touched-task rule counts them
like any run: if one runs an evaluation task, the task leaves the sample and the
list says so. A dry run (`--dry-run`) writes no episode and needs no prefix.

### 19.5 The experiment's command cannot start on a dirty tree

The command of a run with the `dny` prefix cannot carry `--allow-dirty-tree`.
The dirty-tree gate is how a measurement-defining change stops the run (the
25 September addendum to A.9); this flag starts the run anyway and only writes
"dirty" into the manifest. `scripts/check_declared_conditions.py` therefore
refuses the command before it compares any value (`K-180`). The check matches
the way argparse matches: `--allow` also reaches the flag and is refused too.

### 19.6 Conditions (`dny`), in absolute values

Phase 1's conditions, before the first `dny` episode. The rows of §18.2 that apply to the
experiment, plus the experiment's own. The rows particular to the accumulation (block,
ceiling, first sweep, mining thresholds) are absent: the experiment mines nothing, it reads
the library §18.2 delivered. Every row's key is a single word, because the check does not
read a key with a space in it at all. For the experiment, a single row that is not read or
cannot be compared with its source fails the check (`K-187`).

| Field | Value | From |
|---|---|---|
| `model_tag` | `qwen2.5-coder:32b-instruct-q4_K_M` | the primary cell's model (the 25 September addendum to preregistration A.2) |
| `serving_mode` | `local` | Ollama |
| `max_output_tokens` | **4000** | `config/recording.yaml` |
| `no_progress_limit` | **40** | `config/recording.yaml`; the stopping rule |
| `shield_mode` | **`shadow`** | the runner's mount default |
| `temperature` | **0.2** | `config/models.yaml` |
| `base_seed` | **123** | `config/models.yaml` |
| `seed_count` | **3** | `config/models.yaml`; every task with three seeds |
| `num_ctx_requested` | **32768** | `config/models.yaml` |
| `kv_cache_type` | **`q8_0`** | `config/models.yaml` |
| `flash_attention` | **1** | `config/models.yaml` |
| `step_ceiling` | `min(max(2 × anchor, 20), 150)` | the band scan's formula; `scripts/run_experiment.py` carries the same three numbers |
| `min_expected_saving` | **1** | the same in all five condition configurations (`K-175`) |
| `library_id` | `v0-gap2-sup3-0c3f4ac` | the library §18.2 delivered; the analysis sets were derived with it |
| `index_id` | `v0-sup1-0c3f4ac` | the index mined in the same block |
| `task_set` | **104** | the action stratum of the evaluation sample (`results/experiment-order.json`) |
| `covered_tasks` | **103** | the tasks the carded arm reaches with at least one card (`results/experiment-sets.json`) |
| `task_order_seed` | **123** | `base_seed`; each task's key is `sha256("123:" + task_id)` and the order is the keys ascending (`K-183`) |
| `task_order` | `dcbdbd43cdc495372cdd7a0149647888881110fd9d49ca4fda1010bcfdbd32b8` | the order's digest (`results/experiment-order.json`) |
| `conditions` | `baseline, skills_failures, irrelevant_retrieval` | phase 1; phase 2's two conditions (`skills`, `failures`) with the same runner, later |
| `runtime` | **A100** | the 32B's measured file is 19.851 GB; it does not fit a T4's 15360 MiB (§16.1) |
| `model_file_gb` | **19.851** | the measured file size of this tag in §16.1 |
| Command | `uv run python scripts/run_experiment.py dny --tasks 10` | the first slice; `--tasks` is the slice's size, not a condition: the user chooses it each session |

**The task with no card (K1).** On `8ce6779_3` the carded arm gets no card at all. Only
the baseline runs there, three episodes; none of the card-carrying conditions starts on
this task. The task is outside A.3's covered tasks, so it is in no confirmatory contrast.

**The two tasks whose volume does not match.** On `d194965_1` and `d194965_3` the
irrelevant arm runs with three skill cards instead of five. Its episodes carry
`volume_matched = 0` and every confirmatory analysis involving that arm leaves the two
tasks out (the Correction to preregistration A.4, `K-181`).

### 19.7 Analysis sets, from the runner's own slots

The numbers were not typed. The runner's slot function (`zihin.slots.compose`) was called
for every task and every card-carrying condition, and the sets followed by one rule
(`K-184`). A test reads this table against `results/experiment-sets.json`.

| Contrast | Compares | Tasks |
|---|---|---|
| `Y-1` | `skills_failures` – `baseline` | **103** |
| `Y-6.2` | `skills_failures` – `irrelevant_retrieval` | **101** |
| `Y-4` | `failures` – `baseline` | **101** |
| `Y-5` | `skills` – `baseline` | **103** |
| `Y-6.2`, second reading | `skills` – `irrelevant_retrieval` | **101** |

Phase 1 is **930** episodes: 3 conditions × 3 seeds on the 103 covered tasks, the baseline
× 3 on `8ce6779_3`.
