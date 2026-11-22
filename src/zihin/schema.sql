-- ZIHIN recording schema.
--
-- A four-level hierarchy: episode, step, action, observation. The observation
-- hangs off the step, not the action (K-13). The reason is a measured fact:
-- AppWorld's execute() method returns a single output string per step, not a
-- separate output per API call.
--
-- Every recording table is append-only. UPDATE and DELETE are blocked with
-- triggers (K-16). This is an architectural rule rather than a convention, so
-- the machine enforces it.
--
-- There are NO skills or failure_patterns tables. Those are projections; they
-- will be recomputed from the record and are the subject of a later task.

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- Run manifest
-- ---------------------------------------------------------------------------
-- If these fields are not collected during the run, they cannot be collected
-- afterwards. The model tag is written in full, including size and
-- quantisation.
CREATE TABLE run_manifests (
    run_id                  TEXT    PRIMARY KEY,
    created_at              TEXT    NOT NULL,

    -- Interruption resilience. created_at comes from /proc/uptime and is
    -- precise within a boot, but a restart resets uptime: after a power cut the
    -- next episode's start comes out lower than the previous one and the
    -- ordering breaks silently. The two fields below close that.
    --
    -- boot_id makes the seam visible: two manifests with different values ran
    -- under different boots. Because interruptions are frequent here, this is
    -- the one field that makes it readable whether an episode set is a single
    -- piece or a stitched one.
    boot_id                 TEXT    NOT NULL,

    -- The wall clock restores ordering across boots; boot_id is a random UUID
    -- and gives no order on its own. The value comes from SQLite itself:
    -- AppWorld freezes the clock process-wide with freezegun, so any time
    -- computed inside the process is untrustworthy. The INSERT never sends this
    -- column and insert_run_manifest refuses an externally supplied value, so
    -- it is structurally impossible for the process to determine it. UTC,
    -- second resolution; episodes last minutes, so that is enough for ordering.
    wall_clock_utc          TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- How the model is served. The local-only fields (effective context window,
    -- KV cache type, keep_alive, server environment) are mandatory in 'local'
    -- mode only. On a hosted model the effective window cannot be verified, so
    -- writing context_verified=1 would be a lie. The contract is not skipped,
    -- it is narrowed by mode; its fail-closed property is preserved by the
    -- CHECK below.
    serving_mode            TEXT    NOT NULL DEFAULT 'local',

    model_tag               TEXT    NOT NULL,
    num_ctx_requested       INTEGER,
    num_ctx_effective       INTEGER,
    context_verified        INTEGER NOT NULL DEFAULT 0,
    kv_cache_type           TEXT,
    flash_attention         INTEGER,
    temperature             REAL    NOT NULL,
    base_seed               INTEGER NOT NULL,
    keep_alive              TEXT,
    model_server_env        TEXT,

    -- The stopping rule's threshold. Calibrated against the 30 complete
    -- trajectories of the boundary control (K-64), and to be recalibrated as a
    -- transfer control once the family is chosen — so which threshold a run
    -- used must be readable from the manifest.
    no_progress_limit       INTEGER NOT NULL,

    -- Output budget per step (K-60). It was measured that when this is binding,
    -- the configuration rather than the model determines the result: with the
    -- same model and the same tasks, changing only this value moved the passing
    -- count from 6/30 to 20/30 (S-26). -1 means "not set, the server's
    -- default"; the fact that it was not set is itself recorded, because a
    -- value that cannot be read back later leaves the same question
    -- unanswerable.
    max_output_tokens       INTEGER NOT NULL DEFAULT -1,

    -- The scaffold's own prompt ceiling, in **characters** (S-47).
    --
    -- This is the parameter that actually bounds the context, and it is in a
    -- different unit from the window. Measured: 50000 characters of real
    -- recorded content is 12799 tokens, i.e. 39% of the 32K window — so the
    -- effective context is about 13K and the window never fills. Thirty-one of
    -- the 105 recorded episodes crossed it, the earliest at step 9.
    --
    -- It has to be in the manifest for the same reason `max_output_tokens` is:
    -- changing it changes what the model sees, and a value that cannot be read
    -- back leaves the question unanswerable. The reference configs for this
    -- agent set it to `null` (no truncation); ours does not, so it is our
    -- parameter and not an inherited default.
    --
    -- -1 means "no ceiling", matching the agent's own `None`. **NULL means "not
    -- recorded"** and that is the honest value for rows written before this
    -- column existed: those episodes ran at 50000, but the manifest is
    -- append-only, so writing the number in afterwards is not possible and would
    -- not be a record if it were. Fresh manifests cannot leave it unset — the
    -- contract refuses them.
    max_prompt_characters   INTEGER,

    -- Identity of the skill library the condition used. There is no skill
    -- library yet, so this is NULL for now; the column is already here because
    -- the resume check treats it as a condition-defining field and it has to
    -- work without a migration once the library arrives.
    library_id              TEXT,

    -- Which shield the run carried, and what it was configured with.
    --
    -- The mode alone is not enough. `shield_violations` rows only mean
    -- something relative to the write set that produced them, and that set has
    -- already changed twice in one day: once when the resolver started taking
    -- the method, once when `update` was dropped from the verb list. Two runs
    -- whose violations were produced by different sets cannot be compared, and
    -- without this column the difference would be invisible.
    --
    -- The digest covers the write set, the cross-app mapping inside it and the
    -- source of the allowed-app inferrer. A digest rather than a version
    -- number: it is computed, so it cannot fall out of date through neglect.
    --
    -- Default 'off' is correct for the rows already written: those episodes ran
    -- before the shield existed, so no shield was mounted. That is a fact, not
    -- a stand-in value.
    shield_mode             TEXT    NOT NULL DEFAULT 'off',
    shield_config_digest    TEXT,

    -- Which sandbox the run carried.
    --
    -- NULL means the episode ran without a sandbox, which is a fact about the
    -- 115 episodes recorded before this layer existed: the agent's code ran in
    -- our own process. It is not a stand-in value.
    --
    -- The limits are here because they can decide the result. If a limit binds,
    -- the sandbox rather than the model ends the episode, and K-D requires that
    -- to be visible: the share of episodes ending at a limit has to be near
    -- zero or the result is a lower bound. Without these columns a tightened
    -- limit would look like a worse model.
    --
    -- `sandbox_proxy_digest` covers the proxy's route policy, the same way
    -- `shield_config_digest` covers the write set: the policy decides which
    -- management routes exist, so two runs under different policies are not
    -- comparable. Computed, not bumped by hand.
    --
    -- `serving_mode` already exists above and says where the model came from;
    -- these say where the agent's code ran.
    sandbox_image           TEXT,
    sandbox_network_mode    TEXT,
    sandbox_memory_bytes    INTEGER,
    sandbox_pids_limit      INTEGER,
    sandbox_step_timeout_seconds INTEGER,
    sandbox_tmpfs_bytes     INTEGER,
    sandbox_cpus            REAL,
    sandbox_version         TEXT,
    sandbox_proxy_digest    TEXT,

    appworld_version        TEXT    NOT NULL,
    appworld_commit         TEXT    NOT NULL,
    code_commit             TEXT    NOT NULL,
    instruction_file_digest TEXT    NOT NULL,
    os_environment          TEXT    NOT NULL,

    -- Durability of the recording store against a hard interruption. Measured,
    -- not assumed: with synchronous OFF even a committed transaction can be
    -- lost, so the episode record shrinks silently and the shrinkage is biased
    -- by episode length. The values are read from the connection itself; the
    -- CHECK below rejects non-durable settings, so no manifest can be written
    -- to a non-durable store.
    journal_mode            TEXT    NOT NULL,
    synchronous_setting     INTEGER NOT NULL,

    -- State of the working tree. `code_commit` records HEAD, not the working
    -- tree; episodes run with uncommitted changes appeared under the same
    -- commit as clean runs. A dirty tree now blocks the run, and overriding it
    -- requires an explicit flag; the flag is written here.
    --
    -- No default: a raw INSERT has to supply the value. `unknown` does not
    -- count as clean either — if git cannot be read, the tree's cleanliness is
    -- not verified.
    working_tree            TEXT    NOT NULL,

    CHECK (serving_mode IN ('local', 'hosted')),
    CHECK (boot_id <> ''),
    CHECK (wall_clock_utc <> ''),

    -- 0 = OFF is rejected. 1 NORMAL, 2 FULL, 3 EXTRA are accepted; all three
    -- protect a committed transaction against a hard interruption.
    CHECK (synchronous_setting IN (1, 2, 3)),
    CHECK (journal_mode NOT IN ('off', 'memory')),
    CHECK (working_tree IN ('clean', 'dirty', 'unknown')),
    CHECK (shield_mode IN ('shadow', 'enforce', 'off')),

    -- Fail-closed: a run that carried a shield has to say which one. Only an
    -- 'off' run may leave the digest empty, because there was nothing to
    -- digest.
    CHECK (shield_mode = 'off' OR (
        shield_config_digest IS NOT NULL AND shield_config_digest <> ''
    )),
    CHECK (num_ctx_requested IS NULL OR num_ctx_requested > 0),
    CHECK (context_verified IN (0, 1)),
    CHECK (flash_attention IS NULL OR flash_attention IN (0, 1)),

    -- Fail-closed, by mode. In a local run these five fields cannot be left
    -- empty and the run does not start before the window is verified (K-37,
    -- K-46). In a hosted run they have no counterpart and are therefore free,
    -- but model_server_env stays mandatory: the provider and transport layer
    -- are read from it.
    CHECK (serving_mode <> 'local' OR (
        num_ctx_requested IS NOT NULL
        AND num_ctx_effective IS NOT NULL
        AND kv_cache_type IS NOT NULL
        AND keep_alive IS NOT NULL
        AND context_verified = 1
    )),
    CHECK (model_server_env IS NOT NULL AND model_server_env <> '')
);

