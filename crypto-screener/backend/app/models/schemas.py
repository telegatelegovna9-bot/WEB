from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class ExchangeType(str, Enum):
    BINANCE = "binance"
    OKX = "okx"
    BYBIT = "bybit"
    MEXC = "mexc"
    GATE = "gate"
    BITGET = "bitget"

class SignalType(str, Enum):
    PUMP = "pump"
    DUMP = "dump"
    BREAKOUT = "breakout"
    CONSOLIDATION = "consolidation"
    WALL_DETECTED = "wall_detected"
    WALL_REMOVED = "wall_removed"
    LISTING = "listing"
    VOLUME_SPIKE = "volume_spike"

class MarketBehavior(str, Enum):
    SMART_MONEY_ACCUMULATION = "smart_money_accumulation"
    DISTRIBUTION = "distribution"
    FOMO = "fomo"
    MANIPULATION = "manipulation"
    BREAKOUT_CONFIRMED = "breakout_confirmed"
    FALSE_BREAKOUT = "false_breakout"

class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class Reason(BaseModel):
    description: str
    weight: float = 1.0
    type: str = "general"

class HistoricalAnalogy(BaseModel):
    date: datetime
    symbol: str
    outcome: str
    price_change_percent: float
    similarity_score: float

class SignalIntelligence(BaseModel):
    reasons: List[Reason]
    market_behavior: MarketBehavior
    probability_score: float = Field(ge=0, le=100)
    confidence_level: ConfidenceLevel
    historical_analogies: List[HistoricalAnalogy] = []
    explanation: str = ""

class TickerData(BaseModel):
    symbol: str
    exchange: ExchangeType
    price: float
    price_change_24h: float = 0.0
    price_change_percent_24h: float = 0.0
    volume_24h: float = 0.0
    quote_volume_24h: float = 0.0
    high_24h: float = 0.0
    low_24h: float = 0.0
    trades_count_24h: int = 0
    bid_price: float = 0.0
    ask_price: float = 0.0
    bid_size: float = 0.0
    ask_size: float = 0.0
    last_update: datetime = Field(default_factory=datetime.utcnow)

class OrderBookLevel(BaseModel):
    price: float
    size: float
    total: float = 0.0

class OrderBook(BaseModel):
    symbol: str
    exchange: ExchangeType
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    wall_detected: bool = False
    wall_type: Optional[str] = None
    wall_price: Optional[float] = None

class Trade(BaseModel):
    symbol: str
    exchange: ExchangeType
    price: float
    size: float
    side: str  # buy or sell
    timestamp: datetime
    is_large: bool = False

class Signal(BaseModel):
    id: str
    type: SignalType
    symbol: str
    exchange: ExchangeType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    price: float
    price_change_percent: float
    volume_change_percent: float
    intelligence: SignalIntelligence
    is_new: bool = True
    tags: List[str] = []

class PatternDetection(BaseModel):
    pattern_type: str  # flag, triangle, head_shoulders, double_top, double_bottom
    symbol: str
    exchange: ExchangeType
    confidence: float
    breakout_level: Optional[float] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    detected_at: datetime = Field(default_factory=datetime.utcnow)

class DensityDetection(BaseModel):
    symbol: str
    exchange: ExchangeType
    density_type: str  # bid_wall, ask_wall, bid_cluster, ask_cluster
    price_level: float
    total_size: float
    order_count: int
    strength: float  # 0-100
    detected_at: datetime = Field(default_factory=datetime.utcnow)

class ScreenerStats(BaseModel):
    total_signals: int
    signals_last_hour: int
    active_exchanges: int
    tracked_symbols: int
    top_gainers: List[TickerData]
    top_losers: List[TickerData]
    top_volume: List[TickerData]
    avg_signal_accuracy: float

class FilterParams(BaseModel):
    exchanges: List[ExchangeType] = []
    signal_types: List[SignalType] = []
    min_probability: float = 0.0
    symbols: List[str] = []
    search_query: str = ""
    sort_by: str = "timestamp"
    sort_order: str = "desc"
    limit: int = 50
