provider "google" {}

# Terraform Enterprise state

#terraform {
#  backend "remote" {
#    hostname     = "app.terraform.io"
#    organization = "your_organization_name"
#
#    required_providers {
#      google = {
#        source  = "hashicorp/google"
#        version = "~> 4.3"
#      }
#    }
#
#    workspaces {
#      name = "terraform-gcp-filestore-backup"
#    }
#  }
#}