-- num_ctx_effective and context_verified together carry K-37's first
-- condition. If the server restarts without its environment variable, the
-- window silently falls back to 4096; a run does not start without filling
-- this field.

-- ---------------------------------------------------------------------------
-- Level 1: episode
-- ---------------------------------------------------------------------------
CREATE TABLE episodes (
    episode_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id              TEXT    NOT NULL REFERENCES run_manifests(run_id),

    task_id             TEXT    NOT NULL,
    split               TEXT    NOT NULL,
    condition           TEXT    NOT NULL,
    model_ref           TEXT    NOT NULL,
    seed                INTEGER NOT NULL,

    -- Position within the run and the model's load state. Both exist because of
    -- a Stage 2 measurement: the same task produced 19 API calls with a cold
    -- model and 1 with a warm one. If the load state is not recorded, that
    -- difference is mistaken for a condition difference. The sequence number
    -- also lets server-state drift be tested later as a covariate.
    sequence_in_run     INTEGER NOT NULL,
    model_load_state    TEXT    NOT NULL,

    -- This episode's step ceiling. The ceiling is computed per task (K-43) and
    -- could not be read back when it was not recorded: `termination_reason`
    -- says the ceiling was hit but not what the ceiling was. Whether the
    -- multiplier changed is also only visible from here.
    step_ceiling        INTEGER,

    -- How many distinct **operations** and distinct **objects** the episode
    -- touched. `distinct_endpoints` is at route-template level:
    -- `tasks/{task_id}/comments` is one operation. `distinct_resources` is at
    -- concrete-path level: `tasks/2851/comments` and `tasks/2854/comments` are
    -- two objects.
    --
    -- The ratio between them is diagnostic in itself and was decisive once.
    -- Many objects with few operations means exploration, not repetition:
    -- `8ce6779_2` reads different resources at 27/9 = 3.0 and passes, while
    -- S-25's pathological episode repeats the same three calls 736 times at
    -- 3/3 = 1.0. The stopping rule's identity being the concrete call rests on
    -- that distinction (K-63), and the error taxonomy will need it again.
    --
    -- A number that is computed and thrown away can rot silently; a recorded
    -- one cannot.
    distinct_endpoints  INTEGER,
    distinct_resources  INTEGER,

    started_at          TEXT    NOT NULL,
    ended_at            TEXT,
    termination_reason  TEXT,
    total_model_calls   INTEGER,
    input_tokens        INTEGER,
    output_tokens       INTEGER,
    duration_seconds    REAL,

    UNIQUE (run_id, sequence_in_run),
    UNIQUE (run_id, task_id, condition, seed),
    CHECK (model_load_state IN ('cold', 'warm', 'unknown')),
    CHECK (sequence_in_run >= 1)
);

