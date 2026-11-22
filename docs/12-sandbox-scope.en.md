# Sandbox scope (roadmap item 8)

Turkish is the source: `12-sandbox-scope.tr.md`.

The first version of this document was written before any code and awaited
approval. Four decisions were made (K-A…K-D), the mandatory second change was
approved, and the five questions the planning measurements raised have now been
decided too (K-92…K-97). Coding starts with this version.

The numbers live in one place each, across three files:
`results/sandbox-onolcum.json` (planning measurements),
`results/wire-identity.json` (the wire-identity verification),
`results/container-network.json` (network modes, both platforms). The tables here
cite those files; the decisive figures also appear in the prose for readability.

**The most consequential finding of this version is not a convenience, it is a
threat.** Moving to served mode opens a twenty-one-route management surface on
the host, the container can reach that surface, and one of its routes makes the
host write a file to any path it is given. Details in §6.4. The first version of
this document did not see it.

---

## 1. Status

| Decision | State |
|---|---|
| K-A — where the recording happens | **Closed:** a recording proxy on loopback (option 3), with three conditions |
| K-B — what is inside the container | **Closed:** the full `appworld` package (option 1) |
| K-C — the resource-limit numbers | **Closed:** not guessed, measured; headroom added; written to the manifest |
| K-D — the limits must not bind | **Closed:** and it will be shown; if the share of episodes ending at a limit is not near zero, the result is a lower bound |
| Mandatory second change | **Closed:** AppWorld moves to served mode |
| Can the container tests run in CI | **Measured:** yes, §9 |
| Network policy | **Closed:** `--network=none` plus a read-only unix socket, measured on both platforms (§10, K-95) |
| Five questions | **Closed:** §11, decisions K-92…K-97 |

---

## 2. What is locked

The threat model (`04-threat-model.tr.md`) and the architecture
(`03-architecture.tr.md`) already define the sandbox. This document builds on them
rather than replacing them.

| Requirement | Source |
|---|---|
| Rootless container (rootless podman) | threat model, K-01 rationale 1 |
| Read-only root | threat model |
| Policy at the network-namespace level: loopback only, fixed app ports | threat model |
| Memory, processes, time and disk bounded | threat model |
| Image pinned by a version stamp | threat model |
| **Reborn every episode** | threat model; the real defence against the second threat |

None of the three threats changes: escape to the host, cross-episode
contamination, irreversible side effect.

---

## 3. What happens today

The code the agent produces runs **in our own Python process**. AppWorld executes
it in an embedded IPython shell through `InteractiveShellEmbed`, and that shell
has full access to the host filesystem, the record database, the configuration
and the network.

So there is currently **no defence at all** against the first threat. That is not
an oversight but scheduled work: the sandbox layer was never built.

AppWorld also serves the APIs **in process**: `fastapi.testclient.TestClient`, so
there is no real socket and no port. Measured.

**podman is not installed** locally. The Ubuntu noble repository offers 4.9.3.
The prerequisites for a rootless run are in place: cgroup v2, delegated
controllers `cpu memory pids`, `subuid/subgid` defined, systemd on. Installing it
is item 8's first job.

---

## 4. The mandatory second change was measured

The `appworld serve apis --port` command exists and `AppWorld(remote_apis_url=...)`
is supported. A container cannot reach an in-process ASGI client, so this change
is mandatory.

The switch goes through **configuration**: the `appworld_config` dict reaches the
reference agent's `AppWorld.initializer(update_defaults=True, **appworld_config)`
call. `remote_apis_url` and `remote_environment_url` are set there, so the
scaffold is untouched (K-19).

### 4.1 Served mode does not change the text the agent sees

The same six code blocks were run in three modes: in-process `TestClient`, a
remote API server, and a remote environment server plus a remote API server. The
blocks were deliberately mixed: reading documentation, reading private data, a
successful login, a 401 with a wrong token, a missing resource.

