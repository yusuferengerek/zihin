# SKILL_SPEC — the data structure of a skill

Turkish is the source: `SKILL_SPEC.tr.md`.

`docs/06-skill-language.en.md` describes **how a skill is mined**. This document
defines **what mining produces**: the record the compiler writes, the retriever
reads, the executor runs and the demotion rule counts.

They are two documents because different things change. The mining parameters are
calibrated after setup (K-50); the fields here are the schema of the `skills` table
and, once written, need a migration to change.

**A design constraint that holds for every field.** The compiler is offline,
deterministic and uses no model (`03-architecture.en.md`). So no field here can be
written by hand, and none can come from a model. Every field has a mechanical
derivation, and the derivation comes from the episodes in the record.

**Correction, 18 October 2026: the table defines what was measured.** This document
was never frozen and describes the designed card. The authoritative description of
the skill record that was measured is the `skills` table (`src/zihin/schema.sql`): it
is part of the measurement-defining code and froze at `4a04e50` (K-202). Nine fields
of this document were designed and not implemented in that form:

- Six have no implementation: `precondition`, `invocations`, `blamed_failures`,
  `postcondition_misses`, `model_failures_gate_1`, `model_failures_gate_2`. Skills
  are delivered to the model as text cards and are not invoked, so precondition
  gates, postcondition misses, blame attribution and invocation counters have no
  implementation.
- Three stand in the table in another form, and the table's form holds: `signature`
  as `free_parameters`; `calls` as `body` and `body_length`; `effect_suffix` holds the
  suffix's calls rather than the indices of the writing calls.

The sentence "the decisions record has no decision" in the 13 October correction
below is closed by this (S-81).

---

## 1. Identity

| Field | Type | Derivation |
|---|---|---|
| `skill_id` | TEXT | A digest of the effect suffix. The same effect suffix is the same skill (`06-skill-language.en.md`) |
| `library_id` | TEXT | The identity of the library build that produced the skill; matches `library_id` in the manifest |
| `signature` | TEXT | The ordered list of free parameters; bound arguments and constants are not here |

That the identity comes from the effect suffix is a decision: sequences that produce
the same effect count as one skill even if the search prefix changes.

## 2. Body

| Field | Type | Derivation |
|---|---|---|
| `calls` | JSON | The ordered list of calls. Each call: `app`, `api`, `http_method`, argument template |
| `bound_arguments` | JSON | Call index → a structural path in the output of an earlier call |
| `constants` | JSON | The embedded values, and in how many distinct tasks each one was seen |

`constants` carries not only the value but its **evidence**. A wrongly frozen
constant breaks the skill silently, and without the count, why a constant was
taken as constant cannot be questioned afterwards.

### The effect suffix cannot be empty: the condition for entering the library

A skill is split into a search prefix and an effect suffix
(`06-skill-language.en.md`). **A skill that enters the library cannot have an empty
effect suffix.** Whether a call produces an effect is decided by the shield's write
set; the same artifact draws both the shield's boundary and the skill's boundary.

| Field | Type | Derivation |
|---|---|---|
| `effect_suffix` | JSON | The indices of the calls that write, according to the write set |
| `kind` | TEXT | `skill` (effect suffix non-empty) or `discovery_prefix` (empty) |

Patterns with an empty effect suffix **are mined but do not enter the library**. As
a separate class — the **discovery prefix** — they are reported separately and are
not given to the retriever.

**Correction, 13 October 2026: the table has no `kind` field.** K-75 writes that
patterns with an empty effect suffix never enter the library, and the `skills` table
follows it: it rejects an empty effect suffix with a `CHECK` constraint. Every record in
the library is a skill, so no field is needed to tell them apart. The ninth invariant
below is enforced by that constraint. For the other fields that differ from the table
the decisions record has no decision; they are recorded in S-81.

**Three reasons, and the third is the main one.**

