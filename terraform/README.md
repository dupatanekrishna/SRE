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

Local terraform.tfstate / terraform.tfstate.backup available?
  ↓ yes
validate carefully and restore

No usable state?
  ↓
inventory real resources
  ↓
reconstruct Terraform configuration
  ↓
import resources back into state
  ↓
terraform plan
  ↓
review and reconcile carefully
```

Never blindly run `terraform apply` immediately after losing state. Terraform may think existing resources are missing and attempt to create duplicates.

### If all state is lost but infrastructure still exists

Terraform cannot automatically reconstruct the complete state relationship from the cloud.

Example resource:

```hcl
resource "aws_instance" "web" {
  ami           = "ami-xxxxxxxx"
  instance_type = "t3.micro"
}
```

Classic import:

```bash
terraform import aws_instance.web i-0123456789abcdef0
```

Modern import block:

```hcl
import {
  to = aws_instance.web
  id = "i-0123456789abcdef0"
}
```

Then:

```bash
terraform plan
```

The goal is:

```text
Terraform configuration
        =
Terraform state
        =
Actual infrastructure
```

## Import

An import block tells Terraform which existing real-world resource should be associated with a Terraform resource address.

It does **not** replace the resource/module configuration.

Recommended pattern:

```hcl
resource "aws_instance" "web" {
  ami           = "ami-xxxxxxxx"
  instance_type = "t3.micro"

  tags = {
    Name = "web"
  }
}

import {
  to = aws_instance.web
  id = "i-0123456789abcdef0"
}
```

Then:

```bash
terraform plan
```

Terraform compares:

```text
resource configuration
        ↓
imported state
        ↓
actual infrastructure
```

If the configuration does not match the existing resource, the plan shows the differences.

### Importing into a module

Example module:

```hcl
module "ec2" {
  source = "./modules/ec2"

  instance_type = "t3.micro"
}
```

If the module contains:

```hcl
resource "aws_instance" "web" {
  instance_type = var.instance_type
}
```

the import address can target the module resource:

```hcl
import {
  to = module.ec2.aws_instance.web
  id = "i-0123456789abcdef0"
}
```

Important mental model:

```text
import block
= tells Terraform which existing resource to adopt

resource/module configuration
= tells Terraform what the resource should look like
```

For recovery, reconstruct enough configuration first, then import, then review `terraform plan`.

## Terraform Outputs and Cross-Stack Dependencies

If another stack needs a value from the current stack, the current stack normally still needs to expose that value with an `output` block.

Example VPC output:

```hcl
output "vpc_id" {
  value = aws_vpc.main.id
}
```

A Terragrunt dependency can then consume it:

```hcl
dependency "vpc" {
  config_path = "../vpc"
}

inputs = {
  vpc_id = dependency.vpc.outputs.vpc_id
}
```

Flow:

```text
Terraform resource
   ↓
Terraform output
   ↓
Terragrunt dependency
   ↓
another Terraform stack
```

Terragrunt simplifies the wiring, but it does not remove the need to publish the required Terraform output.

Without Terragrunt, plain Terraform can also do cross-stack wiring using techniques such as `terraform_remote_state`.

## Terragrunt — Organized Terraform Management

Terragrunt is a thin wrapper around Terraform/OpenTofu that helps keep infrastructure code DRY, organized, and easier to manage across multiple environments.

Simple mental model:

```text
Terraform
= builds infrastructure

Terraform module
= reusable infrastructure logic

Terragrunt
= organizes/orchestrates how those Terraform modules and stacks are reused
```

Terraform modules alone can already support dev/stage/prod reuse. Terragrunt is optional.

Terragrunt becomes useful when there are many environments, accounts, regions, backends, provider settings, common tags, and cross-stack dependencies that would otherwise require repeated configuration.

A simple example is included here:

- [Terragrunt Simple Example](terragrunt-example/README.md)

It demonstrates:

- shared root configuration
- reusable Terraform module source
- environment-specific inputs
- VPC → application dependency flow
- interview-ready Terraform vs Terragrunt explanation

## What If an External Terraform Module Becomes Unmaintained?

If a Terraform module consumed from GitHub is no longer maintained, do not immediately replace it in production.

First determine whether the current pinned version still works.

### Option 1 — Pin the last known-good version

Avoid consuming an unmaintained repository directly from a moving branch such as `main`.

Example:

```hcl
module "vpc" {
  source = "git::https://github.com/example/terraform-vpc.git?ref=v2.4.1"
}
```

A specific commit can also be used:

```hcl
module "vpc" {
  source = "git::https://github.com/example/terraform-vpc.git?ref=8a91d2f"
}
```

This keeps builds reproducible.

### Option 2 — Fork and maintain internally

If only small provider/Terraform compatibility fixes are required:

```text
Abandoned upstream module
        ↓
fork into company GitHub organization
        ↓
fix compatibility/deprecations
        ↓
test
        ↓
tag internal release
        ↓
consume internal fork
```

Example:

```hcl
module "vpc" {
  source = "git::https://github.com/my-company/terraform-vpc.git?ref=v2.4.2-company.1"
}
```

### Option 3 — Bring the module in-house

For a small but important module, copy/own the module code inside your infrastructure repository:

```text
terraform/
├── modules/
│   └── vpc/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── prod/
    └── main.tf
```

Then:

```hcl
module "vpc" {
  source = "../modules/vpc"
}
```

Now the team fully owns the module.

### Option 4 — Migrate to an actively maintained module

If the old module is significantly outdated, move to a maintained alternative.

The most important risk is Terraform state and resource addresses.

Old module address:

```text
module.old_vpc.aws_vpc.main
```

New module address:

```text
module.new_vpc.aws_vpc.this[0]
```

Terraform could interpret this as:

```text
destroy old resource
create new resource
```

even when both addresses represent the same real infrastructure.

Always review:

```bash
terraform plan
```

A `moved` block may be needed:

```hcl
moved {
  from = module.old_vpc.aws_vpc.main
  to   = module.new_vpc.aws_vpc.this[0]
}
```

Depending on how different the modules are, state migration or import may also be required.

### Decision Flow

```text
External module is abandoned
        ↓
Still works safely?
        ↓ yes
pin last known-good version

Needs small compatibility fixes?
        ↓
fork and maintain internally

Small/simple module?
        ↓
bring it in-house

Significantly outdated or risky?
        ↓
migrate to maintained module
        ↓
carefully protect state/resource addresses
```

### Interview Answer

> If an external Terraform module becomes unmaintained, I first pin the last known-good version so deployments remain stable. Then I assess the maintenance risk. For small compatibility fixes, I fork it into our organization, test the changes, and version our fork. If the module is significantly outdated, I migrate to a maintained or internal module. During migration I pay close attention to Terraform state and resource addresses so Terraform does not accidentally destroy and recreate existing infrastructure.

## Useful protections

- remote state
- state locking
- S3 versioning
- encryption
- IAM least privilege
- review/approval gates
- drift detection
- pinned module versions
- internal ownership of critical modules
- `prevent_destroy` where appropriate

`prevent_destroy` protects Terraform-driven destruction, not manual deletion outside Terraform.

## Reproducible No-AWS Hands-On Lab

A safe local experiment is included here:

- [Terraform Local Drift & State Lab](local-drift-state-lab/README.md)

It uses only the HashiCorp `local` provider, so it can be used to practice `init`, `validate`, `plan`, `apply`, state inspection, manual drift, `-detailed-exitcode`, reconciliation and destroy without provisioning anything in AWS.
