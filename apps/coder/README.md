# Coder

Coder uses the official pinned Helm chart, the shared CloudNativePG cluster, Vault-backed ExternalSecrets, and Traefik at **https://coder.shivpatel.xyz**. The Argo CD application tracks `main` and automatically reconciles after merge. Wildcard workspace applications use `*-coder.shivpatel.xyz`.

## Configuration

- `secret/postgresql/coder` in Vault KV v2 must contain `username` (`coder`) and `password`. ExternalSecrets reference the API path `secret/data/postgresql/coder` through `ClusterSecretStore/vault-backend`.
- `coder-db-secret` in `postgresql` supplies the CNPG managed role. The same ExternalSecret name in `coder` builds the connection URL with URL-escaped credentials and `sslmode=require` (encryption, without server certificate verification).
- `Database/coder` in `postgresql` declaratively creates the database owned by the non-superuser `coder` role. Database deletion retains data. It deliberately does not extend the legacy setup Job, which performs unrelated extension changes.
- The control plane uses a ClusterIP Service on port 80. `IngressRoute/coder-ingress` uses `websecure` and Traefik's default `wildcard-cert-new` certificate. DNS must route this hostname to Traefik, and any upstream proxy must support WebSockets.
- `CODER_WILDCARD_ACCESS_URL=*-coder.shivpatel.xyz` enables Coder apps marked `subdomain = true`, including port forwarding. Create a DNS wildcard record for `*.shivpatel.xyz` pointing to Traefik; the existing certificate for `*.shivpatel.xyz` covers these hosts. The IngressRoute accepts both the dashboard hostname and generated `*-coder.shivpatel.xyz` app hostnames. Ensure this broad wildcard does not overlap another service that owns subdomains under `shivpatel.xyz`.
- One control-plane replica has CPU/memory requests and limits, upstream readiness checks, non-root execution, seccomp, and dropped capabilities. Reloader restarts it after database Secret changes. `PodMonitor/coder` supplies metrics to the existing Prometheus installation.
- Control-plane state lives in PostgreSQL; no control-plane PVC is needed. Existing PostgreSQL storage is retained. Kubernetes workspace templates should use `coder-workspaces`, in-cluster authentication, and explicitly choose `longhorn` for persistent workspace volumes. Namespace-scoped RBAC permits pods and PVCs there, with no workspace-management permissions in the control-plane namespace or cluster-wide role.

## Reconciliation and first use

The PostgreSQL managed role list declares CNPG defaults explicitly (`ensure`, `connectionLimit`, and `inherit`). Do not ignore fields inside this list while `RespectIgnoreDifferences=true` is enabled: Argo can preserve the entire live list during sync and omit newly added roles.

Within the PostgreSQL application, the role ExternalSecret is wave `0`, Cluster is wave `1`, and Database is wave `2`. These waves do not order separate Argo applications: Coder may restart until ESO, the role, and the database are ready. The workspace namespace is wave `-1` within Coder and is protected from pruning to preserve workspace PVCs.

After merging, verify `postgresql` and `coder` are Synced/Healthy, `Database/coder` is reconciled, both ExternalSecrets are ready, and the HTTPS endpoint serves Coder. Initialize the first administrator promptly from a trusted connection; until that account exists, anyone who can reach setup can claim it. The default shared GitHub OAuth provider is disabled. Local password login is available; dedicated OIDC/OAuth configuration is a separate follow-up.

Import a Kubernetes workspace template and set its namespace to `coder-workspaces`; default templates targeting `coder` will be denied by design. Use a workspace service account without Kubernetes privileges and disable its token automount unless the template requires API access. Workspace templates and PVCs are created through Coder, not by this chart. Browser apps initially use path-based routing; subdomain apps require a separately configured wildcard access URL, DNS, and certificate.

The single replica can have downtime during rescheduling. The shared database's backup/restore arrangements also cover Coder metadata; workspace volumes need their own backup plan. This deployment does not establish tested recovery guarantees.

## Validation

```sh
helm repo add coder-v2 https://helm.coder.com/v2
helm dependency build apps/coder
helm lint apps/coder
helm template coder apps/coder --namespace coder
```

References: [Kubernetes installation](https://coder.com/docs/install/kubernetes), [release channels](https://coder.com/docs/install/releases).
