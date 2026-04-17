from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from statistics import mean
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
        self._signals: Deque[Signal] = deque(maxlen=1500)

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
            ticks = list(window.ticks)
            if not ticks:
                continue

            last = ticks[-1]
            prev = ticks[-2] if len(ticks) > 1 else last
            open_ref = ticks[-60] if len(ticks) >= 60 else ticks[0]

            change_pct = 0.0 if prev.price == 0 else ((last.price - prev.price) / prev.price) * 100
            day_change_pct = 0.0 if open_ref.price == 0 else ((last.price - open_ref.price) / open_ref.price) * 100

            recent_volumes = [t.volume for t in ticks[-24:]]
            avg_volume = mean(recent_volumes) if recent_volumes else last.volume
            volume_24h = sum(recent_volumes)
            volume_ratio = (last.volume / avg_volume) if avg_volume else 1.0

            returns = []
            for i in range(1, min(24, len(ticks))):
                base = ticks[-i - 1].price
                if base > 0:
                    returns.append(abs((ticks[-i].price - base) / base) * 100)
            natr_like = mean(returns) if returns else 0.0

            signals_for_symbol = [s for s in list(self._signals)[:300] if s.symbol == symbol]
            avg_conf = mean([s.confidence for s in signals_for_symbol]) if signals_for_symbol else 0
            accuracy = min(99.0, max(40.0, avg_conf * 0.85)) if signals_for_symbol else 50.0

            result.append(
                {
                    "symbol": symbol,
                    "price": last.price,
                    "exchange": last.exchange,
                    "last_volume": last.volume,
                    "change_pct": round(change_pct, 3),
                    "day_change_pct": round(day_change_pct, 2),
                    "volume_24h": round(volume_24h, 2),
                    "natr": round(natr_like, 2),
                    "rank": round(accuracy, 1),
                    "volume_ratio": round(volume_ratio, 2),
                }
            )
        return sorted(result, key=lambda x: x["day_change_pct"], reverse=True)
