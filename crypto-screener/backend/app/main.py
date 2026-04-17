from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import logging
from typing import Dict, List, Set
from datetime import datetime

from app.core.config import settings
from app.models.schemas import Signal, TickerData, Exchange
from app.services.exchange_connector import get_connector, BinanceConnector, OKXConnector, BybitConnector
from app.services.signal_engine import (
    SignalIntelligenceEngine, PumpDumpDetector, BreakoutDetector, OrderBookDensityDetector
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Advanced cryptocurrency screening platform with intelligent signals"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
class AppState:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.signals: List[Signal] = []
        self.tickers: Dict[str, TickerData] = {}
        self.running = False
    
    def add_signal(self, signal: Signal):
        self.signals.insert(0, signal)
        self.signals = self.signals[:100]  # Keep last 100 signals
    
    async def broadcast(self, message: dict):
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.add(connection)
        
        self.active_connections -= disconnected

state = AppState()

# Initialize detectors
intelligence_engine = SignalIntelligenceEngine()
pump_dump_detector = PumpDumpDetector(intelligence_engine)
breakout_detector = BreakoutDetector(intelligence_engine)
orderbook_detector = OrderBookDensityDetector(intelligence_engine)


@app.on_event("startup")
async def startup_event():
    """Initialize connections and start data collection"""
    state.running = True
    logger.info("Starting crypto screener backend...")
    
    # Start background task for data collection
    asyncio.create_task(collect_market_data())


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    state.running = False
    logger.info("Shutting down crypto screener backend...")


async def collect_market_data():
    """Main loop for collecting market data and detecting signals"""
    logger.info("Starting market data collection...")
    
    # Initialize connectors
    connectors = [
        BinanceConnector(),
        OKXConnector(),
        BybitConnector(),
    ]
    
    for connector in connectors:
        await connector.connect()
        connector.subscribe_ticker(on_ticker_update)
    
    # Focus on major pairs
    symbols = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
        "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "TRXUSDT", "LINKUSDT"
    ]
    
    while state.running:
        try:
            # Fetch tickers from all exchanges
            tasks = []
            for connector in connectors:
                tasks.append(fetch_and_process_tickers(connector, symbols))
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Wait before next fetch
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Error in market data collection: {e}")
            await asyncio.sleep(10)
    
    # Cleanup
    for connector in connectors:
        await connector.disconnect()


async def fetch_and_process_tickers(connector, symbols: List[str]):
    """Fetch tickers and process for signals"""
    try:
        tickers = await connector.fetch_tickers()
        
        for ticker in tickers:
            # Update global ticker state
            key = f"{ticker.exchange.value}:{ticker.symbol}"
            state.tickers[key] = ticker
            
            # Check for pump/dump signals
            signal = pump_dump_detector.check(ticker)
            if signal:
                state.add_signal(signal)
                await state.broadcast({
                    "type": "signal",
                    "data": signal.dict()
                })
                logger.info(f"Signal detected: {signal.type.value} {signal.symbol} ({signal.intelligence.probability_score:.0f}%)")
            
            # Check for breakout signals (less frequently)
            if ticker.price_change_percent_24h > 3:
                signal = breakout_detector.check(ticker)
                if signal:
                    state.add_signal(signal)
                    await state.broadcast({
                        "type": "signal",
                        "data": signal.dict()
                    })
        
        # Broadcast ticker updates
        if tickers:
            await state.broadcast({
                "type": "tickers",
                "data": [t.dict() for t in tickers[:20]]  # Limit broadcast size
            })
    
    except Exception as e:
        logger.error(f"Error fetching tickers from {connector.exchange}: {e}")


async def on_ticker_update(ticker: TickerData):
    """Handle real-time ticker updates from WebSocket"""
    key = f"{ticker.exchange.value}:{ticker.symbol}"
    state.tickers[key] = ticker
    
    # Check for signals
    signal = pump_dump_detector.check(ticker)
    if signal:
        state.add_signal(signal)
        await state.broadcast({
            "type": "signal",
            "data": signal.dict()
        })
        logger.info(f"Real-time signal: {signal.type.value} {signal.symbol}")


# API Endpoints

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/api/signals")
async def get_signals(limit: int = 50, active_only: bool = True):
    """Get recent signals"""
    signals = state.signals
    if active_only:
        signals = [s for s in signals if s.is_active]
    return signals[:limit]


@app.get("/api/tickers")
async def get_tickers(exchange: str = None):
    """Get current tickers"""
    tickers = list(state.tickers.values())
    if exchange:
        tickers = [t for t in tickers if t.exchange.value == exchange]
    return tickers


@app.get("/api/exchanges")
async def get_exchanges():
    """Get list of supported exchanges"""
    return {
        "exchanges": [e.value for e in Exchange]
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    state.active_connections.add(websocket)
    logger.info(f"Client connected. Total clients: {len(state.active_connections)}")
    
    try:
        # Send initial data
        await websocket.send_json({
            "type": "init",
            "data": {
                "signals": [s.dict() for s in state.signals[:20]],
                "tickers": [t.dict() for t in list(state.tickers.values())[:50]]
            }
        })
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                # Handle client messages if needed
            except WebSocketDisconnect:
                break
            except:
                continue
    
    finally:
        state.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(state.active_connections)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "signals_count": len(state.signals),
        "tickers_count": len(state.tickers),
        "connected_clients": len(state.active_connections),
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
