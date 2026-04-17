import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
import numpy as np
from .base import BaseStrategy
from ...models.schemas import Signal, TickerData, OrderBook, Trade, HistoricalPattern
from ...core.enums import SignalType, MarketBehavior, Exchange


class BreakoutStrategy(BaseStrategy):
    """Detect breakout patterns from consolidation zones"""
    
    def __init__(self, config: Dict[str, Any] = None):
        default_config = {
            'name': 'breakout_detector',
            'enabled': True,
            'min_confidence': 0.65,
            'lookback_periods': 20,
            'breakout_threshold': 2.0,  # % above/below range
            'volume_confirmation': True,
            'min_volume_ratio': 1.5
        }
        config = config or {}
        super().__init__({**default_config, **config})
        
    async def analyze(
        self,
        symbol: str,
        exchange: Exchange,
        ticker: Optional[TickerData] = None,
        orderbook: Optional[OrderBook] = None,
        trades: Optional[List[Trade]] = None,
        historical_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Signal]:
        """Analyze for breakout patterns"""
        
        if not ticker or not historical_data:
            return None
            
        causes = []
        factors = {}
        smart_money_indicators = {}
        
        # Get OHLCV data from historical_data
        candles = historical_data.get('candles', [])
        if len(candles) < self.config['lookback_periods']:
            return None
        
        # Calculate consolidation range
        lookback_candles = candles[-self.config['lookback_periods']:]
        highs = [c['high'] for c in lookback_candles]
        lows = [c['low'] for c in lookback_candles]
        volumes = [c['volume'] for c in lookback_candles]
        
        resistance = max(highs)
        support = min(lows)
        range_size = resistance - support
        avg_volume = np.mean(volumes)
        
        if range_size == 0:
            return None
        
        current_price = ticker.price
        
        # Check for breakout above resistance
        breakout_above = current_price > resistance * (1 + self.config['breakout_threshold'] / 100)
        # Check for breakout below support  
        breakout_below = current_price < support * (1 - self.config['breakout_threshold'] / 100)
        
        if not breakout_above and not breakout_below:
            return None
        
        # Check volume confirmation
        volume_confirmed = False
        if self.config['volume_confirmation']:
            current_volume = ticker.volume_24h
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            if volume_ratio >= self.config['min_volume_ratio']:
                volume_confirmed = True
                causes.append(f"Volume confirmation: {volume_ratio:.2f}x average")
                factors['volume_confirmation'] = min(volume_ratio / 3, 1.0)
                smart_money_indicators['volume_spike'] = volume_ratio
        
        # Determine direction
        if breakout_above:
            signal_type = SignalType.BREAKOUT
            direction = "above resistance"
            price_level = resistance
            causes.append(f"Price broke {direction} at ${price_level:.2f}")
            causes.append(f"Resistance level: ${resistance:.2f}")
            factors['breakout_strength'] = min((current_price - resistance) / range_size, 1.0)
        else:
            signal_type = SignalType.DUMP  # Downward breakout
            direction = "below support"
            price_level = support
            causes.append(f"Price broke {direction} at ${price_level:.2f}")
            causes.append(f"Support level: ${support:.2f}")
            factors['breakout_strength'] = min((support - current_price) / range_size, 1.0)
        
        # Check for consolidation before breakout
        range_bound_count = sum(
            1 for c in lookback_candles 
            if support * 1.01 <= c['close'] <= resistance * 0.99
        )
        consolidation_score = range_bound_count / len(lookback_candles)
        
        if consolidation_score > 0.6:
            causes.append(f"Strong consolidation detected ({consolidation_score*100:.0f}% of candles in range)")
            factors['consolidation'] = consolidation_score
        
        # Analyze order book for confirmation
        if orderbook:
            bid_volume = sum(b.quantity for b in orderbook.bids[:10])
            ask_volume = sum(a.quantity for a in orderbook.asks[:10])
            
            if bid_volume > 0 and ask_volume > 0:
                imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
                
                if breakout_above and imbalance > 0.2:
                    causes.append("Order book confirms bullish pressure")
                    factors['orderbook_confirmation'] = imbalance
                    smart_money_indicators['buy_pressure'] = True
                elif breakout_below and imbalance < -0.2:
                    causes.append("Order book confirms bearish pressure")
                    factors['orderbook_confirmation'] = abs(imbalance)
                    smart_money_indicators['sell_pressure'] = True
        
        # Analyze recent trades for momentum
        if trades and len(trades) > 10:
            recent_trades = trades[-20:]
            buy_volume = sum(t.quantity for t in recent_trades if t.side == 'buy')
            sell_volume = sum(t.quantity for t in recent_trades if t.side == 'sell')
            
            if buy_volume > sell_volume * 1.3 and breakout_above:
                causes.append("Recent trades show strong buying momentum")
                smart_money_indicators['trade_momentum'] = 'bullish'
            elif sell_volume > buy_volume * 1.3 and breakout_below:
                causes.append("Recent trades show strong selling momentum")
                smart_money_indicators['trade_momentum'] = 'bearish'
        
        # Calculate confidence
        confidence = self._calculate_confidence(factors)
        
        # Boost confidence if volume confirmed
        if volume_confirmed:
            confidence = min(confidence * 1.1, 100)
        
        if confidence < self.min_confidence * 100:
            return None
        
        # Determine market behavior
        market_behavior = MarketBehavior.BREAKOUT
        
        # Find historical patterns
        historical_patterns = self._find_historical_patterns(
            symbol,
            {
                'breakout_type': 'above' if breakout_above else 'below',
                'range_size_pct': (range_size / support) * 100,
                'volume_ratio': ticker.volume_24h / avg_volume if avg_volume > 0 else 1
            }
        )
        
        # Generate intelligence
        intelligence = self._generate_signal_intelligence(
            signal_type=signal_type,
            causes=causes,
            confidence=confidence,
            market_behavior=market_behavior,
            historical_patterns=historical_patterns,
            smart_money_indicators=smart_money_indicators
        )
        
        # Create signal
        signal = Signal(
            id=str(uuid.uuid4()),
            type=signal_type,
            symbol=symbol,
            exchange=exchange,
            price=current_price,
            intelligence=intelligence
        )
        
        return signal
