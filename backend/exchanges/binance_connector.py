"""
CryptoMind AI - Binance Exchange Connector
Real-time WebSocket connection to Binance
"""

import asyncio
import json
import websockets
from datetime import datetime
from typing import List, Optional

from models.schemas import TickerData, OrderBookData, TradeData
from exchanges.base_connector import BaseExchangeConnector


class BinanceConnector(BaseExchangeConnector):
    """Binance exchange connector with WebSocket support"""
    
    def __init__(self, signal_detector=None, intelligence_engine=None):
        super().__init__(signal_detector, intelligence_engine)
        self.ws_url = "wss://stream.binance.com:9443/ws"
        self.rest_url = "https://api.binance.com/api/v3"
        self.stream_name = ""
        self.reconnect_delay = 30
    
    def get_exchange_name(self) -> str:
        return "binance"
    
    async def connect(self):
        """Connect to Binance WebSocket"""
        try:
            # Combine streams for efficiency
            streams = []
            for symbol in self.subscribed_symbols:
                symbol_lower = symbol.lower()
                streams.append(f"{symbol_lower}@ticker")
                streams.append(f"{symbol_lower}@depth20@100ms")
                streams.append(f"{symbol_lower}@trade")
            
            if streams:
                self.stream_name = "/".join(streams)
                full_url = f"{self.ws_url}/{self.stream_name}"
                
                self.ws = await websockets.connect(full_url, ping_interval=30, ping_timeout=10)
                self.is_connected = True
                print(f"✅ Connected to Binance WebSocket")
                
                # Start listening
                asyncio.create_task(self._listen())
        except Exception as e:
            print(f"❌ Binance connection error: {e}")
            self.is_connected = False
    
    async def disconnect(self):
        """Disconnect from Binance"""
        self.is_connected = False
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()
        print(f"👋 Disconnected from Binance")
    
    async def subscribe_ticker(self, symbols: list):
        """Subscribe to ticker updates"""
        self.subscribed_symbols = symbols
        if self.is_connected:
            await self.disconnect()
            await self.connect()
    
    async def subscribe_orderbook(self, symbols: list, depth: int = 20):
        """Subscribe to order book updates"""
        # Already included in combined stream
        pass
    
    async def subscribe_trades(self, symbols: list):
        """Subscribe to trade updates"""
        # Already included in combined stream
        pass
    
    def normalize_ticker(self, data: dict) -> TickerData:
        """Normalize Binance ticker data"""
        return TickerData(
            symbol=data.get("s", ""),
            exchange="binance",
            price=float(data.get("c", 0)),
            bid=float(data.get("b", 0)),
            ask=float(data.get("a", 0)),
            volume_24h=float(data.get("v", 0)),
            price_change_24h=float(data.get("p", 0)),
            price_change_percent_24h=float(data.get("P", 0)),
            timestamp=datetime.utcnow()
        )
    
    def normalize_orderbook(self, data: dict) -> OrderBookData:
        """Normalize Binance order book data"""
        bids = [[float(b[0]), float(b[1])] for b in data.get("bids", [])]
        asks = [[float(a[0]), float(a[1])] for a in data.get("asks", [])]
        
        return OrderBookData(
            symbol=data.get("s", ""),
            exchange="binance",
            bids=bids,
            asks=asks,
            timestamp=datetime.utcnow()
        )
    
    def normalize_trade(self, data: dict) -> TradeData:
        """Normalize Binance trade data"""
        return TradeData(
            symbol=data.get("s", ""),
            exchange="binance",
            price=float(data.get("p", 0)),
            amount=float(data.get("q", 0)),
            side="buy" if data.get("m", False) else "sell",
            timestamp=datetime.fromtimestamp(data.get("T", 0) / 1000),
            trade_id=str(data.get("t", ""))
        )
    
    async def _listen(self):
        """Listen to Binance WebSocket messages"""
        while self.is_connected:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                
                # Route message to appropriate handler
                if "e" not in data:
                    continue
                
                event_type = data["e"]
                
                if event_type == "24hrTicker":
                    ticker = self.normalize_ticker(data)
                    await self._process_ticker(ticker)
                
                elif event_type == "depthUpdate":
                    orderbook = self.normalize_orderbook(data)
                    await self._process_orderbook(orderbook)
                
                elif event_type == "trade":
                    trade = self.normalize_trade(data)
                    await self._process_trade(trade)
                
            except websockets.exceptions.ConnectionClosed:
                print("⚠️ Binance WebSocket connection closed")
                await self._reconnect()
                break
            except Exception as e:
                print(f"❌ Binance listen error: {e}")
                await asyncio.sleep(5)
    
    async def get_top_symbols(self, limit: int = 50) -> List[str]:
        """Get top trading symbols by volume"""
        try:
            result = await self._rest_request("/ticker/24hr")
            if isinstance(result, list):
                sorted_by_volume = sorted(result, key=lambda x: float(x.get("quoteVolume", 0)), reverse=True)
                return [item["symbol"] for item in sorted_by_volume[:limit]]
        except Exception as e:
            print(f"Error getting symbols: {e}")
        
        # Default major pairs
        return ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", 
                "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "TRXUSDT", "LINKUSDT"]
