# ShivWS Homelab

GitOps-driven Kubernetes platform running on bare-metal.

## Stack

- **GitOps:** ArgoCD with automated sync and self-healing
- **Secrets:** HashiCorp Vault (HA) + External Secrets Operator
- **Observability:** Prometheus, Grafana, Loki, Tempo
- **Ingress:** Traefik + cert-manager + Cloudflare tunnels
- **Storage:** Longhorn
- **Auth:** Authentik SSO
- **Policy:** Kyverno

## Structure

```
apps/
├── argocd/          # GitOps controller
├── vault/           # Secrets management (HA Raft)
├── external-secrets/# Syncs secrets from Vault
├── kube-prometheus-stack/  # Monitoring
├── traefik/         # Ingress controller
├── authentik/       # Identity provider
├── ...              # 49+ applications
```

## CI/CD

- **Renovate** — Automated dependency updates
- **GitHub Actions** — Helm lint + YAML validation on PRs

## Notes

All secrets are stored in Vault and synced via External Secrets. No credentials are committed to this repo.
