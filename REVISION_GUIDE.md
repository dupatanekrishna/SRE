# Lead SRE Master Revision Guide

> Purpose: fast revision before a Lead SRE interview. This is based on the hands-on work and troubleshooting scenarios covered in the lab. It is written as **mental models + interview answers + commands + failure patterns**, not as a generic textbook.

---

# 0. My SRE Mental Model

For almost every incident, think in this order:

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

Do not stop at “I fixed it.” An SRE answer should always include **validation after mitigation**.

---

# 1. Reference Application Architecture

```text
Users
  ↓
Route53
  ↓
CloudFront / WAF (optional placement depending design)
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

Supporting services can include:

```text
Secrets Manager
KMS
IAM / IRSA / Pod Identity
S3
SQS / SNS
ElastiCache
CloudWatch
Prometheus / Grafana
OpenTelemetry
Loki / Tempo
CloudTrail
GuardDuty / Security Hub
Terraform
CI/CD
ArgoCD
AWS Backup
```

Important interview points:

- Public ALB does **not** mean pods are public.
- Pods should normally stay in private subnets.
- RDS does not sit behind the application ALB; pods connect directly to the RDS endpoint.
- Internal-only services may use an internal ALB/NLB or Kubernetes service-to-service networking.
- Private workloads calling public third-party APIs generally need NAT egress.
- AWS APIs can often be reached privately through VPC endpoints.
- Route53 resolves names; it is not an HTTP reverse proxy.

---

# 2. TLS Flow

Typical external TLS:

```text
Client
  ↓ HTTPS
ALB
  ↓ HTTP or HTTPS
Application Pod
  ↓ TLS
RDS
```

Common model:

- Client → ALB: ACM certificate.
- ALB → Pod: HTTP, or HTTPS if re-encryption is required.
- Pod → RDS: separate database TLS trust using the RDS certificate/CA.

Do not assume one certificate is used everywhere.

---

# 3. Kubernetes Service Discovery

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

Important:

- CoreDNS resolves the Service name.
- The Service/EndpointSlice relationship ultimately maps traffic to pods.
- CoreDNS does not directly choose the final application pod.

Useful commands:

```bash
kubectl get svc
kubectl get endpointslices
kubectl get pods -o wide
kubectl describe svc <service>
```

---

# 4. PostgreSQL Hands-On — What I Actually Practiced

## 4.1 Activity and waits

Useful query:

```sql
SELECT pid, state, wait_event_type, wait_event, query
FROM pg_stat_activity;
```

Key lesson:

> `active` does not necessarily mean CPU-consuming.

A session can be active but waiting.

Example from the latency lab:

```text
wait_event_type = Timeout
wait_event      = PgSleep
```

for:

```sql
SELECT version(), pg_sleep(3);
```

## 4.2 Blocking and locks

A transaction was intentionally left open and blocked another session.

Mental model:

```text
Blocked PID
  ↓
Find blocker
  ↓
Inspect blocker state/query
  ↓
Assess impact
  ↓
Commit / rollback where possible
  ↓
Terminate only when justified
```

Useful PostgreSQL function:

```sql
SELECT pg_blocking_pids(<blocked_pid>);
```

Important lesson:

> `idle in transaction` can still hold locks and block other sessions.

Also:

- `pg_cancel_backend()` cancels the currently running query.
- It may not solve an idle transaction that is still holding locks.
- `pg_terminate_backend()` is stronger and should be used only after impact assessment.

---

# 5. Database Reliability — RTO, RPO, HA and DR

## RTO

**Recovery Time Objective** = how long the business can tolerate the service being unavailable.

## RPO

**Recovery Point Objective** = how much data loss is acceptable.

Example mental model:

```text
RTO = time to restore
RPO = how far back recovery may go
```

## Multi-AZ vs Read Replica vs Backup

### Multi-AZ
Use mainly for:

- high availability
- failover
- infrastructure/database instance failure protection

### Read replica
Use mainly for:

- read scaling
- reducing load on primary
- possible DR option if promoted, depending architecture

Read replicas are generally asynchronous, so monitor replication lag.

### Backup / Snapshot
Use mainly for:

- point-in-time recovery
- corruption recovery
- disaster recovery restore

Key lesson:

> Backup is not proven DR until restore is tested.

---

# 6. Snapshot-Based DR

```text
Production
   ↓