| Mode | Digest of `world.execute`'s output | `api_calls.jsonl` | `environment_io.md` |
|---|---|---|---|
| In-process `TestClient` | `52de8119baea903e` | 424 bytes | 4302 bytes |
| Remote API | `52de8119baea903e` | 424 bytes | 4302 bytes |
| Remote environment + remote API | `52de8119baea903e` | 424 bytes | 4302 bytes |

All three identical. So what the first version of this document wrote as "it does
not change the meaning, it changes the latency" is no longer a guess but a
measurement. The measurement covers six blocks, not the whole API surface.

### 4.2 Three things break in served mode

**4.2.1 State measurement quietly starts lying.** When `remote_apis_url` or
`remote_environment_url` is given, AppWorld does not build the in-process model
collection: `world.models is None`. `state_probe.snapshot` then returns `{}` and
`diff({}, {})` returns `{}` — an empty dict, not `None`. In this repository's
contract an empty dict means **"measured, no change"** and `None` means "not
measured". So if `probe_state` stays on, `steps.state_change` claims a
measurement was taken at every step while none was.

The criterion's weight in the record was measured separately, because "we are
losing it" and "we are losing something that matters" are not the same claim:

| Measured | Count |
|---|---|
| Total steps in the record | 4102 |
| Steps with state not measured (`NULL`) | 0 |
| Measured, unchanged | 4074 |
| State changed | 28 |
| **Steps spared from being counted stagnant by the state criterion alone** | **0** |

So over 4102 steps the state criterion never once changed the stopping rule's
decision. The danger is not in the rule, it is in the record lying. So the probe
was not turned off but moved onto HTTP (K-93, §11.2).

**4.2.2 There is no host-side `Requester` left to wrap.** In remote-environment
mode the host's `AppWorld` object has no `requester` attribute at all
(`hasattr(world, "requester")` is false) and `shell` is `None`. `ApiCapture`
today wraps the methods of the `Requester` class; the class to wrap is now inside
the container. This is the measured form of K-A's rationale.

**4.2.3 Who writes the logs.** `environment_io.md` and `api_calls.jsonl` are
written by the environment server's own `save_logs` call; once the environment
server moves into the container, those two files are written inside it. The
output databases are different: the host-side API server writes them
(`POST /dbs/save`), and the verifier already reads those databases host-side
through `evaluate_dataset`. So **the verdict does not move into the container**;
what moves is two log files, and those two are taken out with `podman cp` after
the episode ends (K-94, §11.3).

### 4.3 Latency

| Measurement | Value |
|---|---|
| Loopback API round trip (n=30, curl process start included) | median 3.54 ms (3.19 – 15.80) |
| Per step, kernel clock, in-process | median 0 ms |
| Per step, kernel clock, remote API | median 10 ms |
| Per step, kernel clock, remote environment + remote API | median 10 ms |
| Typical step duration in the record | ≈ 2.2 s |

The kernel clock is read from `/proc/uptime` and its resolution is 10 ms; the 0
and the 10 in that table may be two roundings of the same quantity. The honest
statement: the added cost is a few thousandths of a step. The proxy adds a second
hop, roughly doubling that figure and leaving it in the same order.

A side finding: in in-process and remote-API mode freezegun freezes the host
process's clock and `time.perf_counter` reads zero. In remote-environment mode
the host clock is not frozen. The repository already uses the kernel clock, so
the records are unaffected; but anything written host-side that reads the wall
clock will behave differently per mode.

### 4.4 Memory — K-C's first number

| Process | RSS |
|---|---|
| API server (all app databases in memory) | 745 MiB |
| Environment server (one world, six code blocks, `models=None`) | 185 MiB |

What goes into the container is the environment server, so the measured baseline
is **185 MiB**. A 512 MiB limit is possible with that baseline but not generous:
roughly 320 MiB of headroom, which erodes quickly once the agent's code starts
accumulating lists. That is exactly the measurement K-C asks for: measure peak
usage inside an episode, add headroom, write it to the manifest.

The API server's 745 MiB stays on the host and does not count against the
container's limit.

---

## 5. The four decisions and what each requires

