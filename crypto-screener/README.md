# Crypto Screener Platform

Advanced cryptocurrency screening platform with intelligent signals and market behavior analysis.

## Architecture

```
crypto-screener/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # REST & WebSocket endpoints
│   │   ├── core/     # Core configuration
│   │   ├── models/   # Data models
│   │   ├── services/ # Business logic
│   │   └── strategies/ # Trading strategies
│   └── data/         # Database migrations
└── frontend/         # Next.js frontend
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── hooks/
    │   ├── services/
    │   └── styles/
    └── public/
```

## Features

- Real-time market data from multiple exchanges (Binance, OKX, Bybit, MEXC, Gate, Bitget)
- Intelligent signal detection with explanations
- Probability scoring for signals
- Historical pattern matching
- Order book analysis
- Telegram notifications
- Modern dashboard UI

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Tech Stack

- **Backend**: Python, FastAPI, WebSockets
- **Database**: PostgreSQL + TimescaleDB
- **Frontend**: Next.js, React, TailwindCSS
- **Charts**: TradingView Lightweight Charts
- **Real-time**: WebSockets, Redis