**The merging rule loses its meaning.** The criterion for being the same skill is
the same effect suffix. Empty suffixes are equal to each other, so all read-only
patterns collapse into one skill. The rule stops being a tool for telling things
apart.

**The skill cannot verify itself.** The postcondition is the intersection of state
differences; a read-only sequence produces no state difference, so the postcondition
necessarily stays empty and the post-execution verification branch is dead in that
skill. A skill that cannot be verified gives the demotion rule no data either.

**The irrelevant-retrieval control cannot separate universal boilerplate.** The
control's logic is "give wrong content from another app, and the gain should
disappear". An app-independent piece of boilerplate has **no** irrelevant version:
`api_docs` discovery is the same in every task and valid in every task. The control
would credit that gain to content, and the attribution would be wrong. If it were
taken into the library, part of the measured gain would become impossible to
separate by any control — not a measurement flaw, but unmeasurability.

**The finding is not lost.** "The scaffold has a discovery prefix repeated in every
task" is reportable on its own and an interesting fact; its measured form is in
`experiments/preregistration.md`. If boilerplate caching is to be claimed as a gain,
it will be **separate and clearly labelled**, not inside the gain attributed to
skills.

**An empty effect suffix and an empty postcondition are not the same thing.** A
skill with a non-empty effect suffix can also produce an empty postcondition: if
its writes are only at field level, row counting does not see them (the known limit
below). That skill enters the library; only its verification branch does not work.
The criterion is the **effect suffix**, not the postcondition.

## 3. Support

| Field | Type | Derivation |
|---|---|---|
| `supporting_tasks` | JSON | The ids of the **distinct tasks** that support the skill |
| `supporting_episodes` | JSON | Episode ids; the set the postcondition is derived from |
| `support` | INTEGER | `len(supporting_tasks)`, not the episode count |

Support is counted over tasks, so that ten episodes of a single task do not put a
pattern into the library.

## 4. Precondition

| Field | Type | Derivation |
|---|---|---|
| `precondition` | JSON | The arguments of the sequence's first call that are not produced within the sequence |

The precondition is already used at the second gate of the attribution of blame
(`06-skill-language.en.md`): if the signature is right but the precondition does
not hold, the error is the model's, not the skill's.

## 5. Postcondition

**This field was undefined until now; it was the only field missing from the
specification.**

### Definition

> The postcondition is the **intersection of the state differences observed** in
> the episodes that support the skill: what changes in every supporting episode.

| Field | Type | Derivation |
|---|---|---|
| `postcondition` | JSON | The **shape** intersection of the state differences over `supporting_episodes`: `{"app.Model": "+" \| "-"}` |

Mechanical, cannot be written by hand, and it uses the existing instrumentation. The
state difference is already measured at every step and is stored in the
`steps.state_change` column (`src/zihin/state_probe.py`). Its form is
`{"app.Model": signed difference}`; an empty dict means "measured, no change", NULL
means "not measured", and the two are different.

### Why this definition

It does work in three places, and all three fill a gap that has no counterpart
today.

**Post-execution verification.** Even if no API returns an error, the skill has
failed if its postcondition does not hold. This is exactly the fault the fifth
category — *silent empty success* — catches (`07-failure-taxonomy.en.md`): the
agent fixes the error by neutralizing the operation, and from outside it looks
clean. Today that category raises no alarm anywhere before the verifier, and in the
measured episodes it was the dominant failure mode of the most capable model
(K-36). The postcondition makes it visible at skill level, without waiting for the
verifier.

**Relevance in retrieval.** A retriever that uses symbolic matching
(`03-architecture.en.md`) can count a skill whose postcondition matches the task's
goal as more relevant. This is a way to raise relevance without embedding-similarity
retrieval, that is, it does not bring back the rejected path.

**The demotion rule.** A skill whose postcondition often does not hold is demoted.
This criterion completes the third gate of the attribution of blame: the third gate
counts API errors, the postcondition counts failure without an error.

