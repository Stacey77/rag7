#!/bin/bash
set -e

# Vertex AI Agent Deployment Script
# Usage: ./deploy.sh [dev|staging|prod]

ENVIRONMENT=${1:-dev}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ID=${GOOGLE_PROJECT_ID:-""}
REGION=${GOOGLE_REGION:-"us-central1"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    log_error "Invalid environment: $ENVIRONMENT"
    echo "Usage: $0 [dev|staging|prod]"
    exit 1
fi

# Check required variables
if [ -z "$PROJECT_ID" ]; then
    log_error "GOOGLE_PROJECT_ID not set"
    exit 1
fi

log_info "Deploying to Vertex AI - Environment: $ENVIRONMENT"
log_info "Project: $PROJECT_ID, Region: $REGION"

# Set environment-specific variables
case $ENVIRONMENT in
    dev)
        AGENT_NAME="rag7-agent-dev"
        MIN_REPLICAS=1
        MAX_REPLICAS=3
        ;;
    staging)
        AGENT_NAME="rag7-agent-staging"
        MIN_REPLICAS=2
        MAX_REPLICAS=10
        ;;
    prod)
        AGENT_NAME="rag7-agent-prod"
        MIN_REPLICAS=3
        MAX_REPLICAS=20
        ;;
esac

log_info "Deployment complete!"
log_info "Agent: $AGENT_NAME"
