# OKE action

Install kubectl and configure access to an Oracle Kubernetes Engine (OKE) cluster using the OCI CLI. The action installs the OCI CLI with uv and caches uv downloads.

## Usage

Set OCI CLI credentials globally or on the job. The user must have permission to access the cluster and create its kubeconfig.

```yaml
env:
  OCI_CLI_USER: ${{ secrets.OCI_CLI_USER }}
  OCI_CLI_TENANCY: ${{ secrets.OCI_CLI_TENANCY }}
  OCI_CLI_FINGERPRINT: ${{ secrets.OCI_CLI_FINGERPRINT }}
  OCI_CLI_KEY_CONTENT: ${{ secrets.OCI_CLI_KEY_CONTENT }}
  OCI_CLI_REGION: ${{ secrets.OCI_CLI_REGION }}

steps:
  - uses: dcz-solutions/oke-action@v1
    with:
      cluster: ${{ secrets.OKE_CLUSTER_OCID }}
  - run: kubectl get namespaces
```

`cluster` is required. Set `enablePrivateEndpoint: "true"` to use the private API endpoint; the runner must have network access to that endpoint. The default is `"false"`.

The action exports `KUBECONFIG` for subsequent steps and stores the generated configuration in the runner's temporary directory. It installs `kubectl` and OCI CLI 3.96.2. OCI CLI remains on `PATH` for later steps. Python 3 and Bash are required on the runner.

## Development

Run `uv run --locked ruff check .`, `uv run --locked ruff format --check .` and `uv run --locked pytest`. Test and release workflows follow ocir-action; release-please creates versions from conventional commits after tests pass on `main`.

## License

MIT. See [LICENSE](LICENSE).
