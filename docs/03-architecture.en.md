# Architecture

Turkish is the source: `03-architecture.tr.md`.

## Two trust zones

**The host is trusted and persistent.** The policy model, the record, the
retriever, the compiler and the shield run here.

**The sandbox is untrusted and is born again every episode.** A rootless
container, read-only root, policy at the network-namespace level (fixed app ports
on loopback only), limited in memory, processes, time and disk, pinned by an
image version digest.

The reason for the split is in the threat model: `04-threat-model.en.md`.

## Seven components

### Policy

Produces the next tool call. **The only replaceable slot in the architecture.**
The only thing that changes between conditions is the context entering it; the
component itself does not change.

### Retriever

Looks at the task and produces skill and failure cards. **It uses symbolic
matching, not semantic embedding.**

The reason embedding was rejected is part of the design: an embedding adds a new
rented component and a new confounder to run time. It would become impossible to
separate how much of the gain came from the mechanism and how much from the
embedding model. This is written as a limitation in `09-limitations.en.md`.

### Shield

A predicate that filters an action before it executes. **Open in all five
conditions.**

Calls with static arguments are checked before the skill starts, those with
dynamic arguments immediately before their own execution. Atomicity is a property
at the model-call level only, not at the level of the check.

### Sandbox

Executes the call in an isolated environment.

### Verifier

Reduces the result to passed or failed. **It comes from the benchmark and is not
written inside the project.** Had we written our own verifier, what we measured
would be our own definition.

### Record

Writes every observation and action in order. **Append-only, the single source of
truth.**

### Compiler

Produces the skill library and the failure index. **Offline and deterministic, it
uses no model.** Putting a model inside the compiler means giving away part of
the gain we are measuring to that model.

## The record/projection split

The skill library and the failure index are **derived projections**. They can be
deleted and recomputed from the record.

**The test for the split:** if I deleted this table, could I bring it back from
the record.

Raw parameters are therefore stored in full rather than as a digest. The
normalization rule will change, and the projection has to remain recomputable
from the record.

## Context management

The assembler is a **pure function** carrying five sections.

**The fixed block never drops:** the system instruction, the task text, the
credentials, the retrieved cards.

**The head and tail turns are preserved.** Only the middle turns are emptied and
replaced by a marker. Emptying is wholesale: room worth a quarter of the budget
is opened at once.

**Long tool outputs are truncated as they enter the context**, not at the moment
of overflow.

### The policy is deliberately stupid

No relevance score, no summary, no model.

The reason is measurement: a clever context policy becomes a mechanism in its own
right and takes part of the gain attributed to skills.

### Measured numbers

About 5958 input tokens per step (phase 2). That number **includes the
accumulated history**, so it is not the fixed block itself.

The fixed block was measured separately (`results/context-cost.json`, the
measurement was verified on the production path):

| | Tokens, median | Share of the 32K window |
|---|---|---|
| Fixed block, no cards | 3172–3185 | 9.7% |
| Card block, k=5+5 | 125–264 | 0.4–0.8% |
| The two together | 3296–3447 | 10.1–10.5% |

So the fixed block is **a tenth**, and with cards still a tenth. This sentence
used to say "a fifth, a quarter with cards" and had not been measured; the
correction is S-46 and the decision K-88.

**The binding limit is not this window.** The reference scaffold truncates the
context by characters, and 50000 characters is 12799 tokens on the measured
content, 39% of the window (S-47). So the effective context is not 32K but around
13K, and the window never fills.

**The assembler's budget is therefore written in characters** (K-90). That is the
binding unit; a budget written in tokens would believe it had 61% of the window
left. The ceiling's value lives in `config/recording.yaml` and is written into the
manifest, because changing it changes the effective context. Measured: 31 of the
105 recorded episodes went past the ceiling.

### A known collision

The reference scaffold has its own context-truncation logic and replaces old
observations with a placeholder. When our assembler comes into play, the two will
collide. It is not touched now; the risk is under `09-limitations.en.md` S-07 and
the decision is `08-decisions.tr.md` K-26.
