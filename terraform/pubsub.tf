resource "google_storage_notification" "storage_upload_notification" {
  bucket         = google_storage_bucket.google_storage_userdata.name
  topic          = google_pubsub_topic.storage_upload_notifications_topic.id
  payload_format = "JSON_API_V1"
  event_types = ["OBJECT_FINALIZE"]
  depends_on = [google_project_service.pubsub]
}

resource "google_pubsub_topic" "storage_upload_notifications_topic" {
  name    = "${var.project_id}-storage-upload-notifications"
  project = var.project_id
  depends_on = [google_project_service.pubsub]
}
resource "google_pubsub_topic_iam_member" "storage_upload_notifications_publisher" {
  topic  = google_pubsub_topic.storage_upload_notifications_topic.id
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:service-${var.project_number}@gs-project-accounts.iam.gserviceaccount.com"
}

resource "google_pubsub_topic" "storage_upload_dead_letter_topic" {
  name    = "${var.project_id}-storage-upload-dead-letter"
  project = var.project_id
  depends_on = [google_project_service.pubsub]
}

resource "google_pubsub_subscription" "storage_upload_notifications_subscription" {
  name  = "${var.project_id}-storage-upload-subscription"
  topic = google_pubsub_topic.storage_upload_notifications_topic.id

  push_config {
    push_endpoint = "${var.api_base_url}/subscriber/storage_upload_notification"
    oidc_token {
      service_account_email = google_service_account.cloud_run_sa.email
    }
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.storage_upload_dead_letter_topic.id
    max_delivery_attempts = 5
  }
  depends_on = [google_project_service.pubsub]
}