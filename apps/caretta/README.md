# Caretta

## Desired Git state

- `Application/caretta` in `argocd` tracks `apps/caretta` on `main`, creates its own namespace `caretta`, and enables automated sync, pruning, and self-healing.
- The Helm wrapper pins upstream chart `0.0.16` and collector image `quay.io/groundcover/caretta:v0.0.16`. `Chart.lock` and the vendored dependency are included. Upgrades use `helm dependency update apps/caretta`.
- One DaemonSet collector runs on each Linux node, including control-plane nodes. Requests are 100m CPU/320 MiB per node; limits are 500m CPU/512 MiB.
- Caretta uses node-wide eBPF tracing and requires a privileged container with host `/proc` and `/sys/kernel/debug` mounts. Its root filesystem remains read-only. The upstream chart's API role is read-only and does not include Secrets. Linux kernel >= 4.16 and CO-RE/BTF support are required. Do not apply restricted Pod Security enforcement to this namespace without redesigning the collector's privileges.
- Obsolete PodSecurityPolicy and OpenShift SCC resources are disabled. Bundled Grafana and VictoriaMetrics servers are disabled; existing observability services handle metrics and UI. The upstream chart still emits its dashboard ConfigMap, but does not deploy a Grafana instance.
- `PodMonitor/caretta` selects collector pods by Helm name/instance labels and scrapes named port `prom-metrics` (`7117`), path `/metrics`, every 15 seconds. Relabeling preserves `caretta_node` and `caretta_pod` for per-node attribution. Existing Prometheus discovers PodMonitors across all namespaces.
- Radar detects Caretta's labelled pods and queries `caretta_links_observed` through `http://kube-prometheus-stack-prometheus.observability.svc.cluster.local:9090`, already configured in Radar. It needs neither a new datasource nor pod port-forward permissions. Caretta provides TCP/L4 byte-flow visibility, not HTTP/L7 traces or historical data from before collection started.
- No ingress, PVC, Vault paths, or ExternalSecrets are required. Prometheus retains flow data under its existing retention/storage policy. No explicit sync wave is required in the existing cluster: Prometheus Operator CRDs already exist, and Radar re-detects available traffic sources as metrics become available.

## Validation and reconciliation

```sh
helm dependency build apps/caretta
helm lint apps/caretta
helm template caretta apps/caretta --namespace caretta --api-versions monitoring.coreos.com/v1
```

Merge through the usual GitOps workflow; do not use Radar's Helm install button or manually install this release. After Argo CD reconciles:

```sh
kubectl rollout status daemonset/caretta --namespace caretta --timeout=5m
kubectl get pods,podmonitor --namespace caretta
```

Verify one healthy collector per Linux node and no eBPF load/attach errors in collector logs. In the existing Prometheus UI, check the Caretta PodMonitor targets are UP and `count(caretta_links_observed)` is nonzero while TCP traffic is active. Open Radar Live Traffic, verify Caretta is available/selected, and confirm actual flows. A healthy collector alone is not proof that Prometheus is scraping it.

The existing Alloy/Beyla warning concerns a different collector and is not fixed by changing Caretta scraping; Caretta supplies Radar's requested flow source without changing Alloy instrumentation.

Upstream references: [Caretta requirements and metric labels](https://github.com/groundcover-com/caretta), [chart repository](https://helm.groundcover.com/).
