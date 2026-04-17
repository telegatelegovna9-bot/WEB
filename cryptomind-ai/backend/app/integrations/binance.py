import asyncio
import json
import websockets
from typing import Optional, Callable, Dict, Any
from datetime import datetime
import logging

from app.integrations.base import BaseExchangeConnector
from app.core.config import settings
from app.models.schemas import Exchange

logger = logging.getLogger(__name__)


class BinanceConnector(BaseExchangeConnector):
    """Binance exchange connector with WebSocket support"""
    
    def __init__(self):
        super().__init__()
        self.name = "binance"
        self.ws_url = settings.BINANCE_WS_URL
        self.api_url = settings.BINANCE_API_URL
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.message_callback: Optional[Callable] = None
        self._reconnect_task: Optional[asyncio.Task] = None
        self._running = True
    
    async def connect(self) -> bool:
        """Connect to Binance WebSocket"""
        try:
            self.ws = await websockets.connect(
                self.ws_url,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=5,
            )
            self.is_connected = True
            logger.info("Connected to Binance WebSocket")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Binance: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Binance WebSocket"""
        self._running = False
        if self._reconnect_task:
            self._reconnect_task.cancel()
        if self.ws:
            await self.ws.close()
        self.is_connected = False
        logger.info("Disconnected from Binance WebSocket")
    
    async def subscribe_ticker(self, symbol: str) -> bool:
        """Subscribe to 24hr ticker for symbol"""
        if not self.ws or not self.is_connected:
            return False
        
        # Binance uses lowercase symbol + @ticker
        stream = f"{symbol.lower()}@ticker"
        
        subscribe_msg = {
            "method": "SUBSCRIBE",
            "params": [stream],
            "id": 1
        }
        
        try:
            await self.ws.send(json.dumps(subscribe_msg))
            self.subscribed_symbols.append(symbol)
            logger.info(f"Subscribed to ticker: {symbol}")
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to {symbol}: {e}")
            return False
    
    async def subscribe_orderbook(self, symbol: str, depth: int = 20) -> bool:
        """Subscribe to order book updates"""
        if not self.ws or not self.is_connected:
            return False
        
        # Binance order book depth: 5, 10, 20
        valid_depths = [5, 10, 20]
        depth = min(valid_depths, key=lambda x: abs(x - depth))
        
        stream = f"{symbol.lower()}@depth{depth}@100ms"
        
        subscribe_msg = {
            "method": "SUBSCRIBE",
            "params": [stream],
            "id": 2
        }
        
        try:
            await self.ws.send(json.dumps(subscribe_msg))
            logger.info(f"Subscribed to orderbook: {symbol} (depth={depth})")
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to orderbook {symbol}: {e}")
            return False
    
    async def subscribe_trades(self, symbol: str) -> bool:
        """Subscribe to trade updates"""
        if not self.ws or not self.is_connected:
            return False
        
        stream = f"{symbol.lower()}@trade"
        
        subscribe_msg = {
            "method": "SUBSCRIBE",
            "params": [stream],
            "id": 3
        }
        
        try:
            await self.ws.send(json.dumps(subscribe_msg))
            logger.info(f"Subscribed to trades: {symbol}")
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to trades {symbol}: {e}")
            return False
    
    def normalize_ticker(self, data: dict) -> Dict[str, Any]:
        """Normalize Binance ticker data"""
        return {
            "symbol": data.get('s', ''),
            "exchange": Exchange.BINANCE,
            "price": float(data.get('c', 0)),
            "volume_24h": float(data.get('v', 0)),
            "price_change_24h": float(data.get('p', 0)),
            "price_change_percent_24h": float(data.get('P', 0)),
            "high_24h": float(data.get('h', 0)),
            "low_24h": float(data.get('l', 0)),
            "timestamp": datetime.fromtimestamp(data.get('E', 0) / 1000),
        }
    
    def normalize_orderbook(self, data: dict) -> Dict[str, Any]:
        """Normalize Binance order book data"""
        bids = [
            {"price": float(b[0]), "amount": float(b[1]), "total": float(b[0]) * float(b[1])}
            for b in data.get('bids', [])
        ]
        asks = [
            {"price": float(a[0]), "amount": float(a[1]), "total": float(a[0]) * float(a[1])}
            for a in data.get('asks', [])
        ]
        
        best_bid = bids[0]['price'] if bids else 0
        best_ask = asks[0]['price'] if asks else 0
        spread = best_ask - best_bid if best_bid and best_ask else 0
        spread_percent = (spread / best_bid * 100) if best_bid else 0
        
        return {
            "symbol": data.get('s', '').replace('_', '') or data.get('ps', ''),
            "exchange": Exchange.BINANCE,
            "bids": bids,
            "asks": asks,
            "timestamp": datetime.fromtimestamp(data.get('E', 0) / 1000),
            "spread": spread,
            "spread_percent": spread_percent,
        }
    
    def normalize_trade(self, data: dict) -> Dict[str, Any]:
        """Normalize Binance trade data"""
        return {
            "symbol": data.get('s', ''),
            "exchange": Exchange.BINANCE,
            "price": float(data.get('p', 0)),
            "amount": float(data.get('q', 0)),
            "side": "sell" if data.get('m', False) else "buy",
            "timestamp": datetime.fromtimestamp(data.get('T', 0) / 1000),
            "trade_id": str(data.get('t', '')),
        }
    
    async def listen(self, callback: Callable):
        """Listen for messages and process them"""
        self.message_callback = callback
        
        while self._running and self.is_connected:
            try:
                message = await asyncio.wait_for(self.ws.recv(), timeout=30.0)
                data = json.loads(message)
                
                # Skip subscription confirmations
                if 'result' in data and data.get('id'):
                    continue
                
                # Handle different message types
                if 'e' in data:
                    event_type = data['e']
                    
                    if event_type == '24hrTicker':
                        normalized = self.normalize_ticker(data)
                        await callback('ticker', normalized)
                    
                    elif event_type == 'depthUpdate':
                        normalized = self.normalize_orderbook(data)
                        await callback('orderbook', normalized)
                    
                    elif event_type == 'trade':
                        normalized = self.normalize_trade(data)
                        await callback('trade', normalized)
                
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    pong = await self.ws.ping()
                    await asyncio.wait_for(pong, timeout=10.0)
                except Exception:
                    pass
            except websockets.ConnectionClosed:
                logger.warning("Binance WebSocket connection closed")
                self.is_connected = False
                if self._running:
                    await self._reconnect()
            except Exception as e:
                logger.error(f"Error processing Binance message: {e}")
    
    async def _reconnect(self):
        """Reconnect to WebSocket"""
        if not self._running:
            return
        
        logger.info(f"Reconnecting to Binance in {settings.WS_RECONNECT_DELAY}s...")
        await asyncio.sleep(settings.WS_RECONNECT_DELAY)
        
        if await self.connect():
            # Resubscribe to all symbols
            for symbol in self.subscribed_symbols:
                await self.subscribe_ticker(symbol)
            
            # Restart listener
            asyncio.create_task(self.listen(self.message_callback))
