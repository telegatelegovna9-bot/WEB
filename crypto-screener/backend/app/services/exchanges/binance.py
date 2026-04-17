import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, Any, Callable
import aiohttp
import websockets
from .base import BaseExchangeConnector
from ...models.schemas import TickerData, OrderBook, Trade, OrderBookEntry
from ...core.enums import Exchange


class BinanceConnector(BaseExchangeConnector):
    """Binance exchange connector"""
    
    EXCHANGE = Exchange.BINANCE
    WS_URL = "wss://stream.binance.com:9443/ws"
    REST_URL = "https://api.binance.com/api/v3"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.callbacks: Dict[str, Callable] = {}
        
    async def connect(self):
        await super().connect()
        
    async def subscribe_ticker(self, symbol: str) -> None:
        """Subscribe to ticker updates for a symbol"""
        stream_name = f"{symbol.lower()}@ticker"
        ws_url = f"{self.WS_URL}/{stream_name}"
        
        async with websockets.connect(ws_url) as websocket:
            self.ws = websocket
            async for message in websocket:
                data = json.loads(message)
                if 'e' in data and data['e'] == '24hrTicker':
                    ticker = self._normalize_ticker(data)
                    if 'ticker' in self.callbacks:
                        await self.callbacks['ticker'](ticker)
    
    async def subscribe_orderbook(self, symbol: str, depth: int = 20) -> None:
        """Subscribe to order book updates"""
        stream_name = f"{symbol.lower()}@depth{depth}"
        ws_url = f"{self.WS_URL}/{stream_name}"
        
        async with websockets.connect(ws_url) as websocket:
            self.ws = websocket
            async for message in websocket:
                data = json.loads(message)
                orderbook = self._normalize_orderbook(data)
                if 'orderbook' in self.callbacks:
                    await self.callbacks['orderbook'](orderbook)
    
    async def subscribe_trades(self, symbol: str) -> None:
        """Subscribe to trade updates"""
        stream_name = f"{symbol.lower()}@trade"
        ws_url = f"{self.WS_URL}/{stream_name}"
        
        async with websockets.connect(ws_url) as websocket:
            self.ws = websocket
            async for message in websocket:
                data = json.loads(message)
                if 'e' in data and data['e'] == 'trade':
                    trade = self._normalize_trade(data)
                    if 'trade' in self.callbacks:
                        await self.callbacks['trade'](trade)
    
    def _normalize_ticker(self, data: Dict[str, Any]) -> TickerData:
        """Normalize Binance ticker data"""
        return TickerData(
            symbol=data['s'],
            exchange=self.EXCHANGE,
            price=float(data['c']),
            volume_24h=float(data['v']),
            price_change_24h=float(data['p']),
            price_change_percent_24h=float(data['P']),
            high_24h=float(data['h']),
            low_24h=float(data['l']),
            timestamp=datetime.utcnow()
        )
    
    def _normalize_orderbook(self, data: Dict[str, Any]) -> OrderBook:
        """Normalize Binance order book data"""
        bids = [
            OrderBookEntry(price=float(b[0]), quantity=float(b[1]))
            for b in data.get('bids', [])
        ]
        asks = [
            OrderBookEntry(price=float(a[0]), quantity=float(a[1]))
            for a in data.get('asks', [])
        ]
        
        # Calculate totals
        bid_total = 0
        for bid in reversed(bids):
            bid_total += bid.quantity
            bid.total = bid_total
            
        ask_total = 0
        for ask in asks:
            ask_total += ask.quantity
            ask.total = ask_total
        
        return OrderBook(
            symbol=data.get('s', 'UNKNOWN'),
            exchange=self.EXCHANGE,
            bids=bids,
            asks=asks,
            timestamp=datetime.utcnow()
        )
    
    def _normalize_trade(self, data: Dict[str, Any]) -> Trade:
        """Normalize Binance trade data"""
        return Trade(
            symbol=data['s'],
            exchange=self.EXCHANGE,
            price=float(data['p']),
            quantity=float(data['q']),
            side='buy' if data['m'] else 'sell',
            timestamp=datetime.fromtimestamp(data['T'] / 1000)
        )
    
    async def get_ticker_rest(self, symbol: str) -> Optional[TickerData]:
        """Get ticker via REST API"""
        if not self.session:
            return None
            
        try:
            url = f"{self.REST_URL}/ticker/24hr"
            params = {'symbol': symbol}
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._normalize_ticker(data)
        except Exception as e:
            print(f"Binance REST error: {e}")
        return None
    
    async def get_orderbook_rest(self, symbol: str, depth: int = 20) -> Optional[OrderBook]:
        """Get order book via REST API"""
        if not self.session:
            return None
            
        try:
            url = f"{self.REST_URL}/depth"
            params = {'symbol': symbol, 'limit': depth}
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    data['s'] = symbol
                    return self._normalize_orderbook(data)
        except Exception as e:
            print(f"Binance REST error: {e}")
        return None
