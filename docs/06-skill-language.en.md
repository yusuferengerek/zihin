# Skill language

Turkish is the source: `06-skill-language.tr.md`.

A skill is a verified call sequence mined from past episodes. The compiler
produces it; the compiler is offline, deterministic and uses no model
(`03-architecture.en.md`).

## Mining

Sequential pattern mining, **closed patterns**, **gap constraint**.

Support counts **distinct tasks**, not distinct episodes. Ten episodes of the
same task count as one task; otherwise the repeats of a single task could push a
pattern into the library.

The lower bound on length is **two**. The real filter is a **value threshold**.

Value is in units of **model calls**: `(observed step count − 1) × task support ×
success rate`. This used to read "length minus one" and counted the wrong unit;
one step is one model call and the agent can make several API calls in one step,
so call length overstates the saving. It was measured, and one of the four skills
came out a factor of two apart (K-82).

The success rate is one by construction in v0: skills are mined only from passing
episodes. The factor will mean something once a record of invocations has
accumulated.

**Skills are mined only from successful episodes.**

## Arguments

There are three classes.

**Bound argument.** Its value appears in the output of an earlier call within the
sequence. Detected by structural path matching. It stays in the body.

**Free parameter.** It varies and is never produced within the sequence. It goes
into the signature.

**Constant.** The same in every instance and not produced within the sequence. It
is embedded.

### The order is critical

**Boundness first, variability second.**

Done the other way round, bound arguments are mistaken for parameters and the
skill becomes worthless, because the caller would already have to know half the
job.

### The threshold for declaring a constant

To declare a constant, the same value has to be seen in a given number of
distinct tasks.

The rationale is **cost asymmetry**: a wrongly frozen constant breaks the skill
silently, whereas an unnecessary free parameter only makes the call longer.

There is a **dynamic type blacklist**: timestamps, identifier patterns and values
labelled secret cannot be declared constant.

## Merging

A skill is split into a **search prefix** and an **effect suffix**. If the effect
suffix is the same, it is the same skill.

Sequences whose effect part differs but which arrive at the same goal stay
separate in v1.

### Two rejected paths

**Clustering by embedding similarity.** The same rationale as the rejection in
the retriever: it adds a new confounder to run time.

**Asking a model "are these the same job".** That puts a model inside the
compiler and breaks the compiler's requirement to be deterministic.

## Execution

A skill is invoked **atomically**. If it breaks partway there is **no rollback**;
it stops at the first error.

A broken skill returns a **structured result**: which calls ran, their outputs,
where it stopped, what the error was, and the observation at the moment it
stopped.

The reason is fairness of measurement: this equalizes the information in the
agent's hands with the baseline condition. If a broken skill left the agent
blinder than the baseline, the measured difference would be the result of
information loss rather than of the mechanism.

Atomicity is a property at the model-call level only; the shield's check operates
separately for every call inside a skill (`04-threat-model.en.md`).

## Attribution of blame

Three gates, in order.

1. **If the call never reached the skill**, it is the model's error. It is not
   written into the skill's statistics.
2. **If the signature is right but the precondition does not hold**, it is the
   model's error. In a separate counter.
3. **If the signature is right, the precondition held, and the API inside
   returned an error**, it is the skill's error.

**Only the third number feeds the demotion rule.** Without the first two gates,
model errors would be written against the skill and good skills would drop out of
the library.

## What is not written yet

The number for the value threshold, the number for the constant-declaration
threshold and the size of the gap constraint are not here. All three are values
the setup phase fills in; the decision rules belong to the pre-registration, the
numbers to after setup (`08-decisions.tr.md` K-50).
