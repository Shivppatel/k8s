---
type: bug
context: confirmed-fixes PR, owner-approved scope on 2026-10-03
---

# Repair confirmed observability failures

## Evidence

At 06:06 UTC, all three Longhorn scrape targets timed out. Each manager remained Ready.
The deployed manager policy excluded the Prometheus pod. A node-local HTTP GET returned 200 from `/metrics`.

All three Alloy agents reported profiling 401s from Argo CD repo-server pods.
The response said that the profiler was not enabled in `argocd-cmd-params-cm`.
The repo-server scrape annotations were present, but `reposerver.profile.enabled` was absent.

The Datadog operator could neither create nor update `datadogagentinternals`.
Chart 2.27.0 omits those permissions when `datadogAgentInternal.enabled` is false.
Operator 1.30.0 requires that resource.

All three Datadog node agents reported `wal_write` errors from `stat_wal_metrics`.
PostgreSQL 18 removed that column. Agent 7.74.0 includes Postgres integration 23.3.3 with the version-specific query fix.

## Approved implementation

1. Add a rendered-policy regression test. Set narrowly scoped `longhorn.networkPolicies.metricsScrapeSources`.
2. Add a profiler regression test. Set `argo-cd.configs.params.reposerver.profile.enabled` to `"true"`.
3. Add an operator-permission regression test. Enable internal-resource RBAC without additional wildcard grants.
4. Add image-contract and runtime checks. Upgrade only the custom Agent base to digest-pinned 7.74.0-jmx.
5. Preserve EMQX 1.1.0, Grafana 1.0.0, and Nextcloud 2.0.0 integration pins.
6. Build the image, import the integrations, and compare old and new PostgreSQL checks against an isolated PostgreSQL 18 fixture.
7. Publish only a tested image. Pin the deployed image reference to its published digest before final review.
8. Validate rendered changes, security, and unchanged behavior before opening the PR.

## Acceptance

The regression suite and CI must pass. Kubernetes schemas must accept the changed resource shapes.
The resource diff must contain no storage, credential, ingress, or Tempo change.
The primary checkouts must retain their unrelated edits.

After an approved deployment, verify all three Longhorn targets, all repo-server profiler endpoints, operator reconciliation, and Datadog check results.
Production delivery and integration behavior remain unverified before deployment.

## Out of scope

No merge, sync, restart, database change, or HomeLab deployment is authorized.
Historical Calico timeouts and DNS failures are not confirmed current failures.
Tempo remains unresolved by explicit owner choice. The append counter increases, but this PR makes no Tempo change.

## Primary sources

- Longhorn 1.13.0: `chart/templates/network-policies/manager-network-policy.yaml` in the vendored chart.
- Argo CD: https://github.com/argoproj/argo-cd/blob/v3.3.0/util/profile/profile.go
- Datadog operator 1.30.0 RBAC: https://github.com/DataDog/datadog-operator/blob/v1.30.0/config/rbac/role.yaml
- PostgreSQL 18 support: https://github.com/DataDog/integrations-core/pull/21947
- Postgres integration release: https://github.com/DataDog/integrations-core/blob/postgres-23.3.3/postgres/CHANGELOG.md
- Tempo 2.9.0: https://github.com/grafana/tempo/blob/v2.9.0/modules/distributor/distributor.go
