from .base import BaseStrategy
from .pump_dump import PumpDumpStrategy
from .orderbook_density import OrderBookDensityStrategy

from typing import Dict, List, Type, Any


STRATEGIES: Dict[str, Type[BaseStrategy]] = {
    'pump_dump_detector': PumpDumpStrategy,
    'orderbook_density_detector': OrderBookDensityStrategy,
}


def get_strategy(name: str, config: Dict[str, Any] = None) -> BaseStrategy:
    """Factory function to get strategy instance"""
    strategy_class = STRATEGIES.get(name)
    if not strategy_class:
        raise ValueError(f"Unknown strategy: {name}")
    return strategy_class(config)


def get_all_strategies(configs: Dict[str, Dict[str, Any]] = None) -> List[BaseStrategy]:
    """Get all available strategies"""
    configs = configs or {}
    strategies = []
    
    for name, strategy_class in STRATEGIES.items():
        strategy_config = configs.get(name, {})
        strategies.append(strategy_class(strategy_config))
    
    return strategies


__all__ = [
    'BaseStrategy',
    'PumpDumpStrategy',
    'OrderBookDensityStrategy',
    'get_strategy',
    'get_all_strategies',
    'STRATEGIES'
]
