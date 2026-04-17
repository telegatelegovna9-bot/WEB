from __future__ import annotations

from statistics import mean

from web.models import DetectorEvent, MarketTick, SignalType
from web.store import MarketStore


class DetectionEngine:
    def detect(self, tick: MarketTick, store: MarketStore) -> list[DetectorEvent]:
        events: list[DetectorEvent] = []
        ticks = store.get_ticks(tick.symbol)
        if len(ticks) < 10:
            return events

        prices = [t.price for t in ticks[-20:]]
        volumes = [t.volume for t in ticks[-20:]]
        prev = ticks[-2]

        pct_move = ((tick.price - prev.price) / prev.price) * 100 if prev.price else 0
        vol_ratio = tick.volume / max(mean(volumes[:-1]), 1)
        acceleration = pct_move - (((prev.price - ticks[-3].price) / ticks[-3].price) * 100 if ticks[-3].price else 0)

        if pct_move > 2 and vol_ratio > 2:
            events.append(
                DetectorEvent(
                    signal_type=SignalType.pump,
                    symbol=tick.symbol,
                    exchange=tick.exchange,
                    severity=min(1.0, (pct_move / 8) + (vol_ratio / 10)),
                    reasons=[
                        f"Price moved +{pct_move:.2f}% in one step",
                        f"Volume spike x{vol_ratio:.2f}",
                        f"Acceleration {acceleration:.2f}%",
                    ],
                    metadata={"pct_move": pct_move, "volume_ratio": vol_ratio, "acceleration": acceleration},
                )
            )

        if pct_move < -2 and vol_ratio > 2:
            events.append(
                DetectorEvent(
                    signal_type=SignalType.dump,
                    symbol=tick.symbol,
                    exchange=tick.exchange,
                    severity=min(1.0, (abs(pct_move) / 8) + (vol_ratio / 10)),
                    reasons=[
                        f"Price moved {pct_move:.2f}% in one step",
                        f"Volume spike x{vol_ratio:.2f}",
                    ],
                    metadata={"pct_move": pct_move, "volume_ratio": vol_ratio},
                )
            )

        # Approximate orderbook density behavior with repeated rejection on one side.
        local_high = max(prices)
        local_low = min(prices)
        range_pct = ((local_high - local_low) / max(local_low, 0.00001)) * 100
        if range_pct < 1.2 and vol_ratio > 1.7:
            events.append(
                DetectorEvent(
                    signal_type=SignalType.order_book_density,
                    symbol=tick.symbol,
                    exchange=tick.exchange,
                    severity=min(1.0, vol_ratio / 4),
                    reasons=[
                        "Tight range with elevated volume suggests hidden liquidity wall",
                        f"Range {range_pct:.2f}% with volume x{vol_ratio:.2f}",
                    ],
                    metadata={"range_pct": range_pct, "volume_ratio": vol_ratio},
                )
            )

        # Listing detector placeholder (would parse exchange listings / announcements).
        if tick.symbol.endswith("1000"):
            events.append(
                DetectorEvent(
                    signal_type=SignalType.listing,
                    symbol=tick.symbol,
                    exchange=tick.exchange,
                    severity=0.7,
                    reasons=["Potential newly listed pair pattern detected"],
                    metadata={"source": "symbol_heuristic"},
                )
            )

        if tick.price >= local_high and vol_ratio > 1.5:
            events.append(
                DetectorEvent(
                    signal_type=SignalType.pattern,
                    symbol=tick.symbol,
                    exchange=tick.exchange,
                    severity=min(1.0, (vol_ratio / 3.5)),
                    reasons=["Breakout above local resistance", f"Volume confirmation x{vol_ratio:.2f}"],
                    metadata={"pattern": "resistance_breakout", "volume_ratio": vol_ratio},
                )
            )

        return events
