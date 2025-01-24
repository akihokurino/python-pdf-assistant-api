resource "google_firestore_database" "firestore" {
  name        = "pdf-assistant"
  project     = var.project_id
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  depends_on = [
    google_project_service.firestore
  ]
}