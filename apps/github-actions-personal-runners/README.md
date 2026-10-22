# GitHub Actions runners for personal repositories

This app deploys repository-scoped [Actions Runner Controller (ARC)](https://docs.github.com/en/actions/how-tos/manage-runners/use-actions-runner-controller)
scale sets for private repositories owned by the `Shivppatel` personal account.
The `ShivWS` organization scale sets (`shivws-runners`, `shivws-docker-runners`)
cannot serve personal-account repositories, so each repository gets its own
scale set. Every scale set keeps `minRunners: 0`, so an idle repository costs
only a small listener pod (in the controller's `actions-runner-system`
namespace) and runner pods exist only while a job runs.

| Repository | `runs-on` (scale set) | Pod | Runners |
|---|---|---|---|
| `Shivppatel/sherlock` | `shivppatel-sherlock` | Docker-in-Docker (builds images with `docker buildx`) | 0-2 |
| `Shivppatel/tf` | `shivppatel-tf` | Hardened plain runner | 0-2 |
| `Shivppatel/k8s-private` | `shivppatel-k8s-private` | Hardened plain runner | 0-2 |
| `Shivppatel/helm` | `shivppatel-helm` | Hardened plain runner | 0-2 |

Use the scale set name as the label, for example `runs-on: shivppatel-tf`. The
`homelab` and `linux` labels (plus `docker` for Sherlock) also match, but each
repository has exactly one scale set, so the name is the unambiguous choice.

## Public repositories must not use these runners

Never add a scale set for a public repository, including `Shivppatel/k8s`. On a
public repository, a pull request from a fork can run its own workflow code on
a self-hosted runner, which would execute attacker-controlled code inside the
homelab. Public repositories use GitHub-hosted runners. Keep pull requests from
forks of private repositories disabled or approval-gated as well.

## GitHub and Vault setup

Create a fine-grained personal access token with:

- Resource owner: `Shivppatel`
- Repository access: only `sherlock`, `tf`, `k8s-private`, and `helm`
- Repository permission **Administration: Read and write** (required to
  register repository-level self-hosted runners; **Metadata: Read** is added
  automatically)
- An expiration date, tracked for rotation

Store it in Vault without committing it, entering the value on standard input
so it never appears in shell history or arguments:

```sh
vault kv put secret/github/actions-runner-personal token=-
```

```text
secret/data/github/actions-runner-personal
  token: <fine-grained-PAT>
```

The `github-actions-personal-runner-auth` `ExternalSecret` refreshes the value
hourly into a same-named Secret with the key `github_token`, which ARC reads.
Runner pods never mount it. The `external-secrets` Vault policy must allow this
path: `github/actions-runner-personal` is declared in `vault/locals.tf` of the
`tf` repository, and its Atlantis apply must complete before this app syncs.
Until the token exists, the `ExternalSecret` reports an error and the scale sets
stay unregistered; they register on their own once the value is present.

## Isolation and limits

All four scale sets share the `github-actions-personal-runners` namespace. The
plain pods are identical to `shivws-runners` (non-root, all capabilities
dropped, no service-account token). The Sherlock pod is identical to
`shivws-docker-runners`: privilege is limited to the Docker daemon sidecar.

- A default-deny network policy blocks ingress and all egress except DNS, the
  Kubernetes API endpoints in `values.yaml`, and public TCP 443. The pod,
  service, node, and link-local ranges are blocked, so jobs cannot reach other
  LAN services such as Vault, MinIO, or Atlantis.
- Public TCP 80 is additionally allowed only for the scale sets listed in
  `network.httpEgressScaleSets` (currently `shivppatel-sherlock`, matching
  `shivws-docker-runners`). The policy selects pods by the
  `actions.github.com/scale-set-name` label.
- A `ResourceQuota` caps the namespace at the sum of the four scale sets' maximum
  concurrency plus one Docker pod of headroom. Raise it together with any
  `maxRunners` change.
- Update the API addresses in `values.yaml` if the cluster's control-plane
  addresses change, as with the other ARC apps.

## Chart layout

`Chart.yaml` declares the vendored `gha-runner-scale-set` chart (same version as
the other ARC apps) once per repository using dependency aliases. The chart
derives every resource name from `runnerScaleSetName`, so the aliases coexist in
one release. `values.yaml` keeps one top-level block per alias and shares the
pod templates through YAML anchors under `shared` (a key Helm ignores).

To add a private repository, add a dependency alias in `Chart.yaml`, a matching
block in `values.yaml` that reuses `*runnerTemplate` or `*dockerRunnerTemplate`,
run `helm dependency update apps/github-actions-personal-runners`, add the new
repository to the token's repository list, and size the `ResourceQuota`.

## Validation and rollout

```sh
helm dependency build apps/github-actions-personal-runners
helm lint apps/github-actions-personal-runners
helm template apps/github-actions-personal-runners \
  --kube-version 1.29.0 \
  --api-versions actions.github.com/v1alpha1 \
  --api-versions external-secrets.io/v1
```

Argo CD creates the namespace and syncs this app (wave 1) after the ARC
controller (wave -1). Once the `ExternalSecret` is `SecretSynced`:

```sh
kubectl get autoscalingrunnerset -n github-actions-personal-runners
kubectl get pods -n actions-runner-system | grep shivppatel
```

Each scale set should have one listener pod. Dispatch a workflow using its
`runs-on` name; ARC creates a runner pod for the queued job and returns to zero
when it finishes.
