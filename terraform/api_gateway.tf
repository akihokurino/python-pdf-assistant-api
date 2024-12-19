# resource "google_api_gateway_api" "api_gateway" {
#   provider = google-beta
#   api_id   = "api-gateway"
#   project  = var.project_id
# }
#
# resource "google_api_gateway_api_config" "api_gateway_config" {
#   provider = google-beta
#   project = var.project_id
#   api = google_api_gateway_api.api_gateway.api_id
#   display_name = "api-gateway-config"
#   gateway_config {
#     backend_config {
#       google_service_account = google_service_account.api_gateway_service_account.email
#     }
#   }
#
#   openapi_documents {
#     document {
#       path = "api_gateway.yaml"
#       contents = filebase64("api_gateway.yaml")
#     }
#   }
#
#   lifecycle {
#     create_before_destroy = true
#   }
# }
#
# resource "google_api_gateway_gateway" "api_gateway_gateway" {
#   provider = google-beta
#   project = var.project_id
#   region = var.region
#   api_config = google_api_gateway_api_config.api_gateway_config.id
#   gateway_id = "api-gateway"
# }