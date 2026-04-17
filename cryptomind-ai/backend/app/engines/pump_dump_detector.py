import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import logging
import numpy as np

from app.models.schemas import (
    Signal, SignalType, SignalExplanation, MarketBehavior,
    HistoricalAnalogy, Exchange, TickerData, OrderBook
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class DataWindow:
    """Maintains a rolling window of data for analysis"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.prices: List[float] = []
        self.volumes: List[float] = []
        self.timestamps: List[datetime] = []
    
    def add(self, price: float, volume: float, timestamp: datetime):
        self.prices.append(price)
        self.volumes.append(volume)
        self.timestamps.append(timestamp)
        
        # Trim if exceeds max size
        if len(self.prices) > self.max_size:
            self.prices = self.prices[-self.max_size:]
            self.volumes = self.volumes[-self.max_size:]
            self.timestamps = self.timestamps[-self.max_size:]
    
    def get_price_change_percent(self, periods: int = 1) -> float:
        if len(self.prices) < periods + 1:
            return 0.0
        old_price = self.prices[-(periods + 1)]
        current_price = self.prices[-1]
        return ((current_price - old_price) / old_price) * 100 if old_price else 0.0
    
    def get_volume_change_percent(self, periods: int = 1) -> float:
        if len(self.volumes) < periods * 2:
            return 0.0
        old_avg = np.mean(self.volumes[-(periods * 2):-periods]) if periods > 0 else self.volumes[-1]
        current_avg = np.mean(self.volumes[-periods:]) if periods > 0 else self.volumes[-1]
        return ((current_avg - old_avg) / old_avg) * 100 if old_avg else 0.0
    
    def get_avg_volume(self, periods: int = 10) -> float:
        if len(self.volumes) < periods:
            return np.mean(self.volumes) if self.volumes else 0.0
        return np.mean(self.volumes[-periods:])
    
    def get_volatility(self, periods: int = 20) -> float:
        if len(self.prices) < periods:
            return 0.0
        returns = np.diff(self.prices[-periods:]) / self.prices[-periods:-1]
        return np.std(returns) if len(returns) > 0 else 0.0


class PumpDumpDetector:
    """Detects pump and dump patterns"""
    
    def __init__(self):
        self.data_windows: Dict[str, DataWindow] = {}
    
    def update(self, symbol: str, ticker: TickerData):
        if symbol not in self.data_windows:
            self.data_windows[symbol] = DataWindow()
        
        self.data_windows[symbol].add(
            ticker.price,
            ticker.volume_24h,
            ticker.timestamp
        )
    
    def detect(self, symbol: str) -> Optional[Signal]:
        if symbol not in self.data_windows:
            return None
        
        window = self.data_windows[symbol]
        
        # Check for significant price movement
        price_change_1m = window.get_price_change_percent(1)
        price_change_5m = window.get_price_change_percent(5)
        volume_change = window.get_volume_change_percent(5)
        
        signal_type = None
        
        # Pump detection
        if price_change_1m > settings.PUMP_THRESHOLD_PERCENT:
            signal_type = SignalType.PUMP
        
        # Dump detection
        elif price_change_1m < settings.DUMP_THRESHOLD_PERCENT:
            signal_type = SignalType.DUMP
        
        # Volume spike without major price movement
        elif volume_change > (settings.VOLUME_SPIKE_MULTIPLIER - 1) * 100:
            signal_type = SignalType.VOLUME_SPIKE
        
        if not signal_type:
            return None
        
        # Calculate confidence score
        confidence = self._calculate_confidence(
            price_change_1m,
            price_change_5m,
            volume_change,
            signal_type
        )
        
        # Generate explanation
        explanation = self._generate_explanation(
            signal_type,
            price_change_1m,
            volume_change,
            window
        )
        
        # Find historical analogies
        analogies = self._find_historical_analogies(symbol, signal_type, window)
        
        return Signal(
            signal_type=signal_type,
            symbol=symbol,
            exchange=Exchange.BINANCE,  # Will be updated based on actual source
            price=window.prices[-1] if window.prices else 0,
            price_change_percent=price_change_1m,
            volume_change_percent=volume_change,
            confidence_score=confidence,
            explanation=explanation,
            historical_analogies=analogies,
            timestamp=datetime.utcnow(),
        )
    
    def _calculate_confidence(
        self,
        price_change: float,
        price_change_5m: float,
        volume_change: float,
        signal_type: SignalType
    ) -> float:
        """Calculate confidence score 0-100%"""
        base_score = 50.0
        
        # Price change contribution
        abs_price_change = abs(price_change)
        if abs_price_change > 10:
            base_score += 20
        elif abs_price_change > 5:
            base_score += 15
        elif abs_price_change > 3:
            base_score += 10
        
        # Volume confirmation
        if volume_change > 200:
            base_score += 20
        elif volume_change > 100:
            base_score += 15
        elif volume_change > 50:
            base_score += 10
        
        # Trend alignment (5min aligns with 1min)
        if (price_change > 0 and price_change_5m > 0) or \
           (price_change < 0 and price_change_5m < 0):
            base_score += 10
        
        return min(95.0, max(30.0, base_score))
    
    def _generate_explanation(
        self,
        signal_type: SignalType,
        price_change: float,
        volume_change: float,
        window: DataWindow
    ) -> SignalExplanation:
        """Generate intelligent explanation for the signal"""
        reasons = []
        market_behavior = MarketBehavior.TRENDING
        smart_money = False
        unusual_volume = volume_change > 100
        orderbook_changes = []
        
        # Price-based reasons
        if abs(price_change) > 10:
            direction = "surge" if price_change > 0 else "crash"
            reasons.append(f"Extreme price {direction}: {price_change:+.1f}%")
        elif abs(price_change) > 5:
            direction = "spike" if price_change > 0 else "drop"
            reasons.append(f"Sharp price {direction}: {price_change:+.1f}%")
        else:
            reasons.append(f"Price movement: {price_change:+.1f}%")
        
        # Volume-based reasons
        if volume_change > 300:
            reasons.append(f"Massive volume spike: +{volume_change:.0f}%")
            smart_money = True
        elif volume_change > 100:
            reasons.append(f"High volume: +{volume_change:.0f}%")
        elif volume_change > 50:
            reasons.append(f"Elevated volume: +{volume_change:.0f}%")
        
        # Determine market behavior
        volatility = window.get_volatility(20)
        
        if price_change > 5 and volume_change > 100:
            market_behavior = MarketBehavior.ACCUMULATION
            reasons.append("Strong buying pressure detected")
        elif price_change < -5 and volume_change > 100:
            market_behavior = MarketBehavior.DISTRIBUTION
            reasons.append("Heavy selling pressure detected")
        elif abs(price_change) < 2 and volume_change > 100:
            market_behavior = MarketBehavior.CONSOLIDATION
            reasons.append("Accumulation/Distribution phase")
        elif volatility > 0.05:
            market_behavior = MarketBehavior.MANIPULATION
            reasons.append("High volatility suggests manipulation")
        
        if smart_money:
            reasons.append("Smart money activity detected")
        
        return SignalExplanation(
            reasons=reasons,
            market_behavior=market_behavior,
            smart_money_activity=smart_money,
            unusual_volume=unusual_volume,
            orderbook_changes=orderbook_changes,
        )
    
    def _find_historical_analogies(
        self,
        symbol: str,
        signal_type: SignalType,
        window: DataWindow
    ) -> List[HistoricalAnalogy]:
        """Find similar historical patterns"""
        # This would query the database for similar patterns
        # For now, return mock data to demonstrate the structure
        
        current_volatility = window.get_volatility(20)
        
        analogies = [
            HistoricalAnalogy(
                date=datetime.utcnow() - timedelta(days=3),
                symbol=symbol,
                similarity_score=0.85,
                outcome="success",
                price_change_after=8.5,
                time_frame="4h"
            ),
            HistoricalAnalogy(
                date=datetime.utcnow() - timedelta(days=7),
                symbol=symbol,
                similarity_score=0.72,
                outcome="success",
                price_change_after=12.3,
                time_frame="4h"
            ),
        ]
        
        return analogies
