# resource "google_cloudbuild_trigger" "deploy" {
#   name            = "deploy"
#   location        = "global"
#   service_account = google_service_account.cloud_build_sa.id
#   filename        = "cloudbuild.yaml"
#
#   github {
#     owner = "akihokurino"
#     name  = "pdf-assistant-api"
#     push {
#       branch = "master"
#     }
#   }
# }