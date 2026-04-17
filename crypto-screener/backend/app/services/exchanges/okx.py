import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, Any, Callable
import aiohttp
import websockets
from .base import BaseExchangeConnector
from ...models.schemas import TickerData, OrderBook, Trade, OrderBookEntry
from ...core.enums import Exchange


class OKXConnector(BaseExchangeConnector):
    """OKX exchange connector"""
    
    EXCHANGE = Exchange.OKX
    WS_URL = "wss://ws.okx.com:8443/ws/v5/public"
    REST_URL = "https://www.okx.com/api/v5"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.callbacks: Dict[str, Callable] = {}
        
    async def subscribe_ticker(self, symbol: str) -> None:
        """Subscribe to ticker updates for a symbol"""
        async with websockets.connect(self.WS_URL) as websocket:
            self.ws = websocket
            
            # Subscribe message
            sub_msg = {
                "op": "subscribe",
                "args": [{
                    "channel": "tickers",
                    "instId": self._normalize_symbol(symbol)
                }]
            }
            await websocket.send(json.dumps(sub_msg))
            
            # Ping interval
            ping_task = asyncio.create_task(self._ping_loop(websocket))
            
            try:
                async for message in websocket:
                    data = json.loads(message)
                    if 'arg' in data and 'data' in data and data['data']:
                        ticker_data = data['data'][0]
                        ticker = self._normalize_ticker(ticker_data, symbol)
                        if 'ticker' in self.callbacks:
                            await self.callbacks['ticker'](ticker)
            finally:
                ping_task.cancel()
    
    async def subscribe_orderbook(self, symbol: str, depth: int = 20) -> None:
        """Subscribe to order book updates"""
        async with websockets.connect(self.WS_URL) as websocket:
            self.ws = websocket
            
            # Subscribe message
            sub_msg = {
                "op": "subscribe",
                "args": [{
                    "channel": "books",
                    "instId": self._normalize_symbol(symbol)
                }]
            }
            await websocket.send(json.dumps(sub_msg))
            
            async for message in websocket:
                data = json.loads(message)
                if 'arg' in data and 'data' in data and data['data']:
                    orderbook = self._normalize_orderbook(data, symbol)
                    if 'orderbook' in self.callbacks:
                        await self.callbacks['orderbook'](orderbook)
    
    async def subscribe_trades(self, symbol: str) -> None:
        """Subscribe to trade updates"""
        async with websockets.connect(self.WS_URL) as websocket:
            self.ws = websocket
            
            sub_msg = {
                "op": "subscribe",
                "args": [{
                    "channel": "trades",
                    "instId": self._normalize_symbol(symbol)
                }]
            }
            await websocket.send(json.dumps(sub_msg))
            
            async for message in websocket:
                data = json.loads(message)
                if 'arg' in data and 'data' in data and data['data']:
                    for trade_data in data['data']:
                        trade = self._normalize_trade(trade_data, symbol)
                        if 'trade' in self.callbacks:
                            await self.callbacks['trade'](trade)
    
    async def _ping_loop(self, ws: websockets.WebSocketClientProtocol):
        """Send ping every 30 seconds"""
        try:
            while True:
                await asyncio.sleep(30)
                await ws.send("ping")
        except asyncio.CancelledError:
            pass
    
    def _normalize_symbol(self, symbol: str) -> str:
        """Convert symbol to OKX format (e.g., BTCUSDT -> BTC-USDT)"""
        if '-' in symbol:
            return symbol
        # Insert dash before USDT, USD, BTC, ETH etc.
        for quote in ['USDT', 'USD', 'BTC', 'ETH', 'USDC']:
            if symbol.endswith(quote):
                base = symbol[:-len(quote)]
                return f"{base}-{quote}"
        return symbol
    
    def _normalize_ticker(self, data: Dict[str, Any], symbol: str) -> TickerData:
        """Normalize OKX ticker data"""
        return TickerData(
            symbol=symbol,
            exchange=self.EXCHANGE,
            price=float(data.get('last', 0)),
            volume_24h=float(data.get('vol24h', 0)),
            price_change_24h=float(data.get('open', 0)) - float(data.get('last', 0)),
            price_change_percent_24h=float(data.get('chg24h', 0)),
            high_24h=float(data.get('high24h', 0)),
            low_24h=float(data.get('low24h', 0)),
            timestamp=datetime.utcnow()
        )
    
    def _normalize_orderbook(self, data: Dict[str, Any], symbol: str) -> OrderBook:
        """Normalize OKX order book data"""
        books_data = data['data'][0] if data.get('data') else {}
        
        bids = [
            OrderBookEntry(price=float(b[0]), quantity=float(b[1]))
            for b in books_data.get('bids', [])
        ]
        asks = [
            OrderBookEntry(price=float(a[0]), quantity=float(a[1]))
            for a in books_data.get('asks', [])
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
            symbol=symbol,
            exchange=self.EXCHANGE,
            bids=bids,
            asks=asks,
            timestamp=datetime.utcnow()
        )
    
    def _normalize_trade(self, data: Dict[str, Any], symbol: str) -> Trade:
        """Normalize OKX trade data"""
        return Trade(
            symbol=symbol,
            exchange=self.EXCHANGE,
            price=float(data.get('px', 0)),
            quantity=float(data.get('sz', 0)),
            side='sell' if data.get('side') == 'sell' else 'buy',
            timestamp=datetime.fromtimestamp(int(data.get('ts', 0)) / 1000)
        )
    
    async def get_ticker_rest(self, symbol: str) -> Optional[TickerData]:
        """Get ticker via REST API"""
        if not self.session:
            return None
            
        try:
            inst_id = self._normalize_symbol(symbol)
            url = f"{self.REST_URL}/market/ticker"
            params = {'instId': inst_id}
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('data'):
                        return self._normalize_ticker(result['data'][0], symbol)
        except Exception as e:
            print(f"OKX REST error: {e}")
        return None
    
    async def get_orderbook_rest(self, symbol: str, depth: int = 20) -> Optional[OrderBook]:
        """Get order book via REST API"""
        if not self.session:
            return None
            
        try:
            inst_id = self._normalize_symbol(symbol)
            url = f"{self.REST_URL}/market/books"
            params = {'instId': inst_id, 'sz': str(depth)}
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('data'):
                        return self._normalize_orderbook({'data': result['data']}, symbol)
        except Exception as e:
            print(f"OKX REST error: {e}")
        return None
