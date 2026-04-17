from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .enums import Exchange, SignalType, MarketBehavior, Timeframe


class TickerData(BaseModel):
    """Normalized ticker data from exchanges"""
    symbol: str
    exchange: Exchange
    price: float
    volume_24h: float
    price_change_24h: float
    price_change_percent_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OrderBookEntry(BaseModel):
    """Single order book entry"""
    price: float
    quantity: float
    total: Optional[float] = None


class OrderBook(BaseModel):
    """Normalized order book data"""
    symbol: str
    exchange: Exchange
    bids: List[OrderBookEntry]
    asks: List[OrderBookEntry]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Trade(BaseModel):
    """Normalized trade data"""
    symbol: str
    exchange: Exchange
    price: float
    quantity: float
    side: str  # 'buy' or 'sell'
    timestamp: datetime


class HistoricalPattern(BaseModel):
    """Historical pattern match result"""
    pattern_id: str
    similarity_score: float
    date: datetime
    outcome: str
    outcome_percent: float
    days_to_outcome: int


class SignalIntelligence(BaseModel):
    """Detailed signal explanation and analysis"""
    causes: List[str] = Field(description="Reasons for this signal")
    market_behavior: MarketBehavior
    confidence_score: float = Field(ge=0, le=100, description="Probability score 0-100%")
    historical_patterns: List[HistoricalPattern] = Field(default_factory=list)
    smart_money_indicators: Dict[str, Any] = Field(default_factory=dict)
    risk_level: str = Field(default="medium", description="low/medium/high")
    recommended_action: Optional[str] = None


class Signal(BaseModel):
    """Complete signal with intelligence"""
    id: str
    type: SignalType
    symbol: str
    exchange: Exchange
    price: float
    intelligence: SignalIntelligence
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StrategyConfig(BaseModel):
    """Strategy configuration"""
    name: str
    enabled: bool = True
    parameters: Dict[str, Any] = Field(default_factory=dict)
    min_confidence: float = 0.6


class UserSettings(BaseModel):
    """User notification settings"""
    telegram_enabled: bool = False
    telegram_chat_id: Optional[str] = None
    min_confidence: float = 0.7
    enabled_exchanges: List[Exchange] = Field(default_factory=lambda: list(Exchange))
    enabled_signal_types: List[SignalType] = Field(default_factory=lambda: list(SignalType))
    cooldown_minutes: int = 5
