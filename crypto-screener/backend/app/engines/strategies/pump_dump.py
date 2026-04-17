import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from .base import BaseStrategy
from ...models.schemas import Signal, TickerData, OrderBook, Trade
from ...core.enums import SignalType, MarketBehavior, Exchange


class PumpDumpStrategy(BaseStrategy):
    """Detect pump and dump patterns based on price and volume spikes"""
    
    def __init__(self, config: Dict[str, Any] = None):
        default_config = {
            'name': 'pump_dump_detector',
            'enabled': True,
            'min_confidence': 0.6,
            'price_change_threshold': 5.0,  # %
            'volume_ratio_threshold': 3.0,
            'acceleration_threshold': 2.0
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
        """Analyze for pump/dump patterns"""
        
        if not ticker:
            return None
            
        causes = []
        factors = {}
        smart_money_indicators = {}
        
        # Check price change
        price_change_pct = ticker.price_change_percent_24h
        if abs(price_change_pct) >= self.config['price_change_threshold']:
            direction = "pump" if price_change_pct > 0 else "dump"
            causes.append(f"Price {direction}: {price_change_pct:.2f}% in 24h")
            factors['price_movement'] = min(abs(price_change_pct) / 10, 1.0)
        
        # Check volume spike
        avg_volume = historical_data.get('avg_volume', 0) if historical_data else 0
        if avg_volume > 0:
            volume_ratio = ticker.volume_24h / avg_volume
            if volume_ratio >= self.config['volume_ratio_threshold']:
                causes.append(f"Volume spike: {volume_ratio:.2f}x average")
                factors['volume_spike'] = min(volume_ratio / 5, 1.0)
                
                # Smart money indicator
                if volume_ratio > 5 and abs(price_change_pct) > 5:
                    smart_money_indicators['unusual_activity'] = True
                    smart_money_indicators['volume_anomaly'] = volume_ratio
        
        # Analyze trades for large orders
        if trades:
            large_trades = [t for t in trades if t.quantity * t.price > 10000]
            if large_trades:
                buy_large = sum(1 for t in large_trades if t.side == 'buy')
                sell_large = len(large_trades) - buy_large
                
                if buy_large > sell_large * 2:
                    causes.append("Large buy orders detected")
                    smart_money_indicators['large_buyers'] = buy_large
                    factors['smart_money'] = 0.8
                elif sell_large > buy_large * 2:
                    causes.append("Large sell orders detected")
                    smart_money_indicators['large_sellers'] = sell_large
                    factors['smart_money'] = 0.8
        
        # Check order book imbalance
        if orderbook:
            bid_volume = sum(b.quantity for b in orderbook.bids[:10])
            ask_volume = sum(a.quantity for a in orderbook.asks[:10])
            
            if bid_volume > 0 and ask_volume > 0:
                imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
                
                if imbalance > 0.3:
                    causes.append("Order book shows strong buy pressure")
                    factors['orderbook_imbalance'] = imbalance
                elif imbalance < -0.3:
                    causes.append("Order book shows strong sell pressure")
                    factors['orderbook_imbalance'] = abs(imbalance)
        
        # Determine signal type
        if not causes or price_change_pct == 0:
            return None
            
        signal_type = SignalType.PUMP if price_change_pct > 0 else SignalType.DUMP
        
        # Calculate confidence
        confidence = self._calculate_confidence(factors)
        
        if confidence < self.min_confidence * 100:
            return None
        
        # Determine market behavior
        volume_ratio = (ticker.volume_24h / avg_volume) if avg_volume > 0 else 1
        orderbook_imbalance = factors.get('orderbook_imbalance', 0)
        
        market_behavior = self._determine_market_behavior(
            price_change_pct,
            volume_ratio,
            orderbook_imbalance
        )
        
        # Find historical patterns
        historical_patterns = self._find_historical_patterns(
            symbol,
            {'price_change': price_change_pct, 'volume_ratio': volume_ratio}
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
            price=ticker.price,
            intelligence=intelligence
        )
        
        return signal
