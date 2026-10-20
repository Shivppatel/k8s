# Ingress services

The shared internal ingress service uses `192.168.20.20` and the existing
`web`/`websecure` entrypoints. These remain the defaults for routers that do not
declare an entrypoint explicitly.

The separate Jellyfin service uses `192.168.20.21:443` and the
`jellyfin-public` entrypoint. It preserves client source addresses with
`externalTrafficPolicy: Local`, uses the existing TLS certificate and security
headers, and is exposed only by the explicit Jellyfin router. Unmatched
hostnames receive no application route.

Use the dedicated Jellyfin service as the destination for a reviewed external
HTTPS forwarding rule. Forwarding external traffic to the shared internal
service would make unrelated application routes reachable. Upstream router
forwarding and public DNS are managed separately from this chart.
