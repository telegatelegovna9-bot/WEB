from __future__ import annotations

from abc import ABC, abstractmethod

from web.detectors import DetectionEngine
from web.intelligence import IntelligenceEngine
from web.models import DetectorEvent, MarketTick, Signal


class Strategy(ABC):
    name: str

    @abstractmethod
    def process(self, event: DetectorEvent, tick: MarketTick) -> Signal | None:
        raise NotImplementedError


class DefaultInterpretationStrategy(Strategy):
    name = "default-interpretation"

    def __init__(self, intelligence_engine: IntelligenceEngine) -> None:
        self.intelligence_engine = intelligence_engine

    def process(self, event: DetectorEvent, tick: MarketTick) -> Signal | None:
        return self.intelligence_engine.interpret(event)


class StrategyEngine:
    def __init__(self, detection_engine: DetectionEngine, intelligence_engine: IntelligenceEngine) -> None:
        self.detection_engine = detection_engine
        self.strategies: list[Strategy] = [DefaultInterpretationStrategy(intelligence_engine)]

    def add_strategy(self, strategy: Strategy) -> None:
        self.strategies.append(strategy)

    def run(self, raw_events: list[DetectorEvent], tick: MarketTick) -> list[Signal]:
        out: list[Signal] = []
        for event in raw_events:
            for strategy in self.strategies:
                maybe_signal = strategy.process(event=event, tick=tick)
                if maybe_signal:
                    out.append(maybe_signal)
        return out