Snapshot / Backup
   ↓
Cross-region / cross-account copy
   ↓
Restore database
   ↓
Validate schema
   ↓
Validate tables
   ↓
Validate row counts / important data
   ↓
Validate connectivity
   ↓
Application cutover
   ↓
Monitor
```

Cross-account considerations:

- manual snapshot sharing may be possible
- encrypted snapshots require correct customer-managed KMS access
- DR account should normally copy the snapshot so it owns the recovery artifact
- AWS Backup can automate cross-account/cross-region copies

Snapshot-based DR normally has higher RTO than continuously replicated designs.

---

# 7. Terraform — Drift

Drift = real infrastructure no longer matches declared configuration/state expectations.

Lab mental model:

```text
terraform apply
     ↓
manual out-of-band change
     ↓
terraform plan -detailed-exitcode
     ↓
drift detected
```

Exit codes:

```text
0 = no changes
1 = error
2 = changes detected
```

Reconciliation:

- manual change was wrong → apply declared configuration
- manual change was legitimate → update code → plan → review → apply

Goal:

```text
Configuration = State = Actual Infrastructure
```

---

# 8. Terraform State Recovery

If state is lost/corrupted:

```text
1. Check remote backend
2. Check state versioning / previous good version
3. Restore known-good state if possible
4. If no good state exists:
      inventory resources
      import/reconstruct carefully
      inspect plan
5. Never blindly apply
```

Remote state should use controls such as:

- encryption
- least privilege IAM
- versioning
- locking where supported
- backups/recovery
- CI/CD access control

---

# 9. Terraform Import

Example:

```hcl
import {
  to = aws_db_instance.production
  id = "finapp-prod-db"
}
```

Remember:

> Import associates an existing resource with Terraform state. It does not magically rebuild the desired Terraform configuration.

---

# 10. Terraform Safety

`prevent_destroy` can protect against Terraform-driven destruction.

It does **not** prevent:

- console deletion
- CLI deletion outside Terraform
- someone with other IAM permissions deleting the resource

Use defense in depth:

```text
prevent_destroy
+ IAM
+ SCP where appropriate
+ approvals
+ remote state
+ versioning
+ review
```

Provisioners are a last resort.

Prefer:

- cloud-init / user_data
- image baking
- Ansible
- Helm
- ArgoCD
- service-native configuration

---

# 11. Terraform Environment Separation

Good production separation:

```text
modules/
environments/
  dev/
  test/
  prod/
```

Also separate:

- state
- AWS accounts when appropriate
- deployment roles
- CI credentials
- approvals

Typical CI:

```text
PR/MR
 ↓
terraform fmt
 ↓
terraform validate
 ↓
Trivy / Checkov
 ↓
terraform plan
 ↓
review
 ↓
merge
 ↓
prod approval
 ↓
terraform apply
```

Scheduled `terraform plan -detailed-exitcode` can help detect drift.

---

# 12. Terraform and Secrets

Do not assume `sensitive = true` removes the value from state.

It mainly controls display behavior.

Safer mental model:

```text
Secrets Manager = secret lifecycle
Terraform       = infrastructure lifecycle
IAM             = authorization
```

Treat Terraform state as sensitive.

Avoid hard-coded secrets in:

- `.tf`
- source code
- Git
- Dockerfiles
- committed Helm values

---

# 13. Kubernetes — Standard Troubleshooting Flow

When the pod looks healthy but users cannot reach the application:

```text
Route53 / DNS
   ↓
Load Balancer
   ↓
Listener / routing rule
   ↓
Target Group
   ↓
Kubernetes Service
   ↓
EndpointSlice
   ↓
Pod readiness
   ↓
Application
   ↓
Database / downstream dependency
```

Core commands:

```bash
kubectl get pods -o wide
kubectl describe pod <pod>
kubectl logs <pod>
kubectl logs <pod> --previous
kubectl get svc
kubectl get endpointslices
kubectl get events --sort-by=.lastTimestamp
```

---

# 14. CrashLoopBackOff

Troubleshooting sequence:

```text
describe pod
   ↓
events
   ↓
