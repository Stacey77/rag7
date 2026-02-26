output "gke_cluster_name" {
  description = "GKE cluster name"
  value       = module.gke.cluster_name
}

output "gke_cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = module.gke.cluster_endpoint
  sensitive   = true
}

output "postgres_connection_name" {
  description = "PostgreSQL connection name"
  value       = google_sql_database_instance.postgres.connection_name
}

output "postgres_private_ip" {
  description = "PostgreSQL private IP"
  value       = google_sql_database_instance.postgres.private_ip_address
}

output "redis_host" {
  description = "Redis host"
  value       = google_redis_instance.cache.host
}

output "redis_port" {
  description = "Redis port"
  value       = google_redis_instance.cache.port
}

output "service_account_email" {
  description = "Application service account email"
  value       = google_service_account.rag7_app.email
}

output "vpc_network_name" {
  description = "VPC network name"
  value       = module.networking.network_name
}

output "vertex_ai_endpoint" {
  description = "Vertex AI endpoint"
  value       = module.vertex_ai.endpoint_id
}
