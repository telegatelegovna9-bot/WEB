# CryptoMind AI - Advanced Crypto Screener with Intelligence

## 🚀 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                       │
│  Dashboard | Signals | Charts | Heatmap | OrderBook Viz    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   API LAYER (FastAPI)                       │
│         REST + WebSocket Server + Signal Streaming          │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  SIGNAL ENGINE   │ │ INTELLIGENCE     │ │  STRATEGY        │
│  - Pump/Dump     │ │  - Explanation   │ │  - Modular       │
│  - OrderBook     │ │  - Probability   │ │  - Extensible    │
│  - Listing       │ │  - History Match │ │                  │
│  - Patterns      │ │  - Smart Money   │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  DATA ENGINE (WebSocket)                    │
│    Binance │ OKX │ Bybit │ MEXC │ Gate │ Bitget            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL + TimescaleDB + Redis               │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
cryptomind-ai/
├── backend/
│   ├── app/
│   │   ├── core/           # Config, security, database
│   │   ├── engines/        # Signal, Intelligence, Strategy engines
│   │   ├── integrations/   # Exchange connectors (Binance, OKX, etc.)
│   │   ├── api/            # REST & WebSocket endpoints
│   │   └── models/         # Pydantic & SQLAlchemy models
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # API & WebSocket clients
│   │   └── styles/         # Tailwind CSS
│   └── public/
├── docker-compose.yml
└── README.md
```

## 🔥 Key Features

1. **Intelligent Signals** - Not just alerts, but explanations
2. **Probability Scoring** - 0-100% confidence rating
3. **Historical Pattern Matching** - Learn from past scenarios
4. **Smart Money Detection** - Track whale movements
5. **Multi-Exchange Support** - 6 major exchanges integrated

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, WebSockets
- **Frontend**: Next.js 14, React, TailwindCSS, TradingView Charts
- **Database**: PostgreSQL + TimescaleDB
- **Cache**: Redis
- **Real-time**: WebSocket streaming

## 🚀 Quick Start

```bash
# Start all services
docker-compose up -d

# Access frontend
http://localhost:3000

# Access API docs
http://localhost:8000/docs
```

## 📊 Metrics

- Signal accuracy tracking
- Latency monitoring (<100ms target)
- Winrate analytics
- User retention metrics
