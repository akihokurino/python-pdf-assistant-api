resource "google_storage_bucket" "datastore_backup" {
  name          = "${var.project_id}-userdata"
  location      = var.region
  storage_class = "REGIONAL"
  force_destroy = false

  versioning {
    enabled = false
  }
}