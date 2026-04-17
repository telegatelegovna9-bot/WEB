from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Exchange(str, Enum):
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
    ACCUMULATION = "accumulation"
    DISTRIBUTION = "distribution"
    ORDER_WALL = "order_wall"
    LISTING = "listing"
    PATTERN = "pattern"


class MarketBehavior(str, Enum):
    SMART_MONEY_ACCUMULATION = "smart_money_accumulation"
    SMART_MONEY_DISTRIBUTION = "smart_money_distribution"
    RETAIL_FOMO = "retail_fomo"
    MANIPULATION = "manipulation"
    BREAKOUT = "breakout"
    CONSOLIDATION = "consolidation"


class OrderBookLevel(BaseModel):
    price: float
    amount: float
    total: float = 0.0


class TickerData(BaseModel):
    symbol: str
    exchange: Exchange
    price: float
    volume_24h: float
    price_change_24h: float
    price_change_percent_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OrderBookData(BaseModel):
    symbol: str
    exchange: Exchange
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TradeData(BaseModel):
    symbol: str
    exchange: Exchange
    price: float
    amount: float
    side: str  # buy or sell
    timestamp: datetime


class SignalReason(BaseModel):
    type: str
    description: str
    value: Optional[float] = None
    impact: float = 1.0  # 0-1 scale


class HistoricalAnalogy(BaseModel):
    date: datetime
    symbol: str
    outcome: str
    price_change_percent: float
    similarity_score: float


class SignalIntelligence(BaseModel):
    reasons: List[SignalReason]
    market_behavior: MarketBehavior
    probability_score: float  # 0-100
    historical_analogies: List[HistoricalAnalogy] = []
    confidence_level: str  # low, medium, high, very_high

    def get_confidence_level(self, score: float) -> str:
        if score >= 80:
            return "very_high"
        elif score >= 65:
            return "high"
        elif score >= 45:
            return "medium"
        else:
            return "low"


class Signal(BaseModel):
    id: str
    type: SignalType
    symbol: str
    exchange: Exchange
    price: float
    price_change_percent: float
    volume_change_percent: float
    intelligence: SignalIntelligence
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_active: bool = True

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StrategyConfig(BaseModel):
    name: str
    enabled: bool
    parameters: Dict[str, Any] = {}


class UserSettings(BaseModel):
    telegram_enabled: bool = False
    telegram_chat_id: Optional[str] = None
    min_probability_score: float = 50.0
    exchanges: List[Exchange] = [
        Exchange.BINANCE, Exchange.OKX, Exchange.BYBIT
    ]
    signal_types: List[SignalType] = [
        SignalType.PUMP, SignalType.DUMP, SignalType.BREAKOUT
    ]


class DashboardWidget(BaseModel):
    id: str
    type: str
    position: Dict[str, int]
    settings: Dict[str, Any] = {}


class DashboardConfig(BaseModel):
    user_id: str
    widgets: List[DashboardWidget]
    layout: str = "grid"
