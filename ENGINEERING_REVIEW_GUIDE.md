# Lead SRE Engineering Review Guide

This guide consolidates the engineering mental models, troubleshooting paths, commands, validation steps, and failure patterns demonstrated across the hands-on SRE labs in this repository.

The goal is not memorization. Use this guide to connect the experiments to operational reasoning: identify user impact, isolate the failing layer, mitigate safely, validate recovery, and capture preventive actions.

---

## 1. Core incident mental model

```text
USER IMPACT
   ↓
DNS / Load Balancer / Network
   ↓
Kubernetes / Compute
   ↓
Application
   ↓
Downstream dependency (DB/API/cache)
   ↓
Metrics + Traces + Logs
   ↓
Mitigate
   ↓
Verify recovery
   ↓
RCA / prevention
```

Incident lifecycle:

```text
Detect → Alert → Acknowledge → Investigate → Mitigate → Verify → RCA
```

A technical fix is not complete until recovery is validated.

---

## 2. Reference AWS / EKS application architecture

```text
Users
  ↓
Route53
  ↓
CloudFront / WAF
  ↓
Internet-facing ALB
  ↓
EKS private application subnets
  ↓
Kubernetes Service
  ↓
Application Pods
  ↓
RDS / Aurora private DB subnets
```

### Key engineering points

- A public ALB does not require public application pods.
- Application pods should normally remain in private subnets.
- RDS is a downstream dependency; application pods connect to the database endpoint directly.
- Internal services can use internal load balancers or Kubernetes service-to-service networking.
- Private workloads calling public endpoints normally require controlled egress such as NAT.
- AWS service access can often be kept private with VPC endpoints.
- Route53 provides DNS resolution; it is not an HTTP reverse proxy.

---

## 3. TLS and certificate boundaries

Typical flow:

```text
Client
  ↓ HTTPS
ALB
  ↓ HTTP or HTTPS
Application Pod
  ↓ TLS
RDS
```

These are separate trust boundaries. The certificate used for client-to-ALB TLS is not automatically the same certificate or CA trust used between the application and RDS.

For certificate rotation, inventory consumers, validate driver compatibility, update trust bundles, roll out through lower environments and controlled production batches, verify TLS/database connectivity, and monitor errors and latency.

---

## 4. Kubernetes service discovery

```text
Pod
 ↓
CoreDNS
 ↓
Service DNS
 ↓
ClusterIP
 ↓
EndpointSlice
 ↓
Pod IP
```

Useful commands:

```bash
kubectl get svc
kubectl get endpointslices
kubectl get pods -o wide
kubectl describe svc <service>
kubectl get events --sort-by=.lastTimestamp
```

CoreDNS resolves service names. The Service/EndpointSlice relationship maps service traffic to ready pod endpoints.

---

## 5. Kubernetes troubleshooting paths

### CrashLoopBackOff

```text
describe pod
→ events
→ previous logs
→ exit code / termination reason
→ OOMKilled?
→ configuration / Secret / ConfigMap?
→ dependency failure?
→ probe failure?
→ command / entrypoint?
```

Important command:

```bash
kubectl logs <pod> --previous
```

### Pending pods

Check scheduler events first. Common causes include insufficient CPU/memory, affinity constraints, taints/tolerations, PVC binding, topology constraints, or node-autoscaling problems.

### Probes

- **Readiness:** can this pod receive traffic?
- **Liveness:** should Kubernetes restart this container?
- **Startup:** has a slow-starting application completed initialization?

Bad liveness settings can turn a recoverable slow application into a restart loop.

### PodDisruptionBudget

A PDB protects against voluntary disruption such as node drain. An overly strict PDB can block maintenance or EKS upgrades.

### Availability

Think in layers:

```text
Multiple AZs
+ multiple replicas
+ topology spread / anti-affinity
+ readiness probes
+ PDB
+ node autoscaling
+ load balancing
+ HA database
```

---

## 6. Autoscaling

- **HPA:** changes pod replica count based on metrics.
- **VPA:** recommends or changes pod resource requests.
- **Cluster Autoscaler / Karpenter:** changes node capacity.

### Key engineering distinction

HPA cannot solve a cluster-capacity shortage by itself. If replicas are Pending because no node can schedule them, node capacity must be added at the infrastructure layer.

---

## 7. Pod-to-RDS troubleshooting

```text
Application configuration
→ DNS resolution
→ RDS endpoint
→ Pod subnet
→ route table
→ security group
→ NACL
→ RDS subnet/security group
→ DB port
```

Useful tests:

```bash
nslookup <rds-endpoint>
nc -vz <rds-endpoint> 5432
```

