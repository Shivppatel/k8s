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
