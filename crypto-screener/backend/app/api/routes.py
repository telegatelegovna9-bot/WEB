from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import asyncio
import json
from datetime import datetime
import structlog

from ..models.schemas import Signal
from ..engines import SignalEngine
from ..services.exchanges import BinanceConnector, get_exchange_connector
from ..core.enums import Exchange
from ..core.config import settings

logger = structlog.get_logger()


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        
    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        if not self.active_connections:
            return
            
        message_json = json.dumps(message, default=str)
        
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected clients
        self.active_connections -= disconnected
        
    async def send_personal(self, message: dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_text(json.dumps(message, default=str))
        except Exception:
            self.disconnect(websocket)


def create_router(app: FastAPI) -> None:
    """Create and register API routes"""
    
    manager = ConnectionManager()
    signal_engine = SignalEngine()
    
    # Store for real-time data
    tickers: Dict[str, Dict] = {}
    orderbooks: Dict[str, Dict] = {}
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await manager.connect(websocket)
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get('type') == 'subscribe':
                    symbol = message.get('symbol')
                    if symbol:
                        await manager.send_personal(
                            {'type': 'subscribed', 'symbol': symbol},
                            websocket
                        )
                        
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            logger.info("Client disconnected")
    
    @app.get("/api/signals")
    async def get_signals(limit: int = 50):
        """Get recent signals"""
        # This would query from database
        return {"signals": [], "count": 0}
    
    @app.get("/api/signals/active")
    async def get_active_signals():
        """Get currently active signals"""
        return {"signals": []}
    
    @app.get("/api/strategies")
    async def get_strategies():
        """Get available strategies"""
        return {"strategies": signal_engine.get_strategy_info()}
    
    @app.get("/api/tickers")
    async def get_tickers():
        """Get latest ticker data"""
        return {"tickers": list(tickers.values())}
    
    @app.get("/api/tickers/{symbol}")
    async def get_ticker(symbol: str):
        """Get ticker for specific symbol"""
        if symbol in tickers:
            return tickers[symbol]
        return {"error": "Symbol not found"}
    
    # Signal callback
    async def on_signal(signal: Signal):
        """Handle new signal"""
        await manager.broadcast({
            'type': 'signal',
            'data': signal.dict()
        })
        
        # Send Telegram notification if configured
        # await telegram_service.send_signal(signal)
    
    signal_engine.register_signal_callback(on_signal)
    
    # Background task to process market data
    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting market data processor")
        
        # Start background data collection
        asyncio.create_task(process_market_data(tickers, orderbooks, signal_engine))
    
    async def process_market_data(
        tickers_store: Dict,
        orderbooks_store: Dict,
        engine: SignalEngine
    ):
        """Background task to collect and process market data"""
        
        # Example: Monitor BTCUSDT on Binance
        symbols_to_monitor = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        
        connector = BinanceConnector({})
        await connector.connect()
        
        # Set up callbacks
        async def on_ticker(ticker):
            key = f"{ticker.exchange.value}:{ticker.symbol}"
            tickers_store[key] = ticker.dict()
            
            # Process through signal engine
            await engine.process_ticker(
                symbol=ticker.symbol,
                exchange=ticker.exchange,
                ticker=ticker
            )
            
            # Broadcast update
            await manager.broadcast({
                'type': 'ticker',
                'data': ticker.dict()
            })
        
        connector.callbacks['ticker'] = on_ticker
        
        # Subscribe to tickers
        for symbol in symbols_to_monitor:
            asyncio.create_task(connector.subscribe_ticker(symbol))
        
        # Keep running
        while True:
            await asyncio.sleep(60)
            logger.info("Market data processor heartbeat")
