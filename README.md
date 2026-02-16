# ShivWS Homelab

GitOps-driven Kubernetes platform running on bare-metal.

## Stack

- **GitOps:** ArgoCD App-of-Apps with automated sync and self-healing
- **Secrets:** HashiCorp Vault (HA Raft) + External Secrets Operator
- **Ingress:** Traefik + cert-manager + Cloudflare Tunnel/Access
- **Observability:** Prometheus, Grafana, Loki, Tempo, Pyroscope, Alloy
- **Data:** CloudNativePG/PostgreSQL, Redis, MinIO, Kafka, RabbitMQ
- **Auth:** Authentik SSO
- **Policy:** Kyverno
- **Storage:** Longhorn

## Architecture

- **Control plane:** `apps/argocd-apps` defines grouped ArgoCD Applications (root app pattern)
- **Platform layer:** networking, security, secrets, and observability are managed as shared services
- **Data layer:** stateful services (PostgreSQL/CNPG, Redis, MinIO, Kafka, RabbitMQ) are centralized
- **Workload layer:** application charts consume shared ingress, secrets, telemetry, and data services

## Structure

```
apps/
├── argocd/                # GitOps controller
├── argocd-apps/           # Root app and grouped application definitions
├── vault/                 # Secrets management (HA Raft)
├── external-secrets/      # Syncs secrets from Vault
├── traefik/               # Ingress controller
├── cert-manager/          # TLS automation
├── kube-prometheus-stack/ # Metrics + Grafana
├── loki/                  # Logs
├── tempo-distributed/     # Traces
├── pyroscope/             # Profiles
├── alloy/                 # Telemetry pipeline
├── cloudnative-pg/        # PostgreSQL operator
├── postgresql/            # PostgreSQL clusters/bootstrap
├── gitlab/                # Git platform + registry
└── ...                    # Additional infrastructure and application charts
```

## CI/CD

- **Renovate** — Automated dependency updates
- **GitHub Actions** — Helm lint + YAML validation on PRs
