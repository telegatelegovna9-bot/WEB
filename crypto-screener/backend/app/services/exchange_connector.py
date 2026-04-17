import aiohttp
import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime
import json

from app.models.schemas import (
    ExchangeType, TickerData, OrderBook, OrderBookLevel, 
    Trade, SignalType, MarketBehavior, ConfidenceLevel,
    Reason, SignalIntelligence, HistoricalAnalogy
)
from app.core.config import settings


class ExchangeConnector:
    """Base connector for all exchanges"""
    
    def __init__(self, exchange: ExchangeType):
        self.exchange = exchange
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws = None
        self.tickers: Dict[str, TickerData] = {}
        self.orderbooks: Dict[str, OrderBook] = {}
        self.callbacks: List[Callable] = []
        
    async def connect(self):
        self.session = aiohttp.ClientSession()
        
    async def disconnect(self):
        if self.session:
            await self.session.close()
        if self.ws:
            await self.ws.close()
            
    def register_callback(self, callback: Callable):
        self.callbacks.append(callback)
        
    async def notify_callbacks(self, data):
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                print(f"Callback error: {e}")


class BinanceConnector(ExchangeConnector):
    def __init__(self):
        super().__init__(ExchangeType.BINANCE)
        self.base_url = settings.BINANCE_REST
        self.ws_url = settings.BINANCE_WS
        
    async def get_tickers(self) -> List[TickerData]:
        """Get all 24h tickers"""
        try:
            url = f"{self.base_url}/api/v3/ticker/24hr"
            async with self.session.get(url) as response:
                data = await response.json()
                tickers = []
                for item in data:
                    symbol = item['symbol']
                    if symbol.endswith('USDT'):
                        ticker = TickerData(
                            symbol=symbol,
                            exchange=self.exchange,
                            price=float(item['lastPrice']),
                            price_change_24h=float(item['priceChange']),
                            price_change_percent_24h=float(item['priceChangePercent']),
                            volume_24h=float(item['volume']),
                            quote_volume_24h=float(item['quoteVolume']),
                            high_24h=float(item['highPrice']),
                            low_24h=float(item['lowPrice']),
                            last_update=datetime.utcnow()
                        )
                        tickers.append(ticker)
                        self.tickers[symbol] = ticker
                return tickers
        except Exception as e:
            print(f"Binance ticker error: {e}")
            return []
            
    async def get_orderbook(self, symbol: str, limit: int = 20) -> OrderBook:
        """Get order book for symbol"""
        try:
            url = f"{self.base_url}/api/v3/depth?symbol={symbol}&limit={limit}"
            async with self.session.get(url) as response:
                data = await response.json()
                bids = [OrderBookLevel(price=float(b[0]), size=float(b[1])) for b in data['bids']]
                asks = [OrderBookLevel(price=float(a[0]), size=float(a[1])) for a in data['asks']]
                
                # Calculate totals
                for i, bid in enumerate(bids):
                    bid.total = sum(b.size for b in bids[:i+1])
                for i, ask in enumerate(asks):
                    ask.total = sum(a.size for a in asks[:i+1])
                    
                # Detect walls
                wall_detected, wall_type, wall_price = self.detect_wall(bids, asks)
                
                orderbook = OrderBook(
                    symbol=symbol,
                    exchange=self.exchange,
                    bids=bids,
                    asks=asks,
                    wall_detected=wall_detected,
                    wall_type=wall_type,
                    wall_price=wall_price
                )
                self.orderbooks[symbol] = orderbook
                return orderbook
        except Exception as e:
            print(f"Binance orderbook error: {e}")
            return None
            
    def detect_wall(self, bids: List[OrderBookLevel], asks: List[OrderBookLevel]):
        """Detect large walls in orderbook"""
        threshold = settings.WALL_SIZE_THRESHOLD_USDT
        
        for bid in bids:
            if bid.price * bid.size > threshold:
                return True, "bid_wall", bid.price
                
        for ask in asks:
            if ask.price * ask.size > threshold:
                return True, "ask_wall", ask.price
                
        return False, None, None
        
    async def connect_websocket(self, symbols: List[str], callback: Callable):
        """Connect to Binance WebSocket for real-time data"""
        streams = "/".join([f"{s.lower()}@ticker" for s in symbols])
        ws_url = f"{self.ws_url}/stream?streams={streams}"
        
        try:
            async with self.session.ws_connect(ws_url) as ws:
                self.ws = ws
                async for message in ws:
                    data = message.json()
                    if 'stream' in data and 'data' in data:
                        stream_data = data['data']
                        symbol = stream_data.get('s', '')
                        if symbol:
                            ticker = TickerData(
                                symbol=symbol,
                                exchange=self.exchange,
                                price=float(stream_data.get('c', 0)),
                                price_change_percent_24h=float(stream_data.get('P', 0)),
                                volume_24h=float(stream_data.get('v', 0)),
                                quote_volume_24h=float(stream_data.get('q', 0)),
                                high_24h=float(stream_data.get('h', 0)),
                                low_24h=float(stream_data.get('l', 0)),
                                last_update=datetime.utcnow()
                            )
                            self.tickers[symbol] = ticker
                            await self.notify_callbacks(('ticker', ticker))
        except Exception as e:
            print(f"Binance WS error: {e}")


