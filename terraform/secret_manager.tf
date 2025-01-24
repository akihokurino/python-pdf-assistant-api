resource "google_secret_manager_secret" "cloud_sql_connection" {
  secret_id = "cloud-sql-connection"

  replication {
    auto {}
  }

  depends_on = [
    google_project_service.secret_manager
  ]
}
resource "google_secret_manager_secret_version" "cloud_sql_connection_version" {
  secret      = google_secret_manager_secret.cloud_sql_connection.id
  secret_data = var.cloud_sql_connection
}

resource "google_secret_manager_secret" "task_queue_token" {
  secret_id = "task-queue-token"

  replication {
    auto {}
  }

  depends_on = [
    google_project_service.secret_manager
  ]
}
resource "google_secret_manager_secret_version" "task_queue_token_version" {
  secret      = google_secret_manager_secret.task_queue_token.id
  secret_data = var.task_queue_token
}

resource "google_secret_manager_secret" "api_base_url" {
  secret_id = "api-base-url"

  replication {
    auto {}
  }

  depends_on = [
    google_project_service.secret_manager
  ]
}
resource "google_secret_manager_secret_version" "api_base_url_version" {
  secret      = google_secret_manager_secret.api_base_url.id
  secret_data = var.api_base_url
}

resource "google_secret_manager_secret" "openai_api_key" {
  secret_id = "openai-api-key"

  replication {
    auto {}
  }

  depends_on = [
    google_project_service.secret_manager
  ]
}
resource "google_secret_manager_secret_version" "openai_api_key_version" {
  secret      = google_secret_manager_secret.openai_api_key.id
  secret_data = var.openai_api_key
}