### K-A — The recording happens in a proxy on loopback

The container connects to the proxy, the proxy forwards to the AppWorld server
and records both directions. The S-16 data (response body and status code) is
preserved, the record stays outside the container, and the shield's natural mount
point becomes the proxy.

Three conditions:

1. **A transparency test.** The same task is run directly and through the proxy;
   the trajectories must be identical. Reference in §7.
2. **The proxy enters `MEASUREMENT_DEFINING_PATHS`.** It is a measurement-defining
   path, because the record itself passes through it. The list was narrowed in
   K-76 and the narrowing found the list's own gap; this addition is of the same
   class.
3. **The proxy's version goes into the manifest.** As the shield's does: if
   something changed, it must be readable from the record.

### K-B — The full `appworld` package in the container

A thin RPC client would silently change the interface the agent sees; K-19's
requirement is that the same messages go out and the same text comes back. The
package is 5.9 MiB, so most of the image is not the package but its dependencies
(`site-packages` is 316 MiB).

The `data/` directory is 198 MiB and the part the container needs is the task
directory (64 KiB) plus the task data. Whether it is given as a read-only mount
or baked into the image is under question 5.

### K-C — The resource limits will be measured

The gap the threat model left will be filled with numbers. The first number is in
§4.4: the environment server's baseline is 185 MiB. The rest will be measured
while episodes run: peak RSS, peak process count, tmpfs usage, step duration.
Once measured, each limit is written as "measured peak + headroom" and goes into
the manifest.

The table from the first version is now **not a proposal but a starting point to
be tested**:

| Limit | Starting point | To be measured |
|---|---|---|
| Memory | 512 MiB | Peak RSS within an episode |
| Processes (pids) | 128 | Peak process count |
| Time | 60 s per step | Step-duration distribution |
| Disk (tmpfs) | 64 MiB | Peak tmpfs usage |
| CPU | 1 core | Effect on step duration |

### K-D — The limits must not bind, and that will be shown

The indicator: the share of episodes that end by hitting a limit. If it is not
near zero the limit is loosened and the result is marked as a lower bound. Same
class as K-60: if a limit binds, the sandbox rather than the model decides the
result.

For this to reach the record, sandbox-caused termination reasons have to be
added; today's three are `step_ceiling`, `no_progress`, `agent_finished`.

---

## 6. The proxy will see traffic today's wrapper never sees

The shield's predicate was written as a pure function and must not change when
the mount point moves. The measurements show that the move changes the traffic in
four places: two harmless, one that touches the record, one that is a threat.

### 6.1 `access_token` is already absent from the record — harmless

The proxy sees the `Authorization: Bearer` header separately from the body, so
the parameters read off the body carry no token. One might expect the record to
change because of this. Measured: **0 of 5261 actions** carry `access_token`. The
reason is `Requester.prepare()`: it `pop`s the token from the **very dict** our
wrapper is holding, and the wrapper takes its record after the call returns. So
the move to the header already happened in today's record. On this axis, what the
proxy sees agrees with what is recorded today.

### 6.2 No call is produced off the wire — harmless

`Requester` produces a response without ever going to HTTP in three cases: an
invalid URL (404), a non-dict body (400), a non-ASCII token (400). The proxy
cannot see those. Measured: the status codes in the record are only 200 (4489),
401 (503), 422 (235) and 409 (34). There is no 400, 404 or 405 at all, and the
`Exception` count is 772 = 503+235+34. So across 115 episodes **all 5261 actions
reached the server**; this class never fired. If it does fire,
`RecordingAgent`'s count comparison writes it as a divergence, so it will not
pass silently.

### 6.3 GET parameter types are lost on the wire — this touches the record

`Requester._get` sends the body as a query string
(`requests.get(url, params=data)`). A query string carries no types:
`page_index=0` is text on the wire. Today's record carries types, and the
identity the stopping rule sees is the JSON of that dict.

| Measured | Count |
|---|---|
| Total actions | 5261 |
| GET actions | 4242 |
| **GET actions carrying a non-string value** | **1090 (25.7% of GETs)** |
| Value types | str 4316, int 1417, bool 172, list 26, float 22, None 3 |

