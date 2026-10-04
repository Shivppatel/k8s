"""Offline checks of the manifests consumed by Argo CD."""

from functools import lru_cache
from pathlib import Path
import subprocess
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
API_VERSIONS = (
    "monitoring.coreos.com/v1",
    "external-secrets.io/v1",
    "traefik.io/v1alpha1",
    "argoproj.io/v1alpha1",
    "kyverno.io/v1",
    "kyverno.io/v2",
)


@lru_cache(maxsize=None)
def render(app: str, namespace: str) -> dict:
    command = ["helm", "template", app, str(ROOT / "apps" / app), "--namespace", namespace]
    for version in API_VERSIONS:
        command.extend(["--api-versions", version])
    output = subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)
    resources = [document for document in yaml.safe_load_all(output.stdout) if document]
    return {(resource["kind"], resource["metadata"]["name"]): resource for resource in resources}


class LonghornMonitoringTest(unittest.TestCase):
    def test_only_intended_prometheus_peer_can_scrape_manager_port(self) -> None:
        policy = render("longhorn", "longhorn-system")[("NetworkPolicy", "longhorn-manager")]
        self.assertEqual(policy["spec"]["podSelector"], {"matchLabels": {"app": "longhorn-manager"}})
        self.assertEqual(policy["spec"]["policyTypes"], ["Ingress"])
        scrape_rules = [rule for rule in policy["spec"]["ingress"] if "ports" in rule]
        self.assertEqual(len(scrape_rules), 1, "The deployed scraper needs a dedicated policy rule")
        self.assertEqual(scrape_rules[0], {
            "from": [{
                "namespaceSelector": {"matchLabels": {"kubernetes.io/metadata.name": "observability"}},
                "podSelector": {"matchLabels": {
                    "app.kubernetes.io/name": "prometheus",
                    "prometheus": "kube-prometheus-stack-prometheus",
                }},
            }],
            "ports": [{"protocol": "TCP", "port": 9500}],
        })


class ArgoProfilingTest(unittest.TestCase):
    def test_advertised_repo_server_profiler_is_enabled(self) -> None:
        resources = render("argocd", "argocd")
        params = resources[("ConfigMap", "argocd-cmd-params-cm")]["data"]
        self.assertEqual(params.get("reposerver.profile.enabled"), "true")
        repo = resources[("Deployment", "argocd-repo-server")]["spec"]["template"]
        self.assertEqual(repo["metadata"]["annotations"]["profiles.grafana.com/cpu.scrape"], "true")
        items = [item for volume in repo["spec"]["volumes"]
                 for item in volume.get("configMap", {}).get("items", [])]
        self.assertIn({"key": "reposerver.profile.enabled", "path": "profiler.enabled"}, items)


class DatadogPermissionsTest(unittest.TestCase):
    def test_operator_can_reconcile_internal_resources(self) -> None:
        resources = render("datadog", "datadog")
        role = resources[("ClusterRole", "datadog-datadog-operator")]
        permissions = {resource: set(rule["verbs"]) for rule in role["rules"]
                       if rule.get("apiGroups") == ["datadoghq.com"]
                       for resource in rule["resources"] if resource.startswith("datadogagentinternals")}
        self.assertEqual(permissions, {
            "datadogagentinternals": {"create", "delete", "get", "list", "patch", "update", "watch"},
            "datadogagentinternals/finalizers": {"create", "delete", "get", "list", "patch", "update", "watch"},
            "datadogagentinternals/status": {"get", "patch", "update"},
        })
        binding = resources[("ClusterRoleBinding", "datadog-datadog-operator")]
        self.assertEqual(binding["roleRef"]["name"], role["metadata"]["name"])
        self.assertIn({"kind": "ServiceAccount", "name": "datadog-datadog-operator",
                       "namespace": "datadog"}, binding["subjects"])


class DatadogImageTest(unittest.TestCase):
    def test_pg18_compatible_image_preserves_community_integrations(self) -> None:
        dockerfile = (ROOT / "apps/datadog/Dockerfile.emqx").read_text()
        self.assertRegex(dockerfile.splitlines()[0], r"^FROM gcr.io/datadoghq/agent:7\.74\.0-jmx@sha256:[a-f0-9]{64}$")
        installs = [line for line in dockerfile.splitlines() if line.startswith("RUN agent integration")]
        self.assertEqual(installs, [
            "RUN agent integration install -r -t datadog-emqx==1.1.0",
            "RUN agent integration install -r -t datadog-grafana==1.0.0",
            "RUN agent integration install -r -t datadog-nextcloud==2.0.0",
        ])
        agent = render("datadog", "datadog")[("DatadogAgent", "datadog")]
        image = agent["spec"]["override"]["nodeAgent"]["image"]
        self.assertTrue(image["jmxEnabled"])
        self.assertEqual(image["name"].split("@")[0],
                         "ghcr.io/shivppatel/datadog-agent-emqx:7.74.0-jmx-emqx-1.1.0-grafana-1.0.0-nextcloud-2.0.0")


if __name__ == "__main__":
    unittest.main()
