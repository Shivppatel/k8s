# Memos

Memos 0.31.0 is pinned by tag and image digest. The public app-of-apps inventory
deploys `apps/memos` into namespace `memos` from `main`, with automated sync,
self-healing, and pruning. HTTPS is available at **https://memos.shivpatel.xyz**
through a ClusterIP Service on port 5230 and a Traefik `IngressRoute` using
`websecure` and the default `wildcard-cert-new` certificate. Existing DNS or
upstream tunnel routing must send this hostname to Traefik.

## Configuration and storage

- Vault KV v2 `secret/postgresql/memos` contains `username` (`memos`) and
  `password`. API references use `secret/data/postgresql/memos` through
  `ClusterSecretStore/vault-backend`.
- `ExternalSecret/memos-db-secret` in `postgresql` supplies the non-superuser
  CNPG managed role. `Database/memos` creates the owned database and retains
  data on deletion. The same ExternalSecret name in `memos` renders the DSN
  with escaped credentials and `sslmode=require`, matching the Coder pattern.
  The container reads the DSN from a mounted file rather than a CLI argument.
- Vault KV v2 `secret/memos/s3` contains `accesskey` (`memos`) and `secretkey`.
  `ExternalSecret/memos-storage-secret` in `memos` renders the supported
  `/etc/secrets/memos-instance-setting-storage.json` file. New attachments use
  named storage `minio-attachments`, private bucket `memos-attachments`, region
  `us-east-1`, and path-style access to
  `http://minio.minio.svc.cluster.local:9000`. The upload limit is 30 MiB.
- The MinIO chart owns the bucket provisioning Sync hook and its bucket-only
  read/write policy. `ExternalSecret/memos-minio-provisioning` in `minio`
  combines the existing `secret/minio` root credentials with the Memos account
  secret. Root credentials stay in the provisioning Job; Memos only receives
  the scoped account. Credentials enter `mc` through files and stdin, and user
  creation output is suppressed. The Job is idempotent, keeps existing
  objects, and disables anonymous bucket access. Removing the chart resources
  does not delete the bucket or account.
- Notes, users, and attachment metadata live in shared PostgreSQL. Attachment
  bytes live in MinIO's existing NAS-backed `minio-nfs` PVC, statically bound
  with an empty storage class. Memos needs no dedicated PVC: `/var/opt/memos` and `/tmp` are disposable
  `emptyDir` volumes. Database and bucket recovery must be coordinated.
- A single non-root replica uses resource limits, health probes, a read-only
  root filesystem, dropped capabilities, and no service-account token. Reloader
  restarts the deployment when either Secret changes. A ConfigMap checksum
  applies access-policy changes through a rollout.

## Reconciliation and first use

Provision the two application Vault paths before merge. ESO and `vault-backend`
must be healthy. Within PostgreSQL, the ExternalSecret is wave `0`, Cluster
is wave `1`, and Database is wave `2`. Within MinIO, the provisioning Secret
and policy are wave `0` and the Sync hook is wave `1`. Waves do not order
separate Applications: the Memos init container waits for bucket access, and
Memos can restart until the database is ready. No manual workload apply is
required. Rotate the MinIO password in Vault and sync `minio` to rerun its
provisioning hook; ESO and Reloader refresh Memos afterward.

The instance uses private access and disables public user registration.
Memos permits initial administrator creation even with registration disabled.
Create the first administrator promptly from a trusted connection: until it
exists, anyone who can reach setup can claim the account. Additional users
must be created by an administrator. Password login remains enabled.

After merge, verify `memos`, `minio`, and `postgresql` are Synced/Healthy,
`Database/memos` is reconciled, and all three new ExternalSecrets are ready.
Confirm HTTPS, then upload and retrieve an attachment through Memos and verify
the object exists in the private MinIO bucket. Changing the default storage
does not migrate existing attachments; preserve the stable storage ID and
credentials while referenced objects exist.

## Validation

```sh
helm dependency build apps/memos
helm lint apps/memos
helm template memos apps/memos --namespace memos
helm lint apps/minio
helm template minio apps/minio --namespace minio
helm lint apps/argocd-apps
helm template argocd-apps apps/argocd-apps --namespace argocd
```

References: [Deployment-managed configuration](https://usememos.com/docs/configuration/deployment-configuration),
[database configuration](https://usememos.com/docs/configuration/database),
[Memos 0.31.0](https://github.com/usememos/memos/releases/tag/v0.31.0).
