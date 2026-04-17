"""
CryptoMind AI - Order Book Detector
Detects large walls and order book anomalies
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import deque

from models.schemas import OrderBookData, SignalType, MarketBehavior
from config import settings


class OrderBookDetector:
    """Detects order book patterns and large walls"""
    
    def __init__(self):
        self.orderbook_history: Dict[str, deque] = {}
        self.wall_cooldown: Dict[str, datetime] = {}
        self.cooldown_period = timedelta(minutes=2)
        self.wall_threshold_usd = settings.ORDER_BOOK_WALL_SIZE
    
    def _update_history(self, symbol: str, bids: List[List[float]], asks: List[List[float]]):
        """Update order book history"""
        now = datetime.utcnow()
        
        if symbol not in self.orderbook_history:
            self.orderbook_history[symbol] = deque(maxlen=20)
        
        self.orderbook_history[symbol].append({
            "timestamp": now,
            "bids": bids[:10],  # Keep top 10 levels
            "asks": asks[:10]
        })
    
    def _find_walls(self, book_side: List[List[float]], current_price: float, is_bid: bool) -> List[dict]:
        """Find significant walls in order book"""
        walls = []
        
        for price, amount in book_side:
            value_usd = price * amount
            
            if value_usd >= self.wall_threshold_usd:
                distance_percent = abs(price - current_price) / current_price * 100
                
                walls.append({
                    "price": price,
                    "amount": amount,
                    "value_usd": value_usd,
                    "distance_percent": distance_percent,
                    "type": "bid" if is_bid else "ask"
                })
        
        return walls
    
    def _calculate_imbalance(self, bids: List[List[float]], asks: List[List[float]], current_price: float) -> float:
        """Calculate buy/sell pressure imbalance (-1 to 1)"""
        bid_volume = sum(amount for price, amount in bids if price >= current_price * 0.99)
        ask_volume = sum(amount for price, amount in asks if price <= current_price * 1.01)
        
        total = bid_volume + ask_volume
        if total == 0:
            return 0.0
        
        return (bid_volume - ask_volume) / total
    
    def _is_in_cooldown(self, symbol: str) -> bool:
        """Check cooldown"""
        if symbol not in self.wall_cooldown:
            return False
        return datetime.utcnow() - self.wall_cooldown[symbol] < self.cooldown_period
    
    def _set_cooldown(self, symbol: str):
        """Set cooldown"""
        self.wall_cooldown[symbol] = datetime.utcnow()
    
    async def detect(self, orderbook: OrderBookData, current_price: float) -> Optional[dict]:
        """Detect order book anomalies"""
        symbol = orderbook.symbol
        
        # Update history
        self._update_history(symbol, orderbook.bids, orderbook.asks)
        
        # Check cooldown
        if self._is_in_cooldown(symbol):
            return None
        
        # Find walls
        bid_walls = self._find_walls(orderbook.bids, current_price, is_bid=True)
        ask_walls = self._find_walls(orderbook.asks, current_price, is_bid=False)
        
        # Calculate imbalance
        imbalance = self._calculate_imbalance(orderbook.bids, orderbook.asks, current_price)
        
        # Check for significant signals
        signal_detected = False
        reasons = []
        market_behavior = MarketBehavior.NORMAL
        
        if bid_walls:
            largest_bid = max(bid_walls, key=lambda x: x["value_usd"])
            reasons.append(f"Large buy wall at ${largest_bid['price']:,.2f} (${largest_bid['value_usd']:,.0f})")
            signal_detected = True
            
            if largest_bid["distance_percent"] < 1:
                market_behavior = MarketBehavior.ACCUMULATION
                reasons.append("Buy wall very close to current price - strong support")
        
        if ask_walls:
            largest_ask = max(ask_walls, key=lambda x: x["value_usd"])
            reasons.append(f"Large sell wall at ${largest_ask['price']:,.2f} (${largest_ask['value_usd']:,.0f})")
            signal_detected = True
            
            if largest_ask["distance_percent"] < 1:
                if market_behavior == MarketBehavior.ACCUMULATION:
                    market_behavior = MarketBehavior.NORMAL
                    reasons.append("Both buy and sell walls present - consolidation")
                else:
                    market_behavior = MarketBehavior.DISTRIBUTION
                    reasons.append("Sell wall very close to current price - resistance")
        
        if abs(imbalance) > 0.5:
            if imbalance > 0:
                reasons.append(f"Strong buy pressure detected (imbalance: {imbalance:.2f})")
            else:
                reasons.append(f"Strong sell pressure detected (imbalance: {imbalance:.2f})")
            signal_detected = True
        
        if not signal_detected:
            return None
        
        # Calculate confidence
        confidence = 50
        if bid_walls or ask_walls:
            confidence += 20
        if abs(imbalance) > 0.5:
            confidence += 15
        if abs(imbalance) > 0.7:
            confidence += 15
        
        confidence = min(100, confidence)
        
        # Set cooldown
        self._set_cooldown(symbol)
        
        # Build order book changes description
        ob_changes = []
        if bid_walls:
            ob_changes.append(f"{len(bid_walls)} buy wall(s) detected")
        if ask_walls:
            ob_changes.append(f"{len(ask_walls)} sell wall(s) detected")
        if abs(imbalance) > 0.5:
            ob_changes.append("Significant order flow imbalance")
        
        return {
            "signal_type": SignalType.ORDER_BOOK_WALL.value,
            "symbol": symbol,
            "exchange": orderbook.exchange,
            "price": current_price,
            "price_change_percent": 0,
            "volume": 0,
            "volume_change_percent": 0,
            "confidence_score": round(confidence, 2),
            "explanation": {
                "reasons": reasons,
                "market_behavior": market_behavior.value,
                "smart_money_activity": len(bid_walls) > 0 or len(ask_walls) > 0,
                "large_orders_detected": True,
                "order_book_changes": ob_changes
            },
            "historical_analogies": [],
            "metadata": {
                "detector": "orderbook",
                "bid_walls": bid_walls,
                "ask_walls": ask_walls,
                "imbalance": imbalance
            }
        }
