# Lead SRE Interview Questions

## Terraform

1. Production infrastructure was manually changed. How do you detect drift and safely reconcile it?
2. Terraform state is lost or corrupted. What recovery options do you use?
3. How do you import an existing production resource without recreating it?

## Ansible

4. What makes an Ansible playbook idempotent?
5. Where would you use Terraform versus Ansible?
6. How would you patch hundreds of Linux servers safely?
7. How do you handle secrets, rolling execution, failures, and rollback?

## Kubernetes / EKS

8. Pods are healthy but users cannot access the application. Walk through your troubleshooting sequence.
9. How would you design workloads to survive node and AZ failures?
10. Explain HPA, VPA, Cluster Autoscaler, and Karpenter.
11. Why can a PodDisruptionBudget block node draining?
12. Explain readiness, liveness, and startup probes.
13. How do you troubleshoot CrashLoopBackOff?
14. How do you troubleshoot Pending pods?
15. A pod cannot connect to RDS. What do you check?
16. How do you troubleshoot Kubernetes DNS failures?
17. Route53 resolves and the ALB exists, but users get 503/504. What do you check?
18. A pod gets AccessDenied to AWS Secrets Manager. How do you debug IRSA/Pod Identity and IAM?

## Security operations

19. How do you rotate a database secret without downtime?
20. What happens if running pods cache an old credential?
21. How do you rotate an RDS CA certificate safely across many applications?
22. What signals do you monitor during certificate/secret rotation?

## Observability / incident response

23. Explain the difference between metrics, logs, and traces.
24. What are the four golden signals?
25. Explain SLI, SLO, SLA, and error budget.
26. An API becomes slow but does not fail. How do you investigate?
27. Explain `PENDING` versus `FIRING` in Prometheus alerts.
28. Why can `rate()` return zero or NaN for a valid metric series?
29. How do Alertmanager grouping, deduplication, and routing help reduce alert noise?
30. Walk through: Detect → Alert → Acknowledge → Investigate → Mitigate → Verify → RCA.

## Database reliability

31. Explain RTO and RPO.
32. Multi-AZ vs read replica vs backup/snapshot: when do you use each?
33. How do you prove that a backup strategy actually supports DR?
34. How do you investigate database lock/blocking incidents?
35. What database saturation signals do you monitor?
36. How do you handle replication lag?
37. How do you approach capacity planning for a business-critical database?

## Combined scenario

38. After a deployment, pods are Running and Ready, ALB targets are healthy, but API latency rises from 200 ms to 4 seconds while CPU and memory look normal. Explain your investigation path using metrics, traces, logs, and database evidence.
