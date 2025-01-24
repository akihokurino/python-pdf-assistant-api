resource "google_firestore_database" "firestore" {
  name        = "(default)"
  project     = var.project_id
  location_id = var.region
  type        = "DATASTORE_MODE"

  depends_on = [
    google_project_service.firestore
  ]
}