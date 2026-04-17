from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncio
import json
from datetime import datetime

from app.models.schemas import (
    ExchangeType, SignalType, TickerData, Signal, OrderBook,
    ScreenerStats, FilterParams, PatternDetection, DensityDetection
)
from app.services.exchange_connector import (
    ExchangeManager, BinanceConnector, OKXConnector, BybitConnector,
    exchange_manager
)
from app.services.signal_engine import (
    intelligence_engine, pattern_detector, density_detector
)

app = FastAPI(title="Crypto Screener Pro", version="2.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
active_connections: List[WebSocket] = []
latest_tickers: List[TickerData] = []
latest_signals: List[Signal] = []
latest_patterns: List[PatternDetection] = []
latest_densities: List[DensityDetection] = []


@app.on_event("startup")
async def startup_event():
    """Initialize exchange connections on startup"""
    # Add connectors
    exchange_manager.add_connector(BinanceConnector())
    exchange_manager.add_connector(OKXConnector())
    exchange_manager.add_connector(BybitConnector())

    # Initialize connections
    await exchange_manager.initialize()

    # Start background tasks
    asyncio.create_task(fetch_tickers_periodically())
    asyncio.create_task(generate_demo_signals())
    print("✅ Crypto Screener Pro started successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await exchange_manager.shutdown()


async def fetch_tickers_periodically():
    """Fetch tickers from all exchanges every 5 seconds"""
    global latest_tickers, latest_signals
    
    while True:
        try:
            tickers = await exchange_manager.get_all_tickers()
            if tickers:
                latest_tickers.clear()
                latest_tickers.extend(tickers[:100])  # Keep top 100

                # Analyze for signals
                for ticker in tickers[:20]:  # Analyze top 20
                    signal = intelligence_engine.analyze_signal(ticker)
                    if signal:
                        latest_signals.insert(0, signal)
                        latest_signals = latest_signals[:50]  # Keep last 50 signals

                # Broadcast to WebSocket clients
                await broadcast_data()

        except Exception as e:
            print(f"Error fetching tickers: {e}")

        await asyncio.sleep(5)


async def generate_demo_signals():
    """Generate realistic demo signals for demonstration"""
    global latest_signals, latest_tickers
    
    demo_symbols = [
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
        "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "TRXUSDT", "LINKUSDT"
    ]

    while True:
        try:
            # Find real ticker data
            for symbol in demo_symbols[:3]:
                ticker = None
                for t in latest_tickers:
                    if t.symbol == symbol:
                        ticker = t
                        break

                if not ticker:
                    continue

                # Randomly generate signals based on real data
                import random
                if random.random() < 0.3:  # 30% chance every cycle
                    # Modify ticker slightly to trigger signal
                    modified_ticker = ticker.copy()
                    if random.random() < 0.6:
                        modified_ticker.price_change_percent_24h = random.uniform(5, 25)
                    else:
                        modified_ticker.price_change_percent_24h = random.uniform(-25, -5)
                    modified_ticker.quote_volume_24h = random.uniform(50_000_000, 500_000_000)

                    signal = intelligence_engine.analyze_signal(modified_ticker)
                    if signal:
                        latest_signals.insert(0, signal)
                        latest_signals = latest_signals[:50]
                        await broadcast_data()

        except Exception as e:
            print(f"Demo signal error: {e}")

        await asyncio.sleep(10)


async def broadcast_data():
    """Broadcast latest data to all connected WebSocket clients"""
    if not active_connections:
        return

    message = {
        "type": "update",
        "tickers": [t.dict() for t in latest_tickers[:50]],
        "signals": [s.dict() for s in latest_signals[:20]],
        "patterns": [p.dict() for p in latest_patterns],
        "densities": [d.dict() for d in latest_densities],
        "timestamp": datetime.utcnow().isoformat()
    }

    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            disconnected.append(connection)

    # Remove disconnected clients
    for conn in disconnected:
        active_connections.remove(conn)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)

    # Send initial data
    initial_data = {
        "type": "initial",
        "tickers": [t.dict() for t in latest_tickers[:50]],
        "signals": [s.dict() for s in latest_signals[:20]],
        "stats": get_stats().dict()
    }
    await websocket.send_json(initial_data)

    try:
        while True:
            # Keep connection alive, receive messages from client
            data = await websocket.receive_text()
            # Handle client messages if needed
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


def get_stats() -> ScreenerStats:
    """Calculate screener statistics"""
    top_gainers = sorted(latest_tickers, key=lambda x: x.price_change_percent_24h, reverse=True)[:6]
    top_losers = sorted(latest_tickers, key=lambda x: x.price_change_percent_24h)[:6]
    top_volume = sorted(latest_tickers, key=lambda x: x.quote_volume_24h, reverse=True)[:6]

    return ScreenerStats(
        total_signals=len(latest_signals),
        signals_last_hour=min(len(latest_signals), 20),
        active_exchanges=len(exchange_manager.active_exchanges),
        tracked_symbols=len(set(t.symbol for t in latest_tickers)),
        top_gainers=top_gainers,
        top_losers=top_losers,
        top_volume=top_volume,
        avg_signal_accuracy=72.5  # Mock accuracy
    )


# REST API Endpoints

@app.get("/api/tickers")
async def get_tickers(
    exchange: Optional[ExchangeType] = None,
    search: Optional[str] = None,
    sort_by: str = "quote_volume_24h",
    limit: int = 100
):
    """Get all tickers with filtering and sorting"""
    tickers = latest_tickers.copy()

    # Filter by exchange
    if exchange:
        tickers = [t for t in tickers if t.exchange == exchange]

    # Filter by search query
    if search:
        search_upper = search.upper()
        tickers = [t for t in tickers if search_upper in t.symbol]

    # Sort
    if sort_by == "price_change_percent_24h":
        tickers.sort(key=lambda x: x.price_change_percent_24h, reverse=True)
    elif sort_by == "quote_volume_24h":
        tickers.sort(key=lambda x: x.quote_volume_24h, reverse=True)
    elif sort_by == "price":
        tickers.sort(key=lambda x: x.price, reverse=True)

    return {"tickers": tickers[:limit]}


@app.get("/api/signals")
async def get_signals(
    exchange: Optional[ExchangeType] = None,
    signal_type: Optional[SignalType] = None,
    min_probability: float = 0,
    search: Optional[str] = None,
    limit: int = 50
):
    """Get signals with filtering"""
    signals = latest_signals.copy()

    # Filter by exchange
    if exchange:
        signals = [s for s in signals if s.exchange == exchange]

    # Filter by signal type
    if signal_type:
        signals = [s for s in signals if s.type == signal_type]

    # Filter by minimum probability
    if min_probability > 0:
        signals = [s for s in signals if s.intelligence.probability_score >= min_probability]

    # Filter by search
    if search:
        search_upper = search.upper()
        signals = [s for s in signals if search_upper in s.symbol]

    return {"signals": signals[:limit]}


@app.get("/api/stats")
async def get_statistics():
    """Get screener statistics"""
    return get_stats()


@app.get("/api/orderbook/{exchange}/{symbol}")
async def get_orderbook(exchange: ExchangeType, symbol: str):
    """Get order book for specific symbol"""
    connector = exchange_manager.connectors.get(exchange)
    if not connector:
        raise HTTPException(status_code=404, detail="Exchange not found")

    orderbook = await connector.get_orderbook(symbol)
    if not orderbook:
        raise HTTPException(status_code=404, detail="Orderbook not found")

    return orderbook


@app.get("/api/exchanges")
async def get_exchanges():
    """Get list of active exchanges"""
    return {
        "exchanges": [
            {"id": "binance", "name": "Binance", "active": True},
            {"id": "okx", "name": "OKX", "active": True},
            {"id": "bybit", "name": "Bybit", "active": True},
            {"id": "mexc", "name": "MEXC", "active": False},
            {"id": "gate", "name": "Gate.io", "active": False},
            {"id": "bitget", "name": "Bitget", "active": False}
        ]
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "tickers_count": len(latest_tickers),
        "signals_count": len(latest_signals),
        "websocket_clients": len(active_connections)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