CREATE INDEX idx_episodes_run ON episodes (run_id);
CREATE INDEX idx_episodes_task ON episodes (task_id);
CREATE INDEX idx_episodes_condition ON episodes (condition);
CREATE INDEX idx_episodes_load_state ON episodes (model_load_state);

-- ---------------------------------------------------------------------------
-- Level 2: step
-- ---------------------------------------------------------------------------
-- A step is a single model call followed by a single execute() call.
CREATE TABLE steps (
    step_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    episode_id          INTEGER NOT NULL REFERENCES episodes(episode_id),

    step_index          INTEGER NOT NULL,
    instruction_digest  TEXT    NOT NULL,
    context_tokens      INTEGER,
    generated_tokens    INTEGER,
    latency_seconds     REAL,
    generated_code      TEXT,

    -- One of K-36's five categories, or NULL when an action was produced.
    outcome_category    TEXT,

    -- The state change the step produced: the row-count delta per model, as
    -- JSON. The empirical write set is built on top of this (K-41). An empty
    -- object means "measured, no change"; NULL means "not measured". The two
    -- must never be conflated.
    state_change        TEXT,

    -- The same question asked a second way, and the reason it is a second
    -- column rather than a second meaning for the first one.
    --
    -- In served mode the in-process model collection does not exist
    -- (`world.models is None`), so the row-count probe cannot run: it would
    -- return an empty object every step and claim "measured, no change" while
    -- measuring nothing. The probe therefore moved onto HTTP (K-93):
    -- `POST /dbs/save` with `format=changes` and `save_model_hashes=true`
    -- reports which `app.Model` pairs differ from the episode's start.
    --
    -- The two carry different information. `state_change` is a signed row-count
    -- delta and cannot see an update that leaves the row count alone;
    -- `state_hashes` sees exactly that (measured: `set_volume` changes no row
    -- count and does show up here) but carries no magnitude. Putting both in one
    -- column would make a value's meaning depend on which mode produced it,
    -- which is the silent lie this schema exists to prevent.
    --
    -- Exactly one of the two is populated per step; the other is NULL.
    state_hashes        TEXT,

    UNIQUE (episode_id, step_index),
    CHECK (step_index >= 1),
    CHECK (outcome_category IS NULL OR outcome_category IN (
        'no_code',
        'unparseable',
        'context_overflow',
        'execution_error_no_action',
        'execution_ok_no_action'
    ))
);

