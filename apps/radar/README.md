# Radar

## Desired Git state

- `Application/radar` in `argocd` tracks `apps/radar` on `main`, creates namespace `radar`, and enables automated sync, pruning, and self-healing.
- The wrapper pins upstream chart and image version `1.15.0`. `Chart.lock` and the vendored chart are included; dependency upgrades use `helm dependency update apps/radar`.
- One non-root replica uses a read-only root filesystem, dropped capabilities, RuntimeDefault seccomp, and bounded CPU/memory. The upstream chart uses `Recreate` for SQLite to prevent concurrent writers during upgrades; upgrades briefly interrupt access.
- Memory is requested at 4 GiB and limited to 8 GiB to retain full cluster-wide report visibility, including raw Trivy SBOM reports, while allowing concurrent dashboard/topology copies and response buffers. `GOMEMLIMIT=4GiB` is a soft Go runtime memory target, not a hard RSS cap; it leaves headroom below the container limit. A lower target cannot reclaim objects still referenced by concurrent requests. Reassess both the request and limit as report volume or concurrent browser usage grows; do not size this workload from idle health probes alone.
- `PersistentVolumeClaim/radar` uses `longhorn`, `ReadWriteOnce`, and 1 GiB. SQLite timeline history survives pod replacement, with seven-day retention and an 800 MiB pruning threshold. Pruning/uninstalling the Application can delete the PVC and history; it is not a backup.
- `Service/radar` is ClusterIP on port `9280`. `IngressRoute/radar-ingress` serves `radar.shivpatel.xyz` on `websecure`, using Traefik's default `wildcard-cert-new` certificate.
- Authentication is provided by the owner's existing Cloudflare access boundary. Radar itself runs without authentication; direct Traefik or in-cluster Service access bypasses Cloudflare. DNS/tunnel routing and the Cloudflare policy must cover this hostname before external use. No Cloudflare configuration is managed by this chart.
- The service account has cluster-wide `get/list/watch` access to every API resource, including Secrets, Helm release storage, RBAC, webhooks, node proxy, and installed/future CRDs; non-resource API URLs permit GET. All visitors share this broad reader identity. Helm writes, workload mutation verbs, exec/port-forward creation, impersonation, and self-upgrades are not granted. This is not a security sandbox: Secret contents can contain powerful credentials, and proxy/streaming GET subresources can expose capabilities beyond ordinary object inspection. Protect both Cloudflare and direct cluster/Traefik access.
- Helm inventory reads Kubernetes release Secrets. Argo CD only templates Helm charts and does not create Helm release records, so GitOps-managed wrapper charts are shown under GitOps, not necessarily as installed Helm releases.
- Prometheus queries use `http://kube-prometheus-stack-prometheus.observability.svc.cluster.local:9090`. [Caretta](../caretta/) runs on each node and supplies `caretta_links_observed` through a cross-namespace PodMonitor. Radar detects the labelled Caretta pods and selects Caretta once the configured Prometheus contains its metrics; no bundled VictoriaMetrics, new datasource, or Radar port-forward permission is needed.
- MCP, Radar Cloud, and usage reporting are disabled. No Vault paths or ExternalSecrets are required. No explicit sync wave is needed in the existing cluster: Traefik/its CRDs, its default TLS certificate, and Longhorn already exist. Prometheus must be available for metrics queries.

## Validation and reconciliation

```sh
helm dependency build apps/radar
helm lint apps/radar
helm template radar apps/radar --namespace radar --api-versions traefik.io/v1alpha1
helm lint apps/argocd-apps
helm template argocd-apps apps/argocd-apps --namespace argocd
```

Merge through the normal GitOps workflow; do not install this chart with Helm or manually apply its manifests. After Argo CD reconciles, verify `radar` is Synced/Healthy, the PVC is Bound, and the Deployment is Available:

```sh
kubectl rollout status deployment/radar --namespace radar --timeout=5m
kubectl get pvc,svc,ingressroute --namespace radar
```

Access `https://radar.shivpatel.xyz` through Cloudflare and confirm an unauthenticated browser is challenged before reaching Radar. Kubernetes-authorized operators can also use `kubectl port-forward --namespace radar svc/radar 9280:9280` and open `http://localhost:9280`.

Upstream references: [in-cluster deployment](https://github.com/skyhook-io/radar/blob/v1.15.0/docs/in-cluster.md), [chart configuration](https://github.com/skyhook-io/radar/blob/v1.15.0/deploy/helm/radar/values.yaml).
