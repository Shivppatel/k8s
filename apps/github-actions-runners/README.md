# GitHub Actions runners

This app deploys an [Actions Runner Controller (ARC)](https://docs.github.com/en/actions/how-tos/manage-runners/use-actions-runner-controller) scale set for the `ShivWS` organization. It keeps one warm runner available and creates up to five short-lived, unprivileged runner pods for trusted jobs from organization repositories allowed to use the `Default` runner group.

The ARC controller is installed separately in the `actions-runner-system` namespace. This scale set, its listener, and each ephemeral runner are installed in `github-actions-runners`, keeping execution workloads away from the controller.

## GitHub and Vault setup

Create a fine-grained personal access token whose resource owner is the `ShivWS` organization. Grant the organization permissions **Administration: Read-only** and **Self-hosted runners: Read and write**. Store the token in Vault without committing it:

```text
secret/data/github/actions-runner
  token: <fine-grained-PAT>
```

The `github-actions-runner-auth` `ExternalSecret` refreshes that value every hour into a same-named Kubernetes Secret. ARC reads the `github_token` key; runner pods never receive this credential.

Use `runs-on: shivws-runners` (or the `homelab` and `linux` scale-set labels) in trusted organization workflows. Configure the `Default` runner group to allow only the private repositories that should use the homelab. Pull requests from forks should remain on GitHub-hosted runners because they execute untrusted code.

The runner namespace has a default-deny network policy. It permits DNS, the Kubernetes API endpoints listed in `values.yaml`, and outbound HTTPS while blocking the pod, service, node, and link-local address ranges used by the homelab. The listed API addresses match the current `10.96.0.1` service and `192.168.20.9`–`192.168.20.12` control-plane endpoints; update both ARC charts if those addresses change. Docker-in-Docker is intentionally disabled here; use the separate `shivws-docker-runners` scale set for trusted jobs that need container actions or image builds.

## Validation and rollout

```sh
helm dependency build apps/actions-runner-controller
helm lint apps/actions-runner-controller
helm template apps/actions-runner-controller --api-versions monitoring.coreos.com/v1

helm dependency build apps/github-actions-runners
helm lint apps/github-actions-runners
helm template apps/github-actions-runners \
  --api-versions actions.github.com/v1alpha1 \
  --api-versions external-secrets.io/v1
```

Argo CD syncs `actions-runner-controller` before `github-actions-runners`. After the ExternalSecret is `SecretSynced`, dispatch a trusted workflow in an allowed `ShivWS` repository that uses `shivws-runners`; ARC should assign the warm runner or create an additional ephemeral runner pod and remove excess runners when jobs finish.
