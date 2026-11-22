# Threat model

Turkish is the source: `04-threat-model.tr.md`.

This document writes down what the sandbox and the shield were built against.

## What we are protecting against

The code the agent produces is untrusted. Its source is a language model, it is
unverified, and it changes over the episode. The threat is not malice but
**unchecked action**: the model doing something irreversible without meaning to,
breaking the measurement, or leaking into the host side.

Three concrete threats:

1. **Leaking into the host side.** If the agent's code reaches the record, the
   compiler or the configuration, the measurement writes itself.
2. **Contamination between episodes.** If state left by one episode carries into
   the next, the episodes stop being independent and the paired design breaks.
3. **Irreversible side effects.** A call that changes the benchmark's state also
   changes the verifier's verdict.

## Sandbox

A rootless container. Read-only root. Policy at the network-namespace level: the
fixed app ports on loopback only. Limited in memory, processes, time and disk.
Pinned by an image version digest.

**It is born again every episode.** That is the real defence against the second
threat.

### As it was built

The network policy was applied to the letter: the container has **no network at
all** (`--network=none`) and its only channel is a unix socket mounted read-only.
The sentence "loopback only" is exactly true in this mode — the external network,
the host ports and the gateway name are all three unreachable, and it was
measured (WSL and the GitHub runner, `results/container-network.json`). The other
three modes — default netavark, `pasta`, `slirp4netns` — reach the external
network, so the configuration accepts no other value.

The **numbers for the limits are not yet frozen.** `config/sandbox.yaml` carries
starting points and the file says so explicitly. K-C asks for measurement rather
than a guess: peak RSS within an episode, peak process count, peak tmpfs usage.
The first real reading was taken — memory 161.7 MiB / 536.9 MiB, processes 4,
network I/O 0B — but from a single episode and with no model call. The limit
numbers will be written after the model run and will enter the manifest in that
form.

### Served mode opened a new attack surface

The first version of the threat model enumerated what the container could do
**outward**. While the sandbox was being built a third path appeared, and it
never leaves the container: AppWorld's API server serves, alongside the twelve
apps, **twenty-one management routes** at the root. `POST /dbs/save` writes a
database to the path it is given and the writing process is the server on the
host side; `POST /seed`, `POST /date_time` and `POST /activate/task/{id}` break
the measurement directly. Code inside the container can reach these routes over
the same channel as `apis.*`, and the read-only root and network isolation do not
stop it because the writing process is not inside the container.

The address the servers bind to is not ours either:
`uvicorn.run(host="0.0.0.0")` is embedded inside AppWorld and has no flag.

**What closes it is the proxy.** It is the container's only path to the API
server, and it filters the management routes by looking at the body fields.
Cutting all of them is impossible (S-50): the environment server itself makes
eleven management calls. Where the escape route stops is the exact-match
requirement on the `to_db_home_path` field.

**This layer is separate from the shield.** The shield gives task-scoped
permission — which app may be written to. The proxy's whitelist determines which
routes exist at all. Conflating the two would add the shield's measured cost to
this filter's cost.

### The inside of the container is not safe, and is not meant to be

The environment server executes the agent's code in the same process, so the
agent can do everything that process can do (S-51). This is a direct consequence
of K-B: if the full package is to be in the container, the thing executing the
code is that package too. What is protected is the host — the record database,
the verifier and the API server's management surface are outside, and every
change made to the world has to pass through the proxy.

## Shield

A predicate that filters an action before it executes, open in all five
conditions.

**The timing of the check depends on the kind of argument.** Calls with static
arguments are checked before the skill starts; those with dynamic arguments
immediately before their own execution, because their values are known only at
that moment.

**Atomicity is a property at the model-call level only, not at the level of the
check.** A skill is invoked atomically but every call inside it is checked
separately.

### The read/write predicate

The predicate rests on the `method` field in the API documentation. The field
covers a hundred percent of the 473 APIs.

Its assumption — that no GET endpoint changes state — was tested and came out
false. A static scan showed that fifteen GET endpoints contain a write call. The
detail and the three systematic groups are in `08-decisions.tr.md` K-41.

**The write set is `static ∪ empirical`.** The blind spots of the two sources lie
in different places: a live count cannot see an update, and a static scan cannot
see calls delegated to a helper function.

### Shield violations do not go straight into the failure index

To enter the index, the same pattern has to have ended in failure in a situation
the shield did not block as well. The shield signal produces no record on its
own; it only strengthens one. The rationale is in `07-failure-taxonomy.en.md`.

## A rejected defence: punishment

Teaching against harmful action by punishment was rejected.

Two reasons. A system able to detect an action well enough to punish it detects
it well enough to block it; in that case punishing is unnecessary when blocking
is available. And if punishment mixes into the reward signal, the agent learns
not to avoid harm but **to avoid detection**.

## Where this document stays silent

The concrete configuration of the sandbox image, the numeric values of the
resource limits and the frozen form of the shield's exception list are not here.
The sandbox layer is not built yet; when it is, this document will be completed
with those numbers.
