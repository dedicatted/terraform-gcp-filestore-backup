locals {
  timestamp = formatdate("YYMMDDhhmmss", timestamp())
}

# Compress source code
data "archive_file" "source" {
  type        = "zip"
  source_dir  = "./src/${var.cluster}/"
  output_path = "/tmp/function-${var.cluster}-${local.timestamp}.zip"
}

# Create bucket that will host the source code
resource "google_storage_bucket" "bucket" {
  project = var.project
  name    = "fs-backup-${var.cluster}-function-terraform"
  location = "US"
}

# Add source code zip to bucket
resource "google_storage_bucket_object" "zip" {
  # Append file MD5 to force bucket to be recreated
  name   = "source.zip#${data.archive_file.source.output_md5}"
  bucket = google_storage_bucket.bucket.name
  source = data.archive_file.source.output_path
}

# Create Cloud Function
resource "google_cloudfunctions_function" "function" {
  project               = var.project
  name                  = "fs-backup-${var.cluster}-terraform"
  runtime               = "python38"
  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.zip.name
  trigger_http          = true
  entry_point           = var.entry_point
  service_account_email = google_service_account.main.email
  timeout               = 540
  region                = var.region

  secret_environment_variables {
    key = "SLACK_URL"
    secret = var.secret_name            # Name of your secret in Google Secret Manager.
    version = "latest"
  }
}

resource "google_service_account" "main" {
  project      = var.project
  account_id   = "fs-backup-${var.cluster}-cf-terraform"
  display_name = "CloudFunctions Filestore ${var.cluster} backup"
}

resource "google_project_iam_member" "main" {
  count   = length(var.roles)
  project = var.project
  member  = "serviceAccount:${google_service_account.main.email}"
  role    = element(var.roles, count.index)
}


resource "google_cloud_scheduler_job" "job" {
  project     = var.project
  name        = "fs-backup-schedule-${var.cluster}-terraform"
  description = "Filestore ${var.cluster} job"
  schedule    = "00 01,13 * * *"
  region      = var.region


  http_target {
    http_method = "GET"
    uri         = "https://${var.region}-${var.project}.cloudfunctions.net/fs-backup-${var.cluster}-terraform"

    oidc_token {
      service_account_email = google_service_account.scheduler.email
    }
  }
}

resource "google_service_account" "scheduler" {
  project      = var.project
  account_id   = "${var.cluster}-fs-backup-cf-scheduler"
  display_name = "CloudFunctions scheduler Filestore ${var.cluster} backup"
}

resource "google_project_iam_member" "scheduler" {
  count   = length(var.roles)
  project = var.project
  member  = "serviceAccount:${google_service_account.scheduler.email}"
  role    = element(var.roles_scheduler, count.index)
}