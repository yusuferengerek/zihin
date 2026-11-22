# Failure taxonomy

Turkish is the source: `07-failure-taxonomy.tr.md`.

The failure index is the record carrying which action failed in which context.
There are three observed levels and one separate axis.

## Action level

Shield block, authorization denied, object not found, invalid parameter,
unsuitable state, no such signature or API, exception, timeout, resource limit,
no error.

**The priority order is fixed:** shield first, then run-time exception, then API
error code. Without a fixed order the same event could be counted under two
different labels.

## Step level

Five categories:

1. **No code produced.**
2. **Could not be parsed.**
3. **Context overflowed.**
4. **Code produced but the execution errored without producing any action.**
   Short name: *category 4*.
5. **The agent fixed the error by neutralizing the operation and it looks clean
   from outside.** Short name: *silent empty success*.

The fifth category raises no alarm anywhere before the verifier; in the measured
episodes it was the dominant failure mode of the most capable model. Its
rationale and measurement are in `08-decisions.tr.md` K-36.

## Episode level

Solved, verifier did not pass it, unexpected side effect, budget exhausted, cut.

## Repetition: a separate axis

**Repetition is an axis independent of the outcome and progress labels.**

It was measured and came out central: one episode made 736 successful calls over
150 steps and never changed the database; another repeated the same wrong login
88 times. In the first the calls succeed, in the second they fail; the only thing
in common is repetition.

### The measured quantity: growth of the endpoint set

Repetition is measured over the **API endpoint set**. The endpoint abstracts the
parameter away: `spotify.library/playlists` is a single endpoint independent of
the page number.

The abstraction is essential. A loop returning with different identifiers
produces a new normalized action at every step; a criterion looking at the action
set could never catch such a loop. The endpoint set, on the other hand, saturates
and stays there.

**The step label.** A step is *stalled* if it did not change verifiable state and
did not reach an endpoint not touched before. The number of consecutive stalled
steps is the episode's position on the repetition axis.

**The measured basis.** 62 recorded episodes:

| Episode | Steps | Endpoints | Longest stall |
|---|---|---|---|
| `09b0ee6_2` | 150 | 3 | 146 |
| `c77c005_3` | 92 | 4 | 87 |
| `59fae45_2` | 11 | 65 | 3 |
| `1150ed6_1` | 8 | 7 | 1 |

In the two pathological episodes the endpoint set saturates at the fourth and
fifth step. In the episodes that really explore, the stall does not exceed 6
steps; the shortest of the pathological ones is 13. There is no episode between
eight and twelve.

The stopping rule rests on this axis (`05-experiment-design.en.md`).

## Derived labels

**Used, requiring no reference:** repeated action, interval without progress.

**Not used, requiring a reference:** unnecessary call, dead end.

The reason: the second kind can only be labelled by knowing the correct
solution, and **the mechanism must not learn from a ground truth.** If it did,
what we measured would be the contribution of the reference solution rather than
of the mechanism.

## A context condition is mandatory

**Every record in the failure index has to carry a context condition.**

An unconditional prohibition record makes the agent worse: a card that says "do
not make this call" without saying when not to make it also blocks the call in
the situations where it is needed.

### The condition language is closed and countable

It can say three things:

- whether the object exists,
- the value of specific fields of the object,
- whether a specific call has already been made earlier in the sequence.

The language has to be closed, because an open condition language puts a second
programming language inside the index and the expressive power of that language
becomes an unmeasured mechanism.

### Reduction is contrastive

Episodes in which the same call sequence passed and failed are compared and the
separating predicate is sought.

**Patterns with no contrastive counterpart are not deleted.** They enter the
index marked "no known success" and are counted separately in retrieval. Deleted,
the errors seen only once but real would be lost.

## Shield violations do not enter directly

To enter the index, the same pattern has to have ended in failure **in a
situation the shield did not block** as well.

The shield signal produces no record on its own; it only strengthens one. If it
did produce one, the index would learn the shield's own predicate and the
mechanism would become a copy of the shield.

## Rejected: teaching by punishment

The rationale is in `04-threat-model.en.md`: a system able to detect can block,
and if punishment mixes into the reward signal the agent learns to avoid
detection.

## What is not written yet

The declared minimum size of the index — the number the abandonment criterion
rests on (`05-experiment-design.en.md`) — is not here. It is a value the setup
phase will fill in.
