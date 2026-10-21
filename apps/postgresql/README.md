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
- Check: with the plugin, `Cluster.status.firstRecoverabilityPoint` and
  `lastSuccessfulBackup` stay empty. Read the recovery window from the
  ObjectStore instead:
  `kubectl -n postgresql get objectstore postgresql-backups -o jsonpath='{.status.serverRecoveryWindow.postgresql}'`
  and list backups with `kubectl -n postgresql get backups.postgresql.cnpg.io`
  (the bare `backup` short name can resolve to another API group).
- A base backup is only restorable once the WAL segment holding its end LSN is
  archived, which can take up to `archive_timeout` (5 minutes) on a quiet
  cluster. A restore started right after a backup may fail once and then
  succeed on retry.

### Restore

Bootstrap a new Cluster with `bootstrap.recovery.source` pointing at an
`externalClusters` entry using the plugin
(`barmanObjectName: postgresql-backups`, `serverName: postgresql`). Use a
different namespace or cluster name; never restore over the live cluster. Give
the new cluster its own `ObjectStore` copy (or the same one in its namespace)
and a different `serverName` if it also archives, so archives never mix.
