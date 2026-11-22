"""The sandbox configuration schema and the fields that reach the manifest.

It needs no container: what is checked is reading the configuration and what it
refuses. The container itself is in `test_sandbox_security.py`.
"""

from __future__ import annotations

import pytest
import yaml

from zihin.sandbox import SandboxError, load_sandbox_config

PATH = "config/sandbox.yaml"


def test_the_shipped_configuration_loads():
    config = load_sandbox_config(PATH)
    assert config.image == "localhost/zihin-sandbox:v1"
    assert config.network_mode == "none"
    assert config.apis_socket.endswith("apis.sock")
    assert config.environment_socket.endswith("environment.sock")


def test_every_limit_reaches_the_manifest():
    """K-C wants the limits written to the manifest: when a limit binds it is the
    sandbox, not the model, that decides the result."""
    config = load_sandbox_config(PATH)
    fields = config.manifest_fields()
    assert fields["sandbox_memory_bytes"] == config.memory_bytes
    assert fields["sandbox_pids_limit"] == config.pids_limit
    assert fields["sandbox_tmpfs_bytes"] == config.tmpfs_bytes
    assert fields["sandbox_step_timeout_seconds"] == config.step_timeout_seconds
    assert fields["sandbox_cpus"] == config.cpus
    assert fields["sandbox_network_mode"] == config.network_mode
    assert fields["sandbox_image"] == config.image


def _yaz(tmp_path, **degisiklik):
    with open(PATH, encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    raw.update(degisiklik)
    target = tmp_path / "sandbox.yaml"
    target.write_text(yaml.safe_dump(raw), encoding="utf-8")
    return target


def test_a_network_mode_other_than_none_is_refused(tmp_path):
    """Measured: the default netavark, pasta and slirp4netns modes all three reach
    the outside network (K-95). An isolation that configuration can switch off is
    not an isolation."""
    for kip in ("bridge", "pasta", "slirp4netns", "host"):
        with pytest.raises(SandboxError, match="network_mode"):
            load_sandbox_config(_yaz(tmp_path, network_mode=kip))


def test_a_missing_field_is_refused(tmp_path):
    with open(PATH, encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    del raw["memory_bytes"]
    target = tmp_path / "missing.yaml"
    target.write_text(yaml.safe_dump(raw), encoding="utf-8")
    with pytest.raises(SandboxError, match="missing field"):
        load_sandbox_config(target)


def test_an_unrecognised_field_is_refused(tmp_path):
    with pytest.raises(SandboxError, match="unrecognised field"):
        load_sandbox_config(_yaz(tmp_path, new_field=1))


@pytest.mark.parametrize(
    "field", ["memory_bytes", "pids_limit", "step_timeout_seconds", "tmpfs_bytes"]
)
def test_a_non_positive_limit_is_refused(tmp_path, field):
    """A zero limit would look like "no limit"; to podman it is invalid."""
    with pytest.raises(SandboxError, match=field):
        load_sandbox_config(_yaz(tmp_path, **{field: 0}))


def test_a_wrongly_typed_field_is_refused(tmp_path):
    with pytest.raises(SandboxError, match="memory_bytes"):
        load_sandbox_config(_yaz(tmp_path, memory_bytes="512m"))


def test_an_integer_is_accepted_where_a_float_is_expected(tmp_path):
    """`cpus: 1` and `cpus: 1.0` say the same thing and YAML reads them
    differently."""
    config = load_sandbox_config(_yaz(tmp_path, cpus=2))
    assert config.cpus == 2.0
