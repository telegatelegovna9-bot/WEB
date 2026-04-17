from .base import BaseExchangeConnector
from .binance import BinanceConnector
from .okx import OKXConnector

# Import other exchanges here when implemented
# from .bybit import BybitConnector
# from .mexc import MEXCConnector
# from .gate import GateConnector
# from .bitget import BitgetConnector

from typing import Dict, Type, Any
from ...core.enums import Exchange


EXCHANGE_CONNECTORS: Dict[Exchange, Type[BaseExchangeConnector]] = {
    Exchange.BINANCE: BinanceConnector,
    Exchange.OKX: OKXConnector,
    # Add other exchanges here
}


def get_exchange_connector(exchange: Exchange, config: Dict[str, Any]) -> BaseExchangeConnector:
    """Factory function to get exchange connector"""
    connector_class = EXCHANGE_CONNECTORS.get(exchange)
    if not connector_class:
        raise ValueError(f"No connector available for exchange: {exchange}")
    return connector_class(config)


__all__ = [
    'BaseExchangeConnector',
    'BinanceConnector',
    'get_exchange_connector',
    'EXCHANGE_CONNECTORS'
]
