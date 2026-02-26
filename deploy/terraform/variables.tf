variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "notification_channels" {
  description = "List of notification channels for alerts"
  type        = list(string)
  default     = []
}

variable "enable_binary_authorization" {
  description = "Enable binary authorization for GKE"
  type        = bool
  default     = false
}

variable "enable_workload_identity" {
  description = "Enable workload identity for GKE"
  type        = bool
  default     = true
}
