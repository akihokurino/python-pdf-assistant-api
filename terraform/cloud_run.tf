resource "google_cloud_run_service" "api" {
  name                       = "pdf-assistant-api"
  location                   = var.region
  autogenerate_revision_name = true

  template {
    spec {
      containers {
        name    = "main"
        image   = "gcr.io/${var.project_id}/pdf-assistant-api:latest"
        command = ["sh"]
        args    = ["-c", "python api.py"]

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
            memory = "512Mi"
          }
        }
      }

      service_account_name = google_service_account.cloud_run_sa.email
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
resource "google_cloud_run_service_iam_binding" "restrict_unauthenticated_access" {
  service  = google_cloud_run_service.api.name
  location = google_cloud_run_service.api.location
  role     = "roles/run.invoker"
  members = [
    "serviceAccount:${google_service_account.api_gateway_sa.email}"
  ]
}

resource "google_cloud_run_v2_job" "batch" {
  provider = google-beta
  name     = "pdf-assistant-batch"
  location = var.region

  template {
    template {
      containers {
        name    = "main"
        image   = "gcr.io/${var.project_id}/pdf-assistant-api:latest"
        command = ["sh"]
        args    = ["-c", "python batch.py"]

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
      }

      service_account = google_service_account.cloud_run_sa.email
    }

    task_count   = 1
    parallelism  = 1
  }
}
resource "google_cloud_run_v2_job_iam_binding" "restrict_unauthenticated_access" {
  name     = google_cloud_run_v2_job.batch.name
  location = google_cloud_run_v2_job.batch.location
  role     = "roles/run.invoker"
  members = [
    "serviceAccount:${google_service_account.cloud_scheduler_sa.email}"
  ]
}