# Jellyfin storage

Jellyfin uses Longhorn PVCs for configuration and cache, and separate NFS PVCs
mounted at `/media/books`, `/media/shows`, `/media/movies`, and `/media/music`.
The parent `/media` mount is an `emptyDir` with `persistence.media.enabled: false`
and `persistence.media.readOnly: false`. Keep this temporary parent writable so
the container runtime can create the nested NFS mountpoints during startup.

The public endpoint is `https://media.shivpatel.xyz`, routed through Traefik.
The private route uses Traefik's shared `websecure` entrypoint. A separate
`jellyfin-public` entrypoint and dedicated ingress service provide a
Jellyfin-only destination for direct external HTTPS forwarding. Both routes
preserve Jellyfin authentication and use the existing TLS certificate.

## Streaming quality

The `configure-proxy-streaming` init container persists
`RemoteClientBitrateLimit=40000000` (40 Mbps) in Jellyfin's server configuration
on startup. Keep changes to that server-wide remote limit in `values.yaml`;
an admin UI-only change is overwritten on the next pod start.

This is the default remote-stream ceiling for users without an explicit
per-user override. It does not force all clients to select 40 Mbps, and it
does not cap local-network playback. Each client controls its own home and
Internet playback quality. Set those preferences to 40 Mbps to request that
quality; source media and client capabilities still determine the result.