previous logs
   ↓
exit code / termination reason
   ↓
OOMKilled?
   ↓
bad config?
   ↓
missing Secret / ConfigMap?
   ↓
dependency failure?
   ↓
probe failure?
   ↓
bad command / entrypoint?
```

Important:

```bash
kubectl logs <pod> --previous
```

because the current container may have restarted already.

---

# 15. Pending Pods

Common reasons:

- insufficient CPU
- insufficient memory
- nodeSelector mismatch
- affinity / anti-affinity
- taints/tolerations
- PVC not bound
- topology constraints
- Karpenter/Cluster Autoscaler issue

Best first check:

```bash
kubectl describe pod <pod>
```

Read scheduler events before guessing.

---

# 16. Probes

## Readiness
“Can this pod receive traffic?”

If readiness fails, the pod can remain running but should be removed from Service traffic.

## Liveness
“Should Kubernetes restart this container?”

If liveness fails repeatedly, kubelet restarts it.

## Startup
“Has this slow-starting app completed initialization?”

Use startup probes to avoid killing applications that legitimately take time to boot.

Interview warning:

> Bad liveness configuration can create an outage by repeatedly restarting a slow but recoverable application.

---

# 17. PodDisruptionBudget

PDB controls **voluntary disruptions**, such as node drain.

Example issue:

```text
EKS node upgrade
   ↓
kubectl drain
   ↓
PDB too strict
   ↓
pod eviction blocked
   ↓
upgrade stalls
```

PDB is not a guarantee against involuntary failures such as hardware/node loss.

---

# 18. EKS Availability

Think across layers:

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

If a node dies:

- pods on the node become unavailable
- Kubernetes reschedules replacement pods if capacity and constraints allow
- autoscaling may need to add capacity

---

# 19. Autoscaling

## HPA
Scales number of pods using metrics.

## VPA
Adjusts/recommends pod resource requests.

## Cluster Autoscaler / Karpenter
Adds/removes node capacity.

Important interview distinction:

> HPA cannot solve a cluster capacity shortage by itself.

If pods are Pending because no node fits them, node provisioning/autoscaling must solve that layer.

---

# 20. Pod → RDS Networking

Troubleshooting path:

```text
Application configuration
   ↓
DNS resolution
   ↓
RDS endpoint
   ↓
Pod subnet
   ↓
route table
   ↓
security group
   ↓
NACL
   ↓
RDS subnet/security group
   ↓
DB port
```

Useful connectivity tests:

```bash
nslookup <rds-endpoint>
nc -vz <rds-endpoint> 5432
```

Do not immediately blame Kubernetes if the failure is AWS networking or RDS configuration.

---

# 21. 503 vs 504 Mental Model

## 503
Think:

- no healthy backend
- readiness failure
- service/endpoints issue
- target group unhealthy
- application unavailable

## 504
Think:

- backend is too slow
- gateway/load-balancer timeout
- downstream database/API delay

Always verify actual logs/metrics; these are troubleshooting hints, not absolute rules.

---

# 22. IAM Trust vs Permission Policy

Mental model:

```text
Trust policy
= WHO may assume the role

Permission policy
= WHAT the role may do after assuming it
```

For EKS:

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

If a pod gets `AccessDenied`, check:

- correct service account
- IRSA/Pod Identity association
- IAM role
- trust relationship
- permission policy
- resource policy
- KMS key policy if encrypted resource involved
- account/region/resource ARN

---

# 23. Secrets Manager with EKS

Preferred concept:

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

Avoid static AWS access keys in the container.

---

# 24. Secret Rotation

Core risk:

```text
DB password rotated
    ↓
running application still has old value
    ↓
new DB connections fail
```

Safe mental model:

```text
Generate new credential
   ↓
make it valid
   ↓
update secret store
   ↓
consumers refresh/reload
   ↓
validate new connections
   ↓
