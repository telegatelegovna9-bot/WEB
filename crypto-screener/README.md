# Crypto Screener Platform

Advanced cryptocurrency screening platform with intelligent signals and market behavior analysis.

## 🎯 Main Features

- Real-time market analysis across multiple exchanges
- Intelligent signal detection with explanations
- Probability scoring for signal reliability
- Historical pattern matching
- Smart money behavior analysis
- Telegram notifications

## 🏗️ Architecture

```
crypto-screener/
├── backend/          # Python FastAPI backend
│   ├── app/
│   │   ├── api/      # REST & WebSocket endpoints
│   │   ├── core/     # Configuration, security
│   │   ├── data/     # Data models, database
│   │   ├── engines/  # Signal detection & intelligence
│   │   ├── models/   # Pydantic models
│   │   ├── services/ # External APIs (exchanges)
│   │   └── utils/    # Helpers, utilities
│   └── tests/
└── frontend/         # React/Next.js frontend
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── hooks/
    │   ├── services/
    │   ├── store/
    │   ├── styles/
    │   └── types/
    └── public/
```

## 🚀 Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 📊 Supported Exchanges

- Binance
- OKX
- Bybit
- MEXC
- Gate
- Bitget

## 🔧 Technology Stack

**Backend:**
- Python 3.11+
- FastAPI
- PostgreSQL + TimescaleDB
- Redis
- WebSockets

**Frontend:**
- React 18
- Next.js 14
- TypeScript
- TradingView Charts
- TailwindCSS

## 📈 Signal Types

1. **Pump/Dump Detection** - Sharp price movements with volume spikes
2. **Order Book Density** - Large limit orders and walls
3. **Listing Detector** - New trading pairs
4. **Pattern Detection** - Breakouts, consolidations, formations

## 🧠 Signal Intelligence

Each signal includes:
- **Causes** - Why this is happening
- **Market Behavior Type** - Accumulation, Distribution, Breakout, Manipulation
- **Probability Score** - 0-100% confidence
- **Historical Analogies** - Similar past situations and outcomes

## 📝 License

MIT
