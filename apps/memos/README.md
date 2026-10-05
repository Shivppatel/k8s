# Memos

Memos uses the same `bjw-s-labs/app-template` 5.2.1 wrapper pattern as Prowlarr.
The chart generates the Deployment, Service, and volumes from `values.yaml`;
Memos 0.31.0 is pinned by tag and image digest. The public app-of-apps inventory
deploys `apps/memos` into namespace `memos` from `main`, with automated sync,
self-healing, and pruning.

## Configuration

- HTTPS: **https://memos.shivpatel.xyz**, a ClusterIP Service on port 5230,
  and a Traefik `IngressRoute` using `websecure` and the default
  `wildcard-cert-new` certificate. Existing DNS/tunnel routing sends the
  hostname to Traefik.
- Vault KV v2 `secret/postgresql/memos`: `username` (`memos`) and `password`.
  `ExternalSecret/memos-db-secret` in `postgresql` follows the shared
  `postgresql-external-secret.yaml` pattern and supplies the CNPG managed role.
  The same ExternalSecret name in `memos` renders a mounted DSN with escaped
  credentials and `sslmode=require`.
- Database creation follows the existing shared PostgreSQL flow:
  `cluster.yaml` includes bootstrap user/database SQL and the non-superuser
  managed role; `setup-job.yaml` creates missing users/databases, grants schema
  ownership, and adds monitoring. Memos creates its application tables through
  its own migrations. There is no separate `Database` CR for Memos.
- Vault KV v2 `secret/memos/s3`: `accesskey` (`memos`) and `secretkey`.
  `ExternalSecret/memos-storage-secret` renders the supported mounted
  `/etc/secrets/memos-instance-setting-storage.json` file. New attachments use
  named storage `minio-attachments`, private bucket `memos-attachments`, region
  `us-east-1`, and path-style access to
  `http://minio.minio.svc.cluster.local:9000`. The upload limit is 30 MiB.
- The companion [Terraform PR #12](https://github.com/Shivppatel/tf/pull/12)
  owns the bucket, scoped MinIO account, and bucket-only read/write policy in
  `minio/`. Its `vault/locals.tf` grants ESO read access to exactly the two new
  Vault paths. Provision both entries before the Atlantis plan and apply the
  Terraform changes before merging this workload. Kubernetes does not provision
  MinIO buckets or users.
- Notes, users, and attachment metadata live in shared PostgreSQL. Attachment
  bytes live in MinIO's existing NAS-backed `minio-nfs` PVC, statically bound
  with an empty storage class. Memos needs no dedicated PVC: `/var/opt/memos`
  and `/tmp` are disposable `emptyDir` volumes. Coordinate PostgreSQL and bucket
  recovery.
- A single non-root replica uses resource limits, health probes, a read-only
  root filesystem, dropped capabilities, and no service-account token. Reloader
  restarts it when either Secret or `memos-config` changes. The init container
  waits for access to the Terraform-managed bucket with the scoped account.

## Reconciliation and first use

ESO and `vault-backend` must be healthy. Within PostgreSQL, the role
ExternalSecret is wave `0`, Cluster is wave `1`, and the existing setup Job
runs PostSync at wave `3`. These waves do not order separate Applications:
Memos can restart until the database is ready. No manual workload apply is
required. For MinIO password rotation, update Vault and apply the `minio`
Terraform project; ESO and Reloader refresh Memos afterward.

The instance uses private access and disables anonymous registration. Memos
permits initial administrator creation even with registration disabled.
Create the first administrator promptly from a trusted connection: until it
exists, anyone who can reach setup can claim the account. Additional users
must be created by an administrator. Password login remains enabled.

After merge, verify `memos` and `postgresql` are Synced/Healthy, the PostgreSQL
setup Job succeeds, and both application ExternalSecrets plus the PostgreSQL
role ExternalSecret are ready. Confirm HTTPS, then upload and retrieve an
attachment through Memos and verify the object exists in the private MinIO
bucket. Changing the default storage does not migrate existing attachments;
preserve the stable storage ID and credentials while objects reference it.

## Validation

```sh
helm dependency build apps/memos
helm lint apps/memos
helm template memos apps/memos --namespace memos
helm lint apps/argocd-apps
helm template argocd-apps apps/argocd-apps --namespace argocd
```

References: [App Template](https://bjw-s-labs.github.io/helm-charts/docs/app-template/),
[deployment-managed configuration](https://usememos.com/docs/configuration/deployment-configuration),
[Memos 0.31.0](https://github.com/usememos/memos/releases/tag/v0.31.0).
