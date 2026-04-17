import asyncio
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
import structlog

from ..models.schemas import Signal, TickerData, OrderBook, Trade
from ..core.enums import Exchange, SignalType
from .strategies import get_all_strategies, BaseStrategy

logger = structlog.get_logger()


class SignalEngine:
    """Main signal detection engine that coordinates all strategies"""
    
    def __init__(self, strategy_configs: Optional[Dict[str, Dict[str, Any]]] = None):
        self.strategies: List[BaseStrategy] = get_all_strategies(strategy_configs)
        self.enabled_strategies = [s for s in self.strategies if s.enabled]
        self.signal_callbacks: List[Callable[[Signal], Any]] = []
        self.cooldowns: Dict[str, datetime] = {}
        self.cooldown_seconds = 300  # 5 minutes default cooldown
        
    def register_signal_callback(self, callback: Callable[[Signal], Any]):
        """Register callback for new signals"""
        self.signal_callbacks.append(callback)
        
    async def process_ticker(
        self,
        symbol: str,
        exchange: Exchange,
        ticker: TickerData,
        orderbook: Optional[OrderBook] = None,
        trades: Optional[List[Trade]] = None,
        historical_data: Optional[Dict[str, Any]] = None
    ) -> List[Signal]:
        """Process ticker data through all strategies"""
        
        signals = []
        
        for strategy in self.enabled_strategies:
            try:
                signal = await strategy.analyze(
                    symbol=symbol,
                    exchange=exchange,
                    ticker=ticker,
                    orderbook=orderbook,
                    trades=trades,
                    historical_data=historical_data
                )
                
                if signal:
                    # Check cooldown
                    cooldown_key = f"{strategy.name}:{symbol}:{signal.type.value}"
                    if self._is_in_cooldown(cooldown_key):
                        logger.debug(
                            "Signal in cooldown",
                            strategy=strategy.name,
                            symbol=symbol,
                            type=signal.type.value
                        )
                        continue
                    
                    # Set cooldown
                    self._set_cooldown(cooldown_key)
                    
                    signals.append(signal)
                    logger.info(
                        "Signal detected",
                        strategy=strategy.name,
                        symbol=symbol,
                        type=signal.type.value,
                        confidence=signal.intelligence.confidence_score
                    )
                    
            except Exception as e:
                logger.error(
                    "Strategy analysis failed",
                    strategy=strategy.name,
                    error=str(e)
                )
        
        # Notify callbacks
        for signal in signals:
            for callback in self.signal_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(signal)
                    else:
                        callback(signal)
                except Exception as e:
                    logger.error(
                        "Signal callback failed",
                        signal_id=signal.id,
                        error=str(e)
                    )
        
        return signals
    
    def _is_in_cooldown(self, key: str) -> bool:
        """Check if signal is in cooldown period"""
        if key not in self.cooldowns:
            return False
        
        cooldown_end = self.cooldowns[key]
        return datetime.utcnow() < cooldown_end
    
    def _set_cooldown(self, key: str):
        """Set cooldown for a signal"""
        self.cooldowns[key] = datetime.utcnow() + timedelta(seconds=self.cooldown_seconds)
        
        # Clean old cooldowns
        now = datetime.utcnow()
        self.cooldowns = {
            k: v for k, v in self.cooldowns.items()
            if v > now
        }
    
    def get_strategy_info(self) -> List[Dict[str, Any]]:
        """Get information about all strategies"""
        return [
            {
                'name': s.name,
                'enabled': s.enabled,
                'min_confidence': s.min_confidence,
                'config': s.config
            }
            for s in self.strategies
        ]
