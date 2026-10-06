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
- Scenario-based SRE knowledge checks

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
- [Engineering Review Guide](ENGINEERING_REVIEW_GUIDE.md)
- [SRE Knowledge Check](knowledge-check/lead-sre-knowledge-check.md)

## Reproducible Hands-On Lab

The full Docker-based observability experiment is available here:

- [FinApp Observability Experimental Lab](labs/observability-finapp/README.md)

It includes the Flask backend, PostgreSQL, OpenTelemetry Collector, Prometheus, Grafana, Loki, Tempo, Node Exporter, Alertmanager, Slack template, Docker Compose deployment, manual Docker setup, PromQL/LogQL queries, traffic generator, and PostgreSQL investigation commands.

This lab is intentionally structured so the complete experiment can be repeated from scratch and used as evidence of hands-on understanding.

## What You Should Be Able to Explain After Completing This Lab

You should be able to:

- Explain how an SRE incident moves from detection through mitigation, validation, and RCA.
- Trace a user request through DNS, load balancing, Kubernetes networking, application code, and downstream dependencies.
- Troubleshoot Kubernetes workload failures, service discovery, Pod-to-RDS connectivity, and IAM access problems.
- Explain RTO/RPO, HA/DR choices, backup validation, and recovery testing.
- Detect and reconcile Terraform drift and reason safely about state recovery and imports.
- Correlate metrics, logs, traces, and PostgreSQL evidence during latency incidents.
- Explain Prometheus alerting, Alertmanager routing, golden signals, SLI/SLO/SLA, and error budgets.
- Describe safe secret and certificate rotation strategies for production workloads.

Use the [Knowledge Check](knowledge-check/lead-sre-knowledge-check.md) to validate that understanding with scenario-based questions.
