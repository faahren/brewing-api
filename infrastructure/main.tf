terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "5.24.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

data "google_client_config" "default" {
}
data "google_project" "project" {}

provider "docker" {
  registry_auth {
    address  = "${var.region_image}-docker.pkg.dev"
    username = "oauth2accesstoken"
    password = data.google_client_config.default.access_token
  }
}

#############################################
#               Enable API's                #
#############################################

# Enable IAM API
resource "google_project_service" "iam" {
  provider = google
  service            = "iam.googleapis.com"
  disable_on_destroy = false
}

# Enable Cloud Run API
resource "google_project_service" "cloudrun" {
  provider = google
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

# Enable Bigquery API
resource "google_project_service" "bigquery" {
  provider = google
  service            = "bigquery.googleapis.com"
  disable_on_destroy = false
}

# Enable Cloud Secret Manager API
resource "google_project_service" "secretmanager" {
  provider = google
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

# Enable Cloud Resource Manager API
resource "google_project_service" "resourcemanager" {
  provider = google
  service            = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
}

# Enable Cloud Resource Manager API
resource "google_project_service" "computeengine" {
  provider = google
  service            = "compute.googleapis.com"
  disable_on_destroy = false
}


# Enable Firestore API
resource "google_project_service" "firestore" {
  provider = google
  service            = "firestore.googleapis.com"
  disable_on_destroy = false
}


# Enable Artifact Registry API
resource "google_project_service" "artifactregistry" {
  provider = google
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

# Enable Cloud Build
resource "google_project_service" "cloudbuild" {
  provider = google
  service            = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}



#############################################
#            Giving Permissions             #
#############################################
data "google_compute_default_service_account" "default" {
    project = var.project_id
    depends_on =  [google_project_service.computeengine]
}

resource "google_project_iam_member" "compute_engine_bigquery" {
    project = var.project_id
    role   = "roles/bigquery.admin"
    member = "serviceAccount:${data.google_compute_default_service_account.default.email}"
    depends_on =  [google_project_service.computeengine]
}


# This is used so there is some time for the activation of the API's to propagate through
# Google Cloud before actually calling them.
resource "time_sleep" "wait_30_seconds" {
  create_duration = "30s"
  depends_on = [
    google_project_service.iam,
    google_project_service.artifactregistry,
    google_project_service.cloudrun,
    google_project_service.resourcemanager,
    google_project_service.secretmanager,
    google_project_service.bigquery,
    google_project_service.firestore,
    google_project_service.computeengine,
    google_project_service.cloudbuild
    ]
}

#############################################
#    Google Artifact Registry Repository    #
#############################################

# Create Artifact Registry Repository for Docker containers
resource "google_artifact_registry_repository" "my_docker_repo" {
  provider = google

  location = var.region_image
  repository_id = var.repository
  description = "My docker repository"
  format = "DOCKER"
  depends_on = [time_sleep.wait_30_seconds]
}

# Create a service account
resource "google_service_account" "docker_pusher" {
  provider = google

  account_id   = "docker-pusher"
  display_name = "Docker Container Pusher"
  depends_on =[time_sleep.wait_30_seconds]
}

# Give service account permission to push to the Artifact Registry Repository
resource "google_artifact_registry_repository_iam_member" "docker_pusher_iam" {
  provider = google

  location = google_artifact_registry_repository.my_docker_repo.location
  repository =  google_artifact_registry_repository.my_docker_repo.repository_id
  role   = "roles/artifactregistry.writer"
  member = "serviceAccount:${google_service_account.docker_pusher.email}"
  depends_on = [
    google_artifact_registry_repository.my_docker_repo,
    google_service_account.docker_pusher
    ]
}



##############################################
#                 Cloud Build                #
##############################################

// Create a secret containing the personal access token and grant permissions to the Service Agent
resource "google_secret_manager_secret" "gh_token_secret" {
    project =  var.project_id
    secret_id = "github-secret-token"
    replication {
        auto {}
    }
    depends_on = [time_sleep.wait_30_seconds]
}

resource "google_secret_manager_secret_version" "gh_token_secret_version" {
    secret = google_secret_manager_secret.gh_token_secret.id
    secret_data = var.gh_token
    
    depends_on = [time_sleep.wait_30_seconds]
}

data "google_iam_policy" "serviceagent_secretAccessor" {
    binding {
        role = "roles/secretmanager.secretAccessor"
        members = ["serviceAccount:service-${data.google_project.project.number}@gcp-sa-cloudbuild.iam.gserviceaccount.com"]
    }

}

resource "google_secret_manager_secret_iam_policy" "policy" {
  project = google_secret_manager_secret.gh_token_secret.project
  secret_id = google_secret_manager_secret.gh_token_secret.secret_id
  policy_data = data.google_iam_policy.serviceagent_secretAccessor.policy_data
}

// Create the GitHub connection
resource "google_cloudbuildv2_connection" "gh_connexion" {
    project = var.project_id
    location = var.region_image
    name = "gh_connexion"

    github_config {
        app_installation_id = var.gh_app_installation_id
        authorizer_credential {
            oauth_token_secret_version = google_secret_manager_secret_version.gh_token_secret_version.id
        }
    }
    depends_on = [google_secret_manager_secret_iam_policy.policy]
}



##############################################
#         Build image to Cloud Build         #
##############################################

resource "google_cloudbuildv2_repository" "link_to_gh_repo" {
  project = var.project_id
  location = var.region_image
  name = "main-service"
  parent_connection = google_cloudbuildv2_connection.gh_connexion.name
  remote_uri = var.gh_repo_url
}

resource "google_cloudbuild_trigger" "trigger_build" {
  project = var.project_id
  location = var.region_image
  name = "trigger-main-service"

  repository_event_config {
    repository = google_cloudbuildv2_repository.link_to_gh_repo.id
    push {
      branch = "main.*"
    }
  }


  substitutions = {
    "_REGION"    = "${var.region_image}"
    "_PROJECT"   = "${var.project_id}"
    "_REPO"      = "${var.repository}"
    "_IMAGE"     = "${var.docker_image}"
  }

  filename = "build/prod/cloudbuild.yaml"
}


data "docker_registry_image" "container_image" {
  name = "${var.region_image}-docker.pkg.dev/${var.project_id}/${var.repository}/${var.docker_image}"
  depends_on = [google_cloudbuild_trigger.trigger_build, google_artifact_registry_repository.my_docker_repo]
}

output digest {
  value = data.docker_registry_image.container_image.sha256_digest
}

##############################################
#       Deploy API to Google Cloud Run       #
##############################################

# Deploy image to Cloud Run
resource "google_cloud_run_service" "main_service" {
  provider = google
  name     = "brewing-api"
  location = var.region
  template {
    spec {
        containers {
            image = "${var.region_image}-docker.pkg.dev/${var.project_id}/${var.repository}/${var.docker_image}@${data.docker_registry_image.container_image.sha256_digest}"
            resources {
                limits = {
                "memory" = "1G"
                "cpu" = "1"
                }
            }
            env {
                name = "project_id"
                value = var.project_id
            }
            env {
                name = "database_id"
                value = var.database_id
            }
            env {
                name = "forward_url"
                value = var.forward_url
            }
            env {
                name = "dataset_id"
                value = var.dataset_id
            }
      }
    }
    
    metadata {
        annotations = {
            "autoscaling.knative.dev/minScale" = "0"
            "autoscaling.knative.dev/maxScale" = "1"
        }
    }
  }
  traffic {
    percent = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_binding" "default" {
  location = google_cloud_run_service.main_service.location
  service  = google_cloud_run_service.main_service.name
  role     = "roles/run.invoker"
  members = [
    "allUsers"
  ]
}

output "cloud_run_instance_url" {
  value = google_cloud_run_service.main_service.status.0.url
}

##############################################
#             Deploy BQ Dataset              #
##############################################

resource "google_bigquery_dataset" "brewing_dataset" {
  dataset_id                  = var.dataset_id
  friendly_name               = "Brewing Hits"
  description                 = "Dataset for all brewing hits"
  location                    = var.region
}

resource "google_bigquery_table" "brewing_dataset" {
  dataset_id = google_bigquery_dataset.brewing_dataset.dataset_id
  table_id   = "pings"
  require_partition_filter = false

  labels = {
    env = "default"
  }

  schema = file("${path.module}/schemas/pings.json")

}