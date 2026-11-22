# Experiment design

Turkish is the source: `05-experiment-design.tr.md`.

## Why honest measurement is hard

Most of this design exists to avoid four classes of mistake. They are checked
whenever a piece of work is done.

**Places where the design determines the result.** If the winner of a comparison
changes with which axis you hold fixed, that comparison measures nothing.

**Places where more than one variable changes at once.** If a package is tested
and attributed to a single mechanism, the result cannot be interpreted.

**Tautological metrics.** If the measured difference follows from the definition,
the result is true by itself and carries no information.

**New confounders produced by patches.** A fix can create a new confounder
somewhere else; patches made under pressure usually do. This fourth one was added
later.

## Conditions

**Addendum, 2026-08-28: one of the six conditions was not written.** After the
criterion ran, the `naive_compiler` condition was **not written** into the
experiment (K-145). The criterion had been declared before the run: on the same
corpus the naive miner reached all four of the compiler's four skills, missing 0
and finding 0 extra. The table below stands as the original declaration; the
number of conditions that will run is **five**.

Six conditions. Each isolates a single thing.

| Condition | Skill cards | Failure cards | What it isolates |
|---|---|---|---|
| Baseline | none | none | the reference point |
| Irrelevant retrieval | irrelevant | irrelevant | context volume |
| Skills only | real | irrelevant | skill content |
| Failures only | irrelevant | real | failure content |
| Both | real | real | the effect of the two together |
| Naive compiler | naive mining | irrelevant | mining quality |

The cards in the **irrelevant retrieval** condition are irrelevant cards taken
from other apps, in the real card format and length. It measures whether the gain
comes from context volume.

The **naive compiler** condition uses the same atomicity, the same card format,
the same retriever and the same token budget. The only difference is mining
quality. The naive side is fixed-length n-grams; no closed patterns, no gap
constraint, and the argument rule is "everything that varies is a free
parameter". It pairs with the skills-only condition. The question it answers: is
our compiler better than a naive one.

### Two critical contrasts

If they break, the whole analysis plan collapses.

1. The difference between **baseline and irrelevant retrieval** is pure context
   volume.
2. The difference between **skills only and irrelevant retrieval** is pure
   content.

### Card count and padding

The card count is determined **per task**, not per condition.

For each task, retrieval is run first; the number of suitable cards found
determines that task's padding allowance; the five card-carrying conditions all
receive the same number of cards. The baseline receives zero cards.

The mechanism conditions get padding too. Without it, the context of a condition
receiving few cards would be shorter and what was measured would be context
length rather than the mechanism.

## The model axis and the controls

### Requirements on the main axis

All four must hold together:

1. **A single family.** As the size changes, the training pipeline, the
   vocabulary and the instruction format have to stay fixed. If families mix, two
   variables change at once on the axis and the direction of the curve can be
   attributed to nothing.
2. **At least three dense sizes**, all fitting into 8 GB with Q4_K_M, a 32K
   context and q8_0 KV.
3. **No reasoning mode, or one that can be turned off completely.**
4. **Available on Ollama and instruction-tuned.**

**Measured reference:** `qwen2.5-coder:7b` Q4_K_M is 5.16 GiB on the card; 32K
q8_0 KV for one slot is about 0.9 GiB; with 7B loaded, the real free VRAM is 1.74
GiB. The ceiling on weights is roughly 5–6 GiB.

### Two controls, not part of the axis

**Family control.** A family different from the main axis, in the band of the
main axis's largest point, **a single point**. Its question: is this effect
specific to this family. It cannot be taken into the main axis; taken in, its
role disappears. It has to pass the precondition as well.

**Boundary control.** DeepSeek V4 Flash 0731, over the API, thinking off. Its
question: is the gain patching the small model's deficiency.

Both are reported separately.

### Eliminated

| Model | Reason |
|---|---|
| Qwen2.5-Coder 14B and above | does not fit into 8 GB |
| Kimi K3 | reasoning cannot be turned off |
| GLM-5.2 | only in High and Max modes |

The last two were boundary-control candidates, not main-axis candidates.

### Constants

Quantization Q4_K_M throughout, KV cache q8_0, context 32K, temperature fixed and
greater than zero, seed per episode.

**Temperature zero was rejected.** At zero the seed becomes meaningless and the
spread across seeds dies, whereas the whole statistical plan rests on that
spread. Also, at zero the agent repeats a failing call forever.

**The seed derives only from the task id and the seed index.** The model and the
condition do not enter. If they did, the paired design would break: the same task
and the same seed index have to give the same seed in every model and every
condition.

**The model load regime is cold**, with an unload before every episode. A warmed
regime is not a single state; the cold regime is uniform in a measured way. Its
cost is about six percent of the total run.

## Metrics

### Primary

**Model calls per task.**

**The answer to the tautology objection.** In this environment the agent writes
stateful Python and the baseline can also call several APIs in one turn. A skill
does not grant the possibility of packaging; it hands over a verified package in
advance. The gain comes from the turns the agent spends discovering which calls
come in which order.

**The raw API call count is not primary**, because counting a skill invocation as
a single step makes the result tautological.

### Mandatory diagnostic metric

**Model calls divided by successful API calls.**

Its interpretation is written in the pre-registration: if the ratio does not
move, the gain comes from packaging; if it moves, it also comes from waste going
down.

### Secondary

Success rate, input tokens, output tokens, shield violation count, DSL coverage
rate, coverage rate, interruption rate, overflow rate, partial-execution rate,
invalid skill invocation, invocation in the wrong context, invocation completion,
missed use, category 4 rate.

**The rule "the two metrics have to move together" was dropped**, because it
interacts with task length: in long episodes the two fall together, while in
short episodes the card cost dominates and tokens rise. Both are reported
unconditionally and broken down by task length.

