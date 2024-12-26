resource "google_cloud_run_service" "api" {
  name                       = "api"
  location                   = var.region
  autogenerate_revision_name = true

  template {
    spec {
      containers {
        image   = "gcr.io/${var.project_id}/pdf-assistant:latest"
        command = ["sh"]
        args    = ["-c", "python -m entrypoint.api"]

        ports {
          container_port = 8080
        }

        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "1Gi"
          }
        }
      }

      service_account_name = google_service_account.cloud_run_sa.email
    }

    metadata {
      annotations = {
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.cloudsql_instance.connection_name
        "run.googleapis.com/client-name"        = "gcloud"
        "run.googleapis.com/client-version"     = "504.0.1"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  metadata {
    annotations = {
      "run.googleapis.com/ingress" = "all"
    }
  }
}
resource "google_cloud_run_service_iam_binding" "api_access" {
  service  = google_cloud_run_service.api.name
  location = google_cloud_run_service.api.location
  role     = "roles/run.invoker"
  members = [
    "serviceAccount:${google_service_account.api_gateway_sa.email}"
  ]
}

resource "google_cloud_run_v2_job" "clean_openai_assistant" {
  provider = google-beta
  name     = "clean-openai-assistant"
  location = var.region

  template {
    template {
      containers {
        image   = "gcr.io/${var.project_id}/pdf-assistant:latest"
        command = ["sh"]
        args    = ["-c", "python -m entrypoint.clean_openai_assistant"]

        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }

        volume_mounts {
          name = "cloudsql"
          mount_path = "/cloudsql"
        }
      }

      volumes {
        name = "cloudsql"
        cloud_sql_instance {
          instances = [google_sql_database_instance.cloudsql_instance.connection_name]
        }
      }

      service_account = google_service_account.cloud_run_sa.email
    }

    task_count   = 1
    parallelism  = 1
  }
}
resource "google_cloud_run_v2_job_iam_binding" "clean_openai_assistant_access" {
  name     = google_cloud_run_v2_job.clean_openai_assistant.name
  location = google_cloud_run_v2_job.clean_openai_assistant.location
  role     = "roles/run.invoker"
  members = [
    "serviceAccount:${google_service_account.cloud_scheduler_sa.email}"
  ]
}