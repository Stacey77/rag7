#!/bin/bash

# ============================================================
# Ragamuffin Platform - Staging Deployment Script
# ============================================================
# This script deploys the platform to a staging environment.
#
# Usage:
#   ./deploy-staging.sh              # Deploy to staging
#   ./deploy-staging.sh --build      # Build and deploy
#   ./deploy-staging.sh --clean      # Clean volumes and deploy fresh
#   ./deploy-staging.sh --status     # Show status of all services
#   ./deploy-staging.sh --logs       # Follow logs
#   ./deploy-staging.sh --stop       # Stop all services
# ============================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.staging.yml"
ENV_FILE=".env.staging"
PROJECT_NAME="ragamuffin-staging"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    print_success "Prerequisites check passed."
}

# Function to check environment file
check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        print_warning "Environment file not found: $ENV_FILE"
        print_info "Creating from template..."
        if [ -f ".env.staging.example" ]; then
            cp .env.staging.example "$ENV_FILE"
            print_warning "Please edit $ENV_FILE with your staging credentials before deploying!"
            print_warning "At minimum, change the following:"
            echo "  - JWT_SECRET_KEY"
            echo "  - N8N_BASIC_AUTH_PASSWORD"
            echo "  - MINIO_ROOT_PASSWORD"
            echo ""
            read -p "Press Enter to continue after editing, or Ctrl+C to cancel..."
        else
            print_error "Template file .env.staging.example not found!"
            exit 1
        fi
    fi
    
    # Check for default/insecure values
    if grep -q "CHANGE_ME" "$ENV_FILE" 2>/dev/null; then
        print_warning "Environment file contains default values that should be changed!"
        print_warning "Please update $ENV_FILE with secure credentials."
    fi
}

# Function to run security checks
security_check() {
    print_info "Running security checks..."
    
    local issues=0
    
    # Check for default JWT secret
    if grep -q "staging-secret-change-me" "$ENV_FILE" 2>/dev/null; then
        print_warning "⚠️  JWT_SECRET_KEY is using default value - CHANGE IT!"
        issues=$((issues + 1))
    fi
    
    # Check for weak passwords
    if grep -qE "password123|admin123|staging123" "$ENV_FILE" 2>/dev/null; then
        print_warning "⚠️  Weak passwords detected in environment file!"
        issues=$((issues + 1))
    fi
    
    if [ $issues -gt 0 ]; then
        print_warning "Security check found $issues issue(s). Review before production deployment."
    else
        print_success "Security checks passed."
    fi
}

# Function to build images
build_images() {
    print_info "Building Docker images..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" -p "$PROJECT_NAME" build
    print_success "Images built successfully."
}

# Function to deploy services
deploy() {
    print_info "Deploying Ragamuffin to staging..."
    
    # Pull latest base images
    print_info "Pulling latest base images..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" -p "$PROJECT_NAME" pull --ignore-pull-failures
    
    # Start services
    print_info "Starting services..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" -p "$PROJECT_NAME" up -d
    
    print_success "Deployment initiated!"
}

# Function to wait for services to be healthy
wait_for_health() {
    print_info "Waiting for services to become healthy..."
    
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        local healthy=0
        local total=0
        
        # Check each service
        for service in etcd minio milvus n8n rag-service langflow backend frontend; do
            total=$((total + 1))
            if docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps "$service" 2>/dev/null | grep -q "healthy\|running"; then
                healthy=$((healthy + 1))
            fi
        done
        
        if [ $healthy -eq $total ]; then
            print_success "All services are healthy!"
            return 0
        fi
        
        echo -ne "\r${BLUE}[INFO]${NC} Services ready: $healthy/$total (attempt $((attempt + 1))/$max_attempts)"
        sleep 5
        attempt=$((attempt + 1))
    done
    
    echo ""
    print_warning "Timeout waiting for all services. Some services may still be starting."
    show_status
}

# Function to show status
show_status() {
    print_info "Service Status:"
    echo ""
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps
    echo ""
    print_info "Access Points:"
    echo "  Frontend:     http://localhost:8080"
    echo "  Backend API:  http://localhost:8000/docs"
    echo "  RAG Service:  http://localhost:8001/docs"
    echo "  LangFlow:     http://localhost:7860"
    echo "  n8n:          http://localhost:5678"
    echo "  MinIO:        http://localhost:9001"
}

# Function to show logs
show_logs() {
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f
}

# Function to stop services
stop_services() {
    print_info "Stopping Ragamuffin staging services..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
    print_success "Services stopped."
}

# Function to clean and redeploy
clean_deploy() {
    print_warning "This will remove all staging data (volumes). Are you sure? [y/N]"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_info "Stopping services and removing volumes..."
        docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down -v
        print_success "Cleaned. Redeploying fresh..."
        deploy
    else
        print_info "Cancelled."
    fi
}

