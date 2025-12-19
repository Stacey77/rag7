# Networking Module

variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "environment" {
  type = string
}

variable "network_name" {
  type = string
}

resource "google_compute_network" "vpc" {
  name                    = "${var.network_name}-${var.environment}"
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
}

resource "google_compute_subnetwork" "subnet" {
  name          = "${var.network_name}-subnet-${var.environment}"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
  
  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.1.0.0/16"
  }
  
  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.2.0.0/22"
  }
  
  private_ip_google_access = true
}

resource "google_compute_router" "router" {
  name    = "${var.network_name}-router-${var.environment}"
  region  = var.region
  network = google_compute_network.vpc.id
}

resource "google_compute_router_nat" "nat" {
  name   = "${var.network_name}-nat-${var.environment}"
  router = google_compute_router.router.name
  region = var.region
  
  nat_ip_allocate_option = "AUTO_ONLY"
  
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

resource "google_compute_firewall" "allow_internal" {
  name    = "${var.network_name}-allow-internal-${var.environment}"
  network = google_compute_network.vpc.name
  
  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  
  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }
  
  allow {
    protocol = "icmp"
  }
  
  source_ranges = ["10.0.0.0/8"]
}

output "network_id" {
  value = google_compute_network.vpc.id
}

output "network_name" {
  value = google_compute_network.vpc.name
}

output "subnet_name" {
  value = google_compute_subnetwork.subnet.name
}

output "master_ipv4_cidr_block" {
  value = "172.16.0.0/28"
}
