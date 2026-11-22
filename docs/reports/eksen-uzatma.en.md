# The axis extension report — from "the experiment cannot be run" to "it runs at 32B"

**It answers one question:** the experiment had stopped when the declared scale
axis gave zero; which measurements were made, in which order, that ended with the
axis extended to 32B.

This is not a results report. It does not say whether the mechanisms work; it
describes the path to the experiment **becoming runnable**.

---

## 1. The precondition gate: declared, then fired

The gate was declared before the design (K-58): the mechanisms' effect can be
measured only if there is a **band** to measure. The band is the range where the
agent solves some tasks and fails others. If everything is zero, a mechanism
turns zero into zero and the measurement says nothing about the mechanism.

**The gate fired.** On the declared axis — `qwen2.5-coder` 1.5B / 3B / 7B,
local, `q4_K_M` — binary success over thirty tasks was zero.

---

## 2. Zero on the declared axis: three runs, and the three are not equal

| Run | Model | Episodes | Passed | Ceiling hits |
|---|---|---|---|---|
| `bant2` | 7B | 30 | 0 | **not in the record** |
| `bant3` | 7B | 30 | 0 | **0.0%** |
| `bant3-kapali` | 7B | 26 | 0 | **96.2%** |

In the third the **stopping rule was entirely off**: the zero is not the rule
cutting episodes short.

**That the three do not carry equal weight was measured afterwards (S-63).**
K-60 requires that, before a zero is interpreted, the ceiling is shown not to
bind, and the threshold is 10%. The three had never been measured against it.
Measured: `bant3` is clean, `bant3-kapali` is a **lower bound** (with the rule
off, the ceiling is the only thing that can end an episode), and `bant2` is
**undetermined** — its termination reason was never written.

The finding stands, because a ceiling can **hide** a pass but cannot manufacture
one. What changes is its strength: not three clean measurements, but one clean
measurement, one lower bound and one undetermined.

---

## 3. What was eliminated — each with its own measurement

The cause of the zero was looked for. In order:

### 3.1 Stratification opened no band

**Three separate ways** of splitting the tasks into difficulty bands were tried.
None produced a range above zero.

### 3.2 The graded score could not be used

With binary success at zero, partial credit might have opened a band. In `bant3`
the graded score is **5/152**, and it is concentrated in **two tasks**
(`1150ed6_1` 4, `59fae45_2` 1). Twenty-eight tasks are at flat zero. No
comparison between conditions can be built on that distribution.

### 3.3 The line was eliminated — the tasks are solvable

On the same thirty tasks:

| Model | Passed |
|---|---|
| `deepseek-v4-flash` (hosted) | **20/30** |
| `gpt-4o-2024-05-13` | **15/30** |
| `qwen2.5-coder:7b` | 0/30 |

**This is the sentence that goes into the record, and it carries both
qualifications:**

> **Twenty** of the thirty tasks are solvable on this line; **thirteen** with the
> stopping rule on, and **seven** when the tasks the rule had cut short were
> re-run with it off. And in those runs **thinking was on**, which was not the
> declared condition (S-34).

The measurement: `sinir3` ran the thirty tasks with the rule on, 13 passed and 16
were cut short by `no_progress`. `sinir3-kapali` re-ran **those same sixteen**
with the rule off, and 7 more passed. The two sets of passes do not intersect,
and their union is twenty.

The shortened form falls short in a defence: "20/30" is not the result of one run
under one condition.

And on the fifteen-task subset gpt-4o solved, 7B was re-run: **0/15**, meaningful
tests 5/67.

So the tasks are solvable and the harness works; what cannot solve them is **the
model at this scale**. That eliminates the readings "the tasks are impossible"
and "the line is broken".

### 3.4 The scaffold-adaptation gate closed

The reason to adapt the scaffold would have been failures concentrating in
**category 4** (format and tool errors). Measured: category 4 is not dominant.
The reason fell away and the gate closed — the scaffold stays as the reference
(K-19).

### 3.5 Teaching the token opened no band

The skill library and the failure index converged, from independent corpora, on
the same bottleneck: the authentication token. In the three-arm run (baseline /
cards / irrelevant cards, five tasks, three repeats) the **entry effect** —
`POST <app>.auth/token` returning 2xx — was reached in **between three and seven**
of fifteen cells.

**Completion: 0/45.** Getting the token solved not a single task. The bottleneck
is not the token; the token is the door to the bottleneck behind it (S-57).

### 3.6 The output budget went from 400 to 4000, and the zero did not move

That 400 was not a chosen budget was measured: `bant3` took that value while the
configuration had **no such key at all**. An accident, not a design. Every point
of the axis has to sit at one budget, or the axis is two measurements rather than
an axis.

The local axis was re-run at 4000:

| Model | Passed | Graded | Ceiling hits | `agent_finished` |
|---|---|---|---|---|
| 1.5B | **0/30** | 0/152 | 33.3% | 0 |
| 3B | **0/30** | 2/152 | 33.3% | 1 |
| 7B | **0/30** | 7/152 | 30.0% | 4 |

The budget was binding — `agent_finished` rose 0 → 1 → 4 and the graded score
0 → 2 → 7 — but it was **not what opened the band**.

