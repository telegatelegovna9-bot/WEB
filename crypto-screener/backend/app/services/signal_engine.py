import uuid
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random

from app.models.schemas import (
    Signal, SignalType, SignalIntelligence, Reason, 
    MarketBehavior, ConfidenceLevel, HistoricalAnalogy,
    TickerData, OrderBook, PatternDetection, DensityDetection
)
from app.core.config import settings


class SignalIntelligenceEngine:
    """Core intelligence engine that analyzes and explains signals"""
    
    def __init__(self):
        self.signal_history: List[Signal] = []
        self.pattern_database: List[Dict] = []
        
    def analyze_signal(self, ticker: TickerData, orderbook: Optional[OrderBook] = None) -> Optional[Signal]:
        """Analyze ticker data and generate intelligent signal"""
        signal_type = self.detect_signal_type(ticker)
        if not signal_type:
            return None
            
        intelligence = self.generate_intelligence(ticker, signal_type, orderbook)
        
        signal = Signal(
            id=str(uuid.uuid4()),
            type=signal_type,
            symbol=ticker.symbol,
            exchange=ticker.exchange,
            timestamp=datetime.utcnow(),
            price=ticker.price,
            price_change_percent=ticker.price_change_percent_24h,
            volume_change_percent=self.calculate_volume_change(ticker),
            intelligence=intelligence,
            tags=self.generate_tags(signal_type, intelligence)
        )
        
        self.signal_history.append(signal)
        return signal
        
    def detect_signal_type(self, ticker: TickerData) -> Optional[SignalType]:
        """Detect what type of signal this is"""
        price_change = ticker.price_change_percent_24h
        volume_ratio = ticker.quote_volume_24h / max(ticker.price * ticker.volume_24h, 1)
        
        # Pump detection
        if price_change >= settings.PUMP_THRESHOLD_PERCENT:
            return SignalType.PUMP
            
        # Dump detection
        if price_change <= settings.DUMP_THRESHOLD_PERCENT:
            return SignalType.DUMP
            
        # Volume spike
        if volume_ratio > settings.VOLUME_SPIKE_MULTIPLIER:
            return SignalType.VOLUME_SPIKE
            
        return None
        
    def generate_intelligence(self, ticker: TickerData, signal_type: SignalType, 
                             orderbook: Optional[OrderBook] = None) -> SignalIntelligence:
        """Generate detailed intelligence for a signal"""
        reasons = []
        market_behavior = MarketBehavior.FOMO
        probability = 50.0
        
        # Analyze price movement
        price_change = abs(ticker.price_change_percent_24h)
        if price_change > 15:
            reasons.append(Reason(
                description=f"Extreme price movement: {ticker.price_change_percent_24h:+.1f}%",
                weight=2.0,
                type="price_action"
            ))
        elif price_change > 8:
            reasons.append(Reason(
                description=f"Strong price movement: {ticker.price_change_percent_24h:+.1f}%",
                weight=1.5,
                type="price_action"
            ))
        else:
            reasons.append(Reason(
                description=f"Moderate price movement: {ticker.price_change_percent_24h:+.1f}%",
                weight=1.0,
                type="price_action"
            ))
            
        # Analyze volume
        if ticker.quote_volume_24h > 100_000_000:  # $100M+ volume
            reasons.append(Reason(
                description="Massive trading volume detected",
                weight=2.0,
                type="volume"
            ))
            probability += 15
        elif ticker.quote_volume_24h > 10_000_000:  # $10M+ volume
            reasons.append(Reason(
                description="High trading volume",
                weight=1.5,
                type="volume"
            ))
            probability += 10
            
        # Analyze order book if available
        if orderbook:
            if orderbook.wall_detected:
                reasons.append(Reason(
                    description=f"Large {'buy' if orderbook.wall_type == 'bid_wall' else 'sell'} wall detected at ${orderbook.wall_price:.2f}",
                    weight=1.8,
                    type="orderbook"
                ))
                if orderbook.wall_type == "bid_wall":
                    market_behavior = MarketBehavior.SMART_MONEY_ACCUMULATION
                    probability += 12
                else:
                    market_behavior = MarketBehavior.DISTRIBUTION
                    probability -= 5
                    
        # Determine market behavior based on signal type
        if signal_type == SignalType.PUMP:
            if price_change > 10 and ticker.quote_volume_24h > 50_000_000:
                market_behavior = MarketBehavior.SMART_MONEY_ACCUMULATION
                probability += 10
            elif price_change > 20:
                market_behavior = MarketBehavior.FOMO
                probability -= 5
            else:
                market_behavior = MarketBehavior.BREAKOUT_CONFIRMED
                probability += 5
                
        elif signal_type == SignalType.DUMP:
            if price_change < -15:
                market_behavior = MarketBehavior.DISTRIBUTION
                probability += 8
            else:
                market_behavior = MarketBehavior.MANIPULATION
                probability -= 3
                
        # Add historical analogies
        historical_analogies = self.find_historical_analogies(ticker.symbol, signal_type)
        
        # Generate explanation
        explanation = self.generate_explanation(signal_type, reasons, market_behavior)
        
        # Determine confidence level
        if probability >= 75:
            confidence = ConfidenceLevel.VERY_HIGH
        elif probability >= 60:
            confidence = ConfidenceLevel.HIGH
        elif probability >= 40:
            confidence = ConfidenceLevel.MEDIUM
        else:
            confidence = ConfidenceLevel.LOW
            
        return SignalIntelligence(
            reasons=reasons,
            market_behavior=market_behavior,
            probability_score=min(max(probability, 0), 100),
            confidence_level=confidence,
            historical_analogies=historical_analogies,
            explanation=explanation
        )
        
    def find_historical_analogies(self, symbol: str, signal_type: SignalType) -> List[HistoricalAnalogy]:
        """Find similar historical patterns"""
        # In production, this would query a database
        # For now, generate realistic mock data
        analogies = []
        
        base_date = datetime.utcnow()
        outcomes = ["bullish", "bearish", "neutral"]
        
        for i in range(random.randint(1, 4)):
            days_ago = random.randint(7, 90)
            analogy = HistoricalAnalogy(
                date=base_date - timedelta(days=days_ago),
                symbol=symbol,
                outcome=random.choice(outcomes),
                price_change_percent=round(random.uniform(-25, 35), 2),
                similarity_score=round(random.uniform(0.6, 0.95), 2)
            )
            analogies.append(analogy)
            
        return analogies
        
    def generate_explanation(self, signal_type: SignalType, reasons: List[Reason], 
                            market_behavior: MarketBehavior) -> str:
        """Generate human-readable explanation"""
        behavior_texts = {
            MarketBehavior.SMART_MONEY_ACCUMULATION: "Smart money accumulation detected",
            MarketBehavior.DISTRIBUTION: "Distribution phase - large holders selling",
            MarketBehavior.FOMO: "FOMO-driven rally with retail participation",
            MarketBehavior.MANIPULATION: "Potential manipulation - exercise caution",
            MarketBehavior.BREAKOUT_CONFIRMED: "Confirmed breakout with strong momentum",
            MarketBehavior.FALSE_BREAKOUT: "Potential false breakout - watch for reversal"
        }
        
        signal_texts = {
            SignalType.PUMP: "Strong upward momentum",
            SignalType.DUMP: "Significant downward pressure",
            SignalType.VOLUME_SPIKE: "Unusual volume activity",
            SignalType.BREAKOUT: "Key level breakout",
            SignalType.WALL_DETECTED: "Large order wall detected"
        }
        
        explanation = f"{signal_texts.get(signal_type, 'Market anomaly detected')}. "
        explanation += f"{behavior_texts.get(market_behavior, 'Market behavior analysis')}. "
        
        key_reasons = [r.description for r in sorted(reasons, key=lambda x: x.weight, reverse=True)[:2]]
        if key_reasons:
            explanation += "Key factors: " + "; ".join(key_reasons) + "."
            
        return explanation
        
    def generate_tags(self, signal_type: SignalType, intelligence: SignalIntelligence) -> List[str]:
        """Generate relevant tags for the signal"""
        tags = []
        
        if intelligence.probability_score >= 70:
            tags.append("high_probability")
        if intelligence.market_behavior == MarketBehavior.SMART_MONEY_ACCUMULATION:
            tags.append("smart_money")
        if intelligence.market_behavior == MarketBehavior.MANIPULATION:
            tags.append("manipulation_risk")
        if len(intelligence.historical_analogies) > 2:
            avg_success = sum(1 for a in intelligence.historical_analogies if a.outcome == "bullish") / len(intelligence.historical_analogies)
            if avg_success > 0.6:
                tags.append("historically_bullish")
                
        tags.append(signal_type.value)
        
        return tags
        
    def calculate_volume_change(self, ticker: TickerData) -> float:
        """Calculate volume change percentage (mock implementation)"""
        # In production, compare with historical average
        return random.uniform(50, 500)


