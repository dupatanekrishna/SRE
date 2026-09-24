# Terraform Reliability

## Drift

Drift means the actual infrastructure differs from the declared Terraform configuration/state relationship.

Example lab flow:

```text
Terraform apply
   ↓
Manual out-of-band change
   ↓
terraform plan -detailed-exitcode
   ↓
Drift detected
```

Exit codes:

```text
0 = no changes
1 = error
2 = changes detected
```

## Reconciliation

If the manual change is wrong:

```text
terraform apply
```

restores declared configuration.

If the manual change is legitimate:

```text
Update code → plan → review → apply
```

Goal:

```text
Configuration = State = Actual Infrastructure
```

## State loss or corruption

Recovery order:

```text
Remote state available?
  ↓ yes
terraform init / backend recovery

S3 versioning available?
  ↓ yes
restore last known-good state version

No usable state?
  ↓
inventory resources
  ↓
import / reconstruct state
  ↓
review plan carefully
```

Never blindly apply after losing state.

## Import

Modern import block example:

```hcl
import {
  to = aws_db_instance.production
  id = "finapp-prod-db"
}
```

Import brings an existing resource into Terraform state; it does not automatically reconstruct the desired configuration for you.

## Useful protections

- remote state
- state locking
- S3 versioning
- encryption
- IAM least privilege
- review/approval gates
- drift detection
- `prevent_destroy` where appropriate

`prevent_destroy` protects Terraform-driven destruction, not manual deletion outside Terraform.
