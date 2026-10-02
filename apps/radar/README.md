# Radar

## Desired Git state

- `Application/radar` in `argocd` tracks `apps/radar` on `main`, creates namespace `radar`, and enables automated sync, pruning, and self-healing.
- The wrapper pins upstream chart and image version `1.15.0`. `Chart.lock` and the vendored chart are included; dependency upgrades use `helm dependency update apps/radar`.
- One non-root replica uses a read-only root filesystem, dropped capabilities, RuntimeDefault seccomp, and bounded CPU/memory. The upstream chart uses `Recreate` for SQLite to prevent concurrent writers during upgrades; upgrades briefly interrupt access.
- `PersistentVolumeClaim/radar` uses `longhorn`, `ReadWriteOnce`, and 1 GiB. SQLite timeline history survives pod replacement, with seven-day retention and an 800 MiB pruning threshold. Pruning/uninstalling the Application can delete the PVC and history; it is not a backup.
- `Service/radar` is ClusterIP on port `9280`. `IngressRoute/radar-ingress` serves `radar.shivpatel.xyz` on `websecure`, using Traefik's default `wildcard-cert-new` certificate.
- Authentication is provided by the owner's existing Cloudflare access boundary. Radar itself runs without authentication; direct Traefik or in-cluster Service access bypasses Cloudflare. DNS/tunnel routing and the Cloudflare policy must cover this hostname before external use. No Cloudflare configuration is managed by this chart.
- The service account can read cluster resources and pod logs, including supported integration CRDs. Secret reads, Helm writes, exec, port-forward, node proxy, and self-upgrades are disabled. All visitors share this read-only identity. Helm release details requiring Kubernetes Secrets are unavailable by design; Argo CD Applications remain visible through CRD access.
- Prometheus queries use `http://kube-prometheus-stack-prometheus.observability.svc.cluster.local:9090`. This does not install a traffic collector; traffic views depend on existing metric sources.
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
