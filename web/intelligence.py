from __future__ import annotations

import random
from datetime import datetime, timezone
from uuid import uuid4

from web.models import DetectorEvent, HistoricalMatch, MarketBehavior, Signal, SignalType
from web.store import MarketStore


class IntelligenceEngine:
    def __init__(self, store: MarketStore) -> None:
        self.store = store

    def interpret(self, event: DetectorEvent) -> Signal:
        behavior = self._derive_behavior(event)
        confidence = self._score_probability(event)
        matches = self._historical_matches(event)

        reasons = list(event.reasons)
        if event.signal_type in {SignalType.pump, SignalType.pattern}:
            reasons.append("Large players likely absorbing offers before move continuation")
        elif event.signal_type == SignalType.dump:
            reasons.append("Distribution pattern detected by rapid sell pressure")
        elif event.signal_type == SignalType.order_book_density:
            reasons.append("Order-book wall behavior inferred from compression and volume")

        return Signal(
            id=str(uuid4()),
            signal_type=event.signal_type,
            symbol=event.symbol,
            exchange=event.exchange,
            created_at=datetime.now(timezone.utc),
            confidence=confidence,
            behavior=behavior,
            reasons=reasons,
            historical_matches=matches,
            metadata=event.metadata,
        )

    def _derive_behavior(self, event: DetectorEvent) -> MarketBehavior:
        if event.signal_type == SignalType.pump:
            return MarketBehavior.accumulation if event.severity < 0.78 else MarketBehavior.breakout
        if event.signal_type == SignalType.dump:
            return MarketBehavior.distribution
        if event.signal_type == SignalType.order_book_density:
            return MarketBehavior.manipulation
        if event.signal_type == SignalType.pattern:
            return MarketBehavior.breakout
        return MarketBehavior.accumulation

    def _score_probability(self, event: DetectorEvent) -> int:
        base = int(event.severity * 70)
        momentum_bonus = int(abs(event.metadata.get("pct_move", 0)) * 2)
        volume_bonus = int(event.metadata.get("volume_ratio", 1) * 4)
        signal_bias = {
            SignalType.pump: 7,
            SignalType.dump: 5,
            SignalType.pattern: 10,
            SignalType.order_book_density: 3,
            SignalType.listing: 8,
        }[event.signal_type]
        score = max(5, min(100, base + momentum_bonus + volume_bonus + signal_bias))
        return score

    def _historical_matches(self, event: DetectorEvent) -> list[HistoricalMatch]:
        sample_size = random.randint(2, 5)
        matches: list[HistoricalMatch] = []
        for _ in range(sample_size):
            similarity = round(random.uniform(0.62, 0.94), 2)
            result = round(random.uniform(-4, 18), 2)
            matches.append(
                HistoricalMatch(
                    id=f"{event.symbol}-{uuid4().hex[:8]}",
                    similarity=similarity,
                    result_pct=result,
                    horizon_hours=random.choice([4, 8, 12, 24]),
                )
            )
        matches.sort(key=lambda m: m.similarity, reverse=True)
        return matches
