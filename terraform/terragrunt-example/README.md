# Terragrunt — Simple DevOps / SRE Example

## What is Terragrunt?

Terragrunt is a thin wrapper around Terraform/OpenTofu that helps keep infrastructure code **organized, reusable, and DRY (Don't Repeat Yourself)**.

A simple way to remember it:

```text
Terraform
    ↓
Creates and manages infrastructure

Terragrunt
    ↓
Organizes how Terraform code is reused across
environments, accounts, regions, and dependencies
```

Terragrunt does **not replace Terraform**. It calls Terraform/OpenTofu underneath.

---

## Why use Terragrunt?

Imagine we have the same VPC Terraform module for:

```text
dev
stage
prod
```

Without good reuse, we may repeat:

- backend configuration
- module source
- region
- environment values
- account-specific configuration
- dependency outputs

Terragrunt allows us to keep common configuration in one place and only specify what changes per environment.

Benefits:

- less duplicated configuration
- cleaner environment structure
- centralized common settings
- easier multi-environment management
- easier multi-account / multi-region organization
- dependency handling between Terraform stacks
- consistent Terraform execution

---

# Simple Folder Structure

```text
terragrunt-example/
├── root.hcl
└── dev/
    ├── vpc/
    │   └── terragrunt.hcl
    └── application/
        └── terragrunt.hcl
```

The idea is:

```text
root.hcl
   ↓
common configuration

dev/vpc/terragrunt.hcl
   ↓
VPC-specific Terraform module + dev values

dev/application/terragrunt.hcl
   ↓
Application module
   ↓
reads VPC output using dependency block
```

---

# 1. Common Root Configuration

File:

```text
root.hcl
```

Example:

```hcl
locals {
  aws_region = "ap-south-1"
  project    = "sre-lab"
}
```

This is where shared configuration can live.

In larger environments this is also commonly where teams centralize things such as:

- remote state configuration
- provider generation
- common tags
- account information
- region information

---

# 2. VPC Environment Configuration

File:

```text
dev/vpc/terragrunt.hcl
```

```hcl
include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../modules/vpc"
}

inputs = {
  environment = "dev"
  vpc_cidr    = "10.10.0.0/16"
}
```

Meaning:

```text
include
   ↓
reuse common root configuration

terraform.source
   ↓
use an existing Terraform module

inputs
   ↓
pass environment-specific variables to Terraform
```

The same Terraform VPC module could then be reused for production with different inputs:

```hcl
inputs = {
  environment = "prod"
  vpc_cidr    = "10.20.0.0/16"
}
```

The Terraform module remains the same.

Only the environment configuration changes.

---

# 3. Dependency Between Stacks

Assume the VPC Terraform module outputs:

```hcl
output "vpc_id" {
  value = aws_vpc.main.id
}
```

The application stack can consume that VPC output.

File:

```text
dev/application/terragrunt.hcl
```

```hcl
include "root" {
  path = find_in_parent_folders("root.hcl")
}

dependency "vpc" {
  config_path = "../vpc"
}

terraform {
  source = "../../../modules/application"
}

inputs = {
  environment = "dev"
  vpc_id      = dependency.vpc.outputs.vpc_id
}
```

Flow:

```text
VPC Terraform module
       ↓
output vpc_id
       ↓
Terragrunt dependency block
       ↓
application module receives vpc_id
```

This is one of Terragrunt's useful features when infrastructure is separated into multiple Terraform stacks.

---

# Terraform vs Terragrunt

| Terraform | Terragrunt |
|---|---|
| Defines resources | Organizes Terraform usage |
| Creates infrastructure | Helps reuse Terraform modules |
| Maintains state | Helps standardize state/backend configuration |
| Uses variables | Passes environment-specific inputs |
| Modules provide reusable infrastructure | Terragrunt helps reuse those modules across environments |
| Can read remote state/dependencies | Terragrunt provides convenient dependency wiring |

---

# Typical Real-World Structure

A larger setup may look like:

```text
infrastructure/
├── modules/
│   ├── vpc/
│   ├── eks/
│   ├── rds/
│   └── application/
│
└── live/
    ├── root.hcl
    │
    ├── dev/
    │   ├── vpc/
    │   ├── eks/
    │   └── application/
    │
    ├── stage/
    │   ├── vpc/
    │   ├── eks/
    │   └── application/
    │
    └── prod/
        ├── vpc/
        ├── eks/
        └── application/
```

The Terraform modules contain the actual resource definitions.

The Terragrunt files tell those modules:

- which environment is being deployed
- which values to use
- where dependencies are
- what common configuration to inherit

---

# Basic Commands

From a Terragrunt environment directory:

```bash
terragrunt init
terragrunt validate
terragrunt plan
terragrunt apply
terragrunt destroy
```

For example:

```bash
cd dev/vpc
terragrunt plan
```

Terragrunt prepares the Terraform configuration and invokes Terraform/OpenTofu underneath.

---

# Interview Answer

A concise answer:

> Terragrunt is a thin wrapper around Terraform that helps keep infrastructure code DRY and organized. I use Terraform modules for the actual infrastructure and Terragrunt to reuse those modules across environments such as dev, stage, and production. It also helps centralize common configuration, manage environment-specific inputs, remote state patterns, and dependencies between infrastructure stacks.

An even simpler explanation:

> Terraform builds the infrastructure. Terragrunt makes the Terraform setup easier to organize and reuse at scale.

---

# Key Point

Terragrunt is mainly about:

```text
Terraform modules
        +
shared configuration
        +
environment-specific inputs
        +
dependency management
        ↓
more organized infrastructure management
```

That is the main concept to remember for interviews.
