from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SignalType(str, Enum):
    pump = "pump"
    dump = "dump"
    order_book_density = "order_book_density"
    listing = "listing"
    pattern = "pattern"


class MarketBehavior(str, Enum):
    accumulation = "Accumulation"
    distribution = "Distribution"
    breakout = "Breakout"
    manipulation = "Manipulation"


class MarketTick(BaseModel):
    exchange: str
    symbol: str
    price: float
    volume: float
    ts: datetime


class DetectorEvent(BaseModel):
    signal_type: SignalType
    symbol: str
    exchange: str
    severity: float = Field(ge=0, le=1)
    reasons: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)


class HistoricalMatch(BaseModel):
    id: str
    similarity: float = Field(ge=0, le=1)
    result_pct: float
    horizon_hours: int


class Signal(BaseModel):
    id: str
    signal_type: SignalType
    symbol: str
    exchange: str
    created_at: datetime
    confidence: int = Field(ge=0, le=100)
    behavior: MarketBehavior
    reasons: list[str]
    historical_matches: list[HistoricalMatch]
    metadata: dict[str, Any] = Field(default_factory=dict)
