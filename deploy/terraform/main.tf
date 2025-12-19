# Main Terraform configuration for RAG7 Multi-Agent System

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
  
  backend "gcs" {
    bucket = "rag7-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "container.googleapis.com",
    "aiplatform.googleapis.com",
    "run.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "servicenetworking.googleapis.com",
    "sqladmin.googleapis.com",
  ])
  
  service            = each.value
  disable_on_destroy = false
}

# Networking module
module "networking" {
  source = "./modules/networking"
  
  project_id   = var.project_id
  region       = var.region
  environment  = var.environment
  network_name = "rag7-vpc"
  
  depends_on = [google_project_service.required_apis]
}

# GKE module
module "gke" {
  source = "./modules/gke"
  
  project_id      = var.project_id
  region          = var.region
  environment     = var.environment
  cluster_name    = "rag7-cluster"
  network         = module.networking.network_name
  subnetwork      = module.networking.subnet_name
  master_ipv4_cidr = module.networking.master_ipv4_cidr_block
  
  node_pools = {
    default = {
      machine_type   = "n1-standard-4"
      min_count      = var.environment == "prod" ? 3 : 1
      max_count      = var.environment == "prod" ? 20 : 5
      disk_size_gb   = 100
      disk_type      = "pd-standard"
      preemptible    = var.environment != "prod"
    }
  }
  
  depends_on = [module.networking]
}

# Vertex AI module
module "vertex_ai" {
  source = "./modules/vertex-ai"
  
  project_id  = var.project_id
  region      = var.region
  environment = var.environment
  
  depends_on = [google_project_service.required_apis]
}

# Monitoring module
module "monitoring" {
  source = "./modules/monitoring"
  
  project_id  = var.project_id
  environment = var.environment
  
  notification_channels = var.notification_channels
  
  depends_on = [
    module.gke,
    module.vertex_ai,
  ]
}

# Cloud SQL for PostgreSQL
resource "google_sql_database_instance" "postgres" {
  name             = "rag7-postgres-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region
  
  settings {
    tier              = var.environment == "prod" ? "db-n1-standard-2" : "db-f1-micro"
    availability_type = var.environment == "prod" ? "REGIONAL" : "ZONAL"
    disk_size         = var.environment == "prod" ? 100 : 20
    disk_autoresize   = true
    
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = var.environment == "prod"
      start_time                     = "03:00"
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
      }
    }
    
    ip_configuration {
      ipv4_enabled    = false
      private_network = module.networking.network_id
      require_ssl     = true
    }
    
    database_flags {
      name  = "max_connections"
      value = var.environment == "prod" ? "200" : "50"
    }
  }
  
  deletion_protection = var.environment == "prod"
  
  depends_on = [
    module.networking,
    google_project_service.required_apis,
  ]
}

resource "google_sql_database" "rag7_db" {
  name     = "rag7_db"
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "rag7_user" {
  name     = "rag7_user"
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}

# Redis (Memorystore)
resource "google_redis_instance" "cache" {
  name           = "rag7-redis-${var.environment}"
  tier           = var.environment == "prod" ? "STANDARD_HA" : "BASIC"
  memory_size_gb = var.environment == "prod" ? 5 : 1
  region         = var.region
  
  authorized_network = module.networking.network_id
  
  redis_version     = "REDIS_7_0"
  display_name      = "RAG7 Redis Cache - ${var.environment}"
  reserved_ip_range = "10.1.0.0/29"
  
  depends_on = [
    module.networking,
    google_project_service.required_apis,
  ]
}

# Service Account for applications
resource "google_service_account" "rag7_app" {
  account_id   = "rag7-app-${var.environment}"
  display_name = "RAG7 Application Service Account - ${var.environment}"
}

resource "google_project_iam_member" "rag7_app_roles" {
  for_each = toset([
    "roles/aiplatform.user",
    "roles/cloudtrace.agent",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter",
    "roles/storage.objectViewer",
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.rag7_app.email}"
}
