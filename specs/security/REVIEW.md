---
type: security-review
context: implementation 2734ae7, based on 333a075, compared with current main 5e3c811
---

# Observability change security review

## Result

The parent performed this review. It is not an independent subagent review.

No new HIGH-confidence, actionable security finding remains in the changed implementation.
This conclusion covers the diff, not the entire homelab or dependency vulnerability inventory.

## Reviewed boundaries

- Longhorn's new ingress peer combines namespace and pod selectors in one entry. It permits only TCP/9500.
- The same port serves the manager API. The permission belongs to the existing trusted Prometheus workload, not every monitoring pod.
- Argo's profiler uses a read-only ConfigMap mount. It introduces no Secret mount, public ingress route, or application-login bypass.
- The profiler remains subject to the existing internal metrics-port network policy. Profiling adds diagnostic access and collection overhead.
- Datadog gains explicit internal-resource permissions through the existing operator identity. Existing wildcard read rules do not expand.
- Both the Agent base and the deployed custom image use immutable digests.
- The community integration pins remain unchanged. The runtime gate precedes registry login and publication.
- Pull-request events skip registry login and publication. Existing package-publisher permissions remain in the build workflow.
- Runtime fixture containers use an internal Docker network with no host socket, host port, or HomeLab credentials.
- Fixture passwords come from `secrets.token_hex`, use process environment or private files, and do not appear in command arguments.
- The fixture's all-zero API-key placeholder is not a credential. External routing is unavailable on the fixture network.
- Docker commands use argument arrays. The readiness shell and seed SQL contain only developer-authored constants.
- YAML manifests use a safe loader. Workflow inspection uses `BaseLoader`, which constructs only primitive values.
- Failure output exposes fixed categories, not raw check output, configuration, passwords, or token values.
- The branch secret scan and commit hooks pass.

## Residual limits

The tests do not establish production admission behavior or real delivery to external telemetry services.
The private profiler endpoint must remain restricted to trusted cluster clients.
CI image checks do not replace a package vulnerability scan or authenticated production integration checks.

Tempo remains outside the approved repair scope. Its failure counter still increases, and its root cause remains unconfirmed.
