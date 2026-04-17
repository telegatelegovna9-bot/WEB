from __future__ import annotations

import random
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from web.models import MarketTick


class ExchangeConnector(ABC):
    name: str

    @abstractmethod
    async def next_tick(self) -> MarketTick:
        raise NotImplementedError


class MockExchangeConnector(ExchangeConnector):
    def __init__(self, name: str, symbols: list[str]) -> None:
        self.name = name
        self._symbols = symbols
        self._state = {
            "BTCUSDT": 68000.0,
            "ETHUSDT": 3400.0,
            "SOLUSDT": 180.0,
            "XRPUSDT": 0.78,
            "DOGEUSDT": 0.16,
        }

    async def next_tick(self) -> MarketTick:
        symbol = random.choice(self._symbols)
        base = self._state.get(symbol, random.uniform(1, 1000))
        drift = random.uniform(-0.011, 0.015)
        spike = random.uniform(0.02, 0.08) if random.random() < 0.04 else 0
        direction = -1 if random.random() < 0.35 else 1
        price = max(base * (1 + drift + direction * spike), 0.00001)
        self._state[symbol] = round(price, 6)
        return MarketTick(
            exchange=self.name,
            symbol=symbol,
            price=round(price, 6),
            volume=round(random.uniform(200, 6000), 2),
            ts=datetime.now(timezone.utc),
        )
