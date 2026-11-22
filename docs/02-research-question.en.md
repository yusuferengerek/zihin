# Research question

Turkish is the source: `02-research-question.tr.md`.

There are two questions. The second depends on the first and is weaker.

## First question — confirmatory

**Do compiled skills and an explicit failure index lower the number of model
calls needed to solve held-out tasks?**

This question is tested **confirmatorily in a single cell**. The cell is defined
as: the mechanisms-on condition against the baseline condition, on the model-call
metric, at the largest local point of the main axis, on the unseen subset,
two-sided.

The largest point is chosen because it is the hardest case for the hypothesis:
as the model grows, the contribution of accumulated experience is expected to
shrink.

**Addendum, 25 September 2026.** The phrase "the largest local point of the main
axis" was updated by the 25 September 2026 addendum to preregistration A.2: the
primary cell's model is `qwen2.5-coder:32b-instruct-q4_K_M`, and the "local"
condition is no longer met. The choice is exploratory; the verdict of `Y-1` is
confirmatory (`K-169`).

## Second question — exploratory

**Within the model sizes examined, does this effect systematically disappear?**

Exploratory, because the scale axis consists of three points and three points are
not enough to determine the shape of a curve confirmatorily. The table for
interpreting the axis goes into the pre-registration: what will be said for flat,
falling, rising and inverted-U is written before the measurement.

**Addendum, 2026-08-20.** A fourth point entered the axis (14B, K-133). The
sentence's number changed, its reason did not: four points are no more enough to
determine the shape of a curve confirmatorily, and the fourth is exploratory on
its own account because it was chosen after the zeros were seen. The original
declaration and the dated addendum are in pre-registration A.11.

The second question depends on the first. For the first question at least two
points of the scale axis have to pass the precondition gate; if only one passes,
the second question becomes unmeasurable.

## What we are not asking

We are not asking whether the success rate rises. The primary metric is not
success but the length of the path to the solution. The success rate is reported
as a secondary metric.

We are not asking whether the mechanisms make the model more "intelligent". The
model is fixed; what changes is the information entering the context.

## Falsification

Which observation brings down which claim is in `11-falsification.tr.md`, written
before the measurement. The three gates are defined in
`05-experiment-design.en.md` under "Gates".
