# Responder feedback preparation

The owner selected a separate Cloudflare Access protected feedback page and only their human identity for the initial HomeLab pilot. Current app values do not enable collection. This document adds no manifests, identity values, network grants or model calls.

The product feature is an opt-in GET/POST `/feedback/incidents/{id}` form. Protect `/feedback/*` with its own Access application, owner-only Allow policy and dedicated audience. Sherlock also validates the signed human assertion, exact issuer/audience/subject and expiry, and rejects service-token identities. No Home Network/Everyone bypass and no webhook/runtime-token reuse. Keep the incident dashboard publicly readable with no public feedback records or author fields.

Future reviewed service configuration belongs in `sherlock.config.feedback` in ../values.yaml:

```yaml
feedback:
  enabled: true
  issuer: https://YOUR-TEAM.cloudflareaccess.com
  audience: DEDICATED_FEEDBACK_APPLICATION_AUD
  allowed_subject: {file: /run/feedback/allowed_subject}
  comments_enabled: false
```

This is an incomplete example, not an activation instruction. Resolve team issuer/audience and exact owner subject privately; no owner email or subject values in public Git. Proposed subject reference: Vault KV v2 `secret/Agents/sherlock/feedback`, field `allowed_subject`, mounted through a dedicated reviewed ExternalSecret. The subject is an identity allowlist, not a credential granting Vault access. No entry, Vault permission, ExternalSecret or mount is created in this documentation change. Terraform owns any Vault external-secrets policy extension and must be reviewed/applied before the Kubernetes rollout.

Feedback records append installation/incident, digest of the exact saved report and evidence, model/prompt provenance, verdict, pseudonymous authenticated author and time. Four verdicts: accurate, partly accurate, inaccurate, insufficient evidence. Recovery/Slack revisions do not invalidate a report review; changed report/evidence/provenance does. Identical retries are idempotent, with ten accepted assessments per author per rolling hour. Native form CSRF and same-origin controls are independent of Access authentication. A revised assessment appends history, rather than replacing the original; don't count one person's revisions as independent votes.

Optional corrections remain disabled. They need an explicit capture/visibility/retention decision before use. Feedback/report retention remains undecided; no cleanup schedule is introduced. Feedback neither edits the RCA nor resolves incidents, triggers investigations/Slack, changes prompts or trains the model.

The source feature requires schema 6. A future service rollout will migrate schema 5 even if feedback is disabled; old schema-5 images cannot restart afterward. Review quiescence, database recovery, image/config, signed-JWT boundary checks and one owner-submitted test assessment before enabling it. The auth PVC/runtime/egress/source scopes and eight-attempt New York AI budget need no change for feedback. New images, migration, Access setup, secret references and live capture are separate reviews.

Related: ../ai/README.md exposes model/prompt/context configuration. Prompts are explicitly mounted evidence-only context; feedback does not automatically update them. The five-case v4 fictional evaluation found useful uncertainty/injection handling but a dependency hypothesis overstated causality. A subsequent profile refinement should qualify suspected causal wording and distinguish direct contradictions from missing history; it needs review and its own semantic evaluation, not an unmeasured accuracy claim.
