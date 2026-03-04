# Deployment Guide

## Local Development (Docker Compose)

### Start all services

```bash
docker compose up -d
```

This starts:
- `trading-engine` on port 8000
- `postgres` (TimescaleDB) on port 5432
- `redis` on port 6379
- `kafka` + `zookeeper` on port 9092
- `prometheus` on port 9090
- `grafana` on port 3000

### View logs

```bash
docker compose logs -f trading-engine
```

### Stop services

```bash
docker compose down
```

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Default | Description |
|---|---|---|
| `ALPACA_API_KEY` | – | Alpaca API key |
| `ALPACA_SECRET_KEY` | – | Alpaca secret key |
| `BINANCE_API_KEY` | – | Binance API key |
| `BINANCE_SECRET_KEY` | – | Binance secret key |
| `TRADING_DB_HOST` | `localhost` | PostgreSQL host |
| `TRADING_DB_PASSWORD` | `changeme` | PostgreSQL password |
| `TRADING_REDIS_HOST` | `localhost` | Redis host |
| `TRADING_RISK_MAX_ORDER_SIZE_USD` | `50000` | Per-order notional limit |
| `TRADING_RISK_MAX_PORTFOLIO_DRAWDOWN_PCT` | `10.0` | Drawdown halt threshold |
| `TRADING_LOG_LEVEL` | `INFO` | Log verbosity |
| `DB_PASSWORD` | `changeme` | Docker Compose DB password |
| `GRAFANA_PASSWORD` | `admin` | Grafana admin password |

---

## Kubernetes Deployment

### Prerequisites

- `kubectl` configured against your cluster
- Container registry credentials

### One-time cluster setup

Create the secrets that hold sensitive values (these are **not** committed to the
repository — they must be created in each target cluster):

```bash
# Create namespace (also applied automatically by the CD pipeline)
kubectl apply -f infrastructure/kubernetes/namespace.yaml

# Exchange API keys
kubectl create secret generic trading-engine-secrets \
  --namespace trading \
  --from-literal=ALPACA_API_KEY=<key> \
  --from-literal=ALPACA_SECRET_KEY=<secret>

# Database password
kubectl create secret generic postgres-secret \
  --namespace trading \
  --from-literal=password=<db-password>
```

### Deploy manually

```bash
# Apply namespace + non-sensitive config
kubectl apply -f infrastructure/kubernetes/namespace.yaml
kubectl apply -f infrastructure/kubernetes/configmap-production.yaml

# Apply workload manifests
kubectl apply -f infrastructure/kubernetes/deployments/

# Monitor rollout
kubectl rollout status deployment/trading-engine --namespace trading
```

### Verify

```bash
kubectl get pods -n trading
kubectl logs -n trading deployment/trading-engine
```

---

## CI/CD — Automated Deployment

The GitHub Actions CD pipeline (`.github/workflows/cd.yml`) deploys automatically:

| Trigger | Target | Job |
|---------|--------|-----|
| Push to `main` | Staging | `deploy-staging` |
| Push a `v*` tag | Production | `deploy-production` |

Both jobs share a **`build`** job that builds and pushes the Docker image to the
container registry before any deployment runs.

### Release to production

```bash
# Tag the commit you want to ship
git tag v1.2.3

# Push the tag — this triggers the CD pipeline's production deploy
git push origin v1.2.3
```

The pipeline will:
1. Build the `trading-engine` image and push it tagged as `v1.2.3` (and `1.2`)
2. Apply the Kubernetes namespace and ConfigMap
3. Apply all workload manifests
4. Roll out the new image (`kubectl set image …`)
5. Wait up to 3 minutes for the rollout to complete (`kubectl rollout status`)

### Required repository secrets

Configure these in **Settings → Secrets and variables → Actions**:

| Secret | Description |
|--------|-------------|
| `REGISTRY_URL` | Container registry hostname (e.g. `ghcr.io/your-org`) |
| `REGISTRY_USERNAME` | Registry login username |
| `REGISTRY_PASSWORD` | Registry login password / token |
| `STAGING_KUBECONFIG` | Base64-encoded kubeconfig for the staging cluster |
| `PRODUCTION_KUBECONFIG` | Base64-encoded kubeconfig for the production cluster |

Encode a kubeconfig file:

```bash
base64 -w 0 ~/.kube/staging-config
```

---

## Health Checks and Monitoring

| Endpoint | Description |
|---|---|
| `GET /health` | Liveness check (returns `{"status": "healthy"}`) |
| `GET /metrics` | Prometheus metrics |

Grafana dashboards are available at `http://localhost:3000` (default credentials: `admin` / `admin`).

### Prometheus scrape targets

Configured in `infrastructure/prometheus/prometheus.yml`:

- `trading-engine:8000/metrics`
- `postgres-exporter:9187`
- `redis-exporter:9121`
- `kafka-exporter:9308`
