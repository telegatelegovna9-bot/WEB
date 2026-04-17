import uuid
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

from app.models.schemas import (
    Signal, SignalType, SignalIntelligence, SignalReason,
    HistoricalAnalogy, MarketBehavior, TickerData, OrderBookData
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class SignalIntelligenceEngine:
    """
    Core intelligence engine that analyzes signals and provides explanations.
    This is the key differentiator of the platform.
    """
    
    def __init__(self):
        self.historical_signals: List[Signal] = []
    
    def analyze_signal(
        self,
        signal_type: SignalType,
        symbol: str,
        price: float,
        price_change_percent: float,
        volume_change_percent: float,
        orderbook_data: Optional[OrderBookData] = None,
        recent_trades: Optional[List] = None
    ) -> SignalIntelligence:
        """
        Analyze a detected signal and generate intelligence report.
        """
        reasons = self._detect_reasons(
            signal_type, price_change_percent, volume_change_percent, orderbook_data
        )
        
        market_behavior = self._classify_market_behavior(
            signal_type, reasons, price_change_percent, volume_change_percent
        )
        
        probability_score = self._calculate_probability(
            signal_type, reasons, market_behavior, volume_change_percent
        )
        
        historical_analogies = self._find_historical_analogies(
            signal_type, symbol, price_change_percent, volume_change_percent
        )
        
        confidence_level = self._get_confidence_level(probability_score)
        
        return SignalIntelligence(
            reasons=reasons,
            market_behavior=market_behavior,
            probability_score=probability_score,
            historical_analogies=historical_analogies,
            confidence_level=confidence_level
        )
    
    def _detect_reasons(
        self,
        signal_type: SignalType,
        price_change: float,
        volume_change: float,
        orderbook_data: Optional[OrderBookData]
    ) -> List[SignalReason]:
        """Detect and explain the reasons behind the signal"""
        reasons = []
        
        # Volume analysis
        if volume_change > 200:
            reasons.append(SignalReason(
                type="volume_spike",
                description=f"Volume increased by {volume_change:.0f}%",
                value=volume_change,
                impact=min(volume_change / 500, 1.0)
            ))
        elif volume_change > 100:
            reasons.append(SignalReason(
                type="volume_increase",
                description=f"Volume increased by {volume_change:.0f}%",
                value=volume_change,
                impact=min(volume_change / 300, 0.8)
            ))
        
        # Price movement analysis
        abs_price_change = abs(price_change)
        if abs_price_change > 10:
            reasons.append(SignalReason(
                type="extreme_price_movement",
                description=f"Price {'surged' if price_change > 0 else 'dropped'} by {abs_price_change:.1f}%",
                value=price_change,
                impact=min(abs_price_change / 20, 1.0)
            ))
        elif abs_price_change > 5:
            reasons.append(SignalReason(
                type="strong_price_movement",
                description=f"Price {'increased' if price_change > 0 else 'decreased'} by {abs_price_change:.1f}%",
                value=price_change,
                impact=min(abs_price_change / 10, 0.7)
            ))
        
        # Order book analysis
        if orderbook_data:
            wall_analysis = self._analyze_order_walls(orderbook_data)
            if wall_analysis:
                reasons.extend(wall_analysis)
            
            imbalance = self._calculate_order_imbalance(orderbook_data)
            if abs(imbalance) > 0.3:
                side = "buy" if imbalance > 0 else "sell"
                reasons.append(SignalReason(
                    type="order_imbalance",
                    description=f"Strong {side} pressure in order book ({imbalance*100:.1f}% imbalance)",
                    value=imbalance,
                    impact=abs(imbalance)
                ))
        
        # Add default reason if none detected
        if not reasons:
            reasons.append(SignalReason(
                type="momentum",
                description="Price momentum detected",
                value=price_change,
                impact=0.5
            ))
        
        return reasons
    
    def _analyze_order_walls(self, orderbook: OrderBookData) -> List[SignalReason]:
        """Analyze order book for significant walls"""
        reasons = []
        
        if not orderbook.bids or not orderbook.asks:
            return reasons
        
        # Calculate total bid/ask volumes
        total_bids = sum(level.amount for level in orderbook.bids)
        total_asks = sum(level.amount for level in orderbook.asks)
        
        # Find largest bid wall
        if orderbook.bids:
            max_bid = max(orderbook.bids, key=lambda x: x.amount)
            if max_bid.amount > total_bids * 0.3:  # Single level > 30% of total
                reasons.append(SignalReason(
                    type="bid_wall",
                    description=f"Large buy wall at ${max_bid.price:.2f} ({max_bid.amount:.2f} units)",
                    value=max_bid.amount,
                    impact=0.6
                ))
        
        # Find largest ask wall
        if orderbook.asks:
            max_ask = max(orderbook.asks, key=lambda x: x.amount)
            if max_ask.amount > total_asks * 0.3:
                reasons.append(SignalReason(
                    type="ask_wall",
                    description=f"Large sell wall at ${max_ask.price:.2f} ({max_ask.amount:.2f} units)",
                    value=max_ask.amount,
                    impact=0.6
                ))
        
        return reasons
    
    def _calculate_order_imbalance(self, orderbook: OrderBookData) -> float:
        """Calculate buy/sell pressure imbalance (-1 to 1)"""
        if not orderbook.bids or not orderbook.asks:
            return 0.0
        
        total_bids = sum(level.amount * level.price for level in orderbook.bids[:10])
        total_asks = sum(level.amount * level.price for level in orderbook.asks[:10])
        
        total = total_bids + total_asks
        if total == 0:
            return 0.0
        
        return (total_bids - total_asks) / total
    
    def _classify_market_behavior(
        self,
        signal_type: SignalType,
        reasons: List[SignalReason],
        price_change: float,
        volume_change: float
    ) -> MarketBehavior:
        """Classify the type of market behavior"""
        
        # Check for smart money accumulation
        if signal_type == SignalType.PUMP and volume_change > 150:
            has_wall = any(r.type in ["bid_wall", "order_imbalance"] for r in reasons)
            if has_wall:
                return MarketBehavior.SMART_MONEY_ACCUMULATION
        
        # Check for smart money distribution
        if signal_type == SignalType.DUMP and volume_change > 150:
            has_wall = any(r.type in ["ask_wall", "order_imbalance"] for r in reasons)
            if has_wall:
                return MarketBehavior.SMART_MONEY_DISTRIBUTION
        
        # Check for retail FOMO
        if signal_type == SignalType.PUMP and price_change > 15 and volume_change > 300:
            return MarketBehavior.RETAIL_FOMO
        
        # Check for manipulation
        if abs(price_change) > 20 and volume_change > 500:
            return MarketBehavior.MANIPULATION
        
        # Check for breakout
        if signal_type == SignalType.BREAKOUT or (signal_type == SignalType.PUMP and price_change > 5):
            return MarketBehavior.BREAKOUT
        
        # Default to consolidation
        return MarketBehavior.CONSOLIDATION
    
    def _calculate_probability(
        self,
        signal_type: SignalType,
        reasons: List[SignalReason],
        market_behavior: MarketBehavior,
        volume_change: float
    ) -> float:
        """Calculate probability score (0-100) for signal success"""
        
        base_score = 50.0
        
        # Volume factor
        if volume_change > 200:
            base_score += 15
        elif volume_change > 100:
            base_score += 10
        elif volume_change > 50:
            base_score += 5
        
        # Number of reasons factor
        reason_bonus = min(len(reasons) * 5, 15)
        base_score += reason_bonus
        
        # Impact-weighted reasons
        total_impact = sum(r.impact for r in reasons)
        impact_bonus = min(total_impact * 10, 15)
        base_score += impact_bonus
        
        # Market behavior factor
        behavior_scores = {
            MarketBehavior.SMART_MONEY_ACCUMULATION: 10,
            MarketBehavior.SMART_MONEY_DISTRIBUTION: 10,
            MarketBehavior.RETAIL_FOMO: 5,
            MarketBehavior.MANIPULATION: -10,
            MarketBehavior.BREAKOUT: 8,
            MarketBehavior.CONSOLIDATION: 0
        }
        base_score += behavior_scores.get(market_behavior, 0)
        
        # Clamp to 0-100
        return max(0, min(100, base_score))
    
    def _find_historical_analogies(
        self,
        signal_type: SignalType,
        symbol: str,
        price_change: float,
        volume_change: float
    ) -> List[HistoricalAnalogy]:
        """Find similar historical situations"""
        # In production, this would query the database for similar patterns
        # For now, generate synthetic analogies based on signal characteristics
        
        analogies = []
        
        # Generate 1-3 analogies
        num_analogies = min(3, max(1, int(abs(price_change) / 10)))
        
        for i in range(num_analogies):
            days_ago = (i + 1) * 7  # Weekly intervals
            date = datetime.utcnow() - timedelta(days=days_ago)
            
            # Simulate outcome based on current signal strength
            base_outcome = "positive" if signal_type == SignalType.PUMP else "negative"
            similarity = max(0.3, 0.9 - (i * 0.2))
            
            analogies.append(HistoricalAnalogy(
                date=date,
                symbol=symbol,
                outcome=base_outcome,
                price_change_percent=price_change * similarity * (0.5 + i * 0.2),
                similarity_score=similarity
            ))
        
        return analogies
    
    def _get_confidence_level(self, probability_score: float) -> str:
        """Convert probability score to confidence level string"""
        if probability_score >= 80:
            return "very_high"
        elif probability_score >= 65:
            return "high"
        elif probability_score >= 45:
            return "medium"
        else:
            return "low"


class PumpDumpDetector:
    """Detect pump and dump patterns"""
    
    def __init__(self, intelligence_engine: SignalIntelligenceEngine):
        self.intelligence_engine = intelligence_engine
        self.price_history: Dict[str, List[float]] = {}
        self.volume_history: Dict[str, List[float]] = {}
    
    def check(self, ticker: TickerData) -> Optional[Signal]:
        """Check if ticker shows pump/dump pattern"""
        symbol = ticker.symbol
        
        # Initialize history if needed
        if symbol not in self.price_history:
            self.price_history[symbol] = []
            self.volume_history[symbol] = []
        
        # Store current data
        self.price_history[symbol].append(ticker.price)
        self.volume_history[symbol].append(ticker.volume_24h)
        
        # Keep only last 100 data points
        self.price_history[symbol] = self.price_history[symbol][-100:]
        self.volume_history[symbol] = self.volume_history[symbol][-100:]
        
        if len(self.price_history[symbol]) < 10:
            return None
        
        # Calculate price change
        old_price = self.price_history[symbol][0]
        price_change_pct = ((ticker.price - old_price) / old_price) * 100 if old_price > 0 else 0
        
        # Calculate volume change
        old_volume = self.volume_history[symbol][0]
        volume_change_pct = ((ticker.volume_24h - old_volume) / old_volume) * 100 if old_volume > 0 else 0
        
        # Check thresholds
        signal_type = None
        if price_change_pct > settings.PUMP_THRESHOLD_PERCENT:
            signal_type = SignalType.PUMP
        elif price_change_pct < settings.DUMP_THRESHOLD_PERCENT:
            signal_type = SignalType.DUMP
        
        if not signal_type:
            return None
        
        # Generate intelligence
        intelligence = self.intelligence_engine.analyze_signal(
            signal_type=signal_type,
            symbol=symbol,
            price=ticker.price,
            price_change_percent=price_change_pct,
            volume_change_percent=volume_change_pct
        )
        
        # Only return signal if probability is decent
        if intelligence.probability_score < 40:
            return None
        
        return Signal(
            id=str(uuid.uuid4()),
            type=signal_type,
            symbol=symbol,
            exchange=ticker.exchange,
            price=ticker.price,
            price_change_percent=price_change_pct,
            volume_change_percent=volume_change_pct,
            intelligence=intelligence
        )


class BreakoutDetector:
    """Detect breakout patterns"""
    
    def __init__(self, intelligence_engine: SignalIntelligenceEngine):
        self.intelligence_engine = intelligence_engine
        self.price_levels: Dict[str, Dict] = {}
    
    def check(self, ticker: TickerData, orderbook: Optional[OrderBookData] = None) -> Optional[Signal]:
        """Check for breakout patterns"""
        symbol = ticker.symbol
        
        # Simple breakout detection based on 24h high/low
        if ticker.price_change_percent_24h > 5:
            # Approaching or breaking 24h high
            distance_to_high = ((ticker.high_24h - ticker.price) / ticker.price) * 100
            
            if distance_to_high < 1:  # Within 1% of high
                intelligence = self.intelligence_engine.analyze_signal(
                    signal_type=SignalType.BREAKOUT,
                    symbol=symbol,
                    price=ticker.price,
                    price_change_percent=ticker.price_change_percent_24h,
                    volume_change_percent=0,
                    orderbook_data=orderbook
                )
                
                if intelligence.probability_score >= 50:
                    return Signal(
                        id=str(uuid.uuid4()),
                        type=SignalType.BREAKOUT,
                        symbol=symbol,
                        exchange=ticker.exchange,
                        price=ticker.price,
                        price_change_percent=ticker.price_change_percent_24h,
                        volume_change_percent=0,
                        intelligence=intelligence
                    )
        
        return None


class OrderBookDensityDetector:
    """Detect large order walls and density changes"""
    
    def __init__(self, intelligence_engine: SignalIntelligenceEngine):
        self.intelligence_engine = intelligence_engine
        self.previous_books: Dict[str, OrderBookData] = {}
    
    def check(self, orderbook: OrderBookData) -> Optional[Signal]:
        """Check for significant order book patterns"""
        symbol = orderbook.symbol
        
        if not orderbook.bids or not orderbook.asks:
            return None
        
        # Calculate total bid/ask volume
        total_bids = sum(level.amount for level in orderbook.bids)
        total_asks = sum(level.amount for level in orderbook.asks)
        
        # Check for large walls
        max_bid = max(orderbook.bids, key=lambda x: x.amount) if orderbook.bids else None
        max_ask = max(orderbook.asks, key=lambda x: x.amount) if orderbook.asks else None
        
        wall_detected = False
        signal_type = SignalType.ORDER_WALL
        
        if max_bid and max_bid.amount > total_bids * 0.4:
            wall_detected = True
        elif max_ask and max_ask.amount > total_asks * 0.4:
            wall_detected = True
        
        if not wall_detected:
            return None
        
        # Generate intelligence
        intelligence = self.intelligence_engine.analyze_signal(
            signal_type=signal_type,
            symbol=symbol,
            price=orderbook.bids[0].price if orderbook.bids else 0,
            price_change_percent=0,
            volume_change_percent=0,
            orderbook_data=orderbook
        )
        
        return Signal(
            id=str(uuid.uuid4()),
            type=signal_type,
            symbol=symbol,
            exchange=orderbook.exchange,
            price=orderbook.bids[0].price if orderbook.bids else 0,
            price_change_percent=0,
            volume_change_percent=0,
            intelligence=intelligence
        )
