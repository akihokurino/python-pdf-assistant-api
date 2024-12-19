resource "google_cloud_run_service" "api" {
  name                       = var.project_id
  location                   = var.region
  autogenerate_revision_name = true

  template {
    spec {
      containers {
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
    "serviceAccount:${google_service_account.api_gateway_service_account.email}"
  ]
}