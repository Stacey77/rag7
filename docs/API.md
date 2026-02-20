# API Reference

Base URL: `http://localhost:8000`

Interactive docs (Swagger UI): `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

---

## System Endpoints

### `GET /`

Returns platform information.

**Response 200**

```json
{
  "service": "AGI Trading Platform",
  "version": "0.1.0",
  "docs": "/docs",
  "health": "/health",
  "metrics": "/metrics"
}
```

---

### `GET /health`

Liveness / readiness check used by Kubernetes probes and Docker HEALTHCHECK.

**Response 200**

```json
{
  "status": "healthy",
  "service": "agi-trading-platform",
  "version": "0.1.0"
}
```

---

### `GET /metrics`

Prometheus metrics in text exposition format.

**Response 200** – `text/plain; version=0.0.4`

```
# HELP python_gc_objects_collected_total ...
# TYPE python_gc_objects_collected_total counter
...
```

---

## Request / Response Schemas

### Order

```json
{
  "order_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "exchange_order_id": "abc123",
  "symbol": "BTCUSDT",
  "side": "BUY",
  "order_type": "MARKET",
  "quantity": "0.01",
  "price": null,
  "time_in_force": "GTC",
  "status": "ACCEPTED",
  "filled_quantity": "0",
  "average_fill_price": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Position

```json
{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "quantity": "0.5",
  "average_entry_price": "45000.00",
  "current_price": "47000.00",
  "unrealised_pnl": "1000.00",
  "realised_pnl": "0",
  "opened_at": "2024-01-01T00:00:00Z"
}
```

### RiskAssessment

```json
{
  "assessment_id": "...",
  "symbol": "BTCUSDT",
  "proposed_quantity": "0.01",
  "proposed_notional_usd": "450.00",
  "current_drawdown_pct": 3.33,
  "is_approved": true,
  "risk_score": 0.05,
  "rejection_reasons": [],
  "warnings": []
}
```

---

## Enum Values

### Side
- `BUY`
- `SELL`

### OrderType
- `MARKET`
- `LIMIT`
- `STOP`
- `STOP_LIMIT`
- `TRAILING_STOP`

### OrderStatus
- `PENDING` → `SUBMITTED` → `ACCEPTED` → `PARTIALLY_FILLED` → `FILLED`
- Terminal: `CANCELLED`, `REJECTED`, `EXPIRED`

### TimeInForce
- `GTC` – Good Till Cancelled
- `IOC` – Immediate Or Cancel
- `FOK` – Fill Or Kill
- `DAY` – Day order
- `GTD` – Good Till Date