Do not assume every connectivity failure is a Kubernetes problem; validate AWS networking and database configuration as well.

---

## 8. 503 vs 504 starting hypotheses

### 503

Common starting points:

- no healthy backend
- readiness failure
- service/endpoints issue
- unhealthy target group
- application unavailable

### 504

Common starting points:

- backend too slow
- gateway/load-balancer timeout
- slow database/API dependency

These are hypotheses, not conclusions. Confirm with logs, metrics, traces, target health, and application evidence.

---

## 9. IAM trust vs permissions

```text
Trust policy      = WHO may assume the role
Permission policy = WHAT the role may do after assuming it
```

For EKS workloads:

```text
Pod
 ↓
ServiceAccount
 ↓
IRSA / Pod Identity
 ↓
IAM role
 ↓
trust policy
 ↓
permission policy
 ↓
AWS service
```

For `AccessDenied`, validate the service account, identity association, role trust relationship, permissions, resource policy, KMS policy where applicable, and the account/region/resource ARN.

---

## 10. Secrets and rotation

Preferred pattern:

```text
Secrets Manager
   ↓
IAM authorization
(IRSA / Pod Identity)
   ↓
CSI Driver or AWS SDK
   ↓
Application Pod
```

Avoid static AWS access keys in containers.

Safe rotation model:

```text
Generate new credential
→ make it valid
→ update secret store
→ refresh/reload consumers
→ validate new connections
→ retire old credential
```

The first design question is always: **How does the application consume and cache the secret?**

During rotation monitor authentication failures, HTTP 5xx, readiness failures, pod restarts, DB connections, and latency.

---

## 11. PostgreSQL activity, waits, and blocking

Useful activity query:

```sql
SELECT pid, state, wait_event_type, wait_event, query
FROM pg_stat_activity;
```

`active` does not necessarily mean CPU-consuming; a session can be active while waiting.

For blocking:

```sql
SELECT pg_blocking_pids(<blocked_pid>);
```

Troubleshooting model:

```text
Blocked PID
→ find blocker
→ inspect blocker state/query
→ assess impact
→ commit / rollback where possible
→ terminate only when justified
```

An `idle in transaction` session can still hold locks.

---

## 12. RTO, RPO, HA, and DR

- **RTO:** acceptable time to restore service.
- **RPO:** acceptable amount of data loss.
- **Multi-AZ:** primarily high availability/failover.
- **Read replica:** primarily read scaling; may contribute to a DR design depending on architecture.
- **Backup/snapshot:** recovery point for restore, corruption recovery, and DR.

Key lesson:

> Backup is not proven disaster recovery until restore is tested.

Snapshot-based DR normally has a higher RTO than continuously replicated designs.

---

## 13. Terraform drift, state, and import

### Drift

```text
terraform apply
→ manual out-of-band change
→ terraform plan -detailed-exitcode
→ drift detected
```

Exit codes:

```text
0 = no changes
1 = error
2 = changes detected
```

Goal:

```text
Configuration = State = Actual Infrastructure
```

### State recovery

```text
1. Check remote backend
2. Check state versioning / previous good version
3. Restore known-good state when possible
4. If no good state exists, inventory and import/reconstruct carefully
5. Inspect the plan
6. Never blindly apply
```

### Import

```hcl
import {
  to = aws_db_instance.production
  id = "finapp-prod-db"
}
```

Import associates an existing resource with Terraform state; it does not automatically create the correct desired configuration.

### Safety

Use defense in depth: IAM, approvals, remote state, versioning, locking where supported, review, and lifecycle protections such as `prevent_destroy` where appropriate.

Treat Terraform state as sensitive. `sensitive = true` mainly controls display behavior; it does not remove the value from state.

---

## 14. Observability model

```text
1. Generate telemetry
2. Collect / transport
3. Store / query
4. Visualize
5. Alert / respond
```

Lab architecture:

```text
Application / PostgreSQL
      ↓
OpenTelemetry SDK
      ↓
OpenTelemetry Collector
   ┌──────┼──────┐
   ↓      ↓      ↓
Prometheus Loki  Tempo
   └──────┼──────┘
          ↓
       Grafana
          ↓
Prometheus Alert Rules
          ↓
Alertmanager
          ↓
Slack / Incident Channel
```

Operational mental model:

```text
METRIC → WHAT is abnormal?
TRACE  → WHERE is time being spent?
LOG    → WHAT happened?
```

Grafana is the visualization/query layer; Prometheus, Loki, and Tempo are the corresponding telemetry backends in this lab.

---

