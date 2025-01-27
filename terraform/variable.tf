variable "project_id" {
  type = string
}

variable "project_number" {
  type = string
}

variable "region" {
  type    = string
  default = "asia-northeast1"
}

variable "db_password" {
  type = string
}

variable "cloud_sql_connection" {
  type = string
}

variable "task_queue_token" {
  type = string
}

variable "api_base_url" {
  type = string
}

variable "openai_api_key" {
  type = string
}