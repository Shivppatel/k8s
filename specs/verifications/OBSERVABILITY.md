---
type: verification
context: confirmed observability repairs on fix/observability-pipelines
---

# Observability repair verification

## Scope and result

This PR repairs the confirmed Longhorn scrape, Argo repo-server profiling, Datadog RBAC, and PostgreSQL check configuration failures.

The owner explicitly deferred Tempo. Its append failures still increase. This PR changes neither Tempo nor its alerts.

No HomeLab deployment, restart, sync, or merge occurred. Production success remains unverified.

## Check 1: cause-specific evidence

- Longhorn managers answer `/metrics` with HTTP 200 from a node. The existing ingress policy excludes the deployed Prometheus identity.
- The new manager rule requires both the `observability` namespace and the deployed Prometheus pod labels on TCP/9500.
- TCP/9500 also serves the manager API. The rule does not permit a whole namespace or an unrestricted peer.
- Argo CD 3.5.3 returns the observed profiler 401 because its flag file is absent.
- The new repo-server volume projects `reposerver.profile.enabled` as `/home/argocd/params/profiler.enabled`, with a read-only directory mount.
- A regression proved that the ConfigMap flag alone was insufficient.
- Datadog operator 1.30.0 requires internal-resource permissions that the existing chart settings omit.
- Agent 7.73 queries `wal_write`, which PostgreSQL 18 removed. Agent 7.74 includes the version-specific Postgres 23.3.3 fix.

## Check 2: manifests and scope

- Eleven local tests pass. They cover policy peer/port constraints, profiler file wiring, internal RBAC, image pins, publication order, and result validation.
- Locked dependency builds, Helm lint/render, YAML lint, workflow validation, and diff checks pass.
- The changed NetworkPolicy, ConfigMap, Deployment, ClusterRole, and DatadogAgent match live Kubernetes or installed CRD schemas.
- Schema checks use GET requests. They do not exercise admission webhooks or replace deployment validation.
- Resource identities, storage classes, PVCs, credential resources, services, ingress routes, HPAs, and disruption budgets remain unchanged.
- Argo chart labels change because the stale 10.9.2 archive now matches the already locked 10.9.6 dependency.
- The Argo CD image stays at 3.5.3. The refreshed chart changes Dex's startup copy flag from `-n` to `-f`.
- Datadog gains only the chart's explicit internal-resource rules. No new wildcard permission appears.
- The Agent retains EMQX 1.1.0, Grafana 1.0.0, Nextcloud 2.0.0, and JMX support.

## Check 3: isolated runtime proof

[CI run 37182360223](https://github.com/Shivppatel/k8s/actions/runs/37182360223) passed these checks before publication:

- The community checks and Postgres 23.3.3 import successfully.
- Java starts successfully in the JMX image.
- The old Agent reproduces the observed `wal_write` SQL failure against disposable PostgreSQL 18.3.
- The candidate emits WAL records/bytes metrics with zero check-runner errors and no new PostgreSQL SQL errors.

The fixture uses an internal Docker network, generated test credentials, and disposable containers. It has no HomeLab connection or public port.

The initial fixture failed because the one-shot CLI required IPC bootstrap files. Normal Agent startup now creates those files inside the fixture.
Publication was skipped on every failed run.

The registry descriptor and CI publication log agree on the tested image digest:

`sha256:cd04dd736f667bc398e69ac4c70378581e90fc88fdb64ec3bf4e9d9a6f70cc83`

The deployed image reference pins that digest. A future tag update cannot replace this image silently.

## Deployment impact and remaining acceptance

**CAUTION:** A merge can trigger automated Argo sync. The shared parameter checksum causes several Argo components to roll, not only repo-server.

The Datadog node agents will roll to the new image. Longhorn storage pods receive no template or storage change.

Production acceptance still requires all three Longhorn targets to stay UP and all annotated repo-server profile requests to succeed.
The operator reconciliation error must clear, and the PostgreSQL check must stop its version-related errors.
Actual EMQX, Grafana, Nextcloud, JMX, logs, traces, and intake delivery still require observation after an approved deployment.

The tests do not prove every production integration, network path, admission policy, or delivery destination.

Historical Calico timeouts and intake DNS failures were not established as current faults. This PR does not claim to repair them.

The fresh 2026-10-04 live check still showed the original four failure signals. That result is expected before deployment.
