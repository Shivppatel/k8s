# Observability connection configuration

Connection lists live in ../values.yaml under `sherlock.config`; every entry has its own stable ID and `enabled` flag. Keep IDs stable across disable/re-enable so stored history stays attributable. Disabling a source prevents credential resolution/client creation and removes its connection-bound network peers. At least one Datadog or Alertmanager intake must stay enabled. Existing mappings/discovery references can remain when their connection is disabled.

| Connection | Existing internal endpoint | Scope / evidence |
| --- | --- | --- |
| homelab-metrics | kube-prometheus-stack-prometheus.observability:9090 | Namespace/pod restart/readiness/CPU and Service-target scrape templates; 25 series and bounded samples |
| homelab-logs | loki-gateway.observability:80 | Namespace/pod LogQL, tenant 1; newest 50 entries |
| homelab-traces | tempo-distributed-query-frontend.tempo-distributed:3200 | Namespace TraceQL; up to 20 matches, not complete traces |
| homelab-dashboards | kube-prometheus-stack-grafana.observability:80 | Only UID homelab-observability, <=20 panel definitions; public link uses grafana.shivpatel.xyz |
| homelab-profiles | pyroscope.observability:4040 | Namespace CPU/in-use-memory profiles; <=50 nodes requested, top 20 individual self/inclusive hot frames |

These private HTTP endpoints have explicit plaintext opt-in and exact current Service-IP CIDRs. Recreated Services with different IPs require a reviewed value update; do not widen to the cluster CIDR. NetworkPolicy destination ports are actual pod ports after Service translation: Grafana 3000 and Loki gateway 8080, rather than their Service port 80. All source grants apply only to Sherlock's service, never the model runtime.

Templates accept unquoted `{{namespace}}`, `{{pod}}`, `{{service}}`, `{{kubernetes_service}}`, `{{workload}}`, `{{host}}`, `{{cluster}}` and `{{environment}}`; the collector supplies literal-quoted safe bindings. Operators choose actual signal names and selectors. The fourth Prometheus query binds `up` to the native Kubernetes namespace/Service labels. This selector is distinct from the Datadog/telemetry service alias; neither substitutes for the other. A failed scrape is not proof of an application outage or its underlying cause. Missing Service bindings skip that query with a coverage gap. Missing pod/namespace attributes skip the query, not the scope check. Native Alertmanager label mappings are explicit configuration, not proof of Argo ownership. Host-only alerts may have no namespace telemetry; do not infer a workload from node scope.

`secret/Agents/sherlock/observability` contains `grafana_token` and `alertmanager_webhook_token`. The service ExternalSecret selects only active Grafana/intake fields; an optional service-only projection permits both to be disabled. Enabled sources with missing credentials fail startup before database access. The Grafana Viewer account has broader org read/data-source-query privileges than Sherlock's fixed UID adapter. Its prepared token expires 2026-10-22T16:00:52Z and must be renewed for continued reads; no automatic renewal or perpetual access is claimed. Values never belong in Git.

homelab-alerts accepts authenticated native v4 POST at the internal Service route `/webhooks/alertmanager/homelab-alerts`. One connection + full labels + exact startsAt produces one incident. Firing repeats deduplicate; recovery affects only that episode, while Datadog renotifications retain their separate-incident policy. Datadog and native incidents remain separate. Only binding/name/severity labels and selected redacted annotations are stored; other labels affect only the identity hash.

The sender is independently switched with `kube-prometheus-stack.sherlockReceiver.enabled` in ../../kube-prometheus-stack/values.yaml. Its URL, matcher list, optional scope-profile children and timings are editable in that values block. The committed sender forwards warning/critical namespace alerts across all namespaces through the reviewed scope profiles, after compatible consumer readiness. Matching alerts also retain canonical Slack delivery. Real data is redacted and bounded before the existing provider and public testing dashboard. Continuing forwarding requires the exact activation review; a boolean alone is not authorization.

## Native scope profiles

The service declares seven additional independently switchable private intake IDs. All use the same existing Alertmanager bearer and pod peer. They separate evidence scope, not authentication roles. Keep connection IDs and classification rules stable: moving a firing episode between IDs can create another incident because connection identity is part of its key.