class PatternDetector:
    """Detect chart patterns and formations"""
    
    def __init__(self):
        self.detected_patterns: List[PatternDetection] = []
        
    def analyze_candles(self, symbol: str, candles: List[Dict]) -> List[PatternDetection]:
        """Analyze candlestick data for patterns"""
        patterns = []
        
        if len(candles) < 20:
            return patterns
            
        # Simple pattern detection (in production, use more sophisticated algorithms)
        prices = [c['close'] for c in candles[-20:]]
        highs = [c['high'] for c in candles[-20:]]
        lows = [c['low'] for c in candles[-20:]]
        
        # Detect consolidation
        if self.is_consolidating(prices):
            patterns.append(PatternDetection(
                pattern_type="consolidation",
                symbol=symbol,
                exchange=candles[0].get('exchange', 'binance'),
                confidence=0.75,
                breakout_level=max(prices) if prices[-1] > prices[0] else min(prices)
            ))
            
        # Detect potential flag
        if self.is_flag_pattern(prices, highs, lows):
            patterns.append(PatternDetection(
                pattern_type="flag",
                symbol=symbol,
                exchange=candles[0].get('exchange', 'binance'),
                confidence=0.65,
                target_price=prices[-1] * 1.05,
                stop_loss=prices[-1] * 0.98
            ))
            
        self.detected_patterns.extend(patterns)
        return patterns
        
    def is_consolidating(self, prices: List[float], threshold: float = 0.03) -> bool:
        """Check if price is consolidating"""
        if len(prices) < 10:
            return False
        recent = prices[-10:]
        range_pct = (max(recent) - min(recent)) / min(recent)
        return range_pct < threshold
        
    def is_flag_pattern(self, prices: List[float], highs: List[float], lows: List[float]) -> bool:
        """Check for flag pattern"""
        if len(prices) < 15:
            return False
        # Simplified flag detection
        return True  # Mock implementation


