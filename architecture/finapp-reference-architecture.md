# FinApp Reference Architecture — Interview Revision

## Main request flow

```text
Internet User
    ↓
Route53
    ↓
CloudFront / WAF (design-dependent)
    ↓
Public ALB
    ↓
Private EKS Worker Nodes / Pods
    ↓
Kubernetes Service
    ↓
Application
    ↓
Private RDS / Aurora
```

## Internal supporting flow

```text
Application Pod
  ├── Secrets Manager via IAM/IRSA/Pod Identity
  ├── S3 via VPC endpoint or NAT depending endpoint design
  ├── AWS APIs via VPC endpoints where available
  ├── Third-party APIs via NAT Gateway
  └── RDS directly through private networking
```

## Observability

```text
App + DB
  ↓
OTel SDK / Collector
  ├── Prometheus → Grafana
  ├── Loki       → Grafana
  └── Tempo      → Grafana

Prometheus alert
  ↓
Alertmanager
  ↓
Slack / incident system
```

## Security

```text
TLS in transit
KMS at rest
private subnets
least privilege IAM
Secrets Manager
IRSA / Pod Identity
Security Groups
NACL where required
WAF
CloudTrail
GuardDuty / Security Hub
```

## DR

```text
Primary region
  ↓
RDS/Aurora backup or replica
  ↓
Cross-region / cross-account recovery capability
  ↓
Restore/promote
  ↓
Validate
  ↓
Cutover
```

## Troubleshooting request path

```text
DNS
→ CDN/WAF
→ ALB
→ target group
→ Service
→ EndpointSlice
→ Pod
→ App
→ RDS
```
