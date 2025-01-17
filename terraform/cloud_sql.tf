resource "google_sql_database_instance" "cloud_sql_instance" {
  name             = "pdf-assistant"
  database_version = "POSTGRES_17"
  instance_type    = "CLOUD_SQL_INSTANCE"

  settings {
    tier                        = "db-f1-micro"
    edition                     = "ENTERPRISE"
    disk_autoresize             = "true"
    disk_autoresize_limit       = "0"
    disk_size                   = "10"
    disk_type                   = "PD_HDD"
    pricing_plan                = "PER_USE"
    deletion_protection_enabled = "false"
    connector_enforcement       = "NOT_REQUIRED"

    ip_configuration {
      enable_private_path_for_google_cloud_services = "false"
      ipv4_enabled                                  = "true"
      server_ca_mode                                = "GOOGLE_MANAGED_INTERNAL_CA"
      ssl_mode                                      = "ENCRYPTED_ONLY"
    }
  }
}

resource "google_sql_user" "postgres" {
  name     = "postgres"
  instance = google_sql_database_instance.cloud_sql_instance.name
  password = var.db_password
}

resource "google_sql_database" "main" {
  name            = "main"
  instance        = google_sql_database_instance.cloud_sql_instance.name
  charset         = "UTF8"
  deletion_policy = "DELETE"
}