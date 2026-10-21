# postgresql

Shared CloudNativePG cluster `postgresql` (3 instances, 100Gi Longhorn). Argo CD
tracks the raw manifests in `templates/` (auto-sync, self-heal).

## Backups

- Plugin: Barman Cloud CNPG-I plugin from `apps/plugin-barman-cloud`
  (namespace `cloudnative-pg`). It must be Healthy before the Cluster references it.
- Store: `ObjectStore/postgresql-backups` -> MinIO bucket `postgresql-backups`
  (Terraform: `tf/minio/postgresql-backup.tf`), gzip, retention `14d`.
- Credentials: `ExternalSecret/postgresql-backup-s3` reads Vault KV v2
  `secret/postgresql/backup-s3` (`accesskey`, `secretkey`). No values in Git.
- WAL archive: `spec.plugins` on the Cluster with `isWALArchiver: true`.
- Base backups: `ScheduledBackup/postgresql-daily`, 03:00 UTC (six-field cron),
  `immediate: true`.
- On demand: `kubectl -n postgresql create -f` a `Backup` with
  `spec.method: plugin`, `spec.cluster.name: postgresql`,
  `spec.pluginConfiguration.name: barman-cloud.cloudnative-pg.io`.
- Check: `kubectl -n postgresql get cluster postgresql -o jsonpath='{.status.firstRecoverabilityPoint}'`
  and `kubectl -n postgresql get backup`.

### Restore

Bootstrap a new Cluster with `bootstrap.recovery.source` pointing at an
`externalClusters` entry using the plugin
(`barmanObjectName: postgresql-backups`, `serverName: postgresql`). Use a
different namespace or cluster name; never restore over the live cluster. Give
the new cluster its own `ObjectStore` copy (or the same one in its namespace)
and a different `serverName` if it also archives, so archives never mix.