| Connection suffix | Canonical input labels | Purpose |
| --- | --- | --- |
| homelab-pod-alerts | namespace, pod, cluster | kube-state-metrics pod/container conditions; discard exporter service |
| homelab-workload-alerts | namespace, deployment/statefulset/daemonset, cluster | Workload conditions; discard exporter pod and service |
| homelab-namespace-alerts | namespace, cluster | Namespace-only conditions such as PDB health |
| homelab-node-alerts | node, cluster | Host context; missing namespace skips namespace queries |
| homelab-target-alerts | namespace, service, cluster | TargetDown service ownership; no claimed Datadog service alias |
| homelab-pvc-alerts | namespace, persistentvolumeclaim, cluster | Storage alerts (PVC capacity, inodes, errors). Binds the `persistentvolumeclaim` scope key and `{{persistentvolumeclaim}}` placeholder; adds a PVC snapshot and selects the `pvc-capacity` Prometheus query profile |
| homelab-unbound-alerts | cluster | Unknown alert families; retain alert metadata and gaps without promoting unknown target labels into query scope |

Seven exact pod/alert-name mappings bind the configured Kafka controller pods and Trivy operator pod to their Argo applications. They were prepared from current controller UIDs, self-referencing tracking annotations and Argo resource membership; they are editable operator assertions, not continuous UID pins. A replacement Trivy pod needs a reviewed mapping update; unmatched pod alerts retain their namespace/pod telemetry but cannot infer Argo ownership from pod name alone. Workload/service profiles use the existing bounded ownership discovery when available. Conflicting or missing relationships remain gaps.

None of these native profiles invents a Datadog service name. Without an independently configured service binding, Datadog logs/spans/RUM/events are skipped explicitly even though the source is enabled. A kube-state-metrics `service` label identifies the exporter and must not become the failing application's telemetry alias. Prometheus/Loki/Tempo/Pyroscope retain the configured namespace/pod query limits; namespace aggregates do not prove which workload caused a condition.

The chart deduplicates shared Alertmanager NetworkPolicy peers, so all profiles retain the existing single ingress grant. Disabling one profile removes that private intake but leaves a shared grant while another profile uses it. Disabling every native intake removes the grant and native bearer projection. Grafana's independently enabled token remains. Sender routes must only target enabled consumers; disabling a consumer alone leaves Alertmanager retrying its rejected notifications.

Optional `sherlockReceiver.profiles` entries require distinct bounded receiver names, explicit matchers and native intake URLs on the parent's exact origin. Children stop after their first match. A reviewed broad route can mirror to the unchanged original Slack receiver while selecting exactly one Sherlock profile. Unknown families use the parent unbound profile. Full-label grouping preserves individual episodes and avoids truncation; inhibition/silences still apply. The exact sender matchers select warning/critical namespace alerts; unknown families use the unbound parent. Each profile must stay enabled while the sender targets it.

All enabled sources share the existing 15-minute incident window, four concurrent reads, sixteen query tasks and 30-second collection deadline. Model budget remains 50 attempts/New York day, including retries. Namespace-wide searches can be incomplete; error logs, trace matches, sampled hot frames and current dashboard definitions are observations, not verified RCA. Profile self/inclusive values overlap and retain units; do not reinterpret memory-in-use as allocation rate or claim CPU utilization/leaks without additional evidence/baselines.

A read-only 2026-10-16 snapshot found fourteen active, unsilenced/uninhibited warning alerts matching the broad namespace filter (nine Kafka, four Trivy and one Longhorn). That is a snapshot, not an activation forecast. Enabling the broad route can create more incidents/Slack updates than the 50-attempt AI cap; deterministic overflow retains evidence and an explicit daily-limit report. The owner selected all namespaces and eligible alerts for this reviewed continuing pilot. The 50-attempt limit also applies to new critical alerts after capacity has been spent. Initial processing may exceed capacity; overflow is explicit and does not create a next-day AI backlog. Some existing episodes began days earlier. Their original startsAt stays authoritative: the 15-minute telemetry window ends at that occurrence, while current Kubernetes/Argo snapshots describe collection time. Historical retention gaps do not prove incident-time health.