### Known limit: updates are not visible

State difference detection relies on **row counting**. Insertions and deletions are
visible, **updates are not**: a `PATCH` that does not change the row count is
invisible to the probe (`state_probe.py`, S-35).

So the postcondition will be incomplete in the same way. A skill that makes only
field-level changes will produce an empty postcondition, and its verification, its
relevance contribution and the demotion criterion will not work for that skill.

**This is the same blind spot that limits the write set.** The two mechanisms rely
on the same instrumentation and are blind in the same place. The second layer
planned for the empirical half of K-41 — AppWorld's own `model_hashes.json` output
at episode close — closes the blindness here too; both close with one solution.

### What the intersection is taken over: **shape**, not magnitude

The definition says "the intersection of state differences". A state difference has
the form `{model: signed difference}`, so the intersection can be taken in three
ways:

| Reading | Claim | Example |
|---|---|---|
| Strict | (model, exact difference) | `{"simple_note.Note": 1}` |
| Loose | model name only | `{"simple_note.Note"}` |
| **Shape** ✅ | (model, sign) | `{"simple_note.Note": "+"}` |

**The specification takes the shape reading, and its justification is not a
measurement but the design of the language itself.**

The strict reading contradicts the parametrization of the skill language. A free
parameter exists so that the skill can be applied to different inputs
(`06-skill-language.en.md`). In a skill that sends a message to N recipients, the
magnitude of the difference changes with N, so the strict reading holds in **no**
supporting episode of that skill and the intersection comes out empty. This is not a
question of measurement: if the free parameter changes by definition, the magnitude
tied to it changes by definition too.

The shape reading claims what can be claimed: **which models changed and in which
direction — insertion or deletion.** The magnitude, if the skill has a free
parameter, is a free variable; it cannot be written down as a fixed claim.

All three uses work at the level of shape. For verification it is enough that the
`Note` count increased — in a silent empty success it does not increase at all. For
relevance, which model changed in which direction is what tells skills apart. For
demotion, "should have increased and did not" is a countable fault.

### What the measurement will say: three interpretations, declared before the result is seen

Whether the magnitude is constant across the supporting episodes will be measured in
item 3. The three possible outcomes and what each one means are written down **now**,
so that there is no choosing afterwards.

1. **If the magnitude is constant across the supporting episodes of every mined
   skill** → the strict reading comes back. The shape reading would be an
   unnecessary weakening, and it means the stronger claim can be had at no cost.

2. **If it changes and the change follows a free parameter** → the shape reading is
   correct and **the cause is the parameter**. This is the expected outcome; the
   design argument above predicts exactly this.

3. **If it changes but follows no parameter** → the state difference
   instrumentation is noisy, and that is **a separate problem**. It has nothing to
   do with the postcondition's reading level; its solution is not here either, but
   in the probe itself.

If the third outcome happens, the whole postcondition mechanism is suspended: a
demotion rule that rests on a noisy measurement demotes good skills.

### Measured context

Over 3909 recorded steps:

| | |
|---|---|
| Steps showing a state change | **28** (0.7%) |
| Distinct models that changed | 18 |
| Models in which more than one magnitude was seen | **9** (half of the 18) |
| Apps the changes occurred in | venmo 17, todoist 12, splitwise 6, phone 4, spotify 4, gmail 3, file_system 1 |

Two caveats, both more important than the number itself. This number is **at step
level** and mixes different operations; the real question is constancy across the
supporting episodes of the same skill, and that can be asked only after skills have
been produced. And the 0.7% change rate comes from this corpus being predominantly
read-only — **the same cause** as the shield's zero blocking rate, the same property
of the corpus.

`supervisor` never appears in the state differences, so the difference between the
infrastructure lists in `state_probe` and `allowed_apps` does not contaminate the
postcondition.

## 6. Expected saving