class DensityDetector:
    """Detect order book density clusters"""
    
    def __init__(self):
        self.detected_densities: List[DensityDetection] = []
        
    def analyze_orderbook(self, orderbook: OrderBook) -> List[DensityDetection]:
        """Analyze order book for density clusters"""
        densities = []
        
        # Analyze bids for clusters
        bid_clusters = self.find_clusters(orderbook.bids, 'bid')
        densities.extend(bid_clusters)
        
        # Analyze asks for clusters
        ask_clusters = self.find_clusters(orderbook.asks, 'ask')
        densities.extend(ask_clusters)
        
        self.detected_densities.extend(densities)
        return densities
        
    def find_clusters(self, levels: List, side: str) -> List[DensityDetection]:
        """Find density clusters in order book levels"""
        clusters = []
        
        if len(levels) < 3:
            return clusters
            
        # Find levels with significantly higher size
        avg_size = sum(l.size for l in levels) / len(levels)
        
        for i, level in enumerate(levels):
            if level.size > avg_size * 3:  # 3x average
                strength = min((level.size / avg_size) * 20, 100)
                cluster = DensityDetection(
                    symbol=orderbook.symbol,
                    exchange=orderbook.exchange,
                    density_type=f"{side}_cluster",
                    price_level=level.price,
                    total_size=level.size,
                    order_count=1,  # Would need actual order count from exchange
                    strength=strength
                )
                clusters.append(cluster)
                
        return clusters


# Create singleton instances
intelligence_engine = SignalIntelligenceEngine()
pattern_detector = PatternDetector()
density_detector = DensityDetector()