The sender's `mirrorToExistingSlack` defaults to true, preserving normal Slack delivery for matching alerts. A separately reviewed narrow synthetic pilot can set it false and use unique test matchers so that test notifications reach only Sherlock's configured test channel; unmatched real alerts still use the original receiver. Optional `routeTiming` keys group_wait/group_interval/repeat_interval inherit the existing policy when omitted. These values do not execute a test or enable traffic by themselves.

The HomeLab sender selects warning/critical alerts with a nonempty namespace and mirrors them to the unchanged canonical Slack route. Known kube-state-metrics pod/container, workload, PDB and TargetDown families select their respective scope profiles. Other eligible families reach the unbound parent. The unique existing synthetic marker has a dedicated child, without a generating rule. Root timings inherit 30-second group wait, 5-minute group interval and 12-hour repeat; one incident per full-label episode persists across repeats. Original startsAt remains authoritative even for old episodes, and real unresolved alerts are not given synthetic recoveries.

Forwarding continues after the initial observed window. To pause only broad forwarding, restore the reviewed test-only matcher/timings and empty profiles while keeping `enabled: true`; that changes the Alertmanager config without removing its bearer mount or ExternalSecret. A full `enabled: false` also removes those resources/mounts and can restart the single replica. Either pause stops real recovery delivery to Sherlock, which may leave incidents open; canonical paging remains intact and Sherlock must not invent resolutions. Configuration changes and source-state reconciliation require review; no cleanup or infrastructure repair is implied.

## PVC alert intake and storage mappings

Alerts that carry a `persistentvolumeclaim` label reach `homelab-pvc-alerts` through the first `sherlockReceiver.profiles` child, `sherlock-pvc`, which matches `persistentvolumeclaim!=""` and stops there. Keep it ahead of the pod, workload and generic profiles or those would claim the alert first. The profile list is capped at twelve children. The connection maps `kube_namespace`, `persistentvolumeclaim` and `kube_cluster_name` to `namespace`, `persistentvolumeclaim` and `cluster`. `homelab-unbound-alerts` also maps `kube_namespace` to `namespace`. `homelab-pvc-alerts` shares the existing Alertmanager NetworkPolicy peer and bearer.

`storageAlertMappings` in `../values.yaml` is expanded by `templates/configmap.yaml` into one mapping per namespace and storage alert name (18 namespaces x 3 alert names = 54). Each selects the Prometheus `pvc-capacity` query profile on `homelab-metrics`. Add a namespace to `storageAlertMappings.applications` (namespace to Argo application), not a hand-written mapping. These are operator assertions about which alerts use the profile, not evidence of capacity trends or root cause.

## Evidence collected per alert

Beyond the telemetry sources above, the pinned service collects: GitOps path history (`github_path_history`) for the bound Argo application path; Kubernetes events for the pod or workload (with a `pre_window_warnings` section for warnings that predate the 15-minute window) and PVC snapshots; compact Prometheus/Loki summaries in place of raw series and repeated lines; and `prior_incidents`, a short history of earlier incidents with the same identity. Quota-limited model attempts are deferred (`model_retry_deferred`) rather than consuming the daily budget. These observations are bounded context, not verified RCA.

## Service metrics

Sherlock serves Prometheus metrics at `GET /metrics` on its main port (8080). Desired state:

- `templates/service-monitor.yaml` scrapes Service `sherlock`, port `http`, path `/metrics`, every 30 seconds (`serviceMonitor.enabled`). The Prometheus `serviceMonitorSelector` is empty, so no extra label is needed.
- `networkPolicy.metricsScrapers` admits the Prometheus pods (namespace `observability`, labels `app.kubernetes.io/name: prometheus` and `operator.prometheus.io/name: kube-prometheus-stack-prometheus`) to TCP 8080 on the app pod. A scraper that can reach 8080 can also reach the bearer-authenticated webhook routes, but cannot use them without a token.
- `../../kube-prometheus-stack/templates/sherlock-rules.yaml` holds the `PrometheusRule` (label `release: kube-prometheus-stack`), taken from the Sherlock `docs/OPERATIONS.md`.
- The public Traefik `IngressRoute` allowlists only `/`, `/healthz`, incident review paths, the Datadog webhook and feedback paths. `/metrics` is not routed publicly; the public host returns 404.

Each finished investigation attempt writes a structured `investigation job finished` log line (`investigation job failed` at WARN on error). No secrets or evidence content are logged.