CREATE INDEX idx_steps_episode ON steps (episode_id);
CREATE INDEX idx_steps_outcome ON steps (outcome_category);

-- ---------------------------------------------------------------------------
-- Level 3: action
-- ---------------------------------------------------------------------------
CREATE TABLE actions (
    action_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    step_id               INTEGER NOT NULL REFERENCES steps(step_id),

    action_index          INTEGER NOT NULL,
    app                   TEXT    NOT NULL,
    api                   TEXT    NOT NULL,
    http_method           TEXT,

    -- K-15: raw parameters in full, not as a digest. The normalisation rule
    -- will change and the projection has to remain recomputable from the
    -- record.
    raw_parameters        TEXT    NOT NULL,
    normalized_parameters TEXT,

    result_status         TEXT,
    error_class           TEXT,
    latency_seconds       REAL,

    UNIQUE (step_id, action_index),
    CHECK (action_index >= 1)
);

CREATE INDEX idx_actions_step ON actions (step_id);
CREATE INDEX idx_actions_api ON actions (app, api);
CREATE INDEX idx_actions_method ON actions (http_method);

-- ---------------------------------------------------------------------------
-- Level 4: observation
-- ---------------------------------------------------------------------------
-- One observation per step (K-13). The full output lives on disk; the database
-- holds only its reference and the truncated text that enters the context
-- (K-17).
CREATE TABLE observations (
    observation_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    step_id          INTEGER NOT NULL UNIQUE REFERENCES steps(step_id),

    full_output_path TEXT,
    truncated_text   TEXT    NOT NULL,
    truncated_bytes  INTEGER NOT NULL,
    full_bytes       INTEGER NOT NULL,
    token_count      INTEGER,
    was_truncated    INTEGER NOT NULL,

    CHECK (was_truncated IN (0, 1)),
    CHECK (truncated_bytes >= 0),
    CHECK (full_bytes >= truncated_bytes)
);

CREATE INDEX idx_observations_step ON observations (step_id);

-- ---------------------------------------------------------------------------
-- Verifier verdict
-- ---------------------------------------------------------------------------
CREATE TABLE verifier_results (
    verifier_result_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    episode_id                 INTEGER NOT NULL UNIQUE REFERENCES episodes(episode_id),

    passed                     INTEGER,
    -- S-04: these two components stay NULL while they cannot be extracted
    -- separately from TestTracker. The columns stay so the place is ready on
    -- the day they can be.
    expected_changes_complete  INTEGER,
    unexpected_changes_present INTEGER,
    num_passed_tests           INTEGER,
    num_failed_tests           INTEGER,
    detail_path                TEXT,

    CHECK (passed IS NULL OR passed IN (0, 1)),
    CHECK (expected_changes_complete IS NULL OR expected_changes_complete IN (0, 1)),
    CHECK (unexpected_changes_present IS NULL OR unexpected_changes_present IN (0, 1))
);

CREATE INDEX idx_verifier_episode ON verifier_results (episode_id);

