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
Both ingress routes exclude `/metrics` and its subpaths, including mixed-case
spellings. Prometheus continues scraping the internal service directly.

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

## Transcoding

Hardware acceleration is intentionally disabled. On this hardware, the
software H.264 path handled the representative 4K HDR/PGS workload faster
than the integrated GPU's Vulkan tone-mapping/overlay path. FFmpeg's
software `tonemapx` filter still performs HDR-to-SDR conversion; the disabled
`EnableTonemapping` option controls the hardware path, not that automatic
software conversion. HEVC and AV1 encoding remain disabled to avoid costly
software encoding. Thread counts, presets, and CRF values retain defaults.

The unused GPU device plugin and host DRM directory mounts are absent.
Re-enable acceleration only after representative media tests demonstrate
sufficient real-time headroom, not merely successful codec capability probes.

Transcoding throttles when sufficiently ahead of playback (180 seconds), and
old HLS segments are cleaned up with a 720-second retention window. These
server settings do not change the web player's own forward-buffer limits.
The separate `/cache` PVC holds generated cache/transcode data.

The deployment uses `Recreate` to avoid overlapping SQLite writers and RWO
configuration-volume attachments during updates. Its service account does
not mount Kubernetes API credentials.
