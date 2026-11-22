# Data model

Turkish is the source: `DATA_MODEL.tr.md`.

The schema itself is in `src/zihin/schema.sql`; this document says why it is the
way it is.

## Tables

Nine tables, two classes. The class distinction is this document's most important
rule, and the machine enforces it (§"Projection rule").

| Table | Class | What it holds |
|---|---|---|
| `run_manifests` | record | The run itself: model, server settings, limits, commits, shield and sandbox identity |
| `episodes` | record | One attempt at a task: condition, seed, termination reason, totals |
| `steps` | record | One model call and the one `execute()` that follows it |
| `actions` | record | The API calls made in that step |
| `observations` | record | That step's output, one per step |
| `shield_violations` | record | The actions the shield rejected |
| `verifier_results` | record | One verdict per episode |
| `skills` | **projection** | The skill library the compiler produces |
| `failure_patterns` | **projection** | The failure index extracted by mining |

**Correction, 13 October 2026: twelve tables.** This section counts nine tables; the
schema has twelve today. The three that came later:

| Table | What it holds | How it entered |
|---|---|---|
| `run_ledger` | The accumulation run's ledger, one row per block boundary (K-162) | `579d4f1`, 10 September 2026; without a PR, straight to `main` |
| `experiment_slices` | The experiment's slices: each slice's task list, written before its first episode | #70 (`4a04e50`) |
| `experiment_episodes` | One row per experiment episode, written in the episode's own transaction | #70 (`4a04e50`) |

The schema defines all three as record; `PROJECTION_TABLES` still names only `skills`
and `failure_patterns`. But none of them carries an append-only trigger: the migration
that adds a missing table to an existing file splits the schema on `;`, and a
trigger's body carries one, so a trigger written here would exist in a fresh file and
not in the series the experiment writes to. On these three tables append-only rests
on the writers (K-182). The record tables that carry triggers are still the seven
above.

## The deletion test

One question decides which class a table belongs to:

> **If I delete this table, can I recompute it from the record?**

If the answer is "yes", it is a projection and has to be deletable and
regenerable. If the answer is "no", it is record and falls under the append-only
rule: once written, it is neither updated nor deleted.

The test is not rhetorical; it runs: `tests/test_compiler.py` and
`tests/test_failure_index.py` delete the projection, regenerate it from the record,
and check that the same rows come out.

**The test has a side that does not pass today, and it is written down.** The
projection cannot be regenerated **with the same identity**: the identity carries
the compiler commit (`v0-gap2-sup3-142662f`), so regenerating it today writes a new
identity. The content can be regenerated; the identity cannot. This is
deliberate — the identity carries the commit to say which rule produced it — but
it is why the sentence "I can delete it and put the same thing back" is not quite
true.

## Projection rule

The `PROJECTION_TABLES` constant (`src/zihin/records.py`) names two tables:
`skills` and `failure_patterns`.

The rule has two consequences, and both are in the code:

1. **Projection tables have no append-only trigger.** On the seven record tables
   `UPDATE` and `DELETE` are blocked with `RAISE(ABORT)`; on projections they are
   not, because being deleted and regenerated is exactly what they are for.
2. **A schema migration can rebuild projections.** When a projection table's
   definition changes, the migration path drops and recreates it; on record
   tables it does not do this, and cannot.

If a table is added to the list, the append-only protection is lifted from it.
That is why the list is in one place and nailed down by a test.

## The record is the single source of truth

The record is the single source of truth. The skill library and the failure index
are derived projections, that is, they can be deleted and recomputed from the
record. That is why the `skills` and `failure_patterns` tables are not here and
will not be.

**Correction, 18 October 2026: the two projection tables are in this schema.** This
paragraph was written when the schema held only record tables (`09ed3fb`, 10 August
2026). `skills` entered the same schema on 16 August (`142662f`) and
`failure_patterns` on 17 August (`771b94f`); both are named in `PROJECTION_TABLES`
and stand in the table above as **projection**. What has not changed: the record is
the single source of truth; the two tables are derived from it, can be deleted and
regenerated, and the append-only rule does not apply to them.

The reason has to do with time. The derivation rules will change several times
over the course of the work. If the projection is taken as the truth, the old data
becomes unusable the moment a rule changes. If the record is taken as the truth,
the only thing to do when a rule changes is to recompute.

The same principle holds for the `actions.raw_parameters` column. Raw parameters
are stored in full, not as a digest (K-15), because the normalization rule will
change and the projection has to be recomputable from the record.

## Four levels

```
run_manifests
  └── episodes            one attempt at a task
        └── steps         one model call and the one execute() that follows it
              ├── actions       the API calls made in that step
              ├── observations  that step's output, one per step
              └── shield_violations  the actions the shield rejected
        └── verifier_results   one verdict per episode
```

