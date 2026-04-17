"""
CryptoMind AI - Main Signal Detector
Orchestrates all signal detection modules
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import uuid
import json
import redis.asyncio as redis

from models.schemas import TickerData, OrderBookData, TradeData
from signals.pump_dump_detector import PumpDumpDetector
from signals.volume_detector import VolumeSpikeDetector
from signals.orderbook_detector import OrderBookDetector
from config import settings


class SignalDetector:
    """Main signal detector that orchestrates all detection modules"""
    
    def __init__(self):
        self.pump_dump_detector = PumpDumpDetector()
        self.volume_detector = VolumeSpikeDetector()
        self.orderbook_detector = OrderBookDetector()
        self.redis_client: Optional[redis.Redis] = None
        self.current_prices: Dict[str, float] = {}  # symbol -> current price
        
        # Statistics
        self.stats = {
            "total_signals": 0,
            "signals_by_type": {},
            "signals_24h": 0
        }
    
    async def initialize(self, redis_client: redis.Redis):
        """Initialize with Redis client"""
        self.redis_client = redis_client
    
    async def process_ticker(self, ticker: TickerData):
        """Process ticker data and detect signals"""
        symbol = ticker.symbol
        self.current_prices[symbol] = ticker.price
        
        signals = []
        
        # Run all detectors
        pump_dump_signal = await self.pump_dump_detector.detect(ticker)
        if pump_dump_signal:
            signals.append(pump_dump_signal)
        
        volume_signal = await self.volume_detector.detect(ticker)
        if volume_signal:
            signals.append(volume_signal)
        
        # Process detected signals
        for signal in signals:
            await self._handle_signal(signal)
    
    async def process_orderbook(self, orderbook: OrderBookData):
        """Process order book data and detect signals"""
        symbol = orderbook.symbol
        
        # Get current price from cache
        current_price = self.current_prices.get(symbol, 0)
        if current_price <= 0:
            return
        
        # Detect order book signals
        ob_signal = await self.orderbook_detector.detect(orderbook, current_price)
        if ob_signal:
            await self._handle_signal(ob_signal)
    
    async def process_trade(self, trade: TradeData):
        """Process trade data (for future trade-based detection)"""
        # Currently used for updating prices
        self.current_prices[trade.symbol] = trade.price
    
    async def _handle_signal(self, signal: dict):
        """Handle detected signal - store and broadcast"""
        # Generate unique ID
        signal_id = str(uuid.uuid4())
        signal["signal_id"] = signal_id
        signal["created_at"] = datetime.utcnow().isoformat()
        
        # Update statistics
        self.stats["total_signals"] += 1
        signal_type = signal["signal_type"]
        self.stats["signals_by_type"][signal_type] = \
            self.stats["signals_by_type"].get(signal_type, 0) + 1
        self.stats["signals_24h"] += 1
        
        # Store in Redis
        if self.redis_client:
            # Add to recent signals list
            await self.redis_client.lpush("signals:recent", json.dumps(signal))
            await self.redis_client.ltrim("signals:recent", 0, 999)  # Keep last 1000
            
            # Store full signal details
            await self.redis_client.hset(f"signal:{signal_id}", mapping={
                k: str(v) if not isinstance(v, (str, int, float, dict, list)) else json.dumps(v) if isinstance(v, (dict, list)) else v
                for k, v in signal.items()
            })
            
            # Set expiry (24 hours)
            await self.redis_client.expire("signals:recent", 86400)
            await self.redis_client.expire(f"signal:{signal_id}", 86400)
            
            # Update platform stats
            await self.redis_client.hincrby("stats:platform", "total_signals", 1)
            await self.redis_client.hincrby("stats:platform", "signals_24h", 1)
            await self.redis_client.hset("stats:platform", "avg_confidence", 
                                        str(signal.get("confidence_score", 0)))
        
        print(f"🚨 SIGNAL DETECTED: {signal_type.upper()} on {signal['symbol']} @ ${signal['price']:,.2f} (Confidence: {signal['confidence_score']}%)")
        
        # Return signal for further processing by intelligence engine
        return signal
    
    def get_stats(self) -> dict:
        """Get detector statistics"""
        return self.stats.copy()
