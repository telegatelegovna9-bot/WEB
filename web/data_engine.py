from __future__ import annotations

import random

from web.exchanges.base import MockExchangeConnector
from web.models import MarketTick
from web.store import MarketStore

SUPPORTED_EXCHANGES = ["binance", "okx", "bybit", "mexc", "gate", "bitget"]


class DataEngine:
    """Aggregates data from exchange connectors and normalizes schema."""

    def __init__(self, store: MarketStore) -> None:
        self.store = store
        symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"]
        self.connectors = [MockExchangeConnector(name=ex, symbols=symbols) for ex in SUPPORTED_EXCHANGES]

    async def next_tick(self) -> MarketTick:
        connector = random.choice(self.connectors)
        # In production this is websocket-first with REST fallback.
        return await connector.next_tick()
