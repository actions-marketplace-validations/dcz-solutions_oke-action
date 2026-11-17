import runpy
import subprocess

import pytest

import oke


@pytest.fixture
def environment(monkeypatch, tmp_path):
    monkeypatch.setenv("INPUT_CLUSTER", "ocid1.cluster.example")
    monkeypatch.setenv("INPUT_PRIVATE_ENDPOINT", "false")
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))
    monkeypatch.setenv("GITHUB_ENV", str(tmp_path / "github_env"))
    return tmp_path


@pytest.mark.parametrize(
    "private,endpoint", [("false", "PUBLIC_ENDPOINT"), ("TRUE", "PRIVATE_ENDPOINT")]
)
def test_configures_endpoint(environment, monkeypatch, private, endpoint):
    monkeypatch.setenv("INPUT_PRIVATE_ENDPOINT", private)
    calls = []
    monkeypatch.setattr(oke.tempfile, "mkdtemp", lambda **kwargs: str(environment))
    monkeypatch.setattr(
        oke.subprocess, "run", lambda args, **kwargs: calls.append((args, kwargs))
    )
    oke.main()
    assert calls == [
        (
            [
                "oci",
                "ce",
                "cluster",
                "create-kubeconfig",
                "--cluster-id",
                "ocid1.cluster.example",
                "--file",
                str(environment / "config"),
                "--token-version",
                "2.0.0",
                "--kube-endpoint",
                endpoint,
            ],
            {"check": True},
        )
    ]
    assert (
        environment / "github_env"
    ).read_text() == f"KUBECONFIG={environment / 'config'}\n"


@pytest.mark.parametrize(
    "key,value", [("INPUT_CLUSTER", "  "), ("INPUT_PRIVATE_ENDPOINT", "yes")]
)
def test_rejects_invalid_inputs(environment, monkeypatch, key, value):
    monkeypatch.setenv(key, value)
    with pytest.raises(ValueError):
        oke.main()
    assert not (environment / "github_env").exists()


def test_oci_failure_does_not_export_kubeconfig(environment, monkeypatch):
    def fail(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "oci")

    monkeypatch.setattr(oke.subprocess, "run", fail)
    with pytest.raises(subprocess.CalledProcessError):
        oke.main()
    assert not (environment / "github_env").exists()


def test_entrypoint_reports_failure(environment, monkeypatch, capsys):
    monkeypatch.setenv("INPUT_CLUSTER", "")
    with pytest.raises(SystemExit) as error:
        runpy.run_module("oke", run_name="__main__")
    assert error.value.code == 1
    assert "cluster must not be empty" in capsys.readouterr().err
