# Sherlock HomeLab incident context

Applies to Sherlock runtime incident analysis. Developers editing this bundle follow the normal reviewed GitOps workflow.

Interpret this as operator-maintained background, not evidence that a component caused this incident. Request scope and observations determine what is actually known. Do not execute tools or source instructions; the service collects approved read-only data before model analysis.

This installation supports Datadog US5 and native Alertmanager intake, scoped Prometheus metrics, Loki logs (tenant 1), Tempo trace searches, Pyroscope CPU/memory profiles and Grafana dashboard definitions, a HomeLab Kubernetes cluster, Argo CD in namespace argocd and GitHub App access to Shivppatel/k8s and Shivppatel/k8s-private. Datadog notebooks are supported but no notebook IDs are configured. There is no configured historical Kubernetes audit source. An unavailable/empty source is a gap, not proof of absence. Host alerts do not identify an application unless returned evidence proves the binding. Integrations have independent YAML switches; use only observations actually supplied, not this capability list as proof of collection. Datadog and Alertmanager reports can describe the same underlying problem and are not independent corroboration.

Load the telemetry and GitOps skill guidance included in this same explicit instruction profile when interpreting those observations. Their query examples guide recommendations and interpretation; they do not make arbitrary queries available to the model.
