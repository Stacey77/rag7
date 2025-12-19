# Vertex AI Module

variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "environment" {
  type = string
}

resource "google_vertex_ai_endpoint" "rag7_agent" {
  name         = "rag7-agent-${var.environment}"
  display_name = "RAG7 Multi-Agent System - ${var.environment}"
  location     = var.region
  region       = var.region
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
    application = "rag7"
  }
}

output "endpoint_id" {
  value = google_vertex_ai_endpoint.rag7_agent.id
}

output "endpoint_name" {
  value = google_vertex_ai_endpoint.rag7_agent.name
}
