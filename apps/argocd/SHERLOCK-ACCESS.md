# Sherlock reader identity

This chart owns the `sherlock-reader` ServiceAccount in the Argo CD release
namespace and its ClusterRole/ClusterRoleBinding. The owner requested read-only
investigation of every HomeLab namespace, so the role permits `get` and `list`
for workload state, nodes, service endpoints, PVCs, retained events, and Argo
Application/ApplicationSet CRs across the cluster.

The role does not grant access to Secrets, pod exec/attach/log subresources,
audit logs, token creation, RBAC mutation, sync actions, or any resource write.
ServiceAccount token automounting is disabled. It does not install or expose the
Sherlock workload or change Argo CD's own service-account permissions.

External bootstrap tests may use a short-lived TokenRequest credential issued
by an authorized operator and stored in Vault KV v2 under
`secret/Agents/sherlock/kubernetes`. Store fields `server`, `ca_certificate`,
`token`, and `expires_at` through protected process input. Never commit a token
or kubeconfig. An external token expires and needs operator renewal; deployed
Sherlock should use an automatically rotated projected token read from a file.

The existing Argo Application follows `main` and reconciles this chart normally.
No manual live apply is required. No Terraform prerequisite is introduced by
these RBAC-only resources; Vault policy/ExternalSecret prerequisites for the
later Sherlock deployment remain separate.