---

## 4. The rule that allowed the extension was written before the pilot

The axis was not extended after the zeros were seen; the rule was declared
**first**.

**S-14**, before the pilot: if the axis's smallest point sticks to a floor
effect, the axis moves up. The same record also wrote down what the obstacle was:

> "There is no upward compensation because 14B does not fit in 8 GB."

So the obstacle was **the hardware, not the design**, and the rule already said
what to do if it lifted. The band scan then measured that **all three points**
were on the floor; the rule was written for the smallest point, and what happened
was wider.

One lock only: *"the model runs on local hardware"*. The family lock was not
opened — all five points are `qwen2.5-coder`, all five `q4_K_M`, and that is now
pinned by a test.

**Correction — 25 September 2026: this section's title and first sentence were
wrong.** No rule permitting the extension had been written before the pilot. The
rule `S-14` wrote before the pilot was to narrow the axis **downwards** — "the axis
comes down to 3B and 7B" — and it wrote the upward way as explicitly closed, for
reasons of hardware. Colab removed that obstacle; the extension is a later
decision taken with the user's explicit approval (the 25 September addenda to
`K-133`). The sentence "the axis was not extended after the zeros were seen" does
not hold either: the extension was made **after** the zeros were seen, and that is
exactly why the addenda to preregistration A.11 label the points exploratory. The
text stays as it was.

---

## 5. The two extension runs

### 5.1 14B — Colab L4

The conditions were declared in section 15.2, but the run **did not use them**:
instead of the declared 400/15/off it ran at 4000/40/shadow, because the place of
declaration and the place of reading were different (S-58's third instance). The
result is **3/30**, ceiling hits **20%**.

### 5.2 32B — Colab A100

The conditions are in section 16.2, before the run, in absolute values. This time
a check (`check_declared_conditions.py`) resolved ten fields out of ten before the
run and all ten agreed. The record was verified independently afterwards:
`code_commit`, `boot_id`, `wall_clock_utc` and eight condition fields.

The result is **11/30**, ceiling hits **6.7%**, `no_progress` **0**. The
configuration verdict is **COMPARABLE**: 49/49 layers on the GPU, flash attention
effective, KV `q8_0`.

---

## 6. The axis — lower bound and measurement kept apart

| Point | Result | Ceiling hits | Label |
|---|---|---|---|
| 1.5B | 0/30 | 33.3% | **LOWER BOUND** |
| 3B | 0/30 | 33.3% | **LOWER BOUND** |
| 7B | 0/30 | 30.0% | **LOWER BOUND** |
| 14B | 3/30 | 20.0% | **LOWER BOUND** |
| 32B | **11/30** | **6.7%** | **MEASUREMENT** |

K-60's threshold is 10%. Four exceed it, one does not. **These five numbers do
not carry equal weight**, and drawn side by side on one chart they would look as
if they did.

A lower bound means the true value is **greater than or equal to** the number.
That four points are zero or low does not show there is no band there; it shows
the ceiling was binding.

---

## 7. The task-type split — more important than the headline

The thirty tasks were split into two types from the evaluation files
**themselves**:

- **Answer type (5 tasks):** the evaluation checks only the answer and "change
  nothing". The single meaningful test is a string equality.
- **Answer+world type (25 tasks):** the evaluation also looks for a change in the
  world.

| Model | Answer (5) | Answer+world (25) |
|---|---|---|
| 14B | 2/5 | **1/25** |
| 32B | 4/5 | **7/25** |

**Why this matters more than the headline.** The skill library teaches **API call
sequences**; the failure index teaches which call fails under which condition.
Both can only help on tasks that change the world. A gain on an answer-type task
does not test the mechanisms.

So the real question is not "did 32B give 11/30" but **"is there a band on the
answer+world type"**. At 32B there is 7/25; at 14B there was 1/25.

**The band label is separately misleading (S-62).** The anchor measures the
reference solution's path, not what the task requires: `09b0ee6_1` carries an
anchor of 102, appears in the `90+` band, and was passed in six steps — because
its only meaningful test is a string equality.

---

## 8. What this report does not establish

**Whether the mechanisms reduce the model-call count is unknown.** This report
only describes where a measurable band begins. The primary question has not been
measured.

**Four of the local zeros are ceiling-limited.** The numbers for 1.5B, 3B, 7B and
14B are lower bounds. The sentence "success rises with size" cannot be built on
this table.

**The extension runs are exploratory.** The axis points — 14B and 32B — were
chosen **after the zeros were seen**. A data-driven extension of an axis cannot
be confirmatory, however well it comes out. Two dated addenda were made to
pre-registration A.11 and the original declaration was not changed.

**14B's conditions were corrected after the run.** 14B did not run with the
values section 15.2 declares. That they coincide with 32B's conditions is the
outcome of an accident; the agreement makes the comparison possible but it is
**not a design declared in advance**.

**The axis's points were measured on three different cards (S-61).** RTX 4070
(Ada), L4 (Ada), A100 (**Ampere**). The configuration verdict compares three
things; every difference between the cards that is not measured stays open.

**Five points do not determine the shape of a curve.** The four-shape table in
the pre-registration is there for interpretation discipline, not for a
statistical claim.
