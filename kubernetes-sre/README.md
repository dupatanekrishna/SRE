# Kubernetes / EKS SRE Troubleshooting

## Healthy pods but users cannot reach the application

Work from outside to inside:

```text
DNS
 ↓
Load Balancer
 ↓
Listener / routing rules
 ↓
Target health
 ↓
Kubernetes Service
 ↓
EndpointSlice
 ↓
Pod readiness
 ↓
Application
 ↓
Downstream dependency
```

## CrashLoopBackOff

Check:

```bash
kubectl get pods
kubectl describe pod <pod>
kubectl logs <pod> --previous
```

Common causes:

- application crash
- bad configuration
- missing secret/configmap
- dependency unavailable
- OOMKilled
- incorrect command/entrypoint
- failed startup/liveness probe

## Pending pods

Check:

- insufficient CPU/memory
- node selectors
- affinity/anti-affinity
- taints/tolerations
- PVC binding
- topology constraints
- node provisioning/autoscaler failures

## Readiness vs liveness vs startup

- **Readiness**: should this pod receive traffic?
- **Liveness**: should Kubernetes restart this container?
- **Startup**: has the application completed startup yet?

Bad probe configuration can itself cause an outage.

## PDB

A PodDisruptionBudget limits voluntary disruption. During maintenance or node upgrades, an overly restrictive PDB can prevent successful node drain.

## Network troubleshooting

For pod → RDS:

```text
Application config
  ↓
DNS resolution
  ↓
Pod networking
  ↓
Subnet route
  ↓
Security Group
  ↓
NACL
  ↓
RDS endpoint/listener
```

## DNS

Kubernetes service discovery commonly uses:

```text
Pod → CoreDNS → Service DNS → ClusterIP
                       ↓
                 EndpointSlices
                       ↓
                     Pods
```

For AWS service endpoints also check VPC DNS settings and resolver behavior.

## IAM / IRSA troubleshooting

For a pod receiving `AccessDenied`:

```text
ServiceAccount
  ↓
IRSA / Pod Identity association
  ↓
IAM trust relationship
  ↓
IAM role
  ↓
Permission policy
  ↓
Target AWS service
```

Authentication and authorization must both be correct.
