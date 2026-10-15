# Responder feedback preparation

The HomeLab feedback page uses the full existing Homelab Lockdown human Allow policy: three private email identities, with its existing sign-in providers and 24-hour session. Values enable attributed assessments with an explicit retention hold pending an owner deletion/retention decision. Optional corrections stay disabled. This feature does not invoke the model or Slack.

The product feature is an opt-in GET/POST `/feedback/incidents/{id}` form. Protect `/feedback/*` with its own Access application, existing human Allow policy and dedicated audience. Sherlock also validates the signed human assertion, exact issuer/audience/expiry and signed human membership, and rejects service-token identities. No Home Network/Everyone bypass and no webhook/runtime-token reuse. Keep the incident dashboard publicly readable with no public feedback records or author fields.

Service configuration belongs in `sherlock.config.feedback` in ../values.yaml:

```yaml
feedback:
  enabled: true
  issuer: https://shivppatel.cloudflareaccess.com
  audience: e2f0a6566722fc9026e207a8337c488124d9e2520c43eaa34e45c2ee594c74b8
  allowed_emails: {file: /run/feedback/allowed_emails}
  comments_enabled: false
```

Cloudflare application `73ccdef7-8315-4e96-92d6-80eea3eba4ea` protects `sherlock.shivpatel.xyz/feedback/*` with only the existing Homelab Lockdown Allow policy attached. The dedicated audience above is public configuration, not a bearer credential. The backend accepts a bounded private JSON list only after signature and human-token verification; an email request header alone confers no access. Attribution still uses the signed subject. Shared edge policy changes require a matching reviewed private mirror update; there is no automatic synchronization or fallback to all signed-in users.

Vault KV v2 `secret/Agents/sherlock/feedback`, field `allowed_emails`, is mirrored by `ExternalSecret/sherlock-feedback-secret` and mounted read-only at `/run/feedback` in the service only. No email/subject values are in public Git. The prepared mirror/mount remains available independently of the feedback route switch; disabling collection must omit the populated feedback identity settings, as required by service configuration validation. Terraform [PR #15](https://github.com/Shivppatel/tf/pull/15) applied the exact read-only path prerequisite before this consumer change. The backup recovery-key path is excluded from External Secrets access.

Only GET/POST `/feedback/incidents/{32 lowercase hex characters}` is routed to the service. A separate middleware chain preserves the existing rate/body bounds and sets `Referrer-Policy: same-origin` for native form submission; dashboard/webhook routes retain their original headers. No bypass, service token, wildcard Access change, new source access or runtime mount is needed. The configured issuer's fixed JWKS endpoint uses the service's existing HTTPS egress grant.

Feedback records append installation/incident, digest of the exact saved report and evidence, model/prompt provenance, verdict, pseudonymous authenticated author and time. Four verdicts: accurate, partly accurate, inaccurate, insufficient evidence. Recovery/Slack revisions do not invalidate a report review; changed report/evidence/provenance does. Identical retries are idempotent, with ten accepted assessments per author per rolling hour. Native form CSRF and same-origin controls are independent of Access authentication. A revised assessment appends history, rather than replacing the original; don't count one person's revisions as independent votes.

Assessments are held until the owner decides deletion/retention; there is no automatic cleanup. Optional corrections remain disabled and need a separate capture/visibility/retention decision before use. Report/evidence retention remains undecided. Feedback neither edits the RCA nor resolves incidents, triggers investigations/Slack, changes prompts or trains the model.

The source feature requires schema 6. Startup migrates schema 5 even if collection is disabled; old schema-5 images cannot restart afterward. The live rollout review must require quiescence, a verified Sherlock-only encrypted backup and isolated restore rehearsal, exact image/config checks, signed-JWT rejection boundaries and one owner-submitted assessment. A failure afterward needs a separately reviewed forward fix or Sherlock-only restore, never an automatic shared-cluster restore. The auth PVC/runtime/egress/source scopes and eight-attempt New York AI budget need no change for feedback. Preparing this GitOps source does not authorize live rollout or the owner-submitted assessment; those need the exact rollout review.

Related: ../ai/README.md exposes model/prompt/context configuration. Prompts are explicitly mounted evidence-only context; feedback does not automatically update them. The five-case v4 fictional evaluation found useful uncertainty/injection handling but a dependency hypothesis overstated causality. A subsequent profile refinement should qualify suspected causal wording and distinguish direct contradictions from missing history; it needs review and its own semantic evaluation, not an unmeasured accuracy claim.
