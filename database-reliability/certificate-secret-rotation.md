# Certificate and Secret Rotation

## Certificate rotation

Typical layers:

```text
Client → ALB      : ACM certificate
ALB → Application: optional backend TLS
Application → RDS: RDS server certificate / CA trust
```

These are separate certificate concerns.

## RDS CA rotation approach

```text
Inventory
  ↓
Identify applications and drivers
  ↓
Check compatibility with new CA
  ↓
Update trust stores / CA bundles where required
  ↓
Test in DEV
  ↓
Test in STAGE
  ↓
Rotate a small production batch
  ↓
Validate TLS and DB connectivity
  ↓
Continue rollout
  ↓
Monitor
```

Watch:

- TLS handshake failures
- database connection failures
- application 5xx rate
- latency
- connection counts
- readiness failures

## Secret rotation

A secret change is a coordination problem between the secret store, the service using the secret, and the target system.

Unsafe pattern:

```text
Change DB password
   ↓
Application still uses old credential
   ↓
New DB connections fail
```

Safer pattern:

```text
Generate new credential
   ↓
Make new credential valid
   ↓
Update secret store
   ↓
Consumers refresh/reload
   ↓
Verify new connections
   ↓
Retire old credential
```

## EKS pattern

```text
AWS Secrets Manager
      ↓
IAM / IRSA / Pod Identity
      ↓
Secrets Store CSI Driver or application retrieval
      ↓
EKS Pod
      ↓
RDS
```

Important operational point: rotating a secret in Secrets Manager does not guarantee every running process immediately uses the new value. Applications may cache credentials, read them only at startup, or consume mounted files that must be reread.

## Do not store secrets in

- source code
- Dockerfiles
- Git repositories
- committed Helm values
- plain Terraform configuration
- public documentation

Treat Terraform state as sensitive because secret values can exist there even when CLI output is marked `sensitive`.
