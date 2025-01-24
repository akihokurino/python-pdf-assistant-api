resource "google_storage_bucket" "google_storage_userdata" {
  name          = "${var.project_id}-userdata"
  location      = var.region
  storage_class = "REGIONAL"
  force_destroy = false

  versioning {
    enabled = false
  }

  depends_on = [
    google_project_service.cloud_storage
  ]
}