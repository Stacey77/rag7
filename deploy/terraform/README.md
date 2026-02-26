# Terraform Infrastructure

This directory contains Terraform configurations for deploying the RAG7 Multi-Agent System infrastructure on Google Cloud Platform.

## Structure

```
terraform/
├── main.tf              # Main infrastructure configuration
├── variables.tf         # Input variables
├── outputs.tf           # Output values
├── backend.tf           # State backend configuration
├── modules/             # Reusable modules
│   ├── gke/            # GKE cluster module
│   ├── vertex-ai/      # Vertex AI configuration
│   ├── networking/     # VPC and networking
│   └── monitoring/     # Monitoring and alerting
└── environments/        # Environment-specific configs
    ├── dev/
    ├── staging/
    └── prod/
```

## Prerequisites

1. **Google Cloud SDK**: Install and configure `gcloud`
2. **Terraform**: Install Terraform >= 1.5.0
3. **GCP Project**: Create a GCP project and enable billing
4. **Service Account**: Create a service account with appropriate permissions

## Initial Setup

### 1. Create GCS Bucket for State

```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"

# Create bucket for Terraform state
gsutil mb -p $PROJECT_ID -l $REGION gs://${PROJECT_ID}-terraform-state

# Enable versioning
gsutil versioning set on gs://${PROJECT_ID}-terraform-state
```

### 2. Configure Backend

Update `backend.tf` with your bucket name:

```hcl
terraform {
  backend "gcs" {
    bucket = "your-project-terraform-state"
    prefix = "terraform/state"
  }
}
```

### 3. Create Environment Configuration

Create `environments/dev/terraform.tfvars`:

```hcl
project_id  = "your-project-id"
region      = "us-central1"
environment = "dev"
db_password = "your-secure-password"

notification_channels = [
  "projects/your-project/notificationChannels/123456"
]
```

## Deployment

### Initialize Terraform

```bash
make terraform-init
```

### Plan Changes

```bash
make terraform-plan env=dev
```

### Apply Changes

```bash
make terraform-apply env=dev
```

## Modules

### GKE Module

Creates a GKE cluster with:
- Private nodes
- Workload Identity enabled
- Horizontal Pod Autoscaling
- Network policies
- Multiple node pools

### Vertex AI Module

Sets up Vertex AI endpoints for agent deployment.

### Networking Module

Creates:
- VPC network
- Subnets with secondary IP ranges for pods and services
- Cloud NAT for private node internet access
- Firewall rules

### Monitoring Module

Configures:
- Alert policies for error rates and costs
- Monitoring dashboards
- Notification channels

## Resources Created

The Terraform configuration creates:

1. **GKE Cluster**: Kubernetes cluster for agent deployment
2. **Cloud SQL (PostgreSQL)**: Database for persistent storage
3. **Redis (Memorystore)**: Caching layer
4. **VPC Network**: Private networking
5. **Service Accounts**: IAM for applications
6. **Monitoring**: Dashboards and alerts
7. **Vertex AI**: Endpoints for model deployment

## Cost Estimation

Development environment (minimal):
- GKE: ~$150/month (1 node, preemptible)
- Cloud SQL: ~$25/month (db-f1-micro)
- Redis: ~$50/month (1GB, basic)
- **Total: ~$225/month**

Production environment (recommended):
- GKE: ~$500/month (3-20 nodes, standard)
- Cloud SQL: ~$200/month (db-n1-standard-2, HA)
- Redis: ~$200/month (5GB, HA)
- **Total: ~$900/month**

## Security Best Practices

1. **Secrets**: Never commit `terraform.tfvars` with actual credentials
2. **State**: Use GCS backend with versioning enabled
3. **IAM**: Follow principle of least privilege
4. **Encryption**: Enable encryption at rest for databases
5. **Network**: Use private GKE nodes
6. **Monitoring**: Set up alerts for cost and errors

## Outputs

After applying, Terraform will output:

- GKE cluster endpoint
- Database connection name
- Redis host
- Service account email
- VPC network name

Access outputs:

```bash
cd deploy/terraform
terraform output
```

## Troubleshooting

### State Lock Issues

If state is locked:

```bash
cd deploy/terraform
terraform force-unlock LOCK_ID
```

### Permission Errors

Ensure your service account has these roles:
- `roles/compute.admin`
- `roles/container.admin`
- `roles/iam.serviceAccountAdmin`
- `roles/resourcemanager.projectIamAdmin`

### API Enablement

If APIs are not enabled:

```bash
gcloud services enable \
  compute.googleapis.com \
  container.googleapis.com \
  aiplatform.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com
```

## Cleanup

To destroy all resources (WARNING: destructive):

```bash
make terraform-destroy env=dev
```

## Support

For issues or questions:
- Check Terraform logs: `terraform show`
- Review GCP console for resource status
- Check deployment documentation in `docs/DEPLOYMENT.md`
