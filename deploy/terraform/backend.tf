terraform {
  backend "gcs" {
    bucket = "rag7-terraform-state"
    prefix = "terraform/state"
  }
}
