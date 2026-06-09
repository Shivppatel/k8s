# Repository Guidelines

## Project Structure & Module Organization

This repository is the GitOps source for a Kubernetes homelab. Workloads live under `apps/<app>/`. Most apps are Helm wrapper charts with `Chart.yaml`, `Chart.lock`, `values.yaml`, vendored `charts/`, and custom manifests in `templates/`. `apps/argocd/` bootstraps Argo CD; `apps/argocd-apps/` defines the app-of-apps inventory.

## Build, Test, and Development Commands

Run validation from the root.

```sh
helm dependency build apps/<app>
helm lint apps/<app>
helm template apps/<app> # use CI API versions for CRDs when needed
pre-commit run gitleaks --all-files
```

Use `helm dependency update apps/<app>` only when changing chart dependencies; commit `Chart.lock` and `charts/` updates. CI runs Helm lint/render checks for changed charts and relaxed YAML lint for changed non-template YAML files.

## Coding Style & Naming Conventions

Use two-space YAML indentation. Keep app names and manifest filenames lowercase kebab-case, for example `apps/kube-prometheus-stack/templates/grafana-ingress.yaml`. Prefer declarative Kubernetes resources and Helm values over scripts. Quote annotation values and Kubernetes string fields, especially Argo CD sync options and numeric-looking values.

## Documentation Rules

Update docs in the same PR as behavior changes. For app changes, document desired Git state, not temporary live-cluster drift. Include required Vault paths, `ExternalSecret` names, storage classes, ingress hostnames, and Argo CD sync-wave assumptions, but never secret values. Prefer short examples over broad explanations.

## Testing Guidelines

There are no unit tests; validation is manifest-focused. For Helm-backed apps, run dependency build, lint, and template rendering before opening a PR. For raw manifests, run YAML lint and consider `kubectl apply --dry-run=server -f <file>` when CRDs exist in the target cluster.

## Commit & Pull Request Guidelines

Recent human commits use Conventional Commit style, such as `feat(postgresql): ...` and `fix(postgresql): ...`. Renovate commits use `Update Helm release ...` or `Update all non-major Helm chart dependencies ...`. PRs should describe the affected app, intent, validation, and any secret, storage, CRD, or sync-order considerations.

## Definition of Done

A change is done when GitOps source is updated, generated Helm artifacts are committed when dependencies changed, docs are current, secrets remain externalized, and validation has run or the skip reason is stated. Argo CD should reconcile without manual `kubectl apply`, one-off cluster edits, or undocumented follow-up steps.

## Security & Configuration Tips

Never commit plaintext secrets. Use Vault-backed `ExternalSecret` resources and keep secret material outside Git. Run Gitleaks before committing sensitive changes. Avoid manual `kubectl apply` for normal changes; this repo is intended to be reconciled by Argo CD.
