# GPU device allocation

The pinned upstream generic-device-plugin chart advertises one `devic.es/dri`
resource per node with `/dev/dri/renderD128`. It replaces the upstream default
device list, so serial, audio, camera, and FUSE resources are not advertised.
Only the DRM device directory is mounted read-only, alongside the kubelet
device-plugin socket directory required for registration.

The device-plugin DaemonSet runs privileged as required by the upstream chart
for node device registration. Its service account does not mount API
credentials. Applications requesting `devic.es/dri: 1` receive the render
device through Kubernetes device allocation and need not run privileged or
mount the entire host `/dev/dri` directory.

Keep Jellyfin hardware acceleration disabled until its allocated device
passes `vainfo` and representative FFmpeg encoding and tone-mapping probes.
