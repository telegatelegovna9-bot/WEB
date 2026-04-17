import asyncio
import aiohttp
from typing import Dict, List, Optional, Callable
from datetime import datetime
import logging

from app.models.schemas import Exchange, TickerData, OrderBookData, OrderBookLevel
from app.core.config import settings

logger = logging.getLogger(__name__)


class ExchangeConnector:
    """Base class for exchange connectors"""
    
    def __init__(self, exchange: Exchange):
        self.exchange = exchange
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws_url: str = ""
        self.rest_url: str = ""
        self._callbacks: Dict[str, List[Callable]] = {
            "ticker": [],
            "orderbook": [],
            "trade": []
        }
        self._running = False
    
    async def connect(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def disconnect(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def subscribe_ticker(self, callback: Callable):
        """Subscribe to ticker updates"""
        self._callbacks["ticker"].append(callback)
    
    def subscribe_orderbook(self, callback: Callable):
        """Subscribe to order book updates"""
        self._callbacks["orderbook"].append(callback)
    
    def subscribe_trades(self, callback: Callable):
        """Subscribe to trade updates"""
        self._callbacks["trade"].append(callback)
    
    async def fetch_tickers(self) -> List[TickerData]:
        """Fetch all tickers via REST API"""
        raise NotImplementedError
    
    async def fetch_orderbook(self, symbol: str, limit: int = 20) -> OrderBookData:
        """Fetch order book for a symbol"""
        raise NotImplementedError
    
    async def start_websocket(self, symbols: List[str]):
        """Start WebSocket connection for real-time data"""
        raise NotImplementedError
    
    async def _notify_ticker(self, ticker: TickerData):
        """Notify ticker subscribers"""
        for callback in self._callbacks["ticker"]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(ticker)
                else:
                    callback(ticker)
            except Exception as e:
                logger.error(f"Error in ticker callback: {e}")
    
    async def _notify_orderbook(self, orderbook: OrderBookData):
        """Notify order book subscribers"""
        for callback in self._callbacks["orderbook"]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(orderbook)
                else:
                    callback(orderbook)
            except Exception as e:
                logger.error(f"Error in orderbook callback: {e}")


class BinanceConnector(ExchangeConnector):
    """Binance exchange connector"""
    
    def __init__(self):
        super().__init__(Exchange.BINANCE)
        self.rest_url = "https://api.binance.com"
        self.ws_url = "wss://stream.binance.com:9443/ws"
    
    async def fetch_tickers(self) -> List[TickerData]:
        """Fetch 24hr ticker price change statistics"""
        try:
            async with self.session.get(f"{self.rest_url}/api/v3/ticker/24hr") as response:
                data = await response.json()
                
                tickers = []
                for item in data:
                    if item['symbol'].endswith('USDT'):
                        tickers.append(TickerData(
                            symbol=item['symbol'],
                            exchange=self.exchange,
                            price=float(item['lastPrice']),
                            volume_24h=float(item.get('quoteVolume', 0)),
                            price_change_24h=float(item.get('priceChange', 0)),
                            price_change_percent_24h=float(item.get('priceChangePercent', 0)),
                            high_24h=float(item.get('highPrice', 0)),
                            low_24h=float(item.get('lowPrice', 0))
                        ))
                return tickers
        except Exception as e:
            logger.error(f"Binance fetch_tickers error: {e}")
            return []
    
    async def fetch_orderbook(self, symbol: str, limit: int = 20) -> OrderBookData:
        """Fetch order book"""
        try:
            url = f"{self.rest_url}/api/v3/depth?symbol={symbol}&limit={limit}"
            async with self.session.get(url) as response:
                data = await response.json()
                
                bids = [OrderBookLevel(
                    price=float(b[0]),
                    amount=float(b[1])
                ) for b in data.get('bids', [])]
                
                asks = [OrderBookLevel(
                    price=float(a[0]),
                    amount=float(a[1])
                ) for a in data.get('asks', [])]
                
                return OrderBookData(
                    symbol=symbol,
                    exchange=self.exchange,
                    bids=bids,
                    asks=asks
                )
        except Exception as e:
            logger.error(f"Binance fetch_orderbook error: {e}")
            return OrderBookData(symbol=symbol, exchange=self.exchange, bids=[], asks=[])
    
    async def start_websocket(self, symbols: List[str]):
        """Start WebSocket stream"""
        self._running = True
        
        streams = "/".join([f"{s.lower()}@ticker" for s in symbols])
        ws_url = f"{self.ws_url}/{streams}"
        
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                logger.info(f"Binance WebSocket connected")
                
                async for message in ws:
                    if message.type == aiohttp.WSMsgType.TEXT:
                        data = message.json()
                        
                        if 'e' in data and data['e'] == '24hrTicker':
                            ticker = TickerData(
                                symbol=data['s'],
                                exchange=self.exchange,
                                price=float(data['c']),
                                volume_24h=float(data.get('q', 0)),
                                price_change_24h=float(data.get('p', 0)),
                                price_change_percent_24h=float(data.get('P', 0)),
                                high_24h=float(data.get('h', 0)),
                                low_24h=float(data.get('l', 0))
                            )
                            await self._notify_ticker(ticker)
                    
                    elif message.type == aiohttp.WSMsgType.ERROR:
                        logger.error(f"Binance WebSocket error: {ws.exception()}")
                        break
                
                self._running = False


class OKXConnector(ExchangeConnector):
    """OKX exchange connector"""
    
    def __init__(self):
        super().__init__(Exchange.OKX)
        self.rest_url = "https://www.okx.com"
        self.ws_url = "wss://ws.okx.com:8443/ws/v5/public"
    
    async def fetch_tickers(self) -> List[TickerData]:
        """Fetch 24hr tickers"""
        try:
            url = f"{self.rest_url}/api/v5/market/tickers?instType=SP"
            async with self.session.get(url) as response:
                data = await response.json()
                
                tickers = []
                if data.get('code') == '0':
                    for item in data.get('data', []):
                        if '-USDT' in item.get('instId', ''):
                            tickers.append(TickerData(
                                symbol=item['instId'].replace('-', ''),
                                exchange=self.exchange,
                                price=float(item.get('last', 0)),
                                volume_24h=float(item.get('volUsd24h', 0)),
                                price_change_24h=float(item.get('open24h', 0)),
                                price_change_percent_24h=float(item.get('chgUtc24h', 0)),
                                high_24h=float(item.get('high24h', 0)),
                                low_24h=float(item.get('low24h', 0))
                            ))
                return tickers
        except Exception as e:
            logger.error(f"OKX fetch_tickers error: {e}")
            return []
    
    async def fetch_orderbook(self, symbol: str, limit: int = 20) -> OrderBookData:
        """Fetch order book"""
        try:
            inst_id = f"{symbol[:len(symbol)-4]}-{symbol[-4:]}"  # BTC-USDT format
            url = f"{self.rest_url}/api/v5/market/books?instId={inst_id}&sz={limit}"
            async with self.session.get(url) as response:
                data = await response.json()
                
                if data.get('code') == '0' and data.get('data'):
                    book = data['data'][0]
                    
                    bids = [OrderBookLevel(
                        price=float(b[0]),
                        amount=float(b[1])
                    ) for b in book.get('bids', [])]
                    
                    asks = [OrderBookLevel(
                        price=float(a[0]),
                        amount=float(a[1])
                    ) for a in book.get('asks', [])]
                    
                    return OrderBookData(
                        symbol=symbol.replace('-', ''),
                        exchange=self.exchange,
                        bids=bids,
                        asks=asks
                    )
        except Exception as e:
            logger.error(f"OKX fetch_orderbook error: {e}")
        
        return OrderBookData(symbol=symbol, exchange=self.exchange, bids=[], asks=[])
    
    async def start_websocket(self, symbols: List[str]):
        """Start WebSocket subscription"""
        self._running = True
        
        args = []
        for symbol in symbols:
            inst_id = f"{symbol[:len(symbol)-4]}-{symbol[-4:]}"
            args.append({
                "channel": "tickers",
                "instId": inst_id
            })
        
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.ws_url) as ws:
                # Subscribe
                await ws.send_json({
                    "op": "subscribe",
                    "args": args
                })
                
                logger.info(f"OKX WebSocket connected")
                
                async for message in ws:
                    if message.type == aiohttp.WSMsgType.TEXT:
                        data = message.json()
                        
                        if data.get('arg', {}).get('channel') == 'tickers':
                            for item in data.get('data', []):
                                inst_id = item.get('instId', '').replace('-', '')
                                ticker = TickerData(
                                    symbol=inst_id,
                                    exchange=self.exchange,
                                    price=float(item.get('last', 0)),
                                    volume_24h=float(item.get('volUsd24h', 0)),
                                    price_change_24h=float(item.get('open24h', 0)),
                                    price_change_percent_24h=float(item.get('chgUtc24h', 0)),
                                    high_24h=float(item.get('high24h', 0)),
                                    low_24h=float(item.get('low24h', 0))
                                )
                                await self._notify_ticker(ticker)
                    
                    elif message.type == aiohttp.WSMsgType.ERROR:
                        logger.error(f"OKX WebSocket error: {ws.exception()}")
                        break
                
                self._running = False


class BybitConnector(ExchangeConnector):
    """Bybit exchange connector"""
    
    def __init__(self):
        super().__init__(Exchange.BYBIT)
        self.rest_url = "https://api.bybit.com"
        self.ws_url = "wss://stream.bybit.com/v5/public/spot"
    
    async def fetch_tickers(self) -> List[TickerData]:
        """Fetch 24hr tickers"""
        try:
            url = f"{self.rest_url}/v5/market/tickers?category=spot"
            async with self.session.get(url) as response:
                data = await response.json()
                
                tickers = []
                if data.get('retCode') == 0:
                    for item in data.get('result', {}).get('list', []):
                        if item.get('symbol', '').endswith('USDT'):
                            tickers.append(TickerData(
                                symbol=item['symbol'],
                                exchange=self.exchange,
                                price=float(item.get('lastPrice', 0)),
                                volume_24h=float(item.get('volume24h', 0)),
                                price_change_24h=float(item.get('price24hPcnt', 0)),
                                price_change_percent_24h=float(item.get('price24hPcnt', 0)) * 100,
                                high_24h=float(item.get('highPrice24h', 0)),
                                low_24h=float(item.get('lowPrice24h', 0))
                            ))
                return tickers
        except Exception as e:
            logger.error(f"Bybit fetch_tickers error: {e}")
            return []
    
    async def fetch_orderbook(self, symbol: str, limit: int = 20) -> OrderBookData:
        """Fetch order book"""
        try:
            url = f"{self.rest_url}/v5/market/orderbook?category=spot&symbol={symbol}&limit={limit}"
            async with self.session.get(url) as response:
                data = await response.json()
                
                if data.get('retCode') == 0:
                    book = data.get('result', {})
                    
                    bids = [OrderBookLevel(
                        price=float(b[0]),
                        amount=float(b[1])
                    ) for b in book.get('bids', [])]
                    
                    asks = [OrderBookLevel(
                        price=float(a[0]),
                        amount=float(a[1])
                    ) for a in book.get('asks', [])]
                    
                    return OrderBookData(
                        symbol=symbol,
                        exchange=self.exchange,
                        bids=bids,
                        asks=asks
                    )
        except Exception as e:
            logger.error(f"Bybit fetch_orderbook error: {e}")
        
        return OrderBookData(symbol=symbol, exchange=self.exchange, bids=[], asks=[])
    
    async def start_websocket(self, symbols: List[str]):
        """Start WebSocket subscription"""
        self._running = True
        
        args = [f"tickers.{s}" for s in symbols]
        
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.ws_url) as ws:
                # Subscribe
                await ws.send_json({
                    "op": "subscribe",
                    "args": args
                })
                
                logger.info(f"Bybit WebSocket connected")
                
                async for message in ws:
                    if message.type == aiohttp.WSMsgType.TEXT:
                        data = message.json()
                        
                        if data.get('topic', '').startswith('tickers.'):
                            topic_data = data.get('data', {})
                            symbol = topic_data.get('symbol', '')
                            ticker = TickerData(
                                symbol=symbol,
                                exchange=self.exchange,
                                price=float(topic_data.get('lastPrice', 0)),
                                volume_24h=float(topic_data.get('turnover24h', 0)),
                                price_change_24h=float(topic_data.get('price24hPcnt', 0)),
                                price_change_percent_24h=float(topic_data.get('price24hPcnt', 0)) * 100,
                                high_24h=float(topic_data.get('highPrice24h', 0)),
                                low_24h=float(topic_data.get('lowPrice24h', 0))
                            )
                            await self._notify_ticker(ticker)
                    
                    elif message.type == aiohttp.WSMsgType.ERROR:
                        logger.error(f"Bybit WebSocket error: {ws.exception()}")
                        break
                
                self._running = False


def get_connector(exchange: Exchange) -> ExchangeConnector:
    """Factory function to get exchange connector"""
    connectors = {
        Exchange.BINANCE: BinanceConnector,
        Exchange.OKX: OKXConnector,
        Exchange.BYBIT: BybitConnector,
    }
    
    connector_class = connectors.get(exchange)
    if connector_class:
        return connector_class()
    
    raise ValueError(f"No connector available for exchange: {exchange}")