# Function to run pre-deployment checklist
run_checklist() {
    print_info "Pre-Deployment Checklist"
    echo "========================="
    echo ""
    
    local passed=0
    local total=10
    
    # 1. Check Docker
    if command -v docker &> /dev/null; then
        echo -e "✅ Docker installed"
        passed=$((passed + 1))
    else
        echo -e "❌ Docker not installed"
    fi
    
    # 2. Check Docker Compose
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        echo -e "✅ Docker Compose installed"
        passed=$((passed + 1))
    else
        echo -e "❌ Docker Compose not installed"
    fi
    
    # 3. Check environment file
    if [ -f "$ENV_FILE" ]; then
        echo -e "✅ Environment file exists"
        passed=$((passed + 1))
    else
        echo -e "❌ Environment file missing"
    fi
    
    # 4. Check compose file
    if [ -f "$COMPOSE_FILE" ]; then
        echo -e "✅ Compose file exists"
        passed=$((passed + 1))
    else
        echo -e "❌ Compose file missing"
    fi
    
    # 5. Check JWT secret
    if [ -f "$ENV_FILE" ] && ! grep -q "CHANGE_ME\|staging-secret" "$ENV_FILE" | grep -q "JWT_SECRET"; then
        echo -e "✅ JWT secret configured"
        passed=$((passed + 1))
    else
        echo -e "⚠️  JWT secret may need updating"
        passed=$((passed + 1))
    fi
    
    # 6. Check disk space (need at least 10GB)
    local available_space=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$available_space" -gt 10 ]; then
        echo -e "✅ Sufficient disk space (${available_space}GB available)"
        passed=$((passed + 1))
    else
        echo -e "⚠️  Low disk space (${available_space}GB available, 10GB+ recommended)"
    fi
    
    # 7. Check memory (need at least 8GB)
    local total_mem=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$total_mem" -ge 8 ]; then
        echo -e "✅ Sufficient memory (${total_mem}GB available)"
        passed=$((passed + 1))
    else
        echo -e "⚠️  Low memory (${total_mem}GB available, 8GB+ recommended)"
    fi
    
    # 8. Check ports availability
    local ports_free=true
    for port in 8000 8001 8080 7860 5678 9000 9001 19530; do
        if lsof -i ":$port" &> /dev/null; then
            echo -e "⚠️  Port $port is in use"
            ports_free=false
        fi
    done
    if $ports_free; then
        echo -e "✅ Required ports are available"
        passed=$((passed + 1))
    fi
    
    # 9. Check network connectivity
    if ping -c 1 docker.io &> /dev/null 2>&1 || ping -c 1 hub.docker.com &> /dev/null 2>&1; then
        echo -e "✅ Network connectivity OK"
        passed=$((passed + 1))
    else
        echo -e "⚠️  Network connectivity issues"
    fi
    
    # 10. Documentation check
    if [ -f "SECURITY.md" ] && [ -f "PRODUCTION.md" ]; then
        echo -e "✅ Documentation files present"
        passed=$((passed + 1))
    else
        echo -e "⚠️  Documentation files missing"
    fi
    
    echo ""
    echo "========================="
    print_info "Checklist: $passed/$total passed"
    
    if [ $passed -ge 8 ]; then
        print_success "Ready for staging deployment!"
        return 0
    else
        print_warning "Review warnings before deploying."
        return 1
    fi
}

# Main script
main() {
    echo "============================================================"
    echo "  Ragamuffin Platform - Staging Deployment"
    echo "============================================================"
    echo ""
    
    case "${1:-}" in
        --build)
            check_prerequisites
            check_env_file
            security_check
            build_images
            deploy
            wait_for_health
            show_status
            ;;
        --clean)
            check_prerequisites
            clean_deploy
            wait_for_health
            show_status
            ;;
        --status)
            show_status
            ;;
        --logs)
            show_logs
            ;;
        --stop)
            stop_services
            ;;
        --checklist)
            run_checklist
            ;;
        --help|-h)
            echo "Usage: $0 [OPTION]"
            echo ""
            echo "Options:"
            echo "  (no option)   Deploy to staging"
            echo "  --build       Build images and deploy"
            echo "  --clean       Remove volumes and deploy fresh"
            echo "  --status      Show status of all services"
            echo "  --logs        Follow service logs"
            echo "  --stop        Stop all services"
            echo "  --checklist   Run pre-deployment checklist"
            echo "  --help        Show this help message"
            ;;
        *)
            check_prerequisites
            check_env_file
            security_check
            run_checklist || true
            echo ""
            read -p "Continue with deployment? [y/N] " response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                deploy
                wait_for_health
                show_status
            else
                print_info "Deployment cancelled."
            fi
            ;;
    esac
}

# Run main function
main "$@"
