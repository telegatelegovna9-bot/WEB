"""
CryptoMind AI - Pydantic Models and Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SignalType(str, Enum):
    PUMP = "pump"
    DUMP = "dump"
    VOLUME_SPIKE = "volume_spike"
    ORDER_BOOK_WALL = "order_book_wall"
    BREAKOUT = "breakout"
    CONSOLIDATION = "consolidation"
    LISTING = "listing"


class MarketBehavior(str, Enum):
    ACCUMULATION = "accumulation"
    DISTRIBUTION = "distribution"
    BREAKOUT = "breakout"
    MANIPULATION = "manipulation"
    NORMAL = "normal"


class Explanation(BaseModel):
    """Signal explanation model"""
    reasons: List[str] = Field(..., description="Reasons for the signal")
    market_behavior: MarketBehavior = Field(..., description="Type of market behavior")
    smart_money_activity: bool = Field(default=False, description="Smart money detected")
    large_orders_detected: bool = Field(default=False, description="Large orders detected")
    order_book_changes: List[str] = Field(default_factory=list, description="Order book changes")


class HistoricalAnalogy(BaseModel):
    """Historical analogy for pattern matching"""
    similarity_score: float = Field(..., ge=0, le=1, description="Similarity score 0-1")
    outcome: str = Field(..., description="Outcome: success, failure, neutral")
    price_change_after: float = Field(..., description="Price change % after pattern")
    date: Optional[str] = None
    symbol: Optional[str] = None
    timeframe: Optional[str] = None


class Signal(BaseModel):
    """Signal model"""
    signal_id: str
    signal_type: SignalType
    symbol: str
    exchange: str
    price: float
    price_change_percent: float
    volume: float
    volume_change_percent: float
    confidence_score: float = Field(..., ge=0, le=100, description="Confidence score 0-100")
    explanation: Explanation
    historical_analogies: List[HistoricalAnalogy] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True


class SignalResponse(BaseModel):
    """Signal response model for API"""
    signal_id: str
    signal_type: str
    symbol: str
    exchange: str
    price: float
    price_change_percent: float
    volume: float
    volume_change_percent: float
    confidence_score: float
    explanation: Dict[str, Any]
    historical_analogies: List[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TickerData(BaseModel):
    """Normalized ticker data from exchanges"""
    symbol: str
    exchange: str
    price: float
    bid: float
    ask: float
    volume_24h: float
    price_change_24h: float
    price_change_percent_24h: float
    timestamp: datetime


class OrderBookData(BaseModel):
    """Normalized order book data"""
    symbol: str
    exchange: str
    bids: List[List[float]]  # [[price, amount], ...]
    asks: List[List[float]]
    timestamp: datetime


class TradeData(BaseModel):
    """Normalized trade data"""
    symbol: str
    exchange: str
    price: float
    amount: float
    side: str  # buy or sell
    timestamp: datetime
    trade_id: str
