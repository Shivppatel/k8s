# Coder

Coder uses the official pinned Helm chart, the shared CloudNativePG cluster, Vault-backed ExternalSecrets, and Traefik at **https://coder.shivpatel.xyz**. The Argo CD application tracks `main` and automatically reconciles after merge.

## Configuration

- `secret/postgresql/coder` in Vault KV v2 must contain `username` (`coder`) and `password`. ExternalSecrets reference the API path `secret/data/postgresql/coder` through `ClusterSecretStore/vault-backend`.
- `coder-db-secret` in `postgresql` supplies the CNPG managed role. The same ExternalSecret name in `coder` builds the connection URL with URL-escaped credentials and `sslmode=require` (encryption, without server certificate verification).
- `Database/coder` in `postgresql` declaratively creates the database owned by the non-superuser `coder` role. Database deletion retains data. It deliberately does not extend the legacy setup Job, which performs unrelated extension changes.
- The control plane uses a ClusterIP Service on port 80. `IngressRoute/coder-ingress` uses `websecure` and Traefik's default `wildcard-cert-new` certificate. DNS must route this hostname to Traefik, and any upstream proxy must support WebSockets.
- One control-plane replica has CPU/memory requests and limits, upstream readiness checks, non-root execution, seccomp, and dropped capabilities. Reloader restarts it after database Secret changes. `PodMonitor/coder` supplies metrics to the existing Prometheus installation.
- Control-plane state lives in PostgreSQL; no control-plane PVC is needed. Existing PostgreSQL storage is retained. Kubernetes workspace templates should use `coder-workspaces`, in-cluster authentication, and explicitly choose `longhorn` for persistent workspace volumes. Namespace-scoped RBAC permits pods and PVCs there, with no workspace-management permissions in the control-plane namespace or cluster-wide role.

## Reconciliation and first use

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