retire old credential
```

First question to ask:

> How does the application consume the secret?

Possible patterns:

- environment variable loaded only at startup
- mounted secret file
- CSI-mounted value
- runtime SDK lookup
- application-side cache

Rotation in Secrets Manager does not automatically guarantee every running process immediately uses the new credential.

Monitor during rotation:

- DB authentication failures
- connection failures
- HTTP 5xx
- readiness failures
- pod restarts
- DB connection count
- latency

---

# 25. Certificate Rotation

Separate concerns:

```text
Client → ALB        = ACM certificate
ALB → Pod           = optional backend TLS certificate
Pod → RDS           = database server certificate / RDS CA trust
```

RDS CA rotation:

```text
Inventory DBs
 ↓
identify consumers/drivers
 ↓
check new CA compatibility
 ↓
update trust store / CA bundle if needed
 ↓
DEV
 ↓
TEST/STAGE
 ↓
small production batch
 ↓
validate TLS + DB connections
 ↓
complete rollout
 ↓
monitor
```

Risk:

```text
RDS switches to new CA
   ↓
old client does not trust it
   ↓
TLS handshake fails
   ↓
DB connectivity incident
```

---

# 26. Observability — Five Layers

```text
1. Generate telemetry
2. Collect / transport
3. Store / query
4. Visualize
5. Alert / respond
```

Our lab:

```text
Flask / PostgreSQL
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
Prometheus Alert
          ↓
Alertmanager
          ↓
Slack
```

---

# 27. Metrics vs Logs vs Traces

Strong interview mental model:

```text
METRIC → WHAT is abnormal?
TRACE  → WHERE is time being spent?
LOG    → WHAT happened?
```

Example slow DB incident:

```text
Prometheus
→ latency is high

Tempo
→ SQL span consumes ~3 seconds

Loki / application log
→ request details / errors

PostgreSQL
→ pg_stat_activity confirms DB wait/query
```

---

# 28. OpenTelemetry vs Prometheus

They are complementary.

## OpenTelemetry
Framework for:

- instrumentation
- receiving telemetry
- processing
- enriching
- routing/exporting

## Prometheus
Primarily:

- metrics scraping
- metrics storage
- PromQL
- alert rule evaluation

Lab architecture:

```text
App SDK
 ↓ PUSH OTLP HTTP
OTel Collector
 ↓ exposes Prometheus format :8889
Prometheus
 ↑ PULL scrape
```

---

# 29. OTel Receivers — Know the Difference

```text
otlp receiver
= applications PUSH telemetry

prometheus receiver
= collector PULLS /metrics

hostmetrics receiver
= collector reads host OS metrics

filelog receiver
= collector tails log files
```

Multiple receivers can feed different telemetry pipelines.

---

# 30. OTel SDK vs Collector

## SDK
Runs inside application process.

Example: Flask instrumentation library.

## Collector
Runs as a separate process/service.

It receives telemetry and routes it to backends.

---

# 31. Node Exporter vs OTel Hostmetrics

Node Exporter:

- mature Prometheus host metrics exporter
- strong existing dashboards/ecosystem

OTel hostmetrics:

- useful when standardizing host telemetry around OpenTelemetry

They overlap in purpose but are not identical.

---

# 32. CloudWatch Mental Model

AWS services can publish native metrics to CloudWatch.

EC2 native metrics include examples such as:

- CPU
- network
- status checks
- disk operation metrics

But OS-level metrics such as memory/filesystem usage generally require an agent/collector.

Traditional EC2 logs:

```text
Application
 ↓
/var/log/app.log
 ↓
CloudWatch Agent
 ↓
CloudWatch Logs
```

EKS logs commonly:

```text
Container stdout/stderr
 ↓
Fluent Bit / OTel Collector
 ↓
CloudWatch Logs or another log backend
```

Application-specific metrics must still be instrumented/generated; installing an agent alone does not magically create business metrics.

---

# 33. Prometheus Metrics Used in the Lab

Flask/OpenTelemetry generated metrics such as:

```text
http_server_duration_milliseconds_bucket
http_server_duration_milliseconds_sum
http_server_duration_milliseconds_count
```

Average latency:

```promql
sum(rate(http_server_duration_milliseconds_sum{http_target="/db"}[1m]))
/
sum(rate(http_server_duration_milliseconds_count{http_target="/db"}[1m]))
```

---

# 34. Prometheus Scrape and Rate Lesson

Initial problem:

- scrape interval was too sparse relative to the `rate(...[1m])` window
- there were not enough useful samples for stable rate calculation

We changed:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
```