class OKXConnector(ExchangeConnector):
    def __init__(self):
        super().__init__(ExchangeType.OKX)
        self.base_url = settings.OKX_REST
        self.ws_url = settings.OKX_WS
        
    async def get_tickers(self) -> List[TickerData]:
        """Get all 24h tickers"""
        try:
            url = f"{self.base_url}/api/v5/market/tickers?instType=SP"
            headers = {"Content-Type": "application/json"}
            async with self.session.get(url, headers=headers) as response:
                result = await response.json()
                tickers = []
                if result.get('code') == '0':
                    for item in result.get('data', []):
                        symbol = item.get('instId', '')
                        if 'USDT' in symbol:
                            ticker = TickerData(
                                symbol=symbol.replace('-', ''),
                                exchange=self.exchange,
                                price=float(item.get('last', 0)),
                                price_change_percent_24h=float(item.get('chg24h', 0)) * 100,
                                volume_24h=float(item.get('vol24h', 0)),
                                quote_volume_24h=float(item.get('volCcy24h', 0)),
                                high_24h=float(item.get('high24h', 0)),
                                low_24h=float(item.get('low24h', 0)),
                                last_update=datetime.utcnow()
                            )
                            tickers.append(ticker)
                            self.tickers[symbol] = ticker
                return tickers
        except Exception as e:
            print(f"OKX ticker error: {e}")
            return []
            
    async def get_orderbook(self, symbol: str, limit: int = 20) -> OrderBook:
        """Get order book for symbol"""
        try:
            inst_id = f"{symbol[:len(symbol)-4]}-{symbol[-4:]}"  # BTC-USDT format
            url = f"{self.base_url}/api/v5/market/books?instId={inst_id}&sz={limit}"
            async with self.session.get(url) as response:
                result = await response.json()
                if result.get('code') == '0' and result.get('data'):
                    data = result['data'][0]
                    bids = [OrderBookLevel(price=float(b[0]), size=float(b[1])) for b in data.get('bids', [])]
                    asks = [OrderBookLevel(price=float(a[0]), size=float(a[1])) for a in data.get('asks', [])]
                    
                    orderbook = OrderBook(
                        symbol=symbol,
                        exchange=self.exchange,
                        bids=bids,
                        asks=asks
                    )
                    self.orderbooks[symbol] = orderbook
                    return orderbook
        except Exception as e:
            print(f"OKX orderbook error: {e}")
            return None


class BybitConnector(ExchangeConnector):
    def __init__(self):
        super().__init__(ExchangeType.BYBIT)
        self.base_url = settings.BYBIT_REST
        self.ws_url = settings.BYBIT_WS
        
    async def get_tickers(self) -> List[TickerData]:
        """Get all 24h tickers"""
        try:
            url = f"{self.base_url}/v5/market/tickers?category=spot"
            async with self.session.get(url) as response:
                result = await response.json()
                tickers = []
                if result.get('retCode') == 0:
                    for item in result.get('result', {}).get('list', []):
                        symbol = item.get('symbol', '')
                        if 'USDT' in symbol:
                            ticker = TickerData(
                                symbol=symbol,
                                exchange=self.exchange,
                                price=float(item.get('lastPrice', 0)),
                                price_change_percent_24h=float(item.get('price24hPcnt', 0)) * 100,
                                volume_24h=float(item.get('volume24h', 0)),
                                quote_volume_24h=float(item.get('turnover24h', 0)),
                                high_24h=float(item.get('highPrice24h', 0)),
                                low_24h=float(item.get('lowPrice24h', 0)),
                                last_update=datetime.utcnow()
                            )
                            tickers.append(ticker)
                            self.tickers[symbol] = ticker
                return tickers
        except Exception as e:
            print(f"Bybit ticker error: {e}")
            return []


class ExchangeManager:
    """Manages all exchange connections"""
    
    def __init__(self):
        self.connectors: Dict[ExchangeType, ExchangeConnector] = {}
        self.active_exchanges: List[ExchangeType] = []
        
    def add_connector(self, connector: ExchangeConnector):
        self.connectors[connector.exchange] = connector
        self.active_exchanges.append(connector.exchange)
        
    async def initialize(self):
        """Initialize all connectors"""
        for connector in self.connectors.values():
            await connector.connect()
            
    async def shutdown(self):
        """Shutdown all connectors"""
        for connector in self.connectors.values():
            await connector.disconnect()
            
    async def get_all_tickers(self) -> List[TickerData]:
        """Get tickers from all active exchanges"""
        all_tickers = []
        tasks = []
        for connector in self.connectors.values():
            tasks.append(connector.get_tickers())
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                all_tickers.extend(result)
        return all_tickers
        
    async def get_orderbook(self, exchange: ExchangeType, symbol: str) -> Optional[OrderBook]:
        """Get orderbook from specific exchange"""
        connector = self.connectors.get(exchange)
        if connector:
            return await connector.get_orderbook(symbol)
        return None
        
    def get_ticker(self, exchange: ExchangeType, symbol: str) -> Optional[TickerData]:
        """Get cached ticker"""
        connector = self.connectors.get(exchange)
        if connector:
            return connector.tickers.get(symbol)
        return None


# Create exchange manager instance
exchange_manager = ExchangeManager()