-- ---------------------------------------------------------------------------
-- Shield violations
-- ---------------------------------------------------------------------------
-- A rejected action never executes, so it does not enter the actions table; it
-- hangs off the step instead. Every action the shield rejects is a labelled
-- negative example obtained before any damage was done.
CREATE TABLE shield_violations (
    violation_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    step_id        INTEGER NOT NULL REFERENCES steps(step_id),

    violation_index INTEGER NOT NULL,
    app            TEXT    NOT NULL,
    api            TEXT    NOT NULL,
    http_method    TEXT,
    raw_parameters TEXT    NOT NULL,
    predicate      TEXT    NOT NULL,
    mode           TEXT    NOT NULL,
    reason         TEXT,

    UNIQUE (step_id, violation_index),
    CHECK (mode IN ('enforce', 'shadow')),
    CHECK (violation_index >= 1)
);

CREATE INDEX idx_shield_step ON shield_violations (step_id);
CREATE INDEX idx_shield_api ON shield_violations (app, api);
CREATE INDEX idx_shield_mode ON shield_violations (mode);

-- ---------------------------------------------------------------------------
-- Skill library
-- ---------------------------------------------------------------------------
-- A **derived projection** (`03-architecture.md`): delete this table and the
-- compiler rebuilds it from the episodes. Nothing here is a source of truth,
-- which is why it can carry a compiler version and be replaced wholesale.
--
-- The record is specified in `SKILL_SPEC.md`. Every column has a mechanical
-- derivation; the compiler is offline, deterministic and uses no model, so
-- nothing in this table was written by judgement.
CREATE TABLE skills (
    skill_id            TEXT    PRIMARY KEY,
    library_id          TEXT    NOT NULL,

    -- The identity. Two patterns with the same effect suffix are one skill
    -- (K-75, `06-skill-language.md`), so this is what `skill_id` digests.
    effect_suffix       TEXT    NOT NULL,
    -- The call sequence that executes: the widest-supported member of the merge.
    body                TEXT    NOT NULL,
    body_length         INTEGER NOT NULL,

    -- Support counts distinct **tasks**, never episodes. `merged_from` says how
    -- many mined patterns collapsed into this skill; a large number there means
    -- the same effect was reached through many prefixes.
    support             INTEGER NOT NULL,
    supporting_tasks    TEXT    NOT NULL,
    supporting_episodes TEXT    NOT NULL,
    merged_from         INTEGER NOT NULL,

    -- Argument classes. Binding is decided first, then variability
    -- (`06-skill-language.md`); the reverse order would turn bound arguments
    -- into parameters and leave the caller knowing half the answer already.
    bound_arguments     TEXT    NOT NULL,
    free_parameters     TEXT    NOT NULL,
    constants           TEXT    NOT NULL,

    -- The shape intersection over the supporting occurrences: `{"app.Model":
    -- "+"}`. NULL means "not attributable", which is different from `{}`,
    -- "attributable and nothing changed" (K-79). Magnitude is deliberately
    -- absent: it follows a free parameter whenever the skill has one.
    postcondition       TEXT,

    -- Expected saving in **model calls**: `(observed steps - 1) * support`.
    -- The primary metric of this project is the model call, one step is one
    -- model call, and a skill is invoked in a single step. Counting API calls
    -- instead overcounts whenever the agent already packed several into one
    -- step: measured, one of the four skills makes three calls in two steps and
    -- the call-based figure doubles its saving (K-82).
    --
    -- **Stored, not applied.** The threshold's number belongs to the setup
    -- phase and has not been chosen (K-50); filtering here would bake an
    -- unchosen number into the record. The reader applies it, and the
    -- sensitivity is reported instead.
    --
    -- **It is a lower bound for the models the skills are meant to help.** The
    -- step counts come from the boundary-control trajectories; a weaker local
    -- model spreads the same calls over more steps, so the skill is worth more
    -- to it than this column says.
    expected_saving     INTEGER,
    -- The call-based figure the specification used to prescribe, kept as a
    -- diagnostic. The gap between the two is what showed the specification was
    -- counting the wrong unit.
    expected_saving_calls INTEGER NOT NULL,
    observed_steps      INTEGER,

    -- How the library was produced. Without these the numbers above cannot be
    -- reproduced: the same episodes give different skills at a different gap,
    -- and the gap's upper bound is set by executability (K-81).
    max_gap             INTEGER NOT NULL,
    min_support         INTEGER NOT NULL,
    constant_threshold  INTEGER NOT NULL,
    compiler_commit     TEXT    NOT NULL,
    write_set_digest    TEXT    NOT NULL,

    UNIQUE (library_id, effect_suffix),
    CHECK (body_length >= 2),
    CHECK (support >= 1),
    CHECK (merged_from >= 1),
    CHECK (effect_suffix <> '' AND effect_suffix <> '[]')
);

