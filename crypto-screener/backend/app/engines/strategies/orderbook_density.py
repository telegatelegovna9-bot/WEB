import uuid
from typing import Optional, List, Dict, Any
from .base import BaseStrategy
from ...models.schemas import Signal, SignalIntelligence, OrderBook, TickerData, Trade, HistoricalPattern
from ...core.enums import SignalType, MarketBehavior, Exchange


class OrderBookDensityStrategy(BaseStrategy):
    """Detect large limit orders and walls in order book"""
    
    def __init__(self, config: Dict[str, Any] = None):
        default_config = {
            'name': 'orderbook_density_detector',
            'enabled': True,
            'min_confidence': 0.6,
            'wall_threshold_percent': 5.0,  # % of total book volume
            'min_wall_value_usd': 50000,
            'depth_levels': 20
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
        """Analyze order book for walls and density anomalies"""
        
        if not orderbook:
            return None
            
        causes = []
        factors = {}
        smart_money_indicators = {}
        
        # Calculate total book volume
        bid_volume = sum(b.quantity for b in orderbook.bids)
        ask_volume = sum(a.quantity for a in orderbook.asks)
        total_volume = bid_volume + ask_volume
        
        if total_volume == 0:
            return None
        
        # Detect buy walls
        buy_walls = []
        for bid in orderbook.bids:
            if bid.total:
                wall_percent = (bid.quantity / total_volume) * 100
                wall_value = bid.quantity * bid.price
                
                if wall_percent >= self.config['wall_threshold_percent'] or \
                   wall_value >= self.config['min_wall_value_usd']:
                    buy_walls.append({
                        'price': bid.price,
                        'quantity': bid.quantity,
                        'value': wall_value,
                        'percent': wall_percent
                    })
        
        # Detect sell walls
        sell_walls = []
        for ask in orderbook.asks:
            if ask.total:
                wall_percent = (ask.quantity / total_volume) * 100
                wall_value = ask.quantity * ask.price
                
                if wall_percent >= self.config['wall_threshold_percent'] or \
                   wall_value >= self.config['min_wall_value_usd']:
                    sell_walls.append({
                        'price': ask.price,
                        'quantity': ask.quantity,
                        'value': wall_value,
                        'percent': wall_percent
                    })
        
        # Analyze walls
        if buy_walls:
            largest_buy = max(buy_walls, key=lambda x: x['value'])
            causes.append(f"Large buy wall detected: ${largest_buy['value']:,.0f} at ${largest_buy['price']:,.2f}")
            causes.append(f"Buy wall represents {largest_buy['percent']:.2f}% of order book")
            factors['buy_wall'] = min(largest_buy['percent'] / 10, 1.0)
            smart_money_indicators['buy_wall_size'] = largest_buy['value']
            
        if sell_walls:
            largest_sell = max(sell_walls, key=lambda x: x['value'])
            causes.append(f"Large sell wall detected: ${largest_sell['value']:,.0f} at ${largest_sell['price']:,.2f}")
            causes.append(f"Sell wall represents {largest_sell['percent']:.2f}% of order book")
            factors['sell_wall'] = min(largest_sell['percent'] / 10, 1.0)
            smart_money_indicators['sell_wall_size'] = largest_sell['value']
        
        # Check for wall imbalance
        if buy_walls and sell_walls:
            buy_wall_total = sum(w['value'] for w in buy_walls)
            sell_wall_total = sum(w['value'] for w in sell_walls)
            
            if buy_wall_total > sell_wall_total * 1.5:
                causes.append("Buy walls significantly larger than sell walls")
                factors['wall_imbalance'] = 0.8
            elif sell_wall_total > buy_wall_total * 1.5:
                causes.append("Sell walls significantly larger than buy walls")
                factors['wall_imbalance'] = 0.8
        
        # Check for sudden changes (if we have historical data)
        if historical_data and 'previous_book' in historical_data:
            prev_bid = historical_data['previous_book'].get('bid_volume', 0)
            prev_ask = historical_data['previous_book'].get('ask_volume', 0)
            
            if prev_bid > 0 and bid_volume < prev_bid * 0.5:
                causes.append("Buy side liquidity decreased significantly")
                factors['liquidity_change'] = 0.7
            elif prev_ask > 0 and ask_volume < prev_ask * 0.5:
                causes.append("Sell side liquidity decreased significantly")
                factors['liquidity_change'] = 0.7
        
        if not causes:
            return None
        
        # Calculate confidence
        confidence = self._calculate_confidence(factors)
        
        if confidence < self.min_confidence * 100:
            return None
        
        # Determine market behavior based on walls
        current_price = ticker.price if ticker else orderbook.bids[0].price
        
        if buy_walls and not sell_walls:
            # Large buy support - potential accumulation
            market_behavior = MarketBehavior.ACCUMULATION
        elif sell_walls and not buy_walls:
            # Large sell pressure - potential distribution
            market_behavior = MarketBehavior.DISTRIBUTION
        else:
            market_behavior = MarketBehavior.NORMAL
        
        # Generate intelligence
        intelligence = self._generate_signal_intelligence(
            signal_type=SignalType.ORDER_BOOK_WALL,
            causes=causes,
            confidence=confidence,
            market_behavior=market_behavior,
            historical_patterns=[],
            smart_money_indicators=smart_money_indicators
        )
        
        # Create signal
        signal = Signal(
            id=str(uuid.uuid4()),
            type=SignalType.ORDER_BOOK_WALL,
            symbol=symbol,
            exchange=exchange,
            price=current_price,
            intelligence=intelligence
        )
        
        return signal
