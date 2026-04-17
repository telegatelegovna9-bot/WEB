"""
CryptoMind AI - Database Models and Initialization
PostgreSQL + TimescaleDB for time-series data
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from datetime import datetime
import redis.asyncio as redis

from config import settings

# SQLAlchemy Base
Base = declarative_base()

# Async engine
engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class SignalModel(Base):
    """Signal database model"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(String(64), unique=True, index=True)
    signal_type = Column(String(32), index=True)  # pump, dump, volume_spike, order_book_wall
    symbol = Column(String(32), index=True)  # BTCUSDT
    exchange = Column(String(32), index=True)  # binance, okx, bybit
    price = Column(Float)
    price_change_percent = Column(Float)
    volume = Column(Float)
    volume_change_percent = Column(Float)
    confidence_score = Column(Float)  # 0-100
    explanation = Column(JSON)  # {reasons, market_behavior, smart_money_activity}
    historical_analogies = Column(JSON)  # List of similar historical signals
    metadata = Column(JSON)  # Additional data
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HistoricalPattern(Base):
    """Historical pattern storage for analogy matching"""
    __tablename__ = "historical_patterns"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_id = Column(String(64), unique=True)
    symbol = Column(String(32), index=True)
    pattern_type = Column(String(32))  # accumulation, distribution, breakout, manipulation
    features = Column(JSON)  # Pattern features for ML matching
    outcome = Column(String(32))  # success, failure, neutral
    price_change_after = Column(Float)  # Price change % after pattern
    timeframe = Column(String(16))  # 1m, 5m, 15m, 1h, 4h
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized")


async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


# Redis client (initialized in main.py)
redis_client: redis.Redis = None


async def get_redis() -> redis.Redis:
    """Get Redis client"""
    return redis_client
