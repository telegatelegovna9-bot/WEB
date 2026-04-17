from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from typing import List, Dict
import asyncio
import json
import logging

from app.models.schemas import Signal
from app.engines.signal_engine import SignalEngine

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_personal(self, message: dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)


# Global instances
manager = ConnectionManager()
signal_engine: SignalEngine = None


async def signal_handler(signal: Signal):
    """Handle detected signals and broadcast to clients"""
    # Convert signal to dict
    signal_dict = {
        "type": "signal",
        "data": {
            "id": str(signal.id) if signal.id else None,
            "signal_type": signal.signal_type.value,
            "symbol": signal.symbol,
            "exchange": signal.exchange.value,
            "price": signal.price,
            "price_change_percent": signal.price_change_percent,
            "volume_change_percent": signal.volume_change_percent,
            "confidence_score": signal.confidence_score,
            "explanation": {
                "reasons": signal.explanation.reasons,
                "market_behavior": signal.explanation.market_behavior.value,
                "smart_money_activity": signal.explanation.smart_money_activity,
                "unusual_volume": signal.explanation.unusual_volume,
                "orderbook_changes": signal.explanation.orderbook_changes,
            },
            "historical_analogies": [
                {
                    "date": a.date.isoformat(),
                    "symbol": a.symbol,
                    "similarity_score": a.similarity_score,
                    "outcome": a.outcome,
                    "price_change_after": a.price_change_after,
                    "time_frame": a.time_frame,
                }
                for a in signal.historical_analogies
            ],
            "timestamp": signal.timestamp.isoformat(),
        }
    }
    
    await manager.broadcast(signal_dict)


def setup_signal_engine():
    """Setup global signal engine"""
    global signal_engine
    
    signal_engine = SignalEngine()
    signal_engine.add_signal_callback(signal_handler)
    
    return signal_engine


router = APIRouter()


@router.websocket("/ws/signals")
async def websocket_signals(websocket: WebSocket):
    """WebSocket endpoint for real-time signals"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Keep connection alive, receive messages from client
            data = await websocket.receive_text()
            
            # Handle client messages
            try:
                message = json.loads(data)
                
                if message.get("type") == "subscribe":
                    # Client wants to subscribe to specific symbols
                    symbols = message.get("symbols", [])
                    logger.info(f"Client subscribing to: {symbols}")
                
                elif message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/ws/tickers")
async def websocket_tickers(websocket: WebSocket):
    """WebSocket endpoint for ticker updates"""
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
