---
name: sherlock-gitops
description: Correlate HomeLab Argo, Kubernetes and repository observations without confusing GitOps revisions, application builds or infrastructure ownership.
---

Repository ownership background:
- Shivppatel/k8s is public GitOps source: apps/<name>/ has Helm wrapper Chart.yaml, values.yaml, vendored dependencies and custom templates. The app-of-apps inventory tracks main. Argo's actual synced revision, not just branch main or latest merge, determines deployed desired state.
- Shivppatel/k8s-private is separate private GitOps source. Multiple-source Argo Applications can connect a chart source and values source from different repositories. Match each source path to its actual revision; do not apply one SHA to every source.
- The HomeLab tf/ checkout contains independent Terraform roots such as vault, minio, datadog and cloudflare. Terraform/Atlantis owns those external resources, including MinIO users/buckets and Vault policies. This Sherlock GitHub installation currently has no tf repository access. Background ownership does not prove a Terraform plan/apply happened; require a supplied artifact or record.
- The HomeLab helm/ checkout contains chart source (for example dozzle). It is not automatically the chart artifact deployed by Argo. Require the Application chart/repository/version plus build or registry provenance to identify a deployed chart. No separate Helm repository is configured for Sherlock reads today.
- Shared PostgreSQL bootstrap roles/databases and CA mirroring are Kubernetes GitOps-owned; application migrations are service-owned. Do not attribute a database incident to a migration from a current schema snapshot alone.

Correlation workflow:
Match the originating Datadog or configured native Alertmanager scope to a returned namespace/workload/service binding, then confirm UID and Argo tracking ownership. Preserve ambiguity or missing bindings. Compare the alert window with retained sync/change/event times. Distinguish desired state, current observed state and historical snapshots. Healthy/Synced now does not prove healthy at the alert time.

A GitOps commit can change values, image digests, ingress or configuration. It is not the application source/build commit unless independent image labels, digest provenance or deployment records establish that relationship. Consider both a change-related mechanism and an independent dependency/traffic mechanism only when evidence supports them. State missing provenance and contradictions explicitly. Suggest checks before a rollback; never claim a proposed fix was executed.
