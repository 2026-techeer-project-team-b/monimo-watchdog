terraform {
  required_version = ">= 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.7"
    }
  }

  # 버킷 · 키 · 리전은 레포에 두지 않는다. `terraform init -backend-config=...` 로 넣는다
  backend "s3" {}
}

provider "aws" {
  region = var.aws_region
}