CREATE INDEX idx_skills_library ON skills (library_id);
CREATE INDEX idx_skills_support ON skills (support);
CREATE INDEX idx_skills_saving ON skills (expected_saving);

-- ---------------------------------------------------------------------------
-- Failure index
-- ---------------------------------------------------------------------------
-- The other derived projection, and rebuildable on the same terms as `skills`.
--
-- **Every row carries a context condition, and the column is NOT NULL for it.**
-- An unconditional prohibition makes the agent worse: a card that says "do not
-- make this call" without saying when also blocks it where it is required
-- (`07-failure-taxonomy.md`). A pattern with no expressible condition is left
-- out of the index rather than stored conditionless, and the count of those is
-- reported.
CREATE TABLE failure_patterns (
    pattern_id        TEXT    PRIMARY KEY,
    index_id          TEXT    NOT NULL,

    app               TEXT    NOT NULL,
    api               TEXT    NOT NULL,
    http_method       TEXT    NOT NULL,
    -- Which argument names the call carried, never their values (K-83). Keying
    -- on values would explode the pattern space and collapse support, the way
    -- keying skills on concrete paths would have.
    argument_shape    TEXT    NOT NULL,

    status_code       TEXT    NOT NULL,
    -- Read from the status code, not from `error_class`: that column is
    -- uniformly 'Exception' because AppWorld raises on every failed response
    -- (S-44).
    failure_label     TEXT    NOT NULL,

    -- The closed language, third form: whether a given call had already
    -- succeeded earlier in the sequence. `present=false` is a condition too.
    --
    -- **NULL exactly when there was nothing to contrast against.** A condition
    -- is derived contrastively; with no successful occurrence of the endpoint
    -- there is nothing to separate from, so every admissible condition
    -- separates trivially and none of them is a finding. Carrying one anyway
    -- would be an empty claim wearing the shape of a real one. Measured: one
    -- such pattern had 59 admissible conditions (S-45).
    condition         TEXT,
    -- Which of the two things separated this pattern from the endpoint's
    -- successes: the condition itself, or the argument shape. Recorded so the
    -- report can tell a card that says "log in first" from one that says "you
    -- are logged in but not carrying the token". NULL with the condition.
    discriminator     TEXT,

    support           INTEGER NOT NULL,
    supporting_tasks  TEXT    NOT NULL,
    failure_count     INTEGER NOT NULL,
    contrast_successes INTEGER NOT NULL,
    -- A pattern whose endpoint never succeeded anywhere. Kept rather than
    -- dropped: a failure seen once but real would otherwise vanish. Counted
    -- separately in retrieval (`07-failure-taxonomy.md`).
    --
    -- **It carries no condition at all**, and the CHECK below enforces that.
    no_known_success  INTEGER NOT NULL DEFAULT 0,

    -- How much to trust the condition, carried on the card rather than left in
    -- a report. The candidate space is every call in the alphabet, present or
    -- absent, so with a small failure group a condition can separate by
    -- coincidence. A high count means the choice among separating conditions
    -- was arbitrary; `own_app_condition = 0` means the only separating
    -- conditions were about other apps, which is a correlation and not a cause.
    --
    -- **No threshold is applied here.** The multiple-comparison problem has no
    -- ad hoc constraint as its antidote — a "same app" rule would also reject
    -- legitimate cross-app conditions, since the credentials come from
    -- `supervisor`. The counters travel with the card and the retriever filters
    -- at read time on a parameter that is reported with its sensitivity rather
    -- than chosen here (K-85).
    discriminating_count INTEGER,
    own_app_condition    INTEGER,

    min_support       INTEGER NOT NULL,
    compiler_commit   TEXT    NOT NULL,

    UNIQUE (index_id, app, api, http_method, argument_shape, status_code),
    CHECK (support >= 1),
    CHECK (failure_count >= 1),
    CHECK (condition IS NULL OR condition <> ''),
    CHECK (discriminator IS NULL OR discriminator IN ('condition', 'argument_shape')),
    CHECK (no_known_success IN (0, 1)),
    CHECK (own_app_condition IS NULL OR own_app_condition IN (0, 1)),
    CHECK (discriminating_count IS NULL OR discriminating_count >= 1),
    -- Fail-closed: a pattern with no contrasting success has to say so, and one
    -- that has contrasting successes cannot claim otherwise.
    CHECK ((contrast_successes = 0) = (no_known_success = 1)),
    -- And the four condition columns are present exactly when a contrast
    -- existed. Written as four CHECKs rather than one so that a violation names
    -- which column drifted.
    CHECK ((no_known_success = 1) = (condition IS NULL)),
    CHECK ((no_known_success = 1) = (discriminator IS NULL)),
    CHECK ((no_known_success = 1) = (discriminating_count IS NULL)),
    CHECK ((no_known_success = 1) = (own_app_condition IS NULL))
);

