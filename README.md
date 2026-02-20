# AGI Trading Platform

An AI-powered algorithmic trading platform with AGI orchestration, multi-exchange connectivity, real-time risk management, and TimescaleDB-backed market data storage.

> **⚠️ Paper / testnet mode is enabled by default.** No real capital is at risk during development.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Application (main.py)           │
├──────────────┬──────────────┬───────────────────────────┤
│ trading_engine│   dataops    │        shared             │
│ ├ connectors │ ├ ingestion  │ ├ models (Pydantic v2)    │
│ ├ execution  │ ├ storage    │ ├ common (config/logger)  │
│ ├ risk_mgmt  │ └ processing │ └ exceptions              │
│ └ portfolio  │              │                           │
└──────────────┴──────────────┴───────────────────────────┘
         │              │
   Alpaca / Binance   Redis · Kafka · TimescaleDB
```

| Layer | Responsibility |
|---|---|
| `shared/` | Pydantic models, config (pydantic-settings), structured logging (loguru), exceptions |
| `trading_engine/` | Exchange connectors (Alpaca, Binance), order lifecycle, pre-trade risk, portfolio P&L |
| `dataops/` | WebSocket market data collection, TimescaleDB persistence, Kafka stream processing |

---

## Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose

### 1. Clone and configure

```bash
cp .env.example .env
# Edit .env with your API keys (leave as placeholders for paper trading)
```

### 2. Start infrastructure

```bash
docker compose up -d postgres redis kafka
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the API server

```bash
export PYTHONPATH=$(pwd)
uvicorn main:app --reload --port 8000
```

The API will be available at <http://localhost:8000>.
Interactive docs: <http://localhost:8000/docs>

### 5. Run tests

```bash
pytest tests/unit/ -v
```

---

## Component Reference

### `shared/models/`

| Model | Description |
|---|---|
| `Order` | Full order lifecycle with fills, status transitions |
| `Position` | Open position with entry price and unrealised P&L |
| `Portfolio` | Aggregate portfolio with drawdown tracking |
| `OHLCV` | Candlestick bar |
| `OrderBook` | Level-2 order book snapshot |
| `TradingSignal` | Directional signal from a single model |
| `RiskAssessment` | Pre-trade risk evaluation result |
| `AGIDecision` | Composite action from the AGI orchestrator |

### `trading_engine/`

- **`AlpacaConnector`** – paper/live trading via alpaca-py
- **`BinanceConnector`** – spot trading via python-binance (testnet default)
- **`OrderManager`** – async order registry with exchange sync
- **`RiskEngine`** – configurable pre-trade limit checks
- **`PortfolioManager`** – thread-safe position and P&L tracking

### `dataops/`

- **`MarketDataCollector`** – WebSocket feed with Redis pub/sub fan-out
- **`TimeSeriesDB`** – asyncpg + TimescaleDB for OHLCV and trade storage
- **`StreamProcessor`** – aiokafka producer/consumer with auto-reconnect

---

## Configuration

All settings live in `config.yaml` and can be overridden by environment variables prefixed with `TRADING_`:

```bash
TRADING_DB_HOST=my-db-server
TRADING_RISK_MAX_ORDER_SIZE_USD=25000
TRADING_LOG_LEVEL=DEBUG
```

See `.env.example` for all available variables.

---

## Paper Trading Note

Both exchange connectors default to paper/testnet mode:

- **Alpaca**: `ALPACA_PAPER=true` (default) → paper-api.alpaca.markets
- **Binance**: `BINANCE_TESTNET=true` (default) → testnet.binance.vision

Set these to `false` only when you are ready to trade with real capital and have reviewed all risk limits in `config.yaml`.
