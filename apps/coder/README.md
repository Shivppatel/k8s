# Coder

Coder uses the official pinned Helm chart, the shared CloudNativePG cluster, Vault-backed ExternalSecrets, and Traefik at **https://coder.shivpatel.xyz**. The Argo CD application tracks `main` and automatically reconciles after merge. Wildcard workspace applications use `*-coder.shivpatel.xyz`.

## Configuration

- `secret/postgresql/coder` in Vault KV v2 must contain `username` (`coder`) and `password`. ExternalSecrets reference the API path `secret/data/postgresql/coder` through `ClusterSecretStore/vault-backend`.
- `coder-db-secret` in `postgresql` supplies the CNPG managed role. The same ExternalSecret name in `coder` builds the connection URL with URL-escaped credentials and `sslmode=require` (encryption, without server certificate verification).
- `Database/coder` in `postgresql` declaratively creates the database owned by the non-superuser `coder` role. Database deletion retains data. It deliberately does not extend the legacy setup Job, which performs unrelated extension changes.
- The control plane uses a ClusterIP Service on port 80. `IngressRoute/coder-ingress` uses `websecure` and Traefik's default `wildcard-cert-new` certificate. DNS must route this hostname to Traefik, and any upstream proxy must support WebSockets.
- `CODER_WILDCARD_ACCESS_URL=*-coder.shivpatel.xyz` enables Coder apps marked `subdomain = true`, including port forwarding. Create a DNS wildcard record for `*.shivpatel.xyz` pointing to Traefik; the existing certificate for `*.shivpatel.xyz` covers these hosts.
  - **Traefik v3 wildcard routing**: The ingress uses ``HostRegexp(`^[a-z0-9-]+-coder\.shivpatel\.xyz$`)``. The former v2 named-group matcher returned 404 for generated app hosts while direct Coder requests returned 303. Anchors and escaped dots reject nested or foreign domains. App and dashboard traffic still use Coder's existing Service on port 80 behind HTTPS; no per-workspace public Service or ingress is needed.
- One control-plane replica has CPU/memory requests and limits, upstream readiness checks, non-root execution, seccomp, and dropped capabilities. Reloader restarts it after database Secret changes. `PodMonitor/coder` supplies metrics to the existing Prometheus installation.
- Control-plane state lives in PostgreSQL; no control-plane PVC is needed. Existing PostgreSQL storage is retained.
- **Deployment and API boundaries**: Coder's in-cluster provisioner role in `coder-workspaces` is scoped to `pods`, `persistentvolumeclaims`, and `deployments`. GitOps creates the namespace, unprivileged `coder-workspace` ServiceAccount, and NetworkPolicy. New templates disable token automount and grant the workspace service account no RBAC permissions; Coder's control-plane identity performs provisioning, not the workspace process.
- **Workspace isolation and NetworkPolicy**: `NetworkPolicy/coder-workspace` applies strictly to pods carrying `app.kubernetes.io/part-of: coder-workspaces` in namespace `coder-workspaces`. Existing unlabelled user workspaces are untouched, preserving backward compatibility and GitOps boundaries.
  - **Ingress**: All unsolicited inbound traffic from outside the pod is denied. Coder agents establish an outbound tunnel to the control plane; local workspace apps (e.g., code-server, web preview) communicate over loopback (`127.0.0.1`), which resides entirely within the pod network namespace and is unaffected by NetworkPolicy.
  - **Egress**: Permits cluster DNS in `kube-system` on port 53 (UDP/TCP), Coder control plane pods on ports 80 and 8080 (Service HTTP and container/DERP relay), and outbound public HTTP (80) & HTTPS (443) for package managers (apt, npm, pip) and PI subscription OAuth flows (OpenAI, Gemini).
  - **Blocked networks**: Egress explicitly blocks private RFC1918 subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), Carrier-Grade NAT (`100.64.0.0/10`), and link-local / cloud metadata endpoints (`169.254.0.0/16`).
  - **Networking tradeoffs**: Private cluster/LAN endpoints and outbound SSH are blocked; private repository access needs a scoped exception or an HTTPS endpoint. Publicly exposed HomeLab services remain reachable through public HTTP/HTTPS and retain their own authentication. This policy is not a complete multi-tenant security boundary, and custom templates that omit the isolation label are outside its scope.

## Reconciliation and first use

The PostgreSQL managed role list declares CNPG defaults explicitly (`ensure`, `connectionLimit`, and `inherit`). Do not ignore fields inside this list while `RespectIgnoreDifferences=true` is enabled: Argo can preserve the entire live list during sync and omit newly added roles.

Within the PostgreSQL application, the role ExternalSecret is wave `0`, Cluster is wave `1`, and Database is wave `2`. These waves do not order separate Argo applications: Coder may restart until ESO, the role, and the database are ready. The workspace namespace is wave `-1` within Coder and is protected from pruning to preserve workspace PVCs.

After merging, verify `postgresql` and `coder` are Synced/Healthy, `Database/coder` is reconciled, both ExternalSecrets are ready, and the HTTPS endpoint serves Coder. Initialize the first administrator promptly from a trusted connection; until that account exists, anyone who can reach setup can claim it. The default shared GitHub OAuth provider is disabled. Local password login is available; dedicated OIDC/OAuth configuration is a separate follow-up.

The companion Terraform `coder` root publishes `homelab-pi` and `homelab-web` templates. They use namespace `coder-workspaces` and the GitOps-managed `coder-workspace` service account with token automount disabled. Coder owns their pods and PVCs; this chart owns only shared prerequisites. Existing manually created templates/workspaces are not migrated. Subdomain apps and dashboard port forwarding use the wildcard HTTPS route above.

The single replica can have downtime during rescheduling. The shared database's backup/restore arrangements also cover Coder metadata; workspace volumes need their own backup plan. This deployment does not establish tested recovery guarantees.

## Validation

```sh
helm repo add coder-v2 https://helm.coder.com/v2
helm dependency build apps/coder
helm lint apps/coder
helm template coder apps/coder --namespace coder
```

References: [Kubernetes installation](https://coder.com/docs/install/kubernetes), [release channels](https://coder.com/docs/install/releases).
