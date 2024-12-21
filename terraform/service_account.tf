resource "google_service_account" "cloud_run_sa" {
  account_id   = "cloud-run-sa"
  display_name = "Cloud Run Service Account"
}
resource "google_project_iam_member" "cloud_run_editor" {
  project = var.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}
resource "google_project_iam_member" "cloud_run_secret_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_service_account" "api_gateway_sa" {
  account_id   = "api-gateway-sa"
  display_name = "Api Gateway Service Account"
}
resource "google_project_iam_member" "api_gateway_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.api_gateway_sa.email}"
}

resource "google_service_account" "cloud_scheduler_sa" {
  account_id   = "cloud-scheduler-sa"
  display_name = "Cloud Scheduler Service Account"
}
resource "google_project_iam_member" "cloud_scheduler_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.cloud_scheduler_sa.email}"
}

resource "google_service_account" "cloud_build_sa" {
  account_id   = "cloud-build-sa"
  display_name = "Cloud Build Trigger Service Account"
}
resource "google_project_iam_member" "cloud_build_editor" {
  project = var.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${google_service_account.cloud_build_sa.email}"
}