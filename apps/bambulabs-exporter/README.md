# BambuLabs Exporter Helm Chart

This Helm chart deploys the BambuLabs Prometheus Exporter to Kubernetes.

## Prerequisites

- Kubernetes cluster
- ArgoCD (for GitOps deployment)
- Prometheus Operator (for ServiceMonitor)

## Configuration

### Required Environment Variables

The exporter requires configuration via environment variables. Update the `values.yaml` file with your BambuLabs printer details:

```yaml
env:
  - name: BAMBU_HOST
    value: "192.168.1.100"  # Your printer's IP address
  - name: BAMBU_ACCESS_CODE
    valueFrom:
      secretKeyRef:
        name: bambulabs-secret
        key: access-code
```

### Creating the Secret

Before deploying, create a Kubernetes secret with your printer's access code:

```bash
kubectl create secret generic bambulabs-secret \
  --from-literal=access-code=YOUR_ACCESS_CODE \
  -n bambulabs-exporter
```

Or use External Secrets Operator if you have it configured.

## Deployment

### GitOps (Recommended)

This chart is designed to be deployed via ArgoCD. Simply commit and push your changes:

```bash
git add apps/bambulabs-exporter/
git commit -m "Add bambulabs-exporter"
git push
```

Then apply the ArgoCD application:

```bash
kubectl apply -f apps/bambulabs-exporter/application.yaml
```

### Manual Helm Deployment

```bash
helm install bambulabs-exporter ./apps/bambulabs-exporter \
  --namespace bambulabs-exporter \
  --create-namespace
```

## Monitoring

The chart includes a ServiceMonitor resource that will be automatically discovered by Prometheus if `serviceMonitor.enabled` is set to `true` (default).

Metrics will be available at: `http://bambulabs-exporter:9090/metrics`

## Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | `shivppatel/bambulabs-exporter` |
| `image.tag` | Image tag | `0.1.0` |
| `service.port` | Service port | `9090` |
| `serviceMonitor.enabled` | Enable Prometheus ServiceMonitor | `true` |
| `serviceMonitor.interval` | Scrape interval | `30s` |
| `env` | Environment variables | `[]` |
