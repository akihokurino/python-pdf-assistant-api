resource "google_secret_manager_secret" "cloud_sql_connection" {
  secret_id = "cloud-sql-connection"

  replication {
    auto {}
  }
}
resource "google_secret_manager_secret_version" "cloud_sql_connection_version" {
  secret      = google_secret_manager_secret.cloud_sql_connection.id
  secret_data = var.cloud_sql_connection
}