Debugging command:

```promql
count_over_time(
  http_server_duration_milliseconds_count{http_target="/db"}[2m]
)
```

This confirmed multiple samples existed.

Another important lesson:

If the request counter stays:

```text
90
90
90
90
90
```

then:

```promql
rate(counter[2m])
```

is `0`.

If both numerator and denominator rates are zero, latency division may produce `NaN`.

So rate-based request latency needs traffic during the evaluation window.

---

# 35. Prometheus Alert Lifecycle

Rule:

```yaml
- alert: FinAppHighDBLatency
  expr: |
    sum(rate(http_server_duration_milliseconds_sum{http_target="/db"}[1m]))
    /
    sum(rate(http_server_duration_milliseconds_count{http_target="/db"}[1m]))
    > 1000
  for: 30s
```

Lifecycle:

```text
INACTIVE
   ↓ condition true
PENDING
   ↓ condition stays true for 30s
FIRING
   ↓ condition clears
INACTIVE / resolved
```

Observed value was approximately:

```text
3018 ms
```

for the injected 3-second query.

---

# 36. Slow Database Incident — Full Story

Healthy query:

```sql
SELECT version();
```

Injected incident:

```sql
SELECT version(), pg_sleep(3);
```

Observed requests:

```text
~3.02 seconds
```

Investigation:

```text
Metric
→ /db latency > 3 sec

Trace
→ GET /db
   └── SELECT span ~3 sec

PostgreSQL
→ pg_stat_activity
→ wait_event_type = Timeout
→ wait_event = PgSleep

Log
→ request context / application behavior
```

Mitigation:

```sql
SELECT version();
```

Verification:

- latency returns to baseline
- alert condition clears
- service remains healthy

This is a complete interview-ready incident story.

---

# 37. Tempo Trace Model

```text
Trace ID
= one end-to-end request

Span ID
= one operation inside that request
```

Example:

```text
Trace ID: one request
  ├── GET /db span
  └── SELECT span
```

Same Trace ID connects the operations belonging to the same request.

---

# 38. Loki

Loki stores/query logs.

Example LogQL:

```logql
{service_name="finapp-backend"}
{service_name="finapp-backend"} |= "GET /db"
```

Trace/span context in logs allows faster correlation when instrumentation carries the active trace context.

---

# 39. Grafana

Grafana is the visualization/query layer.

It can use:

- Prometheus as metrics datasource
- Loki as logs datasource
- Tempo as traces datasource

Do not describe Grafana as the metrics database itself.

---

# 40. Alertmanager

Prometheus evaluates the alert condition.

Alertmanager handles alert routing/notification concerns such as:

- grouping
- deduplication
- routing
- repeat intervals
- resolved notifications

Lab flow:

```text
Prometheus
   ↓
Alertmanager
   ↓
Slack
```

Do not commit Slack webhook URLs to Git.

---

# 41. Slack Incident Alert

End-to-end lab:

```text
Slow SQL query
 ↓
OTel metric
 ↓
Prometheus
 ↓
FinAppHighDBLatency = FIRING
 ↓
Alertmanager
 ↓
Slack incident channel
```

This demonstrates the full detect-to-notify pipeline.

---

# 42. Golden Signals

Remember:

```text
Latency
Traffic
Errors
Saturation
```

FinApp examples:

- latency → /db response duration
- traffic → requests/sec
- errors → HTTP 5xx
- saturation → CPU/memory/DB connections/IOPS/disk

---

# 43. SLI / SLO / SLA

## SLI
Measured reliability indicator.

Examples:

- availability
- successful request ratio
- p95 latency

## SLO
Target reliability objective.

Example:

```text
99.9% successful requests per month
```

## SLA
External/contractual commitment.

## Error budget

```text
Error Budget = 100% - SLO
```

For a 99.9% monthly availability objective, the allowed unavailable time is roughly 43.8 minutes in a 30.4-day month.

---

# 44. Alert Quality

Do not page just because:

```text
CPU > 70%
```

High CPU may be healthy under load.

Prefer alerts that represent user/business impact or strong precursors:

- high error rate
- high latency
- availability drop
- DB connection exhaustion
- replication lag
- storage almost full
- failed dependency

Avoid alert fatigue.

