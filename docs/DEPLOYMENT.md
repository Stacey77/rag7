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

### Create namespace and secrets

```bash
kubectl create namespace trading

kubectl create secret generic trading-engine-secrets \
  --namespace trading \
  --from-literal=ALPACA_API_KEY=<key> \
  --from-literal=ALPACA_SECRET_KEY=<secret>

kubectl create secret generic postgres-secret \
  --namespace trading \
  --from-literal=password=<db-password>
```

### Deploy

```bash
kubectl apply -f infrastructure/kubernetes/deployments/
```

### Verify

```bash
kubectl get pods -n trading
kubectl logs -n trading deployment/trading-engine
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
