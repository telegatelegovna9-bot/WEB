"""
CryptoMind AI - Volume Spike Detector
Detects abnormal volume increases
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import deque

from models.schemas import TickerData, SignalType, MarketBehavior
from config import settings


class VolumeSpikeDetector:
    """Detects volume spike patterns"""
    
    def __init__(self):
        self.volume_history: Dict[str, deque] = {}
        self.max_history_size = 60  # Keep last 60 data points (1 hour at 1min intervals)
        self.cooldown: Dict[str, datetime] = {}
        self.cooldown_period = timedelta(minutes=3)
    
    def _update_history(self, symbol: str, volume: float):
        """Update volume history"""
        now = datetime.utcnow()
        
        if symbol not in self.volume_history:
            self.volume_history[symbol] = deque(maxlen=self.max_history_size)
        
        self.volume_history[symbol].append((now, volume))
    
    def _get_average_volume(self, symbol: str, exclude_last: int = 1) -> float:
        """Calculate average volume excluding recent data points"""
        if symbol not in self.volume_history:
            return 0.0
        
        history = list(self.volume_history[symbol])
        
        if len(history) <= exclude_last:
            return 0.0
        
        volumes = [vol for ts, vol in history[:-exclude_last]]
        
        return sum(volumes) / len(volumes) if volumes else 0.0
    
    def _is_in_cooldown(self, symbol: str) -> bool:
        """Check if symbol is in cooldown"""
        if symbol not in self.cooldown:
            return False
        return datetime.utcnow() - self.cooldown[symbol] < self.cooldown_period
    
    def _set_cooldown(self, symbol: str):
        """Set cooldown"""
        self.cooldown[symbol] = datetime.utcnow()
    
    async def detect(self, ticker: TickerData) -> Optional[dict]:
        """Detect volume spike"""
        symbol = ticker.symbol
        
        # Update history
        self._update_history(symbol, ticker.volume_24h)
        
        # Check cooldown
        if self._is_in_cooldown(symbol):
            return None
        
        # Calculate average volume
        avg_volume = self._get_average_volume(symbol, exclude_last=1)
        
        if avg_volume <= 0:
            return None
        
        # Calculate volume ratio
        volume_ratio = ticker.volume_24h / avg_volume
        
        # Check if it's a spike
        if volume_ratio < settings.VOLUME_SPIKE_MULTIPLIER:
            return None
        
        # Determine market behavior based on price direction
        market_behavior = MarketBehavior.NORMAL
        reasons = [f"Volume {volume_ratio:.1f}x above average"]
        
        if ticker.price_change_percent_24h > 5:
            reasons.append("Price surging with volume")
            market_behavior = MarketBehavior.ACCUMULATION
        elif ticker.price_change_percent_24h < -5:
            reasons.append("Price dropping with volume")
            market_behavior = MarketBehavior.DISTRIBUTION
        else:
            reasons.append("Volume spike without major price movement")
            market_behavior = MarketBehavior.NORMAL
        
        # Calculate confidence
        confidence = min(100, (volume_ratio / settings.VOLUME_SPIKE_MULTIPLIER) * 70 + 30)
        
        # Set cooldown
        self._set_cooldown(symbol)
        
        return {
            "signal_type": SignalType.VOLUME_SPIKE.value,
            "symbol": symbol,
            "exchange": ticker.exchange,
            "price": ticker.price,
            "price_change_percent": ticker.price_change_percent_24h,
            "volume": ticker.volume_24h,
            "volume_change_percent": (volume_ratio - 1) * 100,
            "confidence_score": round(confidence, 2),
            "explanation": {
                "reasons": reasons,
                "market_behavior": market_behavior.value,
                "smart_money_activity": volume_ratio > 5,
                "large_orders_detected": volume_ratio > 4,
                "order_book_changes": []
            },
            "historical_analogies": [],
            "metadata": {
                "detector": "volume_spike",
                "volume_ratio": volume_ratio,
                "avg_volume": avg_volume
            }
        }
