terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

provider "local" {}

resource "local_file" "finapp" {
  filename = "${path.module}/finapp.txt"

  content = <<-EOT
  Environment: Production
  Application: FinApp
  Managed-By: Terraform
  EOT
}
