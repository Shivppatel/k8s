# Docker-capable GitHub Actions runners

This app deploys the on-demand `shivws-docker-runners` ARC scale set for trusted
workflows in the `ShivWS` organization that need Docker, service containers, or
system packages. It creates no idle runner and allows at most two concurrent
runner pods.

Each pod has an Actions runner that starts as a non-root user plus a privileged
Docker-in-Docker sidecar. The runner permits `sudo` for trusted workflow steps
that install system dependencies. The pod has no Kubernetes API credential, runs in the separate
`github-actions-docker-runners` namespace, receives no GitHub token, and is
subject to a default-deny network policy and resource quota. The Docker daemon's
ephemeral storage is capped at 20 GiB. Privileged runners should only execute
trusted organization code; do not make this runner group available to public
repositories or pull requests from forks.

The same Vault PAT used by the default scale set is synced into this namespace:

```text
secret/data/github/actions-runner
  token: <fine-grained-PAT>
```

Use `runs-on: shivws-docker-runners` for jobs that need Docker or package
installation. Keep ordinary jobs on the hardened `shivws-runners` scale set.

## Validation and rollout

```sh
helm dependency build apps/github-actions-docker-runners
helm lint apps/github-actions-docker-runners
helm template apps/github-actions-docker-runners \
  --kube-version 1.29.0 \
  --api-versions actions.github.com/v1alpha1 \
  --api-versions external-secrets.io/v1
```

Argo CD creates the namespace and syncs this app after the ARC controller. Once
the ExternalSecret is `SecretSynced`, dispatch a trusted workflow using
`shivws-docker-runners`. ARC should create a runner pod for the queued job and
return the scale set to zero pods after the job finishes.
