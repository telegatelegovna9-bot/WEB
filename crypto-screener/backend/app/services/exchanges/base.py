from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import asyncio
import aiohttp
from ..models.schemas import TickerData, OrderBook, Trade
from ..core.enums import Exchange


class BaseExchangeConnector(ABC):
    """Abstract base class for exchange connectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws = None
        self.is_connected = False
        
    async def connect(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        self.is_connected = True
        
    async def disconnect(self):
        """Close connections"""
        if self.session:
            await self.session.close()
        if self.ws:
            await self.ws.close()
        self.is_connected = False
    
    @abstractmethod
    async def subscribe_ticker(self, symbol: str) -> None:
        """Subscribe to ticker updates"""
        pass
    
    @abstractmethod
    async def subscribe_orderbook(self, symbol: str, depth: int = 20) -> None:
        """Subscribe to order book updates"""
        pass
    
    @abstractmethod
    async def subscribe_trades(self, symbol: str) -> None:
        """Subscribe to trade updates"""
        pass
    
    @abstractmethod
    def _normalize_ticker(self, data: Any) -> TickerData:
        """Normalize ticker data to common format"""
        pass
    
    @abstractmethod
    def _normalize_orderbook(self, data: Any) -> OrderBook:
        """Normalize order book data to common format"""
        pass
    
    @abstractmethod
    def _normalize_trade(self, data: Any) -> Trade:
        """Normalize trade data to common format"""
        pass
    
    async def get_ticker_rest(self, symbol: str) -> Optional[TickerData]:
        """Fallback REST API for ticker data"""
        pass
    
    async def get_orderbook_rest(self, symbol: str, depth: int = 20) -> Optional[OrderBook]:
        """Fallback REST API for order book"""
        pass
