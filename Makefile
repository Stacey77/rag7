.PHONY: help install install-dev test lint format type-check security-check docker-build docker-up docker-down deploy-dev clean db-migrate db-upgrade db-downgrade terraform-init terraform-plan terraform-apply

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt -r requirements-dev.txt

test: ## Run tests with coverage
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

test-unit: ## Run unit tests only
	pytest tests/unit/ -v -m unit

test-integration: ## Run integration tests only
	pytest tests/integration/ -v -m integration

test-orchestration: ## Run orchestration tests
	pytest tests/orchestration/ -v -m orchestration

test-chaos: ## Run chaos tests
	pytest tests/orchestration/ -v -m chaos

test-e2e: ## Run end-to-end tests
	pytest tests/e2e/ -v -m e2e

lint: ## Run linting with ruff
	ruff check src/ tests/

format: ## Format code with black and ruff
	black src/ tests/
	ruff check --fix src/ tests/

type-check: ## Run type checking with mypy
	mypy src/

security-check: ## Run security scanning with bandit
	bandit -r src/ -f json -o bandit-report.json

docker-build: ## Build Docker image
	docker build -t rag7-agent-api:latest .

docker-build-dev: ## Build Docker image for development
	docker build --target development -t rag7-agent-api:dev .

docker-up: ## Start all services with docker-compose
	docker-compose up -d

docker-down: ## Stop all services
	docker-compose down

docker-logs: ## View logs from all services
	docker-compose logs -f

docker-test: ## Run tests in Docker
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit

deploy-dev: ## Deploy to development environment
	@echo "Deploying to development environment..."
	./deploy/cloud-run/deploy.sh dev

deploy-staging: ## Deploy to staging environment
	@echo "Deploying to staging environment..."
	./deploy/cloud-run/deploy.sh staging

deploy-prod: ## Deploy to production environment
	@echo "Deploying to production environment..."
	./deploy/cloud-run/deploy.sh prod

clean: ## Clean up generated files
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .mypy_cache/ htmlcov/ .coverage
	rm -f bandit-report.json

local-setup: ## Set up local development environment
	cp .env.example .env
	@echo "Please edit .env file with your configuration"
	make install-dev

run-local: ## Run application locally
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8080

monitoring-up: ## Start monitoring stack (Prometheus + Grafana)
	docker-compose up -d prometheus grafana

# Database migration commands
db-migrate: ## Create a new database migration
	alembic revision --autogenerate -m "$(m)"

db-upgrade: ## Upgrade database to latest version
	alembic upgrade head

db-downgrade: ## Downgrade database by one version
	alembic downgrade -1

db-reset: ## Reset database (WARNING: destructive)
	alembic downgrade base
	alembic upgrade head

# Terraform commands
terraform-init: ## Initialize Terraform
	cd deploy/terraform && terraform init

terraform-plan: ## Run Terraform plan
	cd deploy/terraform && terraform plan -var-file=environments/$(env)/terraform.tfvars

terraform-apply: ## Apply Terraform changes
	cd deploy/terraform && terraform apply -var-file=environments/$(env)/terraform.tfvars

terraform-destroy: ## Destroy Terraform resources (WARNING: destructive)
	cd deploy/terraform && terraform destroy -var-file=environments/$(env)/terraform.tfvars

all: format lint type-check test ## Run all checks and tests
