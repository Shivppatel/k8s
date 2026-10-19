# Internal load balancer

MetalLB allocates the internal Traefik ingress address from `home-lab-pool`
and advertises it through `l2-ad-pool`. The pool is `192.168.20.20–192.168.20.40`;
Traefik uses `192.168.20.20`.

All three cluster nodes are control-plane nodes that also host workloads.
Keep `metallb.speaker.ignoreExcludeLB: true` so the speakers can advertise
services despite the kubeadm `node.kubernetes.io/exclude-from-external-load-balancers`
label. Without this override, no node is eligible to advertise the ingress VIP.

Home DNS may point application hostnames at the VIP after HTTPS reachability
has been verified from the client VLAN. Kubernetes node-local VIP reachability
alone does not verify that Layer 2 advertisement works for other clients.
