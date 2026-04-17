from typing import Dict, List, Optional, Callable
from datetime import datetime
import logging
import asyncio

from app.models.schemas import Signal, TickerData, OrderBook, Exchange
from app.engines.pump_dump_detector import PumpDumpDetector
from app.engines.orderbook_detector import OrderBookDetector
from app.integrations.binance import BinanceConnector

logger = logging.getLogger(__name__)


class SignalEngine:
    """Main signal detection engine that coordinates all detectors"""
    
    def __init__(self):
        self.pump_dump_detector = PumpDumpDetector()
        self.orderbook_detector = OrderBookDetector()
        self.exchange_connectors: Dict[str, any] = {}
        self.signal_callbacks: List[Callable] = []
        self._running = False
        self._tasks: List[asyncio.Task] = []
    
    def add_signal_callback(self, callback: Callable):
        """Add callback for when signals are detected"""
        self.signal_callbacks.append(callback)
    
    async def start(self, symbols: List[str]):
        """Start the signal engine with given symbols"""
        self._running = True
        
        # Initialize exchange connectors
        await self._initialize_connectors()
        
        # Subscribe to symbols
        for symbol in symbols:
            await self._subscribe_symbol(symbol)
        
        logger.info(f"Signal engine started with {len(symbols)} symbols")
    
    async def stop(self):
        """Stop the signal engine"""
        self._running = False
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        # Disconnect all connectors
        for connector in self.exchange_connectors.values():
            await connector.disconnect()
        
        logger.info("Signal engine stopped")
    
    async def _initialize_connectors(self):
        """Initialize exchange connectors"""
        # Start with Binance
        binance = BinanceConnector()
        if await binance.connect():
            self.exchange_connectors['binance'] = binance
            # Start listening
            task = asyncio.create_task(binance.listen(self._handle_message))
            self._tasks.append(task)
            logger.info("Binance connector initialized")
        
        # TODO: Add other exchanges (OKX, Bybit, etc.)
    
    async def _subscribe_symbol(self, symbol: str):
        """Subscribe to a symbol on all connected exchanges"""
        for exchange_name, connector in self.exchange_connectors.items():
            await connector.subscribe_ticker(symbol)
            await connector.subscribe_orderbook(symbol)
            await connector.subscribe_trades(symbol)
            logger.info(f"Subscribed to {symbol} on {exchange_name}")
    
    async def _handle_message(self, msg_type: str, data: Dict):
        """Handle incoming messages from exchanges"""
        try:
            if msg_type == 'ticker':
                await self._process_ticker(data)
            elif msg_type == 'orderbook':
                await self._process_orderbook(data)
            elif msg_type == 'trade':
                await self._process_trade(data)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _process_ticker(self, ticker_data: Dict):
        """Process ticker data and check for signals"""
        symbol = ticker_data.get('symbol', '')
        
        # Convert to TickerData model
        ticker = TickerData(**ticker_data)
        
        # Update detectors
        self.pump_dump_detector.update(symbol, ticker)
        
        # Check for signals
        signal = self.pump_dump_detector.detect(symbol)
        
        if signal:
            # Update exchange from actual data
            signal.exchange = ticker.exchange
            await self._emit_signal(signal)
    
    async def _process_orderbook(self, orderbook_data: Dict):
        """Process order book data and check for signals"""
        symbol = orderbook_data.get('symbol', '')
        
        # Convert to OrderBook model
        orderbook = OrderBook(**orderbook_data)
        
        # Update detector
        self.orderbook_detector.update(symbol, orderbook)
        
        # Check for signals
        signal = self.orderbook_detector.detect(symbol)
        
        if signal:
            signal.exchange = orderbook.exchange
            await self._emit_signal(signal)
    
    async def _process_trade(self, trade_data: Dict):
        """Process trade data (for future use)"""
        # Currently not used for signal detection
        pass
    
    async def _emit_signal(self, signal: Signal):
        """Emit signal to all callbacks"""
        logger.info(
            f"SIGNAL DETECTED: {signal.signal_type.value} on {signal.symbol} "
            f"({signal.exchange.value}) - Confidence: {signal.confidence_score:.1f}%"
        )
        
        for callback in self.signal_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(signal)
                else:
                    callback(signal)
            except Exception as e:
                logger.error(f"Error in signal callback: {e}")
    
    def get_active_signals(self) -> List[Signal]:
        """Get currently active signals"""
        # This would query from database or cache
        return []