| Field | Type | Derivation |
|---|---|---|
| `observed_steps` | INTEGER | The number of steps the body occupies across its occurrences, median |
| `expected_saving` | INTEGER | `(observed_steps − 1) × support` |
| `expected_saving_calls` | INTEGER | `(body_length − 1) × support`, for diagnosis |

**The unit is the model call, not the API call.** This project's primary metric is
the model call, one step is one model call, and a skill is invoked in a single
step. So the saving is the **observed step count** minus one, times support.

`06-skill-language.tr.md` wrote this as "length minus one", and that overcounts if
the agent already batches calls. Measured: the `spotify.auth/token` skill makes
three calls in two steps, so the call-based formula raises the saving from 7 to 14.
In three of the four skills the two numbers are the same; in one there is a twofold
difference.

The call-based number stands beside it as a diagnosis: the difference between the
two numbers is the very thing that shows the specification was counting the wrong
unit.

### The estimate is a lower bound, and reading it requires that

The observed step count comes from the boundary-control trajectories. **A weak local
model makes the same calls in more steps**, so the skill is worth more to it than
this column says.

The models the skills are expected to help are exactly those weak models. So every
number here is a **lower bound** for its target audience. The pilot report will read
it with this sentence.

### The threshold is not applied, it is stored

The number for the value threshold has not been chosen (K-50) and **will not be
chosen before the pilot**: the corpus is twenty tasks, the estimate is specific to
the corpus, and choosing a threshold would be fitting a small sample. The column is
stored, the threshold is applied at read time, and the sensitivity grid is in
`experiments/preregistration.md`. The retriever takes all four of the four skills,
and the sensitivity note stands beside it.

## 7. Track record

| Field | Type | Derivation |
|---|---|---|
| `invocations` | INTEGER | How many times it was invoked |
| `blamed_failures` | INTEGER | The failures that pass the **third** gate of the attribution of blame |
| `postcondition_misses` | INTEGER | The invocations in which the postcondition did not hold while there was no API error |
| `model_failures_gate_1` | INTEGER | The call never reached the skill |
| `model_failures_gate_2` | INTEGER | The signature is right, the precondition does not hold |

The counters of the first two gates are kept separately and do not feed the
demotion rule. Without the gates, model errors would be written against the skill
and good skills would drop out of the library.

`postcondition_misses` is the **second** number that enters the demotion rule.

---

## Invariants

What the compiler's output has to satisfy. The verification gate will be written in
item 3 and will test these.

1. `support == len(supporting_tasks)` and `supporting_tasks` has no duplicates.
2. `len(calls) >= 2` — the lower bound on length is two.
3. `signature` and `bound_arguments` are disjoint: a bound argument cannot be in the
   signature.
4. The task count of every value in `constants` cannot be less than the
   constant-declaration threshold.
5. `constants` cannot contain a value from the dynamic type blacklist.
6. `postcondition` comes out the same when recomputed over `supporting_episodes` —
   the condition for being a derived projection (`03-architecture.en.md`).
7. An empty `postcondition` is a valid value and different from NULL: the first
   means "the intersection is empty", the second "not computed".
8. `postcondition` values are only `"+"` and `"-"`; no number can be written. The
   shape reading is a decision, not a form the code happened to produce, and if the
   magnitude leaks in, the claim silently turns back into the strict reading.
9. In every record with `kind == "skill"`, `effect_suffix` is non-empty, and in
   every record with `kind == "discovery_prefix"` it is empty. A record with an empty
   effect suffix cannot reach the library or the retriever.

## What is not written yet

The numbers for the value threshold, the constant-declaration threshold and the gap
constraint are not here; the decision rules belong to the pre-registration, the
numbers to after setup (K-50).

The postcondition's reading level **has been decided** — shape — and its
justification comes from the design, not from measurement. What will be measured in
item 3 is not the decision itself but which of the three interpretations comes true;
all three were written down in advance above.
