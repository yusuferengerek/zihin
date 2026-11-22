"""Transparency test: does the transport layer change what the agent sees.

**One of K-A's three conditions.** The proxy is a new layer inside the
measurement path, and where it enters it must not change the text the agent sees.
What is compared is the digest of `logs/environment_io.md`: all of the text the
agent sees is in that file, and the digest definition is the same one
`scripts/check_determinism.py` uses.

**Three arms, and why three.** Two changes land at once: the transport moves from
in-process ASGI to real HTTP, and the proxy comes in between. Merged into a single
test, the resulting difference becomes unattributable (K-96).

    1. in-process    — today's state, `TestClient`
    2. served        — `appworld serve apis`, no proxy
    3. served+proxy  — container, bridge, recording proxy

**The code sequence does not come from the model.** It runs with no model call:
what is under test is the transport layer, not the model's decisions. The
sequence is deliberately mixed — reading documentation, private data, a
successful login, a 401 with a wrong token, a missing resource, a paged read —
because each one goes through a different encoding path (query string, form,
JSON).

Output: `results/transparency.json`.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("OPENAI_API_KEY", "unused-local-model")

from appworld import AppWorld  # noqa: E402
from appworld.common.path_store import path_store  # noqa: E402

from zihin.recording_proxy import PROXY_VERSION, policy_for_episode, proxy_for_episode  # noqa: E402
from zihin.sandbox import Sandbox, image_digest, load_sandbox_config  # noqa: E402

OUTPUT = "results/transparency.json"

# The reference: a task whose determinism has been measured and that carries
# calls. The demo's episodes that produce the same trajectory carry 0 and 2 calls
# and discriminate nothing; `6104387_1` gives a single trajectory over six
# repeats and carries 20 calls (K-96).
TASK = os.environ.get("ZIHIN_TASK_ID", "6104387_1")
SEED = 100
APIS_PORT = 8123

# A fixed sequence instead of the agent's code. **Its bytes are frozen.** The
# digest in `results/transparency.json` is a function of exactly this text;
# renaming a variable here would produce a different transcript and
# invalidate the recorded reference. `scripts/check_language.py` exempts
# these lines by name for that reason. Each line goes through a
# different encoding path.
CODE = [
    "print(apis.api_docs.show_app_descriptions())",
    "sifreler = apis.supervisor.show_account_passwords()\nprint(len(sifreler))",
    "print(apis.supervisor.show_profile()['email'])",
    (
        "hesap = [s for s in sifreler if s['account_name'] == 'spotify'][0]\n"
        "eposta = apis.supervisor.show_profile()['email']\n"
        "jeton = apis.spotify.login(username=eposta, password=hesap['password'])['access_token']\n"
        "print(jeton[:8])"
    ),
    "print(apis.spotify.show_playlist_library(access_token=jeton, page_index=0))",
    "print(apis.spotify.show_song_library(access_token='yanlis-jeton'))",
    "print(apis.spotify.show_song(song_id=999999))",
]


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def transcript_digest(experiment: str) -> tuple[str, int]:
    """The digest and size of `environment_io.md`. This is the text the agent
    sees."""
    path = os.path.join(
        path_store.experiment_outputs, experiment, "tasks", TASK, "logs", "environment_io.md"
    )
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    return digest(text), len(text)


def run_steps(world: AppWorld) -> list[dict]:
    steps = []
    for code in CODE:
        try:
            output = world.execute(code)
        except Exception as error:  # noqa: BLE001
            output = f"<<istisna>> {type(error).__name__}: {error}"
        steps.append({"code": code, "output_digest": digest(output), "length": len(output)})
    return steps


def arm_in_process() -> dict:
    experiment = "transparency-in-process"
    world = AppWorld(task_id=TASK, experiment_name=experiment, random_seed=SEED)
    steps = run_steps(world)
    world.save_logs()
    world.close()
    digest, boyut = transcript_digest(experiment)
    return {"steps": steps, "transcript_digest": digest, "transcript_bytes": boyut}


def arm_served() -> dict:
    experiment = "transparency-served"
    world = AppWorld(
        task_id=TASK,
        experiment_name=experiment,
        remote_apis_url=f"http://127.0.0.1:{APIS_PORT}",
        random_seed=SEED,
    )
    steps = run_steps(world)
    world.save_logs()
    world.close()
    digest, boyut = transcript_digest(experiment)
    return {"steps": steps, "transcript_digest": digest, "transcript_bytes": boyut}


def arm_served_with_proxy() -> dict:
    experiment = "seffaflik-vekilli"
    config = load_sandbox_config("config/sandbox.yaml")
    policy = policy_for_episode(experiment_name=experiment, task_id=TASK, random_seed=SEED)
    proxy = proxy_for_episode(
        socket_path=config.apis_socket,
        upstream_port=APIS_PORT,
        shield=None,
        policy=policy,
    )
    proxy.start()
    sandbox = Sandbox(config=config, name=f"zihin-seffaflik-{TASK}")
    sandbox.start()
    try:
        sandbox.wait_until_ready(timeout_seconds=300)
        world = AppWorld(
            task_id=TASK,
            experiment_name=experiment,
            remote_environment_url=sandbox.environment_url,
            remote_apis_url=f"http://127.0.0.1:{config.bridge_port}",
            remote_docker=True,
            random_seed=SEED,
        )
        steps = run_steps(world)
        world.save_logs()
        usage = sandbox.usage()
        world.close()
        # The log is inside the container; it is copied after the episode ends
        # (K-94).
        host_directory = os.path.join(
            path_store.experiment_outputs, experiment, "tasks", TASK, "logs"
        )
        copied = sandbox.copy_out(
            f"/zihin/experiments/outputs/{experiment}/tasks/{TASK}/logs",
            host_directory,
        )
        if not copied:
            raise SystemExit(
                "the logs could not be copied out of the container; the arm was not measured"
            )
        digest, boyut = transcript_digest(experiment)
        return {
            "steps": steps,
            "transcript_digest": digest,
            "transcript_bytes": boyut,
            "recorded_calls": [
                {
                    "method": c.method,
                    "url": c.url,
                    "status": c.status_code,
                    "parameters": c.data,
                }
                for c in proxy.capture.calls
            ],
            "refusals": [
                {"method": r.method, "path": r.path, "reason": r.reason} for r in proxy.refusals
            ],
            "total_requests": proxy.request_count,
            "image_digest": image_digest(config),
            "proxy_digest": policy.digest(),
            "proxy_version": PROXY_VERSION,
            "usage": usage,
            "exited_at_limit": sandbox.exited_at_limit(),
        }
    finally:
        sandbox.stop()
        proxy.stop()


def apis_server_running() -> bool:
    import urllib.error
    import urllib.request

    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{APIS_PORT}/dbs", timeout=5) as response:
            return response.status == 200
    except (urllib.error.URLError, OSError):
        return False


def main() -> None:
    if not apis_server_running():
        sys.exit(
            f"no API server on 127.0.0.1:{APIS_PORT}. "
            "Start it with: python -m appworld.cli serve apis --port 8123 --no-show-usage"
        )
    started = time.time()
    arms = {
        "1-surec-ici": arm_in_process(),
        "2-sunulan": arm_served(),
        "3-sunulan-vekilli": arm_served_with_proxy(),
    }
    digests = {name: arm["transcript_digest"] for name, arm in arms.items()}
    report = {
        "ne": "Tasima katmani ajanin gordugu metni degistiriyor mu",
        "gorev": TASK,
        "gorev_gerekcesi": (
            "a task whose determinism was measured (6 repeats, 1 trajectory) and that "
            "the demo episodes that produce the same trajectory carry 0 and 2 calls (K-96)"
        ),
        "olcut": (
            "sha256(logs/environment_io.md)[:16], the same definition check_determinism.py uses"
        ),
        "kollar": arms,
        "ozetler": digests,
        "ucu_de_ayni": len(set(digests.values())) == 1,
        "surec_ici_ile_sunulan_ayni": digests["1-surec-ici"] == digests["2-sunulan"],
        "sunulan_ile_vekilli_ayni": digests["2-sunulan"] == digests["3-sunulan-vekilli"],
        "sure_saniye": round(time.time() - started, 1),
    }
    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    for name, digest in digests.items():
        print(f"{name:22s} {digest}  ({arms[name]['transcript_bytes']} bytes)")
    print()
    print("in-process = served   :", report["surec_ici_ile_sunulan_ayni"])
    print("served     = proxied  :", report["sunulan_ile_vekilli_ayni"])
    print("all three identical   :", report["ucu_de_ayni"])
    proxied = arms["3-sunulan-vekilli"]
    print(f"calls recorded by proxy : {len(proxied['recorded_calls'])}")
    print(f"refused request         : {len(proxied['refusals'])}")
    print(f"container usage         : {json.dumps(proxied['usage'], ensure_ascii=False)[:200]}")
    print("written:", OUTPUT)

    # If there is a difference the exit status is non-zero: the transparency
    # condition is K-A's gate and must not pass silently.
    sys.exit(0 if report["ucu_de_ayni"] else 1)


if __name__ == "__main__":
    _ = subprocess
    main()