### Why the observation is tied to the step

The specification tied the observation to the action. The measurement said
otherwise: AppWorld's `execute()` method returns a single output string per step
and gives no separate output for individual API calls. A "full output" at action
level does not exist as a notion in the environment. The decision is in K-13: the
observation is tied to the step.

This has a consequence: there is a `UNIQUE` constraint on `observations.step_id`,
that is, exactly one observation per step.

### A step that produces no action is still in the table

K-36's fourth and fifth categories produce no action at all. If those steps
dropped out of the record, an episode with zero actions would look the same as an
episode in which the agent chose not to call. `steps.outcome_category` carries
that distinction, and the `episode_timeline` view returns the steps without an
action row too.

## Why shield violations are in a separate table

An action the shield rejects is not executed, so it does not enter the `actions`
table. But it must not be lost: every rejected action is a labelled negative
example obtained before any damage occurred, and it will be written directly into
the failure index.

`shield_violations` is tied to the step, because a violation happens inside the
code a step produced. The `mode` column takes the values `enforce` and `shadow`; in
shadow mode the action goes through, but the violation is still recorded.

## Why the episode row has two fields

`sequence_in_run` and `model_load_state` were added because of a Stage 2
measurement.

The measured fact is this: same task, same seed, same temperature. With the model
cold the episode produces 19 API calls; warmed up, 1. Both runs repeat exactly
within their own regime. So the load state is a hidden variable, and if it is not
recorded, a difference between episodes is taken for a difference between
conditions.

`sequence_in_run` is for testing drift within a run afterwards. If the server state
drifts over time, the sequence number can enter the model as a covariate. The
`UNIQUE (run_id, sequence_in_run)` constraint keeps the number from repeating;
otherwise the test would be meaningless.

## Manifest

`run_manifests` carries the fields that cannot be collected afterwards if they are
not collected during the run. The model tag is written in full, size and
quantization included.

### The manifest contract: fields that must be filled

If one of these fields is empty the manifest is **not written** and the run fails
(K-46). The reason has to do with time: if this information is not collected
during the run it cannot be collected afterwards, so an incomplete manifest makes
the run worthless. The list is in the `ZORUNLU_KUNYE_ALANLARI` constant, in one
place.

**Correction, 13 October 2026: the constant's name.** The constant took the name
`REQUIRED_MANIFEST_FIELDS` in the commit that translated the identifiers into English
(`acef1d8`, 18 August 2026); it is in `src/zihin/records.py`.

| Field | Why it is required |
|---|---|
| `run_id` | The run's identity |
| `model_tag` | Which model; size and quantization included |
| `temperature`, `base_seed` | The two numbers that determine the trajectory |
| `no_progress_limit` | The parameter that can end an episode; 0 means "rule off", and that is written too |
| `max_output_tokens` | Measured: changing only this value took the passing tasks from 6/30 to 20/30 (S-26) |
| `max_prompt_characters` | The number that determines the effective context (S-47); -1 "no ceiling", NULL "not recorded" |
| `model_server_env` | The server settings live outside the repository |
| `appworld_commit`, `code_commit` | Which code produced it |
| `instruction_file_digest` | The digest of the text sent to the model |
| `os_environment` | Platform |
| `shield_mode` | Which regime the `shield_violations` rows were produced under |

In local serving, server-specific fields are required as well; a hosted model has
no counterpart for them, so they are not required in that mode.

**Being nullable and being allowed to stay empty are not the same thing.** A column
may accept `NULL`; the contract may still require it to be filled. The schema side
is loose so that old rows can migrate, the Python side is strict for new rows. This
distinction is the lesson of S-29: `CHECK` constraints cannot be carried over to
columns added through a migration.

**Context is bounded in two different units, and the manifest carries both.**
`num_ctx_requested` / `num_ctx_effective` are the token window;
`max_prompt_characters` is the scaffold's own prompt ceiling, in characters. The
binding one is the second: measured, 50000 characters of real record content are
12799 tokens, that is, 39% of the 32K window (S-47). The value is read from
`config/recording.yaml`, the number passed to the agent and the number entering
the manifest come from the same source, and the field is on the resume check's
reject list. NULL means "not recorded" — the manifest is append-only, so once the
column was added no number could be written into the old rows; -1 means "no
ceiling".

Two fields are K-37's condition: `num_ctx_effective` and `context_verified`. The
context window comes from an environment variable on the server side, that is, it
lives outside the repository. If the server is restarted once without that
variable, the window silently falls back to 4096 and the measurement breaks, yet no
error appears anywhere. That is why the runner asks the server before the run and
stops if the window does not hold.

