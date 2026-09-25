include "root" {
  path = find_in_parent_folders("root.hcl")
}

# Example Terraform module location.
# The module itself is intentionally not included in this small theory example.
terraform {
  source = "../../../modules/vpc"
}

inputs = {
  environment = "dev"
  vpc_cidr    = "10.10.0.0/16"
}
