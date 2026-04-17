from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import numpy as np
from datetime import datetime, timedelta
from ...models.schemas import (
    Signal, SignalIntelligence, HistoricalPattern, TickerData, 
    OrderBook, Trade
)
from ...core.enums import SignalType, MarketBehavior, Exchange


class BaseStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', self.__class__.__name__)
        self.enabled = config.get('enabled', True)
        self.min_confidence = config.get('min_confidence', 0.6)
        
    @abstractmethod
    async def analyze(
        self,
        symbol: str,
        exchange: Exchange,
        ticker: Optional[TickerData] = None,
        orderbook: Optional[OrderBook] = None,
        trades: Optional[List[Trade]] = None,
        historical_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Signal]:
        """Analyze market data and return signal if conditions met"""
        pass
    
    def _calculate_confidence(
        self,
        factors: Dict[str, float],
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """Calculate confidence score from multiple factors"""
        if weights is None:
            weights = {k: 1.0 for k in factors.keys()}
            
        total_weight = sum(weights.values())
        weighted_sum = sum(factors.get(k, 0) * weights.get(k, 0) for k in factors.keys())
        
        return min(100, max(0, (weighted_sum / total_weight) * 100))
    
    def _determine_market_behavior(
        self,
        price_change: float,
        volume_ratio: float,
        orderbook_imbalance: float
    ) -> MarketBehavior:
        """Determine market behavior type based on indicators"""
        
        # Strong volume with price increase = accumulation
        if price_change > 2 and volume_ratio > 2 and orderbook_imbalance > 0.3:
            return MarketBehavior.ACCUMULATION
        
        # Strong volume with price decrease = distribution
        if price_change < -2 and volume_ratio > 2 and orderbook_imbalance < -0.3:
            return MarketBehavior.DISTRIBUTION
        
        # Moderate movement with breakout characteristics
        if abs(price_change) > 3 and volume_ratio > 1.5:
            return MarketBehavior.BREAKOUT
        
        # Suspicious patterns = manipulation
        if volume_ratio > 5 and abs(price_change) > 5:
            return MarketBehavior.MANIPULATION
        
        return MarketBehavior.NORMAL
    
    def _find_historical_patterns(
        self,
        symbol: str,
        current_pattern: Dict[str, Any],
        lookback_days: int = 30
    ) -> List[HistoricalPattern]:
        """Find similar historical patterns (placeholder)"""
        # This would query the database for similar patterns
        # For now, return empty list
        return []
    
    def _generate_signal_intelligence(
        self,
        signal_type: SignalType,
        causes: List[str],
        confidence: float,
        market_behavior: MarketBehavior,
        historical_patterns: List[HistoricalPattern],
        smart_money_indicators: Dict[str, Any]
    ) -> SignalIntelligence:
        """Generate detailed signal intelligence"""
        
        risk_level = "low"
        recommended_action = None
        
        if confidence >= 80:
            risk_level = "medium"
            if signal_type in [SignalType.PUMP, SignalType.BREAKOUT]:
                recommended_action = "Consider long position with tight stop-loss"
            elif signal_type == SignalType.DUMP:
                recommended_action = "Consider short position or exit longs"
        elif confidence >= 60:
            risk_level = "medium"
            recommended_action = "Monitor closely, wait for confirmation"
        else:
            risk_level = "high"
            recommended_action = "High risk, avoid trading"
        
        return SignalIntelligence(
            causes=causes,
            market_behavior=market_behavior,
            confidence_score=confidence,
            historical_patterns=historical_patterns,
            smart_money_indicators=smart_money_indicators,
            risk_level=risk_level,
            recommended_action=recommended_action
        )
