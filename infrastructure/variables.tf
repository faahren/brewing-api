variable "project_id" {
  description = "The name of the project"
  type        = string
}

variable "project_number" {
  description = "The number of the project"
  type        = string
}

variable "region" {
  description = "The default compute region"
  type        = string
}

variable "region_image" {
  description = "The default compute region"
  type        = string
  default = "us-central1"
}

variable "zone" {
  description = "The default compute zone"
  type        = string
}

variable "gh_token" {
  description = "Github Token"
  type        = string
  sensitive   = true
}

variable "gh_app_installation_id" {
  description = "Github App"
  type        = string
}

variable "gh_repo_url" {
  type        = string
}

variable "repository" {
    type    = string
    default  = "brewing-api"
}

variable "docker_image" {
    type = string
    default = "brewing-api"
}