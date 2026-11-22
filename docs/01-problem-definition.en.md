# Problem definition

Turkish is the source: `01-problem-definition.tr.md`.

## What is observed

Language-model agents solve every task from scratch. A problem they solved a week
ago they rediscover today, and the mistake they made last time they make again.

The cost of this is directly measurable. Every step is a model call, and every
call is time and money. The system does not get faster as it runs: the hundredth
task is as expensive as the first.

## The known solution and what it costs

The known solution is a larger model. That means two things: more expensive
hardware, and a dependency on someone else. Neither is a price this project
accepts, because what we want to measure is a gain that is independent of the
model growing.

## The alternative under test

Lowering the cost by using accumulated experience, without growing the model.

There are two mechanisms. **Compiled skills**: verified call sequences mined from
past episodes. **An explicit failure index**: a record carrying which action
failed in which context.

Neither one changes the agent itself. The model is not touched, there is no
training and no fine-tuning. The only thing that changes is the information that
enters the agent's context.

## What is outside this document's scope

This project does not improve the model, does not improve the benchmark, and does
not propose a general memory architecture. It measures a single question: does
accumulated experience lower the number of model calls.

The full form of the research questions is in `02-research-question.en.md`.