CREATE INDEX idx_failures_index ON failure_patterns (index_id);
CREATE INDEX idx_failures_endpoint ON failure_patterns (app, api, http_method);
CREATE INDEX idx_failures_label ON failure_patterns (failure_label);

-- ---------------------------------------------------------------------------
-- Append-only (K-16)
-- ---------------------------------------------------------------------------
CREATE TRIGGER run_manifests_no_update BEFORE UPDATE ON run_manifests
BEGIN SELECT RAISE(ABORT, 'run_manifests is append-only'); END;
CREATE TRIGGER run_manifests_no_delete BEFORE DELETE ON run_manifests
BEGIN SELECT RAISE(ABORT, 'run_manifests is append-only'); END;

CREATE TRIGGER episodes_no_update BEFORE UPDATE ON episodes
BEGIN SELECT RAISE(ABORT, 'episodes is append-only'); END;
CREATE TRIGGER episodes_no_delete BEFORE DELETE ON episodes
BEGIN SELECT RAISE(ABORT, 'episodes is append-only'); END;

CREATE TRIGGER steps_no_update BEFORE UPDATE ON steps
BEGIN SELECT RAISE(ABORT, 'steps is append-only'); END;
CREATE TRIGGER steps_no_delete BEFORE DELETE ON steps
BEGIN SELECT RAISE(ABORT, 'steps is append-only'); END;

CREATE TRIGGER actions_no_update BEFORE UPDATE ON actions
BEGIN SELECT RAISE(ABORT, 'actions is append-only'); END;
CREATE TRIGGER actions_no_delete BEFORE DELETE ON actions
BEGIN SELECT RAISE(ABORT, 'actions is append-only'); END;

CREATE TRIGGER observations_no_update BEFORE UPDATE ON observations
BEGIN SELECT RAISE(ABORT, 'observations is append-only'); END;
CREATE TRIGGER observations_no_delete BEFORE DELETE ON observations
BEGIN SELECT RAISE(ABORT, 'observations is append-only'); END;

CREATE TRIGGER verifier_results_no_update BEFORE UPDATE ON verifier_results
BEGIN SELECT RAISE(ABORT, 'verifier_results is append-only'); END;
CREATE TRIGGER verifier_results_no_delete BEFORE DELETE ON verifier_results
BEGIN SELECT RAISE(ABORT, 'verifier_results is append-only'); END;

CREATE TRIGGER shield_violations_no_update BEFORE UPDATE ON shield_violations
BEGIN SELECT RAISE(ABORT, 'shield_violations is append-only'); END;
CREATE TRIGGER shield_violations_no_delete BEFORE DELETE ON shield_violations
BEGIN SELECT RAISE(ABORT, 'shield_violations is append-only'); END;

-- `skills` deliberately has **no** append-only trigger. K-16 protects the
-- record; the skill library is a derived projection of it and has to be
-- replaceable, because a change to the compiler must be able to rebuild it
-- (`03-architecture.md`). A library that could not be deleted would become a
-- second source of truth, which is exactly what the projection rule prevents.
-- What makes a rebuild auditable is not immutability but the provenance columns
-- on every row: gap, support, thresholds, compiler commit, write-set digest.

