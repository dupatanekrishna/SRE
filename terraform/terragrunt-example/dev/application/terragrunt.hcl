include "root" {
  path = find_in_parent_folders("root.hcl")
}

# Read outputs from the VPC Terragrunt stack.
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
