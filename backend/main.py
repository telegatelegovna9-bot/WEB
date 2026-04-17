"""
CryptoMind AI - Main Application Entry Point
FastAPI backend for crypto signal detection and intelligence engine
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
from typing import Dict, List
import redis.asyncio as redis

from config import settings
from database import init_db
from exchanges.binance_connector import BinanceConnector
from signals.detector import SignalDetector
from intelligence.engine import IntelligenceEngine
from models.schemas import Signal, SignalResponse

# Global instances
signal_detector: SignalDetector = None
intelligence_engine: IntelligenceEngine = None
binance_connector: BinanceConnector = None
redis_client: redis.Redis = None
active_connections: List[WebSocket] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    global signal_detector, intelligence_engine, binance_connector, redis_client
    
    print("🚀 Starting CryptoMind AI...")
    
    # Initialize database
    await init_db()
    
    # Initialize Redis
    redis_client = redis.from_url(settings.REDIS_URL)
    
    # Initialize components
    signal_detector = SignalDetector()
    intelligence_engine = IntelligenceEngine()
    binance_connector = BinanceConnector(signal_detector, intelligence_engine)
    
    # Start exchange connectors
    await binance_connector.connect()
    
    print("✅ CryptoMind AI is ready!")
    
    yield
    
    # Shutdown
    print("👋 Shutting down CryptoMind AI...")
    await binance_connector.disconnect()
    await redis_client.close()


app = FastAPI(
    title="CryptoMind AI",
    description="Advanced Crypto Screener with Intelligent Signals",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "CryptoMind AI",
        "version": "1.0.0",
        "status": "running",
        "description": "Advanced Crypto Screener with Intelligent Signals"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "components": {
            "database": "connected",
            "redis": "connected",
            "exchanges": "active"
        }
    }


@app.get("/api/signals", response_model=List[SignalResponse])
async def get_signals(
    limit: int = 50,
    signal_type: str = None,
    exchange: str = None,
    min_confidence: float = 0
):
    """Get recent signals with optional filtering"""
    try:
        # Get signals from Redis cache
        signals_data = await redis_client.lrange("signals:recent", 0, limit - 1)
        
        signals = []
        for data in signals_data:
            signal = json.loads(data)
            
            # Apply filters
            if signal_type and signal.get("signal_type") != signal_type:
                continue
            if exchange and signal.get("exchange") != exchange:
                continue
            if min_confidence > 0 and signal.get("confidence_score", 0) < min_confidence:
                continue
                
            signals.append(signal)
        
        return signals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/signals/{signal_id}")
async def get_signal(signal_id: str):
    """Get a specific signal by ID"""
    try:
        signal_data = await redis_client.hgetall(f"signal:{signal_id}")
        if not signal_data:
            raise HTTPException(status_code=404, detail="Signal not found")
        
        return {k.decode(): v.decode() if isinstance(v, bytes) else v 
                for k, v in signal_data.items()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/statistics")
async def get_statistics():
    """Get platform statistics"""
    try:
        stats = await redis_client.hgetall("stats:platform")
        return {
            "total_signals": int(stats.get(b"total_signals", 0)),
            "accuracy_rate": float(stats.get(b"accuracy_rate", 0)),
            "active_exchanges": len(["binance"]),  # Dynamic in real impl
            "avg_confidence": float(stats.get(b"avg_confidence", 0)),
            "signals_24h": int(stats.get(b"signals_24h", 0))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/signals")
async def websocket_signals(websocket: WebSocket):
    """WebSocket endpoint for real-time signal streaming"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive, wait for client messages
            data = await websocket.receive_text()
            
            # Handle client commands
            if data == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


async def broadcast_signal(signal: dict):
    """Broadcast signal to all connected WebSocket clients"""
    if not active_connections:
        return
    
    message = json.dumps({
        "type": "new_signal",
        "data": signal
    })
    
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception:
            disconnected.append(connection)
    
    # Clean up disconnected clients
    for conn in disconnected:
        if conn in active_connections:
            active_connections.remove(conn)


# Background task to periodically broadcast signals
async def signal_broadcaster():
    """Background task to broadcast recent signals"""
    while True:
        await asyncio.sleep(5)  # Broadcast every 5 seconds
        # Implementation would fetch and broadcast latest signals


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
