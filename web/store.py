from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import DefaultDict, Deque

from web.models import MarketTick, Signal


@dataclass
class MarketWindow:
    ticks: Deque[MarketTick]


class MarketStore:
    def __init__(self, window_size: int = 240) -> None:
        self._window_size = window_size
        self._markets: DefaultDict[str, MarketWindow] = defaultdict(
            lambda: MarketWindow(ticks=deque(maxlen=self._window_size))
        )
        self._signals: Deque[Signal] = deque(maxlen=1000)

    def add_tick(self, tick: MarketTick) -> None:
        self._markets[tick.symbol].ticks.append(tick)

    def get_ticks(self, symbol: str) -> list[MarketTick]:
        return list(self._markets[symbol].ticks)

    def get_last_price(self, symbol: str) -> float | None:
        ticks = self._markets[symbol].ticks
        return ticks[-1].price if ticks else None

    def add_signal(self, signal: Signal) -> None:
        self._signals.appendleft(signal)

    def get_recent_signals(self, limit: int = 100) -> list[Signal]:
        return list(self._signals)[:limit]

    def market_snapshot(self) -> list[dict]:
        result = []
        for symbol, window in self._markets.items():
            if not window.ticks:
                continue
            last = window.ticks[-1]
            prev = window.ticks[-2] if len(window.ticks) > 1 else last
            change_pct = 0.0 if prev.price == 0 else ((last.price - prev.price) / prev.price) * 100
            result.append(
                {
                    "symbol": symbol,
                    "price": last.price,
                    "exchange": last.exchange,
                    "volume": last.volume,
                    "change_pct": round(change_pct, 3),
                }
            )
        return sorted(result, key=lambda x: x["symbol"])
