# EMQX

This chart runs a three-node EMQX cluster with persistent data stored in the
StatefulSet's `emqx-data` claims.

The image is pinned to EMQX 5.8.9. EMQX 5.9 and later require a license for
clustered deployments, so the image must not move to that release line until a
license is configured through the chart's license secret settings.

Dashboard credentials come from the `emqx-dashboard-secret` ExternalSecret and
remain outside Git.
