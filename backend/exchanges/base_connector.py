"""
CryptoMind AI - Base Exchange Connector
Abstract base class for all exchange connectors
"""

from abc import ABC, abstractmethod
from typing import Callable, Optional, Dict, Any
import asyncio
import websockets
import aiohttp
from datetime import datetime

from models.schemas import TickerData, OrderBookData, TradeData


class BaseExchangeConnector(ABC):
    """Abstract base class for exchange connectors"""
    
    def __init__(self, signal_detector=None, intelligence_engine=None):
        self.signal_detector = signal_detector
        self.intelligence_engine = intelligence_engine
        self.ws_url: str = ""
        self.rest_url: str = ""
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected: bool = False
        self.subscribed_symbols: list = []
        self.callbacks: Dict[str, Callable] = {
            "ticker": None,
            "orderbook": None,
            "trade": None
        }
    
    @abstractmethod
    async def connect(self):
        """Connect to exchange WebSocket"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from exchange"""
        pass
    
    @abstractmethod
    async def subscribe_ticker(self, symbols: list):
        """Subscribe to ticker updates"""
        pass
    
    @abstractmethod
    async def subscribe_orderbook(self, symbols: list, depth: int = 20):
        """Subscribe to order book updates"""
        pass
    
    @abstractmethod
    async def subscribe_trades(self, symbols: list):
        """Subscribe to trade updates"""
        pass
    
    @abstractmethod
    def normalize_ticker(self, data: Any) -> TickerData:
        """Normalize ticker data to common format"""
        pass
    
    @abstractmethod
    def normalize_orderbook(self, data: Any) -> OrderBookData:
        """Normalize order book data to common format"""
        pass
    
    @abstractmethod
    def normalize_trade(self, data: Any) -> TradeData:
        """Normalize trade data to common format"""
        pass
    
    @abstractmethod
    def get_exchange_name(self) -> str:
        """Get exchange name"""
        pass
    
    async def _rest_request(self, endpoint: str, params: dict = None) -> dict:
        """Make REST API request"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.rest_url}{endpoint}"
        try:
            async with self.session.get(url, params=params) as response:
                return await response.json()
        except Exception as e:
            print(f"REST request error: {e}")
            return {}
    
    def set_callback(self, event_type: str, callback: Callable):
        """Set callback for event type"""
        if event_type in self.callbacks:
            self.callbacks[event_type] = callback
    
    async def _process_ticker(self, data: TickerData):
        """Process ticker data and send to signal detector"""
        if self.callbacks["ticker"]:
            await self.callbacks["ticker"](data)
        
        if self.signal_detector:
            await self.signal_detector.process_ticker(data)
    
    async def _process_orderbook(self, data: OrderBookData):
        """Process order book data"""
        if self.callbacks["orderbook"]:
            await self.callbacks["orderbook"](data)
        
        if self.signal_detector:
            await self.signal_detector.process_orderbook(data)
    
    async def _process_trade(self, data: TradeData):
        """Process trade data"""
        if self.callbacks["trade"]:
            await self.callbacks["trade"](data)
        
        if self.signal_detector:
            await self.signal_detector.process_trade(data)
    
    async def _reconnect(self):
        """Reconnect to exchange"""
        print(f"🔄 Reconnecting to {self.get_exchange_name()}...")
        await self.disconnect()
        await asyncio.sleep(5)
        await self.connect()
