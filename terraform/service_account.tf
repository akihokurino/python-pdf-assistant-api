resource "google_service_account" "cloud_run_sa" {
  account_id   = "cloud-run-sa"
  display_name = "Cloud Run Service Account"
}
resource "google_project_iam_member" "cloud_run_editor" {
  project = var.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_service_account" "api_gateway_service_account" {
  account_id   = "api-gateway-sa"
}
resource "google_project_iam_member" "api_gateway_service_account" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.api_gateway_service_account.email}"
}