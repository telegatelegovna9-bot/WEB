from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.models.schemas import (
    Signal, SignalType, SignalExplanation, MarketBehavior,
    HistoricalAnalogy, Exchange, OrderBook
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class OrderBookAnalyzer:
    """Analyzes order book for walls and significant changes"""
    
    def __init__(self):
        self.orderbook_history: Dict[str, List[OrderBook]] = {}
        self.wall_threshold_usd = settings.ORDER_BOOK_WALL_THRESHOLD
    
    def update(self, symbol: str, orderbook: OrderBook):
        """Store order book snapshot"""
        if symbol not in self.orderbook_history:
            self.orderbook_history[symbol] = []
        
        self.orderbook_history[symbol].append(orderbook)
        
        # Keep last 100 snapshots
        if len(self.orderbook_history[symbol]) > 100:
            self.orderbook_history[symbol] = self.orderbook_history[symbol][-100:]
    
    def detect_walls(self, symbol: str) -> List[Dict[str, Any]]:
        """Detect significant buy/sell walls"""
        if symbol not in self.orderbook_history or not self.orderbook_history[symbol]:
            return []
        
        current_ob = self.orderbook_history[symbol][-1]
        walls = []
        
        # Check bids for buy walls
        for bid in current_ob.bids:
            if bid['total'] >= self.wall_threshold_usd:
                walls.append({
                    'type': 'buy_wall',
                    'price': bid['price'],
                    'amount': bid['amount'],
                    'total_usd': bid['total'],
                    'strength': 'strong' if bid['total'] >= self.wall_threshold_usd * 2 else 'moderate'
                })
        
        # Check asks for sell walls
        for ask in current_ob.asks:
            if ask['total'] >= self.wall_threshold_usd:
                walls.append({
                    'type': 'sell_wall',
                    'price': ask['price'],
                    'amount': ask['amount'],
                    'total_usd': ask['total'],
                    'strength': 'strong' if ask['total'] >= self.wall_threshold_usd * 2 else 'moderate'
                })
        
        return walls
    
    def detect_changes(self, symbol: str) -> Dict[str, Any]:
        """Detect significant changes in order book"""
        if symbol not in self.orderbook_history or len(self.orderbook_history[symbol]) < 2:
            return {}
        
        current_ob = self.orderbook_history[symbol][-1]
        previous_ob = self.orderbook_history[symbol][-2]
        
        changes = {
            'bid_density_change': 0,
            'ask_density_change': 0,
            'spread_change': 0,
            'walls_appeared': [],
            'walls_disappeared': [],
        }
        
        # Calculate total bid/ask density
        current_bid_density = sum(b['total'] for b in current_ob.bids)
        previous_bid_density = sum(b['total'] for b in previous_ob.bids)
        current_ask_density = sum(a['total'] for a in current_ob.asks)
        previous_ask_density = sum(a['total'] for a in previous_ob.asks)
        
        if previous_bid_density > 0:
            changes['bid_density_change'] = ((current_bid_density - previous_bid_density) / previous_bid_density) * 100
        
        if previous_ask_density > 0:
            changes['ask_density_change'] = ((current_ask_density - previous_ask_density) / previous_ask_density) * 100
        
        changes['spread_change'] = current_ob.spread - previous_ob.spread
        
        # Detect wall appearances/disappearances
        current_walls = self.detect_walls(symbol)
        previous_walls = self._get_walls_at(symbol, -2)
        
        current_wall_prices = {w['price'] for w in current_walls}
        previous_wall_prices = {w['price'] for w in previous_walls}
        
        changes['walls_appeared'] = list(current_wall_prices - previous_wall_prices)
        changes['walls_disappeared'] = list(previous_wall_prices - current_wall_prices)
        
        return changes
    
    def _get_walls_at(self, symbol: str, index: int) -> List[Dict[str, Any]]:
        """Get walls at specific historical point"""
        if symbol not in self.orderbook_history:
            return []
        
        idx = index if index >= 0 else len(self.orderbook_history[symbol]) + index
        
        if idx < 0 or idx >= len(self.orderbook_history[symbol]):
            return []
        
        ob = self.orderbook_history[symbol][idx]
        walls = []
        
        for bid in ob.bids:
            if bid['total'] >= self.wall_threshold_usd:
                walls.append({'price': bid['price'], 'type': 'buy'})
        
        for ask in ob.asks:
            if ask['total'] >= self.wall_threshold_usd:
                walls.append({'price': ask['price'], 'type': 'sell'})
        
        return walls


class OrderBookDetector:
    """Detects signals from order book analysis"""
    
    def __init__(self):
        self.analyzer = OrderBookAnalyzer()
    
    def update(self, symbol: str, orderbook: OrderBook):
        """Update with new order book data"""
        self.analyzer.update(symbol, orderbook)
    
    def detect(self, symbol: str) -> Optional[Signal]:
        """Detect order book based signals"""
        walls = self.analyzer.detect_walls(symbol)
        changes = self.analyzer.detect_changes(symbol)
        
        if not walls and not changes:
            return None
        
        # Determine signal type and generate explanation
        reasons = []
        market_behavior = MarketBehavior.CONSOLIDATION
        confidence = 50.0
        
        # Analyze walls
        buy_walls = [w for w in walls if w['type'] == 'buy_wall']
        sell_walls = [w for w in walls if w['type'] == 'sell_wall']
        
        if buy_walls:
            strongest_buy = max(buy_walls, key=lambda x: x['total_usd'])
            reasons.append(f"Large buy wall detected at ${strongest_buy['price']:,.2f} (${strongest_buy['total_usd']:,.0f})")
            
            if strongest_buy['strength'] == 'strong':
                confidence += 15
                market_behavior = MarketBehavior.ACCUMULATION
        
        if sell_walls:
            strongest_sell = max(sell_walls, key=lambda x: x['total_usd'])
            reasons.append(f"Large sell wall detected at ${strongest_sell['price']:,.2f} (${strongest_sell['total_usd']:,.0f})")
            
            if strongest_sell['strength'] == 'strong':
                confidence += 15
                market_behavior = MarketBehavior.DISTRIBUTION
        
        # Analyze changes
        if changes:
            if changes.get('bid_density_change', 0) > 50:
                reasons.append("Bid density increased significantly (+{:.0f}%)".format(changes['bid_density_change']))
                confidence += 10
            
            if changes.get('ask_density_change', 0) < -50:
                reasons.append("Ask density decreased significantly ({:.0f}%)".format(changes['ask_density_change']))
                confidence += 10
                market_behavior = MarketBehavior.BREAKOUT
            
            if changes.get('walls_disappeared'):
                reasons.append(f"Sell walls removed at: {[f'${p:,.0f}' for p in changes['walls_disappeared']]}")
                confidence += 15
                market_behavior = MarketBehavior.BREAKOUT
            
            if changes.get('walls_appeared'):
                reasons.append(f"New walls appeared at: {[f'${p:,.0f}' for p in changes['walls_appeared']]}")
        
        if not reasons:
            return None
        
        # Get current price from order book
        if symbol in self.analyzer.orderbook_history and self.analyzer.orderbook_history[symbol]:
            current_price = self.analyzer.orderbook_history[symbol][-1].bids[0]['price']
        else:
            current_price = 0
        
        return Signal(
            signal_type=SignalType.ORDERBOOK_WALL,
            symbol=symbol,
            exchange=Exchange.BINANCE,
            price=current_price,
            price_change_percent=0.0,
            volume_change_percent=0.0,
            confidence_score=min(95.0, confidence),
            explanation=SignalExplanation(
                reasons=reasons,
                market_behavior=market_behavior,
                smart_money_activity=any(w['strength'] == 'strong' for w in walls),
                unusual_volume=False,
                orderbook_changes=[
                    f"Bid density: {changes.get('bid_density_change', 0):+.0f}%",
                    f"Ask density: {changes.get('ask_density_change', 0):+.0f}%",
                ] if changes else []
            ),
            historical_analogies=[],
            timestamp=datetime.utcnow(),
            metadata={
                'walls': walls,
                'changes': changes
            }
        )
