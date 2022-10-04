variable "project" {
  default = "YOUR_PROJECT_NAME"
}

variable "zone" {
  default = "YOUR_ZONE"
}

variable "cluster" {}

variable "secret_name" {}

variable "region" {
  default = "YOUR_REGION"
}

variable "entry_point" {
  default = "create_backup"
}

variable "roles" {
  description = "A list of roles to apply to the service account"
  default     = ["roles/file.editor", "roles/secretmanager.admin"]
}

variable "roles_scheduler" {
  description = "A list of roles to apply to the service account"
  default     = ["roles/cloudfunctions.invoker"]
}