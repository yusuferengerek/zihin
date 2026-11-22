# The alternatives ledger — the ways out of the power problem

This ledger **does not close**. It holds the ways out of the experiment being
underpowered, with each one's status and price. When the ways inside the frame
run out, this is where we come back to.

**Why a ledger.** When a way is tried or closed, the reasoning of that moment
ends up inside some other record, and answering "was there another option" later
meant reading three documents. There are four rows here and every row is tied to
its own artefact.

**The problem.** The pass-rate threshold derived from the preregistration is
0.75-0.85 (`K-146`); the rate measured on the primary stratum is 0.280. The gap
is `S-68`.

---

## (a) A model with a higher pass rate

**Status: closed by measurement.**

The place the threshold has to be cleared is the action stratum. The **highest
point** this project has measured is DeepSeek V4 Flash and it gives 15/25 =
**0.600** there; the second reference, gpt-4o, gives 10/25 = 0.400. The threshold
is 0.75. The measurements are in `results/stratum-rates.json`, the decision is
`K-147`.

**What is closed and what is not.** What closes is the claim that one of the
models we measured is enough. What does not close is the possibility in
principle: if a model clears 0.75 on the action stratum, this way opens. No such
model has been **measured**, and this row of the ledger changes with a run that
measures one.

**A qualification.** DeepSeek's 20/30 is the union of two runs and in those runs
thinking was on; the detail is in `S-34`.

---

## (b) Enlarging the sample

**Status: deferred, its price written down.**

Bringing the memorisation gate into range asks for **500 action tasks** (for an
expected effect of 20% and above; at 10% the whole pool is not enough). On top of
today's 105 that means 395 of `test_challenge`'s 408 action tasks. The compute
side is 7500 episodes, about **225 session-hours**. The measurement is
`results/sample-size.json`, the record is `K-149`.

**The cost is not only money.** The added tasks have a different anchor
distribution, so the larger sample would give not a more precise answer to the
same question but an answer **about a different task population**.

**It has a trigger.** If, when the experiment runs on the 105 tasks, `Y-1`'s
interval cannot exclude zero, this way is taken. The trigger was declared before
the run.

**Addendum — 25 September 2026: the price is a range.** The 500 above is the
median of seven replicates. Per replicate (`K-168`): for an expected effect of 20%
and above, **400–557** action tasks, the top of the range being the whole pool; at
30% the pool is not enough in two of the seven replicates, at 50% in one; at 10%
in none. The compute side is 6000–8355 episodes, about **180–250 session-hours**.
The stratum is now 104 tasks; the trigger is the same and applies to the 104.

---

## (c) Narrowing the confirmatory distinctions

**Status: chosen and declared, before the run.**

`Y-2` and the first branch of `Y-6` left the confirmatory set; both continue to
be reported directionally. The confirmatory distinctions that remain are `Y-1`,
the second branch of `Y-6`, and `Y-4`/`Y-5`. The declaration is under
`experiments/preregistration.md` A.7, the decision is `K-148`.

**Its cost.** Two questions go unanswered in this run. How much of the gain
memorisation explains, and whether the volume effect separates from zero, stay
**directional**.

---

## (d) Ways outside the frame

**Status: outside the frame. A last resort, and only with an explicit
declaration.**

The three above are **inside** the preregistration's frame: they keep the metric,
the estimand, the split definition and the confirmatory discipline. This row
holds the ways that would change the frame itself.

**This ledger nominates no particular (d) at present**, because none was
nominated. The slot is empty and its emptiness is written down; putting something
here is a separate decision.

**If it is entered, the condition is written in advance.** Every step outside the
frame will be declared with a dated addendum before it is taken, what changed
will be named, and no result after that step will be presented as a result of the
earlier frame.

---

## The qualification under every row

`S-66`: the noise coefficient the threshold and the number 500 rest on was
measured from two repeated cells. Both are **lower bounds**; if the real
variability is larger, (a) closes further, (b) gets more expensive, and (c)
becomes more necessary.
