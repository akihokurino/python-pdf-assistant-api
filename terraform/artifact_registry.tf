resource "google_artifact_registry_repository" "app" {
  location      = var.region
  format        = "DOCKER"
  description   = "Test repository for Docker images"
  repository_id = "app"
}