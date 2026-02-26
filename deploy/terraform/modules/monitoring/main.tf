# Monitoring Module

variable "project_id" {
  type = string
}

variable "environment" {
  type = string
}

variable "notification_channels" {
  type    = list(string)
  default = []
}

# Alert Policy: High Error Rate
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "High Error Rate - ${var.environment}"
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate > 5%"
    
    condition_threshold {
      filter          = "resource.type=\"k8s_container\" AND metric.type=\"logging.googleapis.com/user/error_rate\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 5.0
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = var.notification_channels
  
  alert_strategy {
    auto_close = "1800s"
  }
}

# Alert Policy: High LLM Cost
resource "google_monitoring_alert_policy" "high_llm_cost" {
  display_name = "High LLM Cost - ${var.environment}"
  combiner     = "OR"
  
  conditions {
    display_name = "Daily LLM cost > $100"
    
    condition_threshold {
      filter          = "resource.type=\"k8s_container\" AND metric.type=\"custom.googleapis.com/llm_cost_usd_total\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 100.0
      
      aggregations {
        alignment_period   = "86400s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }
  
  notification_channels = var.notification_channels
}

# Dashboard
resource "google_monitoring_dashboard" "rag7_dashboard" {
  dashboard_json = jsonencode({
    displayName = "RAG7 Multi-Agent System - ${var.environment}"
    mosaicLayout = {
      columns = 12
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "Agent Task Duration (p95)"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"custom.googleapis.com/agent_task_duration_seconds\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_DELTA"
                      crossSeriesReducer = "REDUCE_PERCENTILE_95"
                    }
                  }
                }
              }]
            }
          }
        },
        {
          width  = 6
          height = 4
          xPos   = 6
          widget = {
            title = "LLM API Calls"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"custom.googleapis.com/llm_api_calls_total\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                    }
                  }
                }
              }]
            }
          }
        }
      ]
    }
  })
}

output "alert_policy_ids" {
  value = [
    google_monitoring_alert_policy.high_error_rate.id,
    google_monitoring_alert_policy.high_llm_cost.id,
  ]
}

output "dashboard_id" {
  value = google_monitoring_dashboard.rag7_dashboard.id
}
