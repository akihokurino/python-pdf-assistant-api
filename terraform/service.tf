resource "google_project_service" "cloud_run" {
  project = var.project_id
  service = "run.googleapis.com"
}

resource "google_project_service" "container_registry" {
  project = var.project_id
  service = "containerregistry.googleapis.com"
}

resource "google_project_service" "api_gateway" {
  project = var.project_id
  service = "apigateway.googleapis.com"
}

resource "google_project_service" "service_management" {
  project = var.project_id
  service = "servicemanagement.googleapis.com"
}

resource "google_project_service" "service_control" {
  project = var.project_id
  service = "servicecontrol.googleapis.com"
}

resource "google_project_service" "cloud_dns" {
  project = var.project_id
  service = "dns.googleapis.com"
}

resource "google_project_service" "certificate_manager" {
  project = var.project_id
  service = "certificatemanager.googleapis.com"
}

resource "google_project_service" "cloud_scheduler" {
  project = var.project_id
  service = "cloudscheduler.googleapis.com"
}

resource "google_project_service" "compute_engine" {
  project = var.project_id
  service = "compute.googleapis.com"
}

resource "google_project_service" "secret_manager" {
  project = var.project_id
  service = "secretmanager.googleapis.com"
}

resource "google_project_service" "sqladmin" {
  project = var.project_id
  service = "sqladmin.googleapis.com"
}

resource "google_project_service" "cloud_build" {
  project = var.project_id
  service = "cloudbuild.googleapis.com"
}

resource "google_project_service" "storage_api" {
  project = var.project_id
  service = "storage.googleapis.com"
}