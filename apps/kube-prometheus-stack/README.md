# Sherlock notification routing

`values.yaml` keeps the existing Alertmanager Slack/inhibition configuration as the source of truth. The optional `sherlockReceiver` block adds a separate authenticated internal receiver without modifying its definitions.

The committed route remains restricted to `SherlockObservabilityIntegrationTest`, the unique existing `sherlock_probe` marker and namespace `observability`. No rule generates this marker. Adding scope-profile template support does not enable real-alert forwarding.

`enabled` switches the Sherlock branch. `matchers` select its eligibility. `mirrorToExistingSlack` determines whether matching alerts also reach the original Slack route; it remains false for the isolated test marker. Omitted `routeTiming` keys inherit the existing policy. Full-label grouping keeps separate native alert episodes; the original Watchdog null route and inhibition rules remain in force.

Optional `profiles` are ordered child routes sharing the parent URL's exact scheme/host, native intake path pattern and existing bearer file. Every entry needs a unique `sherlock-` name, nonempty matchers and a compatible enabled Sherlock consumer. At most twelve children are accepted. Credentials, fragments, query strings, arbitrary paths and cross-origin destinations are rejected. Each child stops after its first match; the parent handles unmatched alerts. These are evidence-scope profiles within one trusted Alertmanager boundary, not independent authentication roles.

A future broad activation must first deploy and verify the compatible Sherlock image/configuration, then change only the generated Alertmanager configuration. Reversing that order sends notifications to missing consumers. Public Git publication, real-data exposure and persistent forwarding require the reviewed activation decision. Existing Slack remains the canonical paging path; Sherlock provides additional investigation messages in its test channel. The eight-attempt model budget does not bound incident count, evidence reads or Slack volume.

See [Sherlock observability configuration](../sherlock/observability/README.md) for source switches, profile bindings, credential references, retention limits and deployment boundaries.
