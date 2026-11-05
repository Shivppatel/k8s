---
type: impact
context: observability repair PR, based on 333a07521789185d56f1af2d14c42cf5c61b73a2
---

# Observability repair impact

## Target

- `apps/longhorn/values.yaml`: permit the deployed Prometheus scraper through the existing manager policy.
- `apps/argocd/values.yaml`: enable the advertised repo-server profiler and mount its required flag file.
- `apps/argocd/charts`: refresh the archive to the already locked 10.9.6 version, with the same Argo CD 3.5.3 image.
- `apps/datadog/values.yaml`: grant the operator required internal-resource permissions.
- `apps/datadog/Dockerfile.emqx`, the image workflow, and the agent template: use a PostgreSQL 18-compatible Agent release.

## Dependents

- Prometheus scrapes three Longhorn managers from the `observability` namespace.
- TCP/9500 also serves the Longhorn REST API. Both namespace and pod selectors must match the scraper.
- Longhorn storage, webhooks, CSI, recurring jobs, and existing policy peers must remain unchanged.
- Three Alloy agents scrape annotated Argo CD repo-server replicas on their internal metrics ports.
- Argo CD 3.5.3 reads `/home/argocd/params/profiler.enabled`. The live repo-server has no profiler mount.
- The new read-only volume projects only `reposerver.profile.enabled`. It uses no Secret and no `subPath` mount.
- The Datadog operator reconciles `DatadogAgentInternal` objects in the `datadog` namespace.
- Three node agents consume the custom Agent image and existing autodiscovery annotations.
- PostgreSQL runs version 18.3. Its pod annotations configure the Datadog PostgreSQL check.
- EMQX, Grafana, Nextcloud, JMX, node checks, logs, and traces share the Agent image.
- The image workflow publishes to GHCR. Publication must follow successful runtime checks.

## Affected stories

This repository has no release-plan story ledger. The repair follows `specs/bugs/BUG-observability.md`.

## Test coverage

Existing CI validates Helm lint and rendering, but not policy reachability, profiler flags, operator permissions, or check compatibility.

New regression checks must cover:

- The rendered Longhorn policy permits only the intended scraper on TCP/9500.
- The existing storage configuration and policy peers do not change.
- The rendered Argo ConfigMap enables the repo-server profiler without new ingress routes.
- The operator receives the required internal-resource verbs through its existing binding.
- The image preserves community integration versions and JMX support.
- The old PostgreSQL check fails against an isolated PostgreSQL 18 fixture with the observed `wal_write` error.
- The candidate image passes that fixture without check errors and emits WAL metrics.
- The workflow tests the image before publication.

## Risk: High

The Agent image serves many integrations. A successful build alone cannot establish compatibility with every production integration.

## Recommended action

Add regression checks before each fix. Build and test the candidate image in CI before using its immutable digest.

Do not alter credentials, database versions, storage classes, replica counts, or Tempo settings.

Production acceptance remains a separate approval gate. No Helm render or isolated fixture proves production delivery.

## Deferred Tempo investigation

Current append failures are verified. Successful ingester pushes and flat discard counters do not identify the failing client RPC cause.

The deployed Tempo 2.9.0 code permits a late replica RPC to inherit cancellation after quorum completion. This remains a hypothesis.

The owner chose the confirmed-fixes PR. This PR does not repair Tempo or alter its alerts.
