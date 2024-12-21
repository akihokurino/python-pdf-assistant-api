resource "google_sql_database_instance" "cloudsql_instance" {
  name             = "app"
  database_version = "MYSQL_8_0_31"
  instance_type    = "CLOUD_SQL_INSTANCE"

  settings {
    tier                        = "db-f1-micro"
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

resource "google_sql_user" "root" {
  name     = "root"
  instance = google_sql_database_instance.cloudsql_instance.name
  host     = "%"
  password = var.db_password
}

resource "google_sql_database" "app" {
  name            = "app"
  instance        = google_sql_database_instance.cloudsql_instance.name
  charset         = "utf8mb4"
  collation       = "utf8mb4_0900_ai_ci"
  deletion_policy = "DELETE"
}