If the proxy builds the dict from the query string with string values, the
identity of 1090 actions changes. The stopping rule compares identities within an
episode, so its behaviour is largely preserved — but **comparability with the 115
episodes recorded so far breaks**: the bodies the compiler mined, the failure
index's `argument_shape` field and the stopping rule's calibration all came from
a typed identity.

So the type is derived from the route's own signature, and the decision was
verified across all 5261 actions: 5261/5261 match with the signature, while 1090
fail to match in the signature-free control arm (K-92, §11.1).

### 6.4 Served mode opens a management surface on the host — a threat

`appworld serve apis` mounts the twelve apps under `/{app}`, but it also has its
own management routes at the root. Counted: **21 routes**. The ones that can
corrupt the measurement:

| Route | What it does |
|---|---|
| `POST /dbs/save` | **Writes databases to the path it is given.** The writing process is the host-side API server. |
| `POST /dbs` | Changes the database paths |
| `POST /seed` | Changes the random seed |
| `POST /date_time`, `DELETE /date_time` | Changes the world's clock |
| `POST /activate/task/{task_id}` | Changes the active task |
| `POST /activate/supervisor/{id}` | Changes the active supervisor |

Three things together make this a threat:

1. These routes **never appear in today's record**, because AppWorld calls them
   with plain `requests.post` rather than through `Requester`
   (`appworld/apps/lib/apis/local_remote.py`). So there is a class of traffic our
   wrapper has never seen, and the proxy will see it.
2. Code inside the container can reach these routes through the same channel it
   reaches `apis.*`. With `POST /dbs/save` it can make the host-side server write
   to any path. A read-only root and network isolation do not stop that, because
   the writing process is not inside the container.
3. The servers bind with `host="0.0.0.0"` and this is **not configurable**: it is
   embedded in `appworld/serve/apis.py:31` and
   `appworld/serve/environment.py:301`, with no flag. So the API server listens
   on every interface. S-47's question applies here too, and this time the answer
   is the opposite: this value is not ours, it is the reference's embedded
   behaviour.

**Consequence:** K-A option 3 turns out to be needed not only to protect the
record but to close the threat model's first threat. The proxy has to be the
container's only route to the API server, and it must structurally refuse the
management routes. This is not a shield decision: the reference agent cannot
reach those routes through `apis.*`, so cutting them cannot change a legitimate
trajectory. Even so, "cannot" is a claim and its test is the seventh test in §8
(K-95, §11.4).

### 6.5 The proxy must record the request path, not the raw URL

`split_endpoint` expects a relative path: `/venmo/x` → `venmo`, `x`. Given an
absolute URL, `http://127.0.0.1:8123/venmo/x` yields the app name `http:` and
endpoint resolution silently collapses. S-32 was a fault of exactly that class.
If the proxy records the request path, today's parser works unchanged.

---

## 7. The transparency test's reference

The trajectory-digest instrument already exists:
`scripts/check_determinism.py`, `sha256(logs/environment_io.md)[:16]`. Everything
the agent saw is in that file, so the thing being compared is the right thing.

The question of which demo episode to use split in two once it met the
measurements.

| Candidate | Calls | Why it is enough / not enough |
|---|---|---|
| `0a9d82a_1` (demo, both arms identical) | 0 | Zero calls exercise the proxy not at all |
| `1150ed6_2` (demo, both arms identical) | 2 | Exercises it, with two calls |
| `0de03ea_1` card arm (demo, richest in calls) | 11 | The two arms did not produce identical trajectories, so repeat stability was not measured for this task |
| `6104387_1` (determinism measurement) | 20 | 6 repetitions, 1 distinct trajectory; 20 calls, all 200 |
| `2a163ab_1` (determinism measurement) | ≈19/run | 6 repetitions, 1 distinct trajectory; includes failing steps |

Two different things are being conflated: the demo's `identical_trajectory` field
says the **card arm and the baseline arm** came out the same; it says nothing
about repeat stability. The tasks whose repeat stability was measured are the ones
in the determinism measurement, and they give a single trajectory over six
repetitions. The transparency test rests on repeat stability, so the reference is
`6104387_1` (K-96, §11.5).

There is also the question of what "directly" means. To isolate the proxy,
"directly" = served mode without the proxy. Going from in-process to served mode
is a separate comparison, and §4.1 measured it with six blocks. So three arms:
in-process, served mode, served mode plus proxy. Merging two of them into one
test would make any difference unattributable.

---

## 8. Security tests

The reviewer's Section D questions, turned into tests:

| Question | Test | Passing criterion |
|---|---|---|
| Why is the host at risk | Attempts from the container to reach the host filesystem, the record database and the configuration | All fail |
| Fork bomb | A process explosion like `:(){ :\|:& };:` | The pids limit engages, the host is unaffected, the episode ends cleanly |
| Filling the disk | A write loop trying to fill tmpfs | It stops at the tmpfs limit, the host disk is unaffected |
| Container root | Becoming root in the container and trying to project that onto the host | Thanks to the rootless mapping the host user stays unprivileged |
| Network escape | Attempts to connect beyond loopback, to the external network and to host services | Only the permitted app ports are reachable |
| Cross-episode contamination | Leaving a file in one episode and reading it in the next | Unreadable; the container is reborn every episode |

**The sandbox is not used until the tests pass.** And a test does not count until
it has been seen to fire: every test will first be shown to **succeed** in an
unprotected environment and then to fail in the protected one. A protection taken
on trust has proved misleading several times in this repository.

§6.4 adds a seventh test: an attempt at `POST /dbs/save` from inside the
container. In an unprotected environment it must write a file to the host; in the
protected one the proxy must cut it.

---

## 9. The container tests can run in CI — measured

The question was whether podman works inside GitHub Actions. If it did not, all
six tests would join the local-only list and S-49's "re-run on a clean install"
gap would grow. The measurement took two runs; the job is a temporary one that
fires on a push to its branch and is deleted once the answer is in.

| Measured | `ubuntu-24.04` runner |
|---|---|
| podman | **present**, 5.8.4, `/usr/local/bin/podman` |
| Rootless | `rootless=true`, `subuid runner:165536:65536` |
| cgroup | v2, delegated controllers `cpu memory pids` |
| Runtime / network backend | `crun` / `netavark` |
| Pulling and running an image | works; container start 0.09 – 0.13 s |

Five protections were seen **firing**:

| Protection | Evidence |
|---|---|
| Read-only root | `touch /kok-yazma-denemesi` → `Read-only file system` |
| Rootless mapping | `uid=0(root)` in the container, process owner `runner` on the host |
| pids limit | under `--pids-limit 32`: `sh: can't fork: Resource temporarily unavailable` |
| Memory limit | under `--memory 64m` a 256 MiB write is `Killed`, `dd` exits 137; the same write succeeded in the unlimited arm |
| tmpfs limit | `dd` exits 1 and the file stops at exactly 8388608 bytes |
| Cross-episode contamination | the second container could not find the first one's `/tmp/iz` |

**Answer: yes, the six security tests can run in CI.** They do not join the
local-only list and S-49's gap does not grow.

**In the first round three steps looked green and proved nothing.** They were
caught because K-49 requires asking separately:

- The memory test hit `/dev/shm`'s own 64 MiB default; 62.5 MiB was written and
  the limit was never touched. Fixed with `--shm-size=512m` and an unlimited
  control arm was added.
- The tmpfs test's exit code came from `tail`, not from `dd`.
- In the loopback test nothing was listening on the host, so "could not connect"
  was empty evidence. The second round opened a real listener on the host.

One version asymmetry remains: podman 4.9.3 locally (from apt), 5.8.4 on the
runner. But the network backend is **netavark** on both, and §10's measurement
gave the same answer on both platforms, so the asymmetry does not affect the
decision.

---

## 10. Network policy: `--network=none` plus a read-only unix socket