The verification has its own cost, and it was measured: `/api/ps` reports only the
model loaded at that moment, so reading the window requires loading the model. The
verification warms the model. That is why `scripts/record_run.py` unloads the
model again after the verification and starts the episode in the cold regime.

## Append-only

On all record tables `UPDATE` and `DELETE` are blocked by triggers that
`RAISE(ABORT)` (K-16). This is not a convention but an architectural rule, so the
machine guards it. `tests/test_record_schema.py` tests each of the seven tables
separately.

**Correction, 13 October 2026.** When this paragraph was written there were seven
record tables. Today there are ten, and the triggers are on those seven only; the
three that came later, `run_ledger`, `experiment_slices` and `experiment_episodes`,
leave append-only to their writers (above, "Tables"; K-182).

This has a consequence: an episode's end time and totals are known only when the
episode ends, and updating is forbidden. That is why `scripts/record_run.py`
accumulates the whole episode in memory and writes it at the end in a single
transaction. If it crashes in the middle of a run, AppWorld's own logs stay on
disk, so the data is not lost; it just has not entered the database.

## Where writing happens

Writing to the record happens on the host side, in the executor process (K-14).
Nothing is written to the record from inside the code the agent runs. The reason
is simple: an agent that breaks its own environment also breaks a record written
from inside it.

The actions come from AppWorld's `logs/api_calls.jsonl` file. That file is a flat
list and does not say which call belongs to which step, so looking at it after the
run, the actions cannot be tied to steps. That is why the record is taken live:
however much the file grew during a step, that much is the step's actions.

Doing this does not touch the scaffold. `SimplifiedReActCodeAgent` is used as it is;
only the environment's execution method is wrapped from outside. The agent's
prompt, parser and loop stay the same.

**The wrapped method depends on the mode, and this was learned by measurement.**
The reference agent calls `world.batch_execute`, not `world.execute`. In in-process
mode `batch_execute` calls `self.execute` for every piece of code, so wrapping
`execute` was enough — the recording worked by this coincidence until now and
nobody noticed. In remote-environment mode `batch_execute` goes straight to an
HTTP call and `self.execute` is never called; the first sandbox episode produced a
32 KB trajectory and wrote zero steps to the record (S-53). In remote mode
`batch_execute` is wrapped, in in-process mode `execute`, and both are nailed down
by mutation in `tests/test_recording_mount.py`.

**In sandbox mode the actions do not come from `api_calls.jsonl`.** That file is
written by the environment server, and the environment server is inside the
container; there is no second source on the host side. The actions come from the
recording proxy and no count comparison is made, because there is no second number
to compare. For a while the absence of the source was read as "zero calls", and
that was the second layer of S-53.

## Columns that cannot be filled

`verifier_results.expected_changes_complete` and `unexpected_changes_present`:
AppWorld's `TestTracker` class gives `passes` and `failures` lists and may not give
the paper's two components as separate booleans (S-04). The columns are kept so
that the place is ready on the day they can be extracted.

**`actions.result_status` is filled now, and that is why this section changed.**
S-05 said that `api_calls.jsonl` carries neither the response body nor the status
code; `ApiCapture` took both by wrapping the `Requester` (S-16). Measured: all 5261
actions have a status code — 200 (4489), 401 (503), 422 (235), 409 (34).

**`actions.error_class` depends on the mode.** In in-process mode it carries the
exception's class name; in sandbox mode it is `NULL`, because the proxy does not
see the exception — the exception arises inside the container (S-52). In the record
the field can be derived one to one from the status code (772 = 503+235+34), so no
information is lost; having the proxy make up a value it does not see was rejected.

**The state measurement is in two columns, and the two cannot both be filled in the
same step.** `steps.state_change` carries the row-count difference and is filled
in in-process mode; `steps.state_hashes` carries which model changed and is filled
in served mode (K-93). They are separate columns because they are separate
meanings: one is "how many rows changed", the other "which model changed". Had they
been put in the same column, the meaning of a value would depend on the mode that
produced it. `insert_step` refuses to write both together.

## Observation size and disk quota

`config/recording.yaml` carries two limits. The upper bound for the truncated text
entering the context is 8192 bytes. Next to the 5958 input tokens per step measured
in Stage 2, this bound keeps a single observation from swallowing the whole
context.

The disk quota per run is 2 GiB. When the quota fills, the run stops. Silently
dropping records produces a data loss that goes unnoticed afterwards; stopping is
better than losing (K-17).

Truncation is applied on entering the context, not at the moment of overflow. The
full text stays on disk and the database carries only its reference.

## Reading an episode with one query

The `episode_timeline` view is the very query the acceptance criterion asks for.

```sql
SELECT * FROM episode_timeline
WHERE episode_id = ?
ORDER BY step_index, action_index;
```

A left outer join is used, so steps that produce no actions give rows too.
