import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    cluster = os.environ["INPUT_CLUSTER"].strip()
    private = os.environ["INPUT_PRIVATE_ENDPOINT"].lower()
    if not cluster:
        raise ValueError("cluster must not be empty")
    if private not in ("true", "false"):
        raise ValueError("enablePrivateEndpoint must be true or false")

    kubeconfig = (
        Path(tempfile.mkdtemp(prefix="oke-", dir=os.environ["RUNNER_TEMP"])) / "config"
    )
    subprocess.run(
        [
            "oci",
            "ce",
            "cluster",
            "create-kubeconfig",
            "--cluster-id",
            cluster,
            "--file",
            str(kubeconfig),
            "--token-version",
            "2.0.0",
            "--kube-endpoint",
            "PRIVATE_ENDPOINT" if private == "true" else "PUBLIC_ENDPOINT",
        ],
        check=True,
    )
    with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as github_env:
        print(f"KUBECONFIG={kubeconfig}", file=github_env)


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"OKE configuration failed: {error}", file=sys.stderr)
        sys.exit(1)
