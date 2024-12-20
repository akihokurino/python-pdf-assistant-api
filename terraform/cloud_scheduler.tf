resource "google_cloud_scheduler_job" "clean_openai_assistant" {
  name      = "clean-openai-assistant"
  region    = var.region
  schedule  = "0 10 * * *"
  time_zone = "Asia/Tokyo"

  http_target {
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.batch.name}:run"
    http_method = "POST"
    body = base64encode(jsonencode({
      "task": "clean-openai-assistant"
    }))

    oauth_token {
      service_account_email = google_service_account.cloud_scheduler_sa.email
    }
  }
}
