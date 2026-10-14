# Sherlock deployment declaration

App-template 5.3.0 wrapper for private Sherlock images. The service includes the verified dashboard/compact Slack presentation, citation readability, MIME compatibility and optional durable daily-model budget from source commit `811be5c10939352511f73512ed12065fe48dd6ba`; runtime/egress retain the verified `36b8433988345b04c57cf54f56f65a0f641338c3` release. Images are pinned by immutable digest and support AMD64/ARM64. The kubelet uses the Vault-held read:packages credential. [Budget/citation release publication](https://github.com/Shivppatel/sherlock/actions/runs/38484595434), [native-contract release publication](https://github.com/Shivppatel/sherlock/actions/runs/38428733752), [presentation release publication](https://github.com/Shivppatel/sherlock/actions/runs/38329864769) and [initial publication](https://github.com/Shivppatel/sherlock/actions/runs/38186192394) provide build provenance. Bootstrap/private runtime/testing prerequisites are [#728](https://github.com/Shivppatel/k8s/pull/728), [#730](https://github.com/Shivppatel/k8s/pull/730) and [#731](https://github.com/Shivppatel/k8s/pull/731).

## Daily analysis budget and schema compatibility

The service configuration sets eight service-managed provider-analysis attempts per America/New_York calendar day across all connections/workers. Successes, failures and retries consume durable permits. Exhausted incidents retain evidence and an explicit unknown-cause budget-limited report; they are not automatically analyzed tomorrow. This does not cap incident storage, source reads, Slack posts or account-wide/token usage. Retention remains undecided and cleanup disabled.

Service startup migrates schema 4 to 5: one durable job-denial flag, one reservation table and its installation/day index. No historical requests are invented and no incident/report data is deleted. The Recreate strategy stops old workers before starting the new service. Require an empty investigation queue before the rollout and verify schema 5 afterward, without valid alerts or model/Slack calls. Older schema-4 executables refuse schema 5 on startup; an image-only rollback to the old service is unsupported. Use a separately reviewed compatible forward fix or restore. Runtime/egress pins, auth PVC, credentials/scopes/routes and completed probe Jobs remain intact.

The normal US5 webhook integration/Service Auth setup and bounded native trigger/ten-minute-renotify/recovery workflow are verified. Real monitor wiring remains a separate review after budget activation; adding this configuration does not activate monitor notifications.

Terraform prerequisites: [#13](https://github.com/Shivppatel/tf/pull/13) and [#14](https://github.com/Shivppatel/tf/pull/14) are applied and merged. Vault `secret/Agents/sherlock` supplies Datadog/Slack, while `secret/Agents/sherlock/webhook` supplies the inbound token through explicit field references. Registry fields in `secret/Agents/sherlock` feed only the kubelet image-pull Secret. GitHub signing key lives in `secret/Agents/sherlock/github`; database role credentials in `secret/Agents/sherlock/database`; public CA in `secret/Agents/sherlock/database-ca`; runtime API token in `secret/Agents/sherlock/runtime`. No values belong in Git.

`ExternalSecret/sherlock-db-secret` in `postgresql` supplies the CNPG managed role. The existing bootstrap/setup resources create only the Sherlock database/schema ownership. The shared setup correction replaces repeated TeslaMate DROP EXTENSION CASCADE operations with CREATE EXTENSION IF NOT EXISTS and existing updates. A dependent table and row survived two runs in disposable PostgreSQL. Only Sherlock's public-schema defaults change. The app uses full database TLS/hostname verification and its own migrations. `PushSecret/sherlock-database-ca` mirrors only ca.crt into the dedicated public-certificate path; private key material is not mirrored or mounted by Sherlock.

In namespace sherlock, ExternalSecrets create sherlock-source-secret, sherlock-db-secret, sherlock-runtime-secret and sherlock-registry-secret. Source secrets/database/projected Kubernetes token mount only in the app. Its ServiceAccount binds the existing GET/LIST sherlock-reader ClusterRole with no new API scopes. Runtime/egress accounts have no bindings or automatic tokens. Registry credentials are not container mounts. NetworkPolicies require an enforcing CNI (Calico is present), and runtime/auth egress is DNS/provider-proxy only; the private-runtime checks verified blocked database/API/source/direct-internet paths against a reachable source-policy baseline, allowed provider CONNECT and rejected unapproved/private destinations. Temporary probes mounted no credentials or auth PVC and were removed.

The retained 1 GiB Longhorn PVC sherlock-codex-auth belongs only to the single-writer native runtime/auth phase. This testing activation declares one runtime replica, leaves the login Job disabled, and enables incident model calls through the private runtime. The owner completed the dedicated Kubernetes login; the completed Job was removed with the PVC preserved. A single 453-byte synthetic provider request returned a validated structured report with unknown cause and known citations in 12.7 seconds; unauthenticated calls returned 401 and invalid envelopes returned 400. No raw report was retained. Runtime limits are one request at a time, a 120-second deadline and 100 KB input; collection lookback is 15 minutes. There is no API-billed fallback. Docker/desktop caches are not copied. Rendering rejects concurrent login/runtime writers.

The enabled testing ingress is sherlock.shivpatel.xyz on Traefik websecure with approved GET review routes and authenticated POST /webhooks/datadog/us5, bounded requests/rate and HTTPS headers. The additional identity-observer POST route is described below. No public readiness, metrics, model, config/admin or mutation routes are declared. Existing wildcard TLS, allowed routes, blocked routes and webhook authentication require an endpoint smoke test after activation. Incident retention remains undecided; no automatic cleanup is applied.

Definition of deployment completion: published immutable private image digests, registry access, all ExternalSecrets ready, exact Argo revisions/Synced/Healthy, database migrations/persistence, CA mirroring, provider credentials and network boundaries, scoped synthetic alert/ack/evidence/report/recovery, and public TLS/authentication boundary. Helm render/server dry-run does not establish any of those live outcomes.

This is a HomeLab testing deployment. The isolated native probe verified retry/renotification/episode identity for the tested US5 configuration; unattended incident traffic still needs a reviewed integration and Access configuration. Complete notebook, spans and RUM coverage is not established. Empty or unavailable evidence remains an explicit coverage gap. Private synthetic provider success does not establish root-cause calibration. Production retention and spending policies remain undecided.

The overview shows compact incident summaries and page-scoped filters/counts; each investigation separates findings, suggested checks, coverage gaps, timeline and expandable evidence. Slack uses short Block Kit summaries and a trusted **View investigation** link from `dashboard_url: https://sherlock.shivpatel.xyz`. Dynamic source/model text stays plain text; only the application-generated review link uses Slack markup. A normal link needs no interactive App callback. Full reports and action prerequisites/risk/verification/rollback remain on the dashboard. Incoming-webhook mode still appends and delivery/retry handling is retained.

The initial presentation release introduced `dashboard_url`; a rollback to the pre-presentation binary must remove that field as well. The overview correction is an image-only update from the compatible presentation release: it uses actual list metadata for page counts and leaves cause/coverage assessments on the detail page. An image-only rollback to the previous presentation digest keeps the existing URL setting. The release also includes the previously merged exact-group Datadog evidence read from source PR #4; current snapshots are not alert-episode history and do not auto-resolve incidents. The bounded native identity exercise verified retry/group/cycle behavior for its specific US5 configuration. Unattended incident monitor wiring remains deferred pending a reviewed normal-webhook integration and Access configuration. Runtime/proxy images, auth PVC, database, source scopes, credential paths, public routes and testing limits retain their existing desired state.

The current service release parses valid JSON media-type parameters, such as
`application/json; charset=utf-8`, while retaining authentication, schema/body
bounds and the existing durable identity/recovery contract. Unsupported or
malformed media types still return 415. This is an image-only update; an
image-only rollback to the preceding presentation digest retains the current
configuration/schema. Runtime/proxy images and the auth PVC stay unchanged.
The [source review](https://github.com/Shivppatel/sherlock/pull/9) records native
observer evidence separately from synthetic HTTP/PostgreSQL regression results.

## Isolated Datadog identity receiver

The identity-probe Jobs accept only Datadog monitor `23061575`, initially OK for
`host:node0-homelab` and `host:node1-homelab` with no notification recipients.
The grouped one-minute uptime query retains per-host native multi-alert behavior;
the redundant `notify_by: [host]` option was rejected by Datadog and omitted.

The original probe image is private and pinned to the digest published from
reviewed Sherlock source PR #5. Sherlock source PR #8 published a corrected,
probe-only image using MIME media-type parsing for the native webhook's JSON
Content-Type. The retained Jobs pin that image by immutable digest. The probe
image remains independent of the normal-service release above; runtime and proxy
images, auth PVC, reader binding, database and incident model settings retain
their previous desired state.

`sherlock-identity-probe-token` selects only field `identity_probe_token` at the
existing allowed Vault KV-v2 path `secret/Agents/sherlock/webhook`. The existing
service selects only its separate `token` field. The owner-prepared probe field
uses CAS; no new controller permission or Terraform resource is required. The
shared registry pull Secret is used by the kubelet and is not mounted into the
Job. No PVC is created.

Each Job uses app-template 5.3.0, an unbound ServiceAccount, no API token or reader
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
and readback verified. Three previous finite Jobs are retained:
`sherlock-identity-probe`, `sherlock-identity-probe-20261013`, and
`sherlock-identity-probe-20261013-json`. In the prior native attempt using the
older image, two Datadog POSTs reached the receiver but returned HTTP 415, with
zero valid receipts. The experiment stopped before renotification or a second
alert episode. Native request headers were not captured, so the rejection cause
is unknown.

The corrected probe-only image parses JSON media types with parameters, and the
existing Datadog webhook declares `Content-Type: application/json`. A corrected-
image listener was deployed, but its safe 34-minute experiment start margin
expired during preflight. The monitor remained safe and no valid native event was
sent. Five invalid-input boundaries and fresh positive uptime coverage passed.

The retained fourth Job, `sherlock-identity-probe-20261013-json-retry`, uses
that same immutable probe image, 44-minute/32-record limits and existing
read-only token mount. The stable receiver Service selects only that controller;
all prior Jobs and Pods remain declared. The owner-reviewed two-episode native
exercise completed on 2026-10-13 at GitOps revision
`290f0125d0c0337be421469db80991d6787a5e5a`. Thirteen hashed receipts included
one deliberate 503 and its exact accepted retry, four actual `Re-Triggered`
renotifications, and four complete group/cycle combinations. The sole approved
local sample was assessed and deleted. The monitor returned to its safe threshold
and original recipient-free message, with both host groups OK and no matching
notification rules. No incident endpoint, AI, Slack or workload fault was used.

The finite Job exited successfully, so its Service has no ready receiver
endpoint. Updating only the normal service image does not change or restart
these Jobs, activate the source monitor, or collect another sample. Resource,
credential and Access cleanup remain separately reviewed. These observations
support this account/configuration only, not a universal delivery guarantee.

The probe-only Cloudflare Access application for
`sherlock.shivpatel.xyz/identity/datadog` has an owner-reviewed dedicated Bypass
for the published US5 webhook source ranges and the existing home-network Bypass.
The original wildcard application and home policy are preserved. Source ranges
are shared provider infrastructure, not tenant authentication; the independent
receiver bearer token remains mandatory. Recheck the Access destination,
attachments and published ranges before activation. The dashboard and normal
incident webhook still fall under the wildcard Access application; successful
home-network checks do not prove anonymous external access. This probe rerun
does not change their Access boundary.

Deployment and source monitor activation require concrete owner review after
private-network/auth/method/body/monitor rejection checks.
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
