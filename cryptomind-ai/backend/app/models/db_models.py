from sqlalchemy import Column, String, Float, DateTime, Boolean, JSON, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class SignalModel(Base):
    __tablename__ = "signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    signal_type = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    price_change_percent = Column(Float, nullable=False)
    volume_change_percent = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    
    # Explanation stored as JSON
    explanation = Column(JSON, nullable=False)
    
    # Historical analogies stored as JSON
    historical_analogies = Column(JSON, default=list)
    
    # Metadata
    metadata_json = Column("metadata", JSON, default=dict)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    was_successful = Column(Boolean, nullable=True)  # Set after outcome is known
    
    # Indexes for performance
    __table_args__ = (
        # Composite index for querying active signals by type
        ('signal_type', 'is_active', 'timestamp'),
    )


class TickerModel(Base):
    __tablename__ = "tickers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    volume_24h = Column(Float, default=0.0)
    price_change_24h = Column(Float, default=0.0)
    price_change_percent_24h = Column(Float, default=0.0)
    high_24h = Column(Float, default=0.0)
    low_24h = Column(Float, default=0.0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # TimescaleDB hypertable will be created via migration
    __table_args__ = (
        # Unique constraint for upserts
        ('symbol', 'exchange'),
    )


class OrderBookSnapshot(Base):
    __tablename__ = "orderbook_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(20), nullable=False, index=True)
    
    # Store bids and asks as JSON for flexibility
    bids = Column(JSON, nullable=False)
    asks = Column(JSON, nullable=False)
    
    spread = Column(Float, nullable=False)
    spread_percent = Column(Float, nullable=False)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class PatternHistory(Base):
    """Historical patterns for analogy matching"""
    __tablename__ = "pattern_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(20), nullable=False)
    pattern_type = Column(String(50), nullable=False, index=True)
    
    # Pattern characteristics (for similarity matching)
    characteristics = Column(JSON, nullable=False)
    
    # Outcome
    outcome = Column(String(20), nullable=True)  # success/failure/neutral
    price_change_after = Column(Float, nullable=True)
    time_frame = Column(String(10), nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Notification settings
    notification_channels = Column(JSON, default=list)
    min_confidence = Column(Float, default=50.0)
    signal_types_filter = Column(JSON, default=list)
    exchanges_filter = Column(JSON, default=list)
    symbols_filter = Column(JSON, default=list)
    
    # Dashboard config
    dashboard_config = Column(JSON, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SignalAccuracy(Base):
    """Track signal accuracy for analytics"""
    __tablename__ = "signal_accuracy"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    signal_id = Column(UUID(as_uuid=True), ForeignKey("signals.id"), nullable=False, index=True)
    
    # Result tracking
    was_profitable = Column(Boolean, nullable=True)
    max_price_change = Column(Float, nullable=True)
    min_price_change = Column(Float, nullable=True)
    final_price_change = Column(Float, nullable=True)
    
    # Time to outcome
    time_to_peak = Column(Integer, nullable=True)  # in minutes
    
    evaluated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