### The graded score as a diagnostic metric

The passed fraction of the tests labelled `no_op_fail`. **A diagnostic metric,
not a secondary outcome.** It does not enter the primary metric or the
falsification gates.

It was born after the data was seen, and that is written down plainly: during
setup, with binary success zero everywhere, it was derived as the only quantity
with discriminating power. If it is to be used in a scan, its definition is
written before the scan and pre-declared for that use.

## Analysis plan

The comparison is **paired per task**.

### Estimand

Over all covered tasks. Unsolved episodes enter as **censored observations** at
the step ceiling, regardless of how many steps they actually took.

The sensitivity analysis is repeated at **1.5× and 2×** the ceiling.

The "solved by both conditions" analysis is secondary and is named **conditional
efficiency**.

### Estimation

The primary estimate is the **mean restricted to the ceiling**, with a confidence
interval by **bootstrap** over the task set. **Wilcoxon** is a robustness check
on the uncensored subset.

### Two quantities are not conflated

**The ceiling-hit rate** is a measurement artefact. It has to stay under ten
percent, and the ceiling multiplier is chosen accordingly.

**The censoring rate** rests on the verifier's verdict and is a result. The ten
percent rule is not applied to it; applied, it would impose a ninety percent
success requirement on the baseline.

Censoring is counted by the verifier's verdict, not by the termination reason.
Every episode the verifier did not pass is censored: whether it hit the ceiling,
closed under the stopping rule, or the agent declared completion. The termination
reason is a separate diagnostic field.

### Mechanism effect

Computed with a subtractive control: from the mechanism condition's gain over the
baseline, the irrelevant-retrieval condition's gain over the baseline is
subtracted, paired per task.

The volume effect and the content effect are assumed to be **additive**, and that
assumption is tested during setup.

### The primary comparison is a single cell

Mechanisms on against the baseline, on the model-call metric, at the largest
local point of the main axis, on the unseen subset, two-sided.

**Everything else is exploratory:** the other models, the other split, the other
condition pairs, the two control points, all the secondary metrics.

**Addendum, 25 September 2026.** The phrase "the largest local point of the main
axis" was updated by the 25 September 2026 addendum to preregistration A.2: the
primary cell's model is `qwen2.5-coder:32b-instruct-q4_K_M`, and the "local"
condition is no longer met. The choice is exploratory; the verdict of `Y-1` is
confirmatory (`K-169`).

### The memorization gate

The in-distribution test set is split in two: tasks whose action sequence was
seen during accumulation and tasks that were not. The splitting criterion is an
**exact match on the normalized action sequence** in the accumulation record.

The gate: the ratio of the gain on unseen tasks to the gain on seen tasks, with a
**threshold of one half**.

### The difficulty split

A separate measurement: transfer across apps. A result close to zero is written
in advance for skills; for the failure index it may come out different from zero,
because failure patterns can be abstract.

### Use of the splits

Accumulation is from train, dev and unused normal-test tasks. Evaluation is from
normal test, with the sample limited to the apps represented in accumulation.

**The difficulty split stays whole and untouched**, and accumulation is not done
from it. It is the only genuinely unseen app data we have.

**Tasks touched during setup are removed from the evaluation sample**; they may
stay in the accumulation pool. The touched task ids are listed and written into
the pre-registration.

### Normalization is secondary

An irreducible floor per task is subtracted from the measured step count, the
remainder is waste, and the waste of the two conditions is compared. The floor
comes from the `metadata.num_api_calls` field.

The primary metric stays the **raw paired difference**, because normalization is
a modelling decision and open to objection.

## Gates

### The precondition gate

If the baseline condition cannot reach the declared minimum success rate on the
held-out set, **the experiment has failed to test the hypothesis and the
mechanism results are not reported.**

The gate is measured under a non-binding budget; in the gate run the codeless
step rate is reported.

**This gate fired once: 11 August 2026.** Qwen2.5-Coder 1.5B, 3B and 7B solved no
task in AppWorld's thirty-task stratified sample. Three stratifications were
tried and none opened a measurable band: reference length, the subset the strong
model solved, and the app set.

On 12 August 2026 the boundary control showed that the zeros came from the model
and not from the apparatus: on the same thirty tasks DeepSeek V4 Flash 0731
scored 20/30 on our pipeline, and the published gpt-4o run 15/30.

The consequence of the firing: the model family is being reselected.

### Falsification gates

1. If the mechanisms do not lower the model-call count on held-out tasks, **the
   hypothesis is unsupported.**
2. If the gain on unseen tasks falls below half the gain on seen tasks,
   **memorization is confirmed.**
3. If the coverage rate is under twenty-five percent, this is not "we could not
   test it" but **the finding that the symbolic retriever cannot find relevant
   experience in this environment.**

### The abandonment criterion, per mechanism

If coverage is sufficient and the index is at its declared minimum size and the
failures-only condition shows no effect, **the failure index is abandoned as a
mechanism, not retuned.** The same holds for the skill compiler.

### The tuning budget

How many parameter revisions are allowed after the setup data has been seen is
written in advance. **Once the budget is exhausted, a negative result is a
conclusion about the design rather than about the parameters.**

The number and the list of revisions consumed to date are in the pre-registration
(`experiments/preregistration.md`).

### The scale axis interpretation table

The interpretation for four possible shapes goes into the pre-registration: flat,
falling, rising, inverted U. **Interpretation after the fact is forbidden.**

Every pre-declared interpretation table also carries a fourth branch: if the
observed pattern fits none of the rows, the table was wrong, the result is
reported without interpretation, and what the table missed is written down
(K-104).
