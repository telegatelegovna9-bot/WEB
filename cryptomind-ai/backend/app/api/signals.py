from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.models.schemas import Signal, SignalStats, Exchange, SignalType
from app.models.db_models import SignalModel
from app.core.database import get_db, AsyncSession
from sqlalchemy import select, func

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("", response_model=List[Signal])
async def get_signals(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    signal_type: Optional[SignalType] = None,
    exchange: Optional[Exchange] = None,
    symbol: Optional[str] = None,
    min_confidence: Optional[float] = Query(None, ge=0, le=100),
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Get signals with filtering options"""
    
    # Build query
    query = select(SignalModel)
    
    if active_only:
        query = query.where(SignalModel.is_active == True)
    
    if signal_type:
        query = query.where(SignalModel.signal_type == signal_type.value)
    
    if exchange:
        query = query.where(SignalModel.exchange == exchange.value)
    
    if symbol:
        query = query.where(SignalModel.symbol == symbol.upper())
    
    if min_confidence is not None:
        query = query.where(SignalModel.confidence_score >= min_confidence)
    
    # Order by timestamp descending
    query = query.order_by(SignalModel.timestamp.desc())
    query = query.limit(limit).offset(offset)
    
    # Execute query
    result = await db.execute(query)
    signals = result.scalars().all()
    
    # Convert to response format
    return [
        {
            "id": str(signal.id),
            "signal_type": signal.signal_type,
            "symbol": signal.symbol,
            "exchange": signal.exchange,
            "price": signal.price,
            "price_change_percent": signal.price_change_percent,
            "volume_change_percent": signal.volume_change_percent,
            "confidence_score": signal.confidence_score,
            "explanation": signal.explanation,
            "historical_analogies": signal.historical_analogies,
            "timestamp": signal.timestamp,
        }
        for signal in signals
    ]


@router.get("/stats", response_model=SignalStats)
async def get_signal_stats(
    hours: int = Query(24, ge=1, le=720),
    db: AsyncSession = Depends(get_db),
):
    """Get signal statistics"""
    
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Total signals
    total_query = select(func.count(SignalModel.id)).where(
        SignalModel.timestamp >= since
    )
    result = await db.execute(total_query)
    total_signals = result.scalar() or 0
    
    # Accuracy rate (signals that were successful)
    accuracy_query = select(func.count(SignalModel.id)).where(
        SignalModel.timestamp >= since,
        SignalModel.was_successful == True
    )
    result = await db.execute(accuracy_query)
    successful_signals = result.scalar() or 0
    
    accuracy_rate = (successful_signals / total_signals * 100) if total_signals > 0 else 0.0
    
    # Average confidence
    avg_conf_query = select(func.avg(SignalModel.confidence_score)).where(
        SignalModel.timestamp >= since
    )
    result = await db.execute(avg_conf_query)
    avg_confidence = result.scalar() or 0.0
    
    # Signals by type
    type_query = select(
        SignalModel.signal_type,
        func.count(SignalModel.id)
    ).where(
        SignalModel.timestamp >= since
    ).group_by(SignalModel.signal_type)
    
    result = await db.execute(type_query)
    signals_by_type = {row[0]: row[1] for row in result.all()}
    
    # Signals by exchange
    exchange_query = select(
        SignalModel.exchange,
        func.count(SignalModel.id)
    ).where(
        SignalModel.timestamp >= since
    ).group_by(SignalModel.exchange)
    
    result = await db.execute(exchange_query)
    signals_by_exchange = {row[0]: row[1] for row in result.all()}
    
    return {
        "total_signals": total_signals,
        "accuracy_rate": accuracy_rate,
        "win_rate": accuracy_rate,  # Same as accuracy for now
        "avg_confidence": avg_confidence,
        "signals_by_type": signals_by_type,
        "signals_by_exchange": signals_by_exchange,
    }


@router.get("/{signal_id}")
async def get_signal(
    signal_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific signal by ID"""
    
    query = select(SignalModel).where(SignalModel.id == signal_id)
    result = await db.execute(query)
    signal = result.scalar_one_or_none()
    
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    return {
        "id": str(signal.id),
        "signal_type": signal.signal_type,
        "symbol": signal.symbol,
        "exchange": signal.exchange,
        "price": signal.price,
        "price_change_percent": signal.price_change_percent,
        "volume_change_percent": signal.volume_change_percent,
        "confidence_score": signal.confidence_score,
        "explanation": signal.explanation,
        "historical_analogies": signal.historical_analogies,
        "timestamp": signal.timestamp,
        "was_successful": signal.was_successful,
    }