---

# 45. MTTD and MTTR

```text
MTTD = Mean Time To Detect
MTTR = Mean Time To Restore/Recover
```

Observability and automation should reduce both.

---

# 46. Severity

Exact definitions vary by company, but a simple model:

```text
SEV1 = major outage / critical business impact
SEV2 = significant degradation
SEV3 = limited impact
```

Always follow the company’s own severity matrix.

---

# 47. RCA

A useful RCA structure:

```text
Impact
Timeline
Detection
Root cause
Contributing factors
Mitigation
Recovery validation
Preventive actions
Owners / follow-up
```

Avoid blame. Focus on system/process improvement.

---

# 48. Interview Scenario — 503/504

Question:

> Route53 works and ALB exists, but application returns 503/504. What do you do?

Answer flow:

```text
DNS
→ ALB listener/rule
→ target group health
→ SG
→ Kubernetes Service
→ EndpointSlice
→ readiness
→ pod logs
→ application
→ RDS/downstream dependency
```

For 504, pay special attention to slow downstream dependencies and timeout configuration.

---

# 49. Interview Scenario — IAM/IRSA

Question:

> Pod gets AccessDenied to Secrets Manager.

Answer:

```text
1. Confirm correct ServiceAccount
2. Confirm IRSA/Pod Identity association
3. Confirm trust relationship
4. Confirm permission policy
5. Confirm secret resource policy if used
6. Confirm KMS permission for encrypted secret
7. Confirm account/region/ARN
8. Re-test from pod/application identity
```

---

# 50. Interview Scenario — Secret Rotation

Question:

> 50 EKS applications use a DB password from Secrets Manager. Rotate without downtime.

Answer:

```text
Inventory consumers
→ identify how each consumes/caches secret
→ create/activate new credential safely
→ update Secrets Manager
→ refresh/restart consumers in controlled batches if required
→ validate new DB connections
→ monitor auth/5xx/readiness
→ retire old credential only after verification
```

---

# 51. Interview Scenario — Certificate Rotation

Question:

> RDS CA is approaching expiry.

Answer:

```text
Inventory RDS + applications
→ verify drivers support new CA
→ update trust bundles
→ DEV
→ STAGE
→ small PROD batch
→ validate TLS/DB connectivity
→ monitor errors/latency
→ complete rollout
```

---

# 52. Interview Scenario — Slow API, CPU Normal

Question:

> Pods are Running/Ready, ALB targets healthy, CPU/memory normal, but latency increased from 200ms to 4s.

Answer:

```text
Confirm user impact with metrics
→ inspect latency by route
→ trace slow request
→ identify slow span/dependency
→ inspect logs around trace/request
→ inspect DB activity/waits/query
→ mitigate dependency/query
→ verify latency and alert recovery
→ RCA
```

This scenario ties together the whole SRE lab.

---

# 53. What Is Still Pending

The major topic not yet completed hands-on is **Ansible**.

Planned revision/lab:

```text
inventory
playbook
vars
roles
handlers
idempotency
Vault
serial / rolling patching
failure handling
Terraform + Ansible responsibilities
```

Do not pretend this section has already been completed. Add it after the actual lab.

---

# 54. 60-Second Final Revision

Before interview, remember these:

```text
SRE incident:
Detect → Alert → Investigate → Mitigate → Verify → RCA

Observability:
Metric = WHAT
Trace  = WHERE
Log    = DETAILS

Prometheus:
scrape → PromQL → alert rule

Alerting:
Prometheus → Alertmanager → Slack

Kubernetes:
DNS → LB → Service → EndpointSlice → Pod → App → Dependency

IAM:
Trust = WHO
Permission = WHAT

RDS:
Multi-AZ = HA
Read replica = read scale / possible DR
Backup = recovery point
Restore test = proven backup

Terraform:
Config = State = Actual
Never blindly apply after state loss

Secret rotation:
Update consumer safely before retiring old credential

Certificate rotation:
Verify trust before switching CA
```

---

# 55. Security / Repository Hygiene

Never commit:

- Slack webhooks
- passwords
- tokens
- AWS keys
- private keys
- employer internal URLs
- customer data
- internal account IDs if sensitive
- real production secrets

Use sanitized examples only.
