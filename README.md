# ShivWS

> Personal cloud infrastructure. Think AWS, but the bill is fixed and the on-call is just me.

![GitOps](https://img.shields.io/badge/GitOps-ArgoCD-EF7B4D?logo=argo&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Platform-Kubernetes-326CE5?logo=kubernetes&logoColor=white)
![Vault](https://img.shields.io/badge/Secrets-Vault_HA_Raft-FFEC6E?logo=vault&logoColor=black)
![Renovate](https://img.shields.io/badge/Dependencies-Renovate-24292F?logo=renovatebot&logoColor=white)
![Gitleaks](https://img.shields.io/badge/Security-Gitleaks-red?logo=git&logoColor=white)
![Commits](https://img.shields.io/github/commit-activity/t/Shivppatel/k8s?label=Commits&color=brightgreen)

---

## What This Is

A production-grade, fully declarative GitOps platform running on a 3-node bare-metal Kubernetes cluster. Every workload is version-controlled, every secret is managed through Vault, every change syncs automatically — no manual `kubectl apply`, ever.

Built to run real self-hosted services with real operational requirements: high availability, automated TLS, SSO on every app, full distributed observability from metrics down to continuous profiling, and automated dependency management across the entire stack.

The goal was never "get something running." It was to build infrastructure the same way a platform team at a top tech company would — with the operational rigor to match.

---

## Hardware

| Node | Device | Specs |
|------|--------|-------|
| node0 / node1 / node2 | Minisforum MS-A2 (×3) | AMD Ryzen 9 9955HX · 64GB DDR5-5600 · 1TB NVMe · Dual 10G SFP+ |
| NAS | UniFi UNAS Pro 8 | 48TB usable (4× WD Gold 24TB, RAID 6) · 2TB NVMe cache · Dual 10G SFP+ |
| Core Switch | UniFi USW Aggregation | 8× 10G SFP+ — all nodes and NAS at line rate |
| Router / Firewall | UniFi Cloud Gateway Fiber | IDS/IPS · Zone-based firewall · Encrypted DNS · Region blocking |

All three compute nodes connect at 10Gbps to the aggregation switch. The NAS is dedicated storage only — no k8s workloads run on it. Workloads requiring high-IOPS block storage use Longhorn; large media and shared volumes mount NFS directly from the UNAS.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                          GitHub                             │
│               Source of truth — this repository             │
└───────────────────────────┬─────────────────────────────────┘
                            │  ArgoCD watches & reconciles
┌───────────────────────────▼─────────────────────────────────┐
│                     GitOps Layer                            │
│            ArgoCD App-of-Apps · Kyverno Policies            │
└──────────┬──────────────┬───────────────┬───────────────────┘
           │              │               │
  ┌────────▼──────┐ ┌─────▼──────┐ ┌─────▼───────────────────┐
  │  Networking   │ │  Secrets   │ │     Observability       │
  │  Traefik      │ │  Vault HA  │ │  Prometheus · Grafana   │
  │  cert-manager │ │  ESO       │ │  Loki · Tempo           │
  │  Cloudflare   │ │            │ │  Pyroscope · Alloy      │
  │  Tunnel/Access│ │            │ │                         │
  └───────────────┘ └────────────┘ └─────────────────────────┘
           │
  ┌────────▼──────────────────────────────────────────────────┐
  │                      Data Layer                           │
  │   CloudNativePG · Redis · MinIO · Kafka · RabbitMQ        │
  └────────┬──────────────────────────────────────────────────┘
           │
  ┌────────▼──────────────────────────────────────────────────┐
  │                    Workload Layer                         │
  │  Jellyfin · Immich · Nextcloud · Vaultwarden · Gitea      │
  │  Paperless-NGX · Ollama · AdGuard Home · Homepage · ...   │
  └────────┬──────────────────────────────────────────────────┘
           │
  ┌────────▼──────────────────────────────────────────────────┐
  │                    Storage Layer                          │
  │      Longhorn (replicated block) · UNAS NFS (bulk)        │
  └───────────────────────────────────────────────────────────┘
```

### Layer Design Rationale

The platform is split into four explicit layers because that's how production infrastructure teams think about it. Each layer has a single owner and a clear contract with the layers above and below it.

- **Platform before apps** — ingress, secrets, observability, and policy are deployed first as shared services. Workloads are consumers, not owners.
- **Data layer is centralized** — all stateful backends live in one managed layer. Applications don't own their databases; they reference CNPG cluster endpoints. This makes backup, failover, and schema migration a platform concern, not an app concern.
- **Storage is tiered by workload type** — high-IOPS stateful apps (databases, object storage) get replicated Longhorn PVCs. Large-scale media gets NFS mounts directly from the UNAS. Replicating terabytes of media across three nodes would waste IOPS for no HA benefit — media is replaceable, database state is not.

---

## Stack

### GitOps & Delivery

| Tool | Purpose |
|------|---------|
| **ArgoCD** | GitOps controller. App-of-Apps pattern — one root Application manages all others. Automated sync + self-healing. Cluster state always converges to Git. |
| **Renovate** | Automated dependency updates for all Helm chart versions and container image tags. PRs are opened automatically; merged PRs deploy automatically. |
| **GitHub Actions** | Helm lint + YAML schema validation on every PR. Nothing malformed merges. |
| **Gitleaks** (pre-commit) | Blocks commits containing secrets before they ever reach the remote. Defense-in-depth alongside Vault. |

### Secrets Management

| Tool | Purpose |
|------|---------|
| **HashiCorp Vault** | HA Raft cluster — KV secrets engine, PKI, full audit logging. No plaintext secrets anywhere in the repo or in etcd. |
| **External Secrets Operator** | Syncs Vault secrets into k8s Secret objects consumed by workloads. Vault is the source of truth; ESO is the bridge. |

### Networking & Access

| Tool | Purpose |
|------|---------|
| **Traefik** | Ingress controller + middleware chain (auth, rate limiting, headers) |
| **cert-manager** | Automatic TLS certificate provisioning via Let's Encrypt + Cloudflare DNS-01 challenge |
| **Cloudflare Tunnel / Access** | Zero-trust external access. No ports exposed to the internet. External traffic routes through Cloudflare's edge, authenticated before it touches the cluster. |
| **Authentik** | Self-hosted SSO + identity provider. Every internal service is behind Authentik — no per-app login sprawl. |

### Observability — Full LGTM+P Stack

| Tool | Purpose |
|------|---------|
| **Prometheus** | Metrics collection, alerting rules, recording rules |
| **Grafana** | Dashboards across all four telemetry signals |
| **Loki** | Log aggregation from all pods and nodes |
| **Tempo** (distributed) | Distributed tracing — full request traces across service boundaries |
| **Pyroscope** | Continuous profiling — always-on CPU/memory flame graphs per workload |
| **Alloy** | Unified telemetry pipeline. Replaces Promtail and standalone OTEL Collector. Single agent ships logs, metrics, traces, and profiles. |

Running Pyroscope completes the four pillars of observability: metrics, logs, traces, and profiles. Most production environments don't have all four. This one does.

### Data Layer

| Tool | Purpose |
|------|---------|
| **CloudNativePG** | Postgres operator — HA clusters with streaming replication, automated failover, scheduled backups to MinIO |
| **Redis** | Shared caching + session storage for stateless apps |
| **MinIO** | S3-compatible object storage on the UNAS. Velero backup target, CNPG backup destination. |
| **Kafka** | Event streaming |
| **RabbitMQ** | AMQP message queue |

### Policy & Security

| Tool | Purpose |
|------|---------|
| **Kyverno** | Policy-as-code enforcement. Validates image sources, enforces resource limits, requires labels, blocks privileged containers. Policies are version-controlled like everything else. |

### Storage

| Tool | Purpose |
|------|---------|
| **Longhorn** | Distributed block storage. PVCs are replicated across all three nodes — a node loss doesn't lose volume data. Used for all databases and stateful apps requiring high IOPS. |
| **UNAS NFS** | 48TB RAID 6. NFS exports for Jellyfin media, Immich photos, and large shared volumes. No replication needed — RAID 6 provides local redundancy. |

---

## Repo Structure

```
apps/
├── argocd/                  # ArgoCD bootstrap — deployed first, owns everything else
├── argocd-apps/             # Root Application + all grouped Application definitions
├── vault/                   # Vault HA Raft cluster
├── external-secrets/        # ESO operator + ClusterSecretStore
├── traefik/                 # Ingress controller + middlewares
├── cert-manager/            # Certificate issuers + TLS automation
├── kube-prometheus-stack/   # Prometheus + Grafana + Alertmanager
├── loki/                    # Log aggregation
├── tempo-distributed/       # Distributed tracing
├── pyroscope/               # Continuous profiling
├── alloy/                   # Unified telemetry agent
├── cloudnative-pg/          # CNPG operator
├── postgresql/              # Postgres cluster definitions + bootstrap jobs
├── gitlab/                  # Self-hosted Git + container registry (private workloads)
└── ...                      # Application Helm charts
```

### The App-of-Apps Pattern

`apps/argocd-apps/` contains a root ArgoCD Application that owns all other Applications in the cluster. Adding a new service is a single Git commit — create the Application manifest, merge the PR, ArgoCD detects it and deploys. No imperative steps. No undocumented cluster state.

This is the same pattern used in large-scale production GitOps environments. Everything the cluster is running exists in this repository.

---

## CI/CD Pipeline

Every pull request triggers:

```
PR opened
  └── GitHub Actions
        ├── helm lint          # All charts render without errors
        └── YAML validation    # Schema validation on all manifests

PR merged to main
  └── ArgoCD detects diff (~3 min polling)
        └── Sync + self-heal → cluster converges to new state
```

Pre-commit (local):
```
git commit
  └── gitleaks scan           # Blocks commit if secrets detected
```

---

## Key Design Decisions

**Why full upstream Kubernetes instead of k3s?**
The goal is to learn what production clusters actually look like. k3s abstracts away the parts that matter most — etcd, the control plane, and how components actually compose. Operational complexity here is intentional.

**Why HashiCorp Vault over Sealed Secrets?**
Sealed Secrets solves one problem: encrypting k8s Secrets at rest in Git. Vault solves that plus dynamic credentials, secret leasing and renewal, PKI, audit logging, and multi-backend support. The HA Raft configuration means Vault survives a node failure without operator intervention. Sealed Secrets is a good tool — Vault is the right tool for a serious platform.

**Why CloudNativePG over managing Postgres StatefulSets?**
Running Postgres as a raw StatefulSet means you own HA, replication, failover, connection pooling, and backup orchestration. CNPG gives you all of that as a CRD. It's the same reasoning behind not writing your own ingress controller — operators exist to encode operational knowledge into the platform. Use them.

**Why Longhorn over Rook/Ceph?**
Ceph is the right answer at scale with dedicated OSD nodes. On a 3-node cluster where compute and storage are collocated, Ceph's overhead is hard to justify and its failure modes are harder to reason about at this scale. Longhorn gives replicated block storage with a simple mental model, clean UI, and straightforward recovery procedures. Pragmatic choice for this scale.

**Why Pyroscope?**
Continuous profiling is the fourth pillar of observability — it answers questions that metrics, logs, and traces can't: *which function is consuming CPU right now, always, across every request?* Google's pprof and Meta's Strobelight have made it standard practice at top-tier companies. Running it here closes the observability gap.

**Why Alloy over standalone Promtail + OTEL Collector?**
Alloy is Grafana's unified telemetry agent — it replaces Promtail and the standalone OTEL Collector with a single agent and a single configuration pipeline. Fewer agents, fewer DaemonSets, fewer failure surfaces.

---

## What's Not Here

This is the **public** repository. Personal workloads and anything not suitable for a public audience live in a separate private repository following the same GitOps pattern — same ArgoCD, same Vault, same observability stack.