-- ---------------------------------------------------------------------------
-- The accumulation run's ledger: one row per block boundary
-- ---------------------------------------------------------------------------
-- It lived in `results/accumulation-ledger.json` and that file is inside the
-- checkout, which Colab re-clones every session; the record is symlinked to
-- Drive and survives. So the episodes were durable and the ledger was not, and
-- the stopping rule reads the ledger: across seven mining events it reported
-- "0 blocks closed" every time and branch A - two consecutive quiet blocks -
-- was never once evaluated (K-162).
--
-- Append-only like the rest of the record. The JSON stays, as a projection
-- rebuilt from these rows; the table is the source.
CREATE TABLE run_ledger (
    ledger_id             INTEGER PRIMARY KEY AUTOINCREMENT,

    prefix                TEXT    NOT NULL,
    block                 INTEGER NOT NULL,
    -- How many block boundaries this one mining stands for. More than one only
    -- when a restart found boundaries that had gone by unmined (K-156).
    blocks_covered        INTEGER NOT NULL DEFAULT 1,
    episodes_run_total    INTEGER NOT NULL,

    library_id            TEXT,
    skills                INTEGER NOT NULL,
    effect_suffixes       TEXT    NOT NULL,
    index_id              TEXT,
    cards                 INTEGER NOT NULL,
    distinct_tasks_passed INTEGER NOT NULL,

    new_skills            INTEGER NOT NULL,
    new_effect_suffixes   TEXT    NOT NULL,
    -- The branch that stopped the run, on the row where it fired. NULL on every
    -- other row: a run that has not stopped says so by having none.
    stopped               TEXT,

    wall_clock_utc        TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (prefix, block),
    CHECK (block >= 1),
    CHECK (blocks_covered >= 1),
    CHECK (skills >= 0),
    CHECK (cards >= 0),
    CHECK (new_skills >= 0)
);

CREATE INDEX idx_run_ledger_prefix ON run_ledger (prefix, block);

-- ---------------------------------------------------------------------------
-- The experiment: slices, and what each experiment episode belongs to
-- ---------------------------------------------------------------------------
-- A slice is the next N tasks of the declared order, opened by one session of
-- the driver. Its task list is written when it opens, before any episode, so a
-- session that dies part-way leaves the slice's membership in the record and the
-- next session completes it rather than starting a new one. In the record, not
-- in `results/`: Colab re-clones the checkout every session and the record is on
-- Drive (K-162).
--
-- Neither table carries an append-only trigger. The migration that adds a
-- missing table to an existing file splits the schema on `;`, and a trigger's
-- body carries one, so a trigger written here would exist in a fresh file and
-- not in the series the experiment writes to. Append-only rests on the writers,
-- as it does for `run_ledger`, and the difference is written down rather than
-- hidden (K-182).
CREATE TABLE experiment_slices (
    slice                INTEGER NOT NULL,
    -- The task's place in the declared order, from 1.
    position             INTEGER NOT NULL,
    task_id              TEXT    NOT NULL,
    -- The session that opened the slice, and the commit it opened on.
    session_id           TEXT    NOT NULL,
    opened_commit        TEXT    NOT NULL,
    wall_clock_utc       TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (slice, task_id),
    UNIQUE (task_id),
    UNIQUE (position),
    CHECK (slice >= 1),
    CHECK (position >= 1),
    CHECK (length(session_id) > 0),
    CHECK (length(opened_commit) > 0)
);

-- One row per experiment episode, written in the episode's own transaction.
CREATE TABLE experiment_episodes (
    episode_id           INTEGER PRIMARY KEY REFERENCES episodes(episode_id),
    slice                INTEGER NOT NULL,
    -- The driver session that ran the episode.
    session_id           TEXT    NOT NULL,
    -- Whether the slot carried the carded arm's card count (A.4, K-181). NULL
    -- for the baseline, which carries no slot; 0 marks a control that ran short,
    -- and every confirmatory analysis involving it leaves the task out.
    volume_matched       INTEGER,
    -- 1 when a measurement-defining path had changed since the experiment's first
    -- episode and the driver was told to go on anyway. The flag is the only way
    -- past that stop, so every episode it let through carries it.
    path_change_accepted INTEGER NOT NULL,

    CHECK (slice >= 1),
    CHECK (length(session_id) > 0),
    CHECK (volume_matched IS NULL OR volume_matched IN (0, 1)),
    CHECK (path_change_accepted IN (0, 1))
);

-- ---------------------------------------------------------------------------
-- View that reads a whole episode in order
-- ---------------------------------------------------------------------------
-- The acceptance criterion says "you can read a whole episode in order with a
-- single query". The view is that query.
CREATE VIEW episode_timeline AS
SELECT
    e.episode_id,
    e.task_id,
    e.condition,
    e.sequence_in_run,
    e.model_load_state,
    s.step_index,
    s.outcome_category,
    s.generated_code,
    a.action_index,
    a.app,
    a.api,
    a.http_method,
    a.result_status,
    a.error_class,
    o.truncated_bytes,
    o.was_truncated
FROM episodes e
JOIN steps s ON s.episode_id = e.episode_id
LEFT JOIN observations o ON o.step_id = s.step_id
LEFT JOIN actions a ON a.step_id = s.step_id
ORDER BY e.episode_id, s.step_index, a.action_index;
