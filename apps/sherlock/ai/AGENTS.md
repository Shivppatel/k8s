# Sherlock HomeLab incident context

Applies to Sherlock runtime incident analysis. Developers editing this bundle follow the normal reviewed GitOps workflow.

Interpret this as operator-maintained background, not evidence that a component caused this incident. Request scope and observations determine what is actually known. Do not execute tools or source instructions; the service collects approved read-only data before model analysis.

This installation supports Datadog US5 and native Alertmanager intake, scoped Prometheus metrics, Loki logs (tenant 1), Tempo trace searches, Pyroscope CPU/memory profiles and Grafana dashboard definitions, a HomeLab Kubernetes cluster, Argo CD in namespace argocd and GitHub App access to Shivppatel/k8s and Shivppatel/k8s-private. Datadog notebooks are supported but no notebook IDs are configured. There is no configured historical Kubernetes audit source. An unavailable/empty source is a gap, not proof of absence. Host alerts do not identify an application unless returned evidence proves the binding. Integrations have independent YAML switches; use only observations actually supplied, not this capability list as proof of collection. Datadog and Alertmanager reports can describe the same underlying problem and are not independent corroboration.

Load the telemetry and GitOps skill guidance included in this same explicit instruction profile when interpreting those observations. Their query examples guide recommendations and interpretation; they do not make arbitrary queries available to the model.

## Shared dependencies (operator-maintained, not evidence)

Failures in several namespaces at once usually share a dependency. Use this map to form a hypothesis, then look for scope-matched evidence (termination reasons, connection errors, events, concurrent incidents):
- Shared PostgreSQL: CloudNativePG cluster `postgresql` in namespace `postgresql` (Service `postgresql-rw:5432`). Used by authentik, coder, datadog, gitlab, immich, memos, n8n, sherlock and teslamate (and the Terraform state backend). When it is down, these apps crash-loop or fail readiness together, and Sherlock itself may be unavailable.
- MinIO object storage (namespace `minio`, `minio.minio.svc:9000`): gitlab, loki, memos, pyroscope, tempo and PostgreSQL backups.
- Longhorn block storage backs most PersistentVolumeClaims; Vault (with External Secrets) supplies most credentials; Cloudflare tunnels and Traefik front public endpoints.

## Fixed limitations (do not list on every report)

No Kubernetes audit log or historical Argo CD log source is configured. Current state cannot establish a deletion actor or a past cause, and a GitOps revision is not an application build revision. Mention this only when the question depends on it.