The threat model says "loopback only, fixed app ports". The requirement: the
container reaches **exactly one host port** — the proxy — and nothing else.

Four modes were measured on both platforms with the same script,
`scripts/setup/measure_container_network.py`. Numbers in
`results/container-network.json`.

| Mode | External network | Host port | Socket bridge | Both platforms |
|---|---|---|---|---|
| **A — `--network=none`** | **unreachable** (`Network unreachable`) | unreachable | **200** | same |
| B — default (netavark) | **reachable** (1.1.1.1 → 403) | unreachable | 200 | same |
| C — `slirp4netns:allow_host_loopback` | reachable; host **open** via 10.0.2.2 | open | 200 | `slirp4netns` absent on the runner (exit 127) |
| D — `pasta` | **reachable** | unreachable | 200 | same |

External reach is real in all three: the request to 1.1.1.1 returns **403**, so
it left the machine and got an answer. Not "could not connect". Only `none`
gives `Network unreachable`.

**Chosen: A, plus a read-only mounted unix socket.** A bridge inside the
container binds that socket to a local TCP port, because the reference's
`Requester` speaks through `requests` and `requests` only knows TCP. Under
`--network=none` the `lo` interface stays up, so that listener works.

There was one risk and it was measured: **a unix socket needs `connect` write
permission, and a read-only mount could have blocked it.** It does not. The
connection succeeded under an `ro` mount and the host returned 200 through the
bridge — on both platforms. So the "one channel" requirement and the "no writable
mount" rule do not conflict.

The bridge is written with the standard library: the image already carries Python
(K-B), so no new dependency.

---

## 11. The five answers

All five are decided. Two of them needed a measurement before they could be
answered, and both measurements carry the decision's own condition, so they are
here with their numbers.

### 11.1 The type comes from the route signature (K-92)

The conversion is not done by a table we wrote but by the server's own
`ModelField.validate`. The same technique as K-63, applied to a query parameter
instead of a path parameter.

The verification was free and it was done —
`scripts/setup/verify_wire_identity.py` puts all 5261 recorded actions through
the wire and rebuilds them:

| Arm | Matches the recorded identity |
|---|---|
| Type derived from the signature | **5261 / 5261** |
| Without looking at the signature (control arm) | 4171 / 5261 |

The 1090 actions that fail in the signature-free arm are exactly the number of
"GET actions carrying a non-string value" measured independently. Without the
control arm a full match would have proved nothing; K-49 is built into this
measurement.

The verification found a detail: the `page_limit` field is `int` but carries
`le=20`, and validation failed on the two calls where the agent wrote 50. What is
wanted is the type, not validity, so when the constraint fails the value is
converted straight to the declared type.

### 11.2 The state probe is not turned off, it moves onto HTTP (K-93)

The question was whether the state probe could be done by asking the environment
in served mode. It can, and four things were measured:

| Measured | Result |
|---|---|
| Granularity | `{"spotify": {"MusicPlayer": 1}}` — the same `app.Model` level as today's probe |
| Sensitivity | `set_volume` (a `PATCH` that changes no row count) **was seen**; today's probe cannot see it |
| Cost | **2.0–2.5 ms** per call, against a step of ~2.2 s |
| Effect on the episode | the pass/fail test sets of a probed and an unprobed run are **identical** |

The fourth was a mandatory check: if the probe consumed the change record, the
`model_hashes.json` written at close would be incomplete and the verifier's
`models.changed_model_names()` test would fail wrongly.

So the stopping rule **stays two-criterion**. The number that grounds the
equivalence of the turn-it-off option is recorded too: over 4102 steps the state
criterion never once changed the rule's decision, so turning it off would not
have changed the rule's behaviour on this record either. Moving it was chosen
because the cost is a thousandth and what it buys is `PATCH` sensitivity.

The difference in semantics goes into a **new column**: `steps.state_change`
carries a signed row-count difference, the hash-based probe carries "which model
changed". Putting two meanings in one column is the very silent lie this
repository tries to avoid.

