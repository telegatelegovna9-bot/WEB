"""
CryptoMind AI - Pump/Dump Signal Detector
Detects rapid price movements with volume confirmation
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque

from models.schemas import TickerData, SignalType, MarketBehavior, Explanation, HistoricalAnalogy
from config import settings


class PumpDumpDetector:
    """Detects pump and dump patterns"""
    
    def __init__(self):
        self.price_history: Dict[str, deque] = {}  # symbol -> deque of (timestamp, price)
        self.volume_history: Dict[str, deque] = {}  # symbol -> deque of (timestamp, volume)
        self.max_history_size = 100  # Keep last 100 data points
        self.cooldown: Dict[str, datetime] = {}  # symbol -> last signal time
        self.cooldown_period = timedelta(minutes=5)  # Prevent spam
    
    def _update_history(self, symbol: str, price: float, volume: float):
        """Update price and volume history"""
        now = datetime.utcnow()
        
        if symbol not in self.price_history:
            self.price_history[symbol] = deque(maxlen=self.max_history_size)
            self.volume_history[symbol] = deque(maxlen=self.max_history_size)
        
        self.price_history[symbol].append((now, price))
        self.volume_history[symbol].append((now, volume))
    
    def _get_price_change(self, symbol: str, minutes: int = 5) -> float:
        """Calculate price change over last N minutes"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < 2:
            return 0.0
        
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=minutes)
        
        prices = [(ts, price) for ts, price in self.price_history[symbol] if ts >= cutoff]
        
        if len(prices) < 2:
            return 0.0
        
        old_price = prices[0][1]
        new_price = prices[-1][1]
        
        return ((new_price - old_price) / old_price) * 100 if old_price > 0 else 0.0
    
    def _get_volume_change(self, symbol: str, minutes: int = 5) -> float:
        """Calculate volume change over last N minutes"""
        if symbol not in self.volume_history or len(self.volume_history[symbol]) < 2:
            return 0.0
        
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=minutes)
        
        volumes = [vol for ts, vol in self.volume_history[symbol] if ts >= cutoff]
        
        if len(volumes) < 2:
            return 0.0
        
        avg_old_volume = sum(volumes[:-1]) / len(volumes[:-1])
        latest_volume = volumes[-1]
        
        return (latest_volume / avg_old_volume) if avg_old_volume > 0 else 0.0
    
    def _is_in_cooldown(self, symbol: str) -> bool:
        """Check if symbol is in cooldown period"""
        if symbol not in self.cooldown:
            return False
        
        return datetime.utcnow() - self.cooldown[symbol] < self.cooldown_period
    
    def _set_cooldown(self, symbol: str):
        """Set cooldown for symbol"""
        self.cooldown[symbol] = datetime.utcnow()
    
    async def detect(self, ticker: TickerData) -> Optional[dict]:
        """Detect pump/dump pattern"""
        symbol = ticker.symbol
        
        # Update history
        self._update_history(symbol, ticker.price, ticker.volume_24h)
        
        # Check cooldown
        if self._is_in_cooldown(symbol):
            return None
        
        # Calculate changes
        price_change = self._get_price_change(symbol, minutes=5)
        volume_change = self._get_volume_change(symbol, minutes=5)
        
        signal_type = None
        threshold = settings.PUMP_THRESHOLD_PERCENT
        
        # Detect pump
        if price_change >= threshold and volume_change >= settings.VOLUME_SPIKE_MULTIPLIER:
            signal_type = SignalType.PUMP
        # Detect dump
        elif price_change <= -threshold and volume_change >= settings.VOLUME_SPIKE_MULTIPLIER:
            signal_type = SignalType.DUMP
        
        if not signal_type:
            return None
        
        # Generate explanation
        reasons = []
        market_behavior = MarketBehavior.NORMAL
        
        if signal_type == SignalType.PUMP:
            reasons.append(f"+{price_change:.2f}% price increase in 5min")
            reasons.append(f"{volume_change:.1f}x volume spike")
            
            if volume_change > 5:
                reasons.append("Extreme volume surge detected")
                market_behavior = MarketBehavior.ACCUMULATION
            elif volume_change > 3:
                market_behavior = MarketBehavior.BREAKOUT
            else:
                market_behavior = MarketBehavior.NORMAL
        else:
            reasons.append(f"{price_change:.2f}% price decrease in 5min")
            reasons.append(f"{volume_change:.1f}x volume spike")
            
            if volume_change > 5:
                reasons.append("Panic selling detected")
                market_behavior = MarketBehavior.DISTRIBUTION
            elif volume_change > 3:
                market_behavior = MarketBehavior.BREAKOUT
            else:
                market_behavior = MarketBehavior.NORMAL
        
        # Calculate confidence score
        confidence = min(100, (abs(price_change) / threshold) * 50 + (volume_change / settings.VOLUME_SPIKE_MULTIPLIER) * 50)
        
        # Set cooldown
        self._set_cooldown(symbol)
        
        return {
            "signal_type": signal_type.value,
            "symbol": symbol,
            "exchange": ticker.exchange,
            "price": ticker.price,
            "price_change_percent": price_change,
            "volume": ticker.volume_24h,
            "volume_change_percent": (volume_change - 1) * 100,
            "confidence_score": round(confidence, 2),
            "explanation": {
                "reasons": reasons,
                "market_behavior": market_behavior.value,
                "smart_money_activity": volume_change > 4,
                "large_orders_detected": volume_change > 3,
                "order_book_changes": []
            },
            "historical_analogies": [],  # Will be filled by intelligence engine
            "metadata": {
                "detector": "pump_dump",
                "timeframe": "5m"
            }
        }
