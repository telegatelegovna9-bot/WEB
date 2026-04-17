from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SignalType(str, Enum):
    PUMP = "pump"
    DUMP = "dump"
    ORDERBOOK_WALL = "orderbook_wall"
    LISTING = "listing"
    PATTERN_BREAKOUT = "pattern_breakout"
    PATTERN_CONSOLIDATION = "pattern_consolidation"
    VOLUME_SPIKE = "volume_spike"


class MarketBehavior(str, Enum):
    ACCUMULATION = "accumulation"
    DISTRIBUTION = "distribution"
    BREAKOUT = "breakout"
    MANIPULATION = "manipulation"
    CONSOLIDATION = "consolidation"
    TRENDING = "trending"


class Exchange(str, Enum):
    BINANCE = "binance"
    OKX = "okx"
    BYBIT = "bybit"
    MEXC = "mexc"
    GATE = "gate"
    BITGET = "bitget"


# Base Models
class TickerData(BaseModel):
    symbol: str
    exchange: Exchange
    price: float
    volume_24h: float
    price_change_24h: float
    price_change_percent_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime


class OrderBookEntry(BaseModel):
    price: float
    amount: float
    total: float


class OrderBook(BaseModel):
    symbol: str
    exchange: Exchange
    bids: List[OrderBookEntry]
    asks: List[OrderBookEntry]
    timestamp: datetime
    spread: float
    spread_percent: float


class Trade(BaseModel):
    symbol: str
    exchange: Exchange
    price: float
    amount: float
    side: str  # buy/sell
    timestamp: datetime
    trade_id: str


# Signal Models
class SignalExplanation(BaseModel):
    reasons: List[str] = Field(..., description="List of reasons triggering this signal")
    market_behavior: MarketBehavior
    smart_money_activity: bool = False
    unusual_volume: bool = False
    orderbook_changes: List[str] = []


class HistoricalAnalogy(BaseModel):
    date: datetime
    symbol: str
    similarity_score: float  # 0-1
    outcome: str  # "success", "failure", "neutral"
    price_change_after: float  # % change after signal
    time_frame: str  # "1h", "4h", "24h"


class Signal(BaseModel):
    id: Optional[str] = None
    signal_type: SignalType
    symbol: str
    exchange: Exchange
    price: float
    price_change_percent: float
    volume_change_percent: float
    confidence_score: float = Field(..., ge=0, le=100, description="Probability score 0-100%")
    explanation: SignalExplanation
    historical_analogies: List[HistoricalAnalogy] = []
    timestamp: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}

    class Config:
        json_schema_extra = {
            "example": {
                "signal_type": "pump",
                "symbol": "BTCUSDT",
                "exchange": "binance",
                "price": 45000.0,
                "price_change_percent": 5.2,
                "volume_change_percent": 300.0,
                "confidence_score": 68.0,
                "explanation": {
                    "reasons": [
                        "+300% volume spike",
                        "Large buy order detected",
                        "Sell wall removed"
                    ],
                    "market_behavior": "accumulation",
                    "smart_money_activity": True,
                    "unusual_volume": True,
                    "orderbook_changes": ["Sell wall at 45500 removed", "Buy density increased at 44800"]
                },
                "historical_analogies": [
                    {
                        "date": "2024-01-15T10:30:00",
                        "symbol": "BTCUSDT",
                        "similarity_score": 0.92,
                        "outcome": "success",
                        "price_change_after": 12.5,
                        "time_frame": "4h"
                    }
                ]
            }
        }


class SignalStats(BaseModel):
    total_signals: int
    accuracy_rate: float
    win_rate: float
    avg_confidence: float
    signals_by_type: Dict[SignalType, int]
    signals_by_exchange: Dict[Exchange, int]


# Strategy Models
class StrategyConfig(BaseModel):
    name: str
    enabled: bool
    parameters: Dict[str, Any] = {}


class StrategySignal(BaseModel):
    strategy_name: str
    signal: Signal
    priority: int = 1  # 1-5, 5 being highest


# Notification Models
class NotificationChannel(str, Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"
    WEBHOOK = "webhook"


class UserNotificationSettings(BaseModel):
    user_id: str
    channels: List[NotificationChannel]
    min_confidence: float = 50.0
    signal_types: List[SignalType] = []
    exchanges: List[Exchange] = []
    symbols: List[str] = []
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


# Dashboard Models
class DashboardWidget(BaseModel):
    id: str
    type: str
    title: str
    config: Dict[str, Any]
    position: Dict[str, int]  # x, y, w, h
    enabled: bool


class DashboardConfig(BaseModel):
    user_id: str
    name: str
    widgets: List[DashboardWidget]
    is_default: bool = False