## 15. Prometheus and alerting

Prometheus primarily handles metrics scraping/storage, PromQL, and alert-rule evaluation. Alertmanager handles grouping, deduplication, routing, repeat intervals, and resolved notifications.

Alert lifecycle:

```text
INACTIVE
→ condition becomes true
PENDING
→ condition remains true for configured duration
FIRING
→ condition clears
INACTIVE / resolved
```

Rate-based queries need sufficient samples and traffic. A counter that remains unchanged produces a rate of zero; divisions where both numerator and denominator are zero can produce `NaN`.

### Golden signals

```text
Latency
Traffic
Errors
Saturation
```

Prefer alerts tied to user impact or strong precursors rather than arbitrary resource thresholds alone.

---

## 16. Slow database incident narrative

The lab intentionally changed a healthy database query to include a delay, then correlated the impact across telemetry and PostgreSQL evidence.

```text
Metric
→ /db latency rises

Trace
→ SQL span consumes most of request time

Logs
→ request/application context

PostgreSQL
→ pg_stat_activity shows the wait/query
```

Mitigation restores the normal query. Recovery is confirmed by latency returning to baseline, alert conditions clearing, and the service remaining healthy.

This is a complete incident investigation narrative because it includes detection, evidence, mitigation, and post-change validation.

---

## 17. Troubleshooting scenarios

### Route53 works and ALB exists, but users receive 503/504

```text
DNS
→ ALB listener/rule
→ target-group health
→ security groups
→ Kubernetes Service
→ EndpointSlice
→ readiness
→ pod logs
→ application
→ RDS/downstream dependency
```

For 504, focus especially on slow dependencies and timeout boundaries.

### Pod receives `AccessDenied` to Secrets Manager

```text
ServiceAccount
→ IRSA/Pod Identity association
→ IAM role trust
→ permission policy
→ resource policy
→ KMS permission
→ account/region/ARN
→ re-test using workload identity
```

### Rotate a DB credential used by many EKS applications

```text
Inventory consumers
→ understand loading/caching behavior
→ create/activate new credential
→ update secret store
→ refresh consumers in controlled batches
→ validate DB connections
→ monitor errors/readiness/latency
→ retire old credential
```

### Pods and ALB targets look healthy but API latency increases sharply

```text
Confirm user impact with metrics
→ inspect latency by route
→ trace a slow request
→ identify slow span/dependency
→ correlate logs
→ inspect DB activity/waits/query
→ mitigate dependency/query
→ verify latency and alert recovery
→ RCA
```

---

## 18. Engineering review summary

```text
SRE incident:
Detect → Alert → Investigate → Mitigate → Verify → RCA

Observability:
Metric = WHAT
Trace  = WHERE
Log    = DETAILS

Kubernetes:
DNS → LB → Service → EndpointSlice → Pod → App → Dependency

IAM:
Trust = WHO
Permission = WHAT

RDS:
Multi-AZ = HA
Read replica = read scale / possible DR role
Backup = recovery point
Restore test = proven recovery

Terraform:
Configuration = State = Actual
Never blindly apply after state loss

Secret rotation:
Refresh consumers safely before retiring old credentials

Certificate rotation:
Verify trust before switching CA
```

---

## 19. What You Should Be Able to Explain After Completing This Lab

You should be able to:

- Walk through an SRE incident from detection through verified recovery and RCA.
- Explain how DNS, load balancing, Kubernetes networking, application behavior, and downstream dependencies fit together.
- Troubleshoot CrashLoopBackOff, Pending pods, readiness failures, service discovery, and Pod-to-RDS connectivity.
- Explain the difference between HPA, VPA, Cluster Autoscaler, and Karpenter.
- Explain IAM trust policies versus permission policies and troubleshoot workload access through IRSA or Pod Identity.
- Design safe secret and certificate rotation workflows with validation and rollback considerations.
- Explain RTO, RPO, Multi-AZ, read replicas, backups, and why restore testing is necessary.
- Detect Terraform drift, reason about state recovery, and safely import existing resources.
- Explain the roles of OpenTelemetry, Prometheus, Loki, Tempo, Grafana, and Alertmanager.
- Use metrics, traces, logs, and database evidence together to isolate a slow dependency.
- Explain Prometheus alert states, rate behavior, golden signals, SLI/SLO/SLA, and error budgets.
- Defend troubleshooting decisions with observed evidence rather than status-code assumptions.

---

## 20. Security / repository hygiene

Never commit real credentials, tokens, Slack webhooks, AWS keys, private keys, employer internal URLs, customer data, or production secrets. Use sanitized lab values only.