### 11.3 The logs are taken with `podman cp` (K-94)

No writable mount. The container filesystem stays read-only for the whole run;
the two log files are copied out after the episode ends. Mounting
`experiments/outputs` writable is precisely the first threat's surface: that
directory also carries the databases the verifier reads.

### 11.4 Network: one channel, and the management routes are cut structurally (K-95)

`--network=none` plus a read-only mounted unix socket. The measurement is in §10,
identical on both platforms. The twenty-one management routes are cut at the proxy
with a fixed allow-list.

The allow-list is a layer apart from the shield's predicate: **the shield grants
task-scoped permission** (which app may be written to), **the allow-list decides
which routes exist**. Conflating them would add the shield's measured cost to this
filter's cost and make both unreadable.

### 11.5 The transparency test has three arms, reference `6104387_1` (K-96)

Three arms: in-process, served mode without the proxy, served mode with the
proxy. The mode change and the proxy do not get mixed into one test.

The reference comes from the determinism measurement rather than the demo: the
demo's two identical-trajectory episodes carry 0 and 2 calls and would not
discriminate anything. `6104387_1` gives a single trajectory over six repetitions
and carries 20 calls, all 200.

The `data/` directory is **mounted read-only** into the container. Baking it in
would let the image stamp cover the data too, but it would duplicate the data in
a second place; mounting keeps a single source, and the data version is written to
the manifest from `data/version.txt` alongside `appworld_version`.

### 11.6 The security tests are a fifth CI check (K-97)

They do not go inside the existing "Testler" job. "Four CI checks" was a
descriptive record, not a constraint to preserve: podman tests lengthen the test
job and blur which layer a failure came from.

---

## 12. Out of scope

- **The shield's enforce mode.** There is no mode other than shadow (K-71) and
  the shape of the substitute response is undecided. §6.4's structural filter is
  a separate thing: not the shield's predicate but the proxy's route allow-list.
- **Parallel episodes.** The sandbox makes parallelism easier, but parallelism
  changes the measurement in a local run (the K-12 correction). Separate work.
- **Windows.** The sandbox was a Linux decision (K-01). It runs inside WSL.
- **A measurement run.** This item produces no measurement; the only numbers it
  produces are the sandbox's own cost.

---

## 13. Deliverables

1. `Containerfile` — a version-stamped image with the `appworld` package pinned,
   carrying the socket bridge.
2. `src/zihin/sandbox.py` — the container lifecycle: create per episode, run
   code, take the logs out with `podman cp`, tear down. Limits from configuration.
3. `src/zihin/kayit_vekili.py` — the proxy on a unix socket: records both
   directions, derives the type from the route signature, calls the shield, cuts
   the management routes with an allow-list. Enters
   `MEASUREMENT_DEFINING_PATHS`.
4. `config/sandbox.yaml` — resource limits, image stamp, socket path, network
   mode. Every value that affects the measurement lives here, not in the
   environment.
5. Sandbox fields in the manifest: image stamp, limits, sandbox version, proxy
   version, serving mode, network mode.
6. A hash-based state column in the record schema (K-93) — beside
   `state_change`, not inside it.
7. `tests/test_sandbox_security.py` — the six tests in §8 plus the
   `POST /dbs/save` test, each shown to fire in an unprotected environment.
8. The transparency test — three arms, reference `6104387_1`.
9. A fifth check in CI: the sandbox job (K-97).
10. An update to `docs/04-threat-model.tr.md`: the numbers, the frozen configuration,
    and §6.4's new attack surface.
11. `docs/09-limitations.tr.md` — whatever could not be measured or closed.

---

## 14. The measurement that still waits on coding

The five questions are closed, but the numbers K-C asks for cannot be taken until
the code exists: peak RSS within an episode, peak process count, peak tmpfs usage
and step duration can only be measured from an episode running with the container
up. That is why the table in §5 still says "starting point" and not "limit". The
limit numbers will be written after that measurement and will enter the manifest
in that form; K-D's binding indicator comes from the same run.
