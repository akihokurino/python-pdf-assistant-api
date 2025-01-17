resource "google_cloud_tasks_queue" "create_openai_assistant" {
  name     = "create-openai-assistant"
  location = var.region

  rate_limits {
    max_dispatches_per_second = 1
    max_concurrent_dispatches = 1
  }

  retry_config {
    max_attempts = 1
    min_backoff  = "0.1s"
    max_backoff  = "3600s"
  }
}