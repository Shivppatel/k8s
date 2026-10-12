# Sherlock deployment declaration

App-template 5.3.0 wrapper for private Sherlock images. The service uses the Slack section-limit correction from source commit `3160a76115bb5fde56e7892661c4cd95ef4b5a61`; runtime/egress retain the verified `36b8433988345b04c57cf54f56f65a0f641338c3` release. Images are pinned by immutable digest and support AMD64/ARM64. The kubelet uses the Vault-held read:packages credential. [Corrected image publication](https://github.com/Shivppatel/sherlock/actions/runs/38207162642) and [initial publication](https://github.com/Shivppatel/sherlock/actions/runs/38186192394) provide build provenance. Bootstrap/private runtime/testing prerequisites are [#728](https://github.com/Shivppatel/k8s/pull/728), [#730](https://github.com/Shivppatel/k8s/pull/730) and [#731](https://github.com/Shivppatel/k8s/pull/731).

Terraform prerequisites: [#13](https://github.com/Shivppatel/tf/pull/13) and [#14](https://github.com/Shivppatel/tf/pull/14) are applied and merged. Vault `secret/Agents/sherlock` supplies Datadog/Slack, while `secret/Agents/sherlock/webhook` supplies the inbound token through explicit field references. Registry fields in `secret/Agents/sherlock` feed only the kubelet image-pull Secret. GitHub signing key lives in `secret/Agents/sherlock/github`; database role credentials in `secret/Agents/sherlock/database`; public CA in `secret/Agents/sherlock/database-ca`; runtime API token in `secret/Agents/sherlock/runtime`. No values belong in Git.

`ExternalSecret/sherlock-db-secret` in `postgresql` supplies the CNPG managed role. The existing bootstrap/setup resources create only the Sherlock database/schema ownership. The shared setup correction replaces repeated TeslaMate DROP EXTENSION CASCADE operations with CREATE EXTENSION IF NOT EXISTS and existing updates. A dependent table and row survived two runs in disposable PostgreSQL. Only Sherlock's public-schema defaults change. The app uses full database TLS/hostname verification and its own migrations. `PushSecret/sherlock-database-ca` mirrors only ca.crt into the dedicated public-certificate path; private key material is not mirrored or mounted by Sherlock.

In namespace sherlock, ExternalSecrets create sherlock-source-secret, sherlock-db-secret, sherlock-runtime-secret and sherlock-registry-secret. Source secrets/database/projected Kubernetes token mount only in the app. Its ServiceAccount binds the existing GET/LIST sherlock-reader ClusterRole with no new API scopes. Runtime/egress accounts have no bindings or automatic tokens. Registry credentials are not container mounts. NetworkPolicies require an enforcing CNI (Calico is present), and runtime/auth egress is DNS/provider-proxy only; the private-runtime checks verified blocked database/API/source/direct-internet paths against a reachable source-policy baseline, allowed provider CONNECT and rejected unapproved/private destinations. Temporary probes mounted no credentials or auth PVC and were removed.

The retained 1 GiB Longhorn PVC sherlock-codex-auth belongs only to the single-writer native runtime/auth phase. This testing activation declares one runtime replica, leaves the login Job disabled, and enables incident model calls through the private runtime. The owner completed the dedicated Kubernetes login; the completed Job was removed with the PVC preserved. A single 453-byte synthetic provider request returned a validated structured report with unknown cause and known citations in 12.7 seconds; unauthenticated calls returned 401 and invalid envelopes returned 400. No raw report was retained. Runtime limits are one request at a time, a 120-second deadline and 100 KB input; collection lookback is 15 minutes. There is no API-billed fallback. Docker/desktop caches are not copied. Rendering rejects concurrent login/runtime writers.

The enabled testing ingress is sherlock.shivpatel.xyz on Traefik websecure with approved GET review routes and authenticated POST /webhooks/datadog/us5, bounded requests/rate and HTTPS headers. The additional identity-observer POST route is described below. No public readiness, metrics, model, config/admin or mutation routes are declared. Existing wildcard TLS, allowed routes, blocked routes and webhook authentication require an endpoint smoke test after activation. Incident retention remains undecided; no automatic cleanup is applied.

Definition of deployment completion: published immutable private image digests, registry access, all ExternalSecrets ready, exact Argo revisions/Synced/Healthy, database migrations/persistence, CA mirroring, provider credentials and network boundaries, scoped synthetic alert/ack/evidence/report/recovery, and public TLS/authentication boundary. Helm render/server dry-run does not establish any of those live outcomes.

This is a HomeLab testing deployment. Real Datadog retry/renotification/episode identity must be verified before wiring unattended monitor traffic; complete notebook, spans and RUM coverage is not established. Empty or unavailable evidence remains an explicit coverage gap. Private synthetic provider success does not establish root-cause calibration. Production retention and spending policies remain undecided.

Slack section text is capped to 3,000 UTF-8 bytes including the truncation marker. Long validated reports remain available on the review dashboard; both webhook and bot senders preserve character boundaries. An update rejected by Slack with a definite HTTP error can be retried through the operator workflow after verifying the corrected image and exact Argo revision. Ambiguous delivery is held for review. The synthetic testing retry changes only its failed delivery job and does not reanalyze evidence or alter the report.

## Isolated Datadog identity receiver

The identity-probe Job accepts only Datadog monitor `23061575`, initially OK for
`host:node0-homelab` and `host:node1-homelab` with no notification recipients.
The grouped one-minute uptime query retains per-host native multi-alert behavior;
the redundant `notify_by: [host]` option was rejected by Datadog and omitted.

The image is private and pinned to the digest published from reviewed Sherlock
source PR #5. The existing service/runtime/proxy images, auth PVC, reader binding,
database and incident model settings retain their previous desired state.

`sherlock-identity-probe-token` selects only field `identity_probe_token` at the
existing allowed Vault KV-v2 path `secret/Agents/sherlock/webhook`. The existing
service selects only its separate `token` field. The new field must be prepared
with CAS before merge; no new controller permission or Terraform resource is
required. The shared registry pull Secret is used by the kubelet and is not
mounted into the Job. No PVC is created.

The Job uses app-template 5.3.0, an unbound ServiceAccount, no API token or reader
binding, one read-only probe-token mount and no egress. Ingress is limited to
Traefik on port 8091. The exact public POST `/identity/datadog` requires the probe
bearer token and is limited to 8 KB and two requests/second, burst four. There is
no public receiver GET/data/configuration route. Disabling the existing public
ingress also removes this route; disabling NetworkPolicy fails rendering.

The process stops after 44 minutes, allowing graceful exit before the independent
45-minute Job deadline. It never restarts/retries and records at most 32 hashed
identity metadata receipts. One initial 503 deliberately exercises Datadog's
retry; no valid local canary may consume it before the real experiment. This
binary has no database, source connector, provider or Slack client.

The finite Job can keep Argo's aggregate Application health Progressing while it
runs. Check the exact Synced revision, healthy existing Deployments and Ready
observer Pod during the experiment; confirm Synced/Healthy after Job completion
or reviewed cleanup. Its health is not suppressed.

The owner-approved probe field and Datadog integration/hidden variable are prepared
and readback verified. Deployment still requires concrete owner review. Source monitor activation is
a separate step after private-network/auth/method/body/monitor rejection checks.
Only this monitor's threshold/message may change for the two-episode experiment;
existing monitors and notification rules must remain untouched. Stop on an
unexpected destination, identity mismatch, quota or deadline. A test result may
be inconclusive and does not guarantee vendor delivery semantics.

The owner approved one owner-readable sample of at most 32 hashed identity
metadata records, with local sample deletion after aggregate results. No raw
request bodies/headers, prompts or model output are collected by the observer.
Experiment resource cleanup requires its own reviewed changes. Existing
centralized/container logs and backups follow their current policies; resource
removal does not prove their deletion. Sherlock report/evidence retention remains
undecided with cleanup disabled.

Preparation requires Helm dependency build/lint/render, YAML lint, secret scan,
server dry-run and a check that existing rendered objects retain identical specs.
These checks do not establish live deployment. After an approved merge, verify
the exact Argo revision, Secret readiness, actual Pod mounts/RBAC/network boundary
and authenticated public receiver before sending real Datadog notifications.
