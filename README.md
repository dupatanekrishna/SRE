# Lead SRE Hands-On Lab

This repository documents practical Site Reliability Engineering work across observability, database reliability, Kubernetes/EKS, Terraform, incident response, and security operations.

## What is covered

- OpenTelemetry + Prometheus + Grafana + Loki + Tempo
- Prometheus alerting and Alertmanager → Slack
- Slow database incident investigation
- PostgreSQL blocking/lock troubleshooting
- RTO/RPO, Multi-AZ, read replicas, backup/restore DR
- Terraform drift detection, state recovery, and import
- Kubernetes/EKS troubleshooting patterns
- IAM/IRSA troubleshooting
- Certificate and secret rotation
- Lead SRE interview questions

## Observability architecture

```text
Application / PostgreSQL
        |
        v
OpenTelemetry SDK
        |
        v
OpenTelemetry Collector
   |        |        |
   v        v        v
Prometheus  Loki    Tempo
   \        |        /
    \       |       /
        Grafana
          |
          v
Prometheus Alert Rules
          |
          v
Alertmanager
          |
          v
Slack / Incident Channel
```

## Incident workflow

```text
Detect → Alert → Acknowledge → Investigate → Mitigate → Verify → RCA
```

## Security note

This repository intentionally excludes real credentials, Slack webhooks, AWS account IDs, private certificates, internal company URLs, and employer-confidential code.

## Repository sections

- [Observability Lab](observability/README.md)
- [Slow Database Incident](incidents/slow-database-incident.md)
- [Database Reliability](database-reliability/README.md)
- [Certificate & Secret Rotation](database-reliability/certificate-secret-rotation.md)
- [Terraform Reliability](terraform/README.md)
- [Kubernetes / EKS SRE](kubernetes-sre/README.md)
- [Interview Questions](interview-questions/lead-sre-questions.md)


## Reproducible Hands-On Lab

The full Docker-based observability experiment is available here:

- [FinApp Observability Experimental Lab](labs/observability-finapp/README.md)

It includes the Flask backend, PostgreSQL, OpenTelemetry Collector, Prometheus, Grafana, Loki, Tempo, Node Exporter, Alertmanager, Slack template, Docker Compose deployment, manual Docker setup, PromQL/LogQL queries, traffic generator, and PostgreSQL investigation commands.

This lab is intentionally structured so the complete experiment can be repeated from scratch and used as evidence of hands-on understanding.
