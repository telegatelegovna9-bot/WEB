from __future__ import annotations

import asyncio
import json
import random
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from web.data_engine import DataEngine
from web.detectors import DetectionEngine
from web.intelligence import IntelligenceEngine
from web.models import MarketTick, Signal
from web.notifications import NotificationEngine
from web.store import MarketStore
from web.strategy import StrategyEngine

app = FastAPI(title="Crypto Screener Intelligence SaaS", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

store = MarketStore()
data_engine = DataEngine(store=store)
detection_engine = DetectionEngine()
intelligence_engine = IntelligenceEngine(store=store)
strategy_engine = StrategyEngine(detection_engine=detection_engine, intelligence_engine=intelligence_engine)
notification_engine = NotificationEngine()

frontend_dir = Path(__file__).parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(frontend_dir / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/api/signals")
async def list_signals(limit: int = 100) -> list[Signal]:
    return store.get_recent_signals(limit)


@app.get("/api/markets")
async def list_markets() -> list[dict]:
    return store.market_snapshot()


@app.post("/api/simulate/tick")
async def simulate_tick(exchange: str = "binance", symbol: str = "BTCUSDT") -> dict:
    last = store.get_last_price(symbol) or 68000
    price = round(last * (1 + random.uniform(-0.007, 0.01)), 2)
    volume = round(random.uniform(100, 5000), 3)
    tick = MarketTick(
        exchange=exchange,
        symbol=symbol,
        price=price,
        volume=volume,
        ts=datetime.now(timezone.utc),
    )
    await process_tick(tick)
    return {"processed": True, "symbol": symbol, "price": price}


async def process_tick(tick: MarketTick) -> list[Signal]:
    store.add_tick(tick)
    raw_events = detection_engine.detect(tick=tick, store=store)
    signals = strategy_engine.run(raw_events=raw_events, tick=tick)

    for signal in signals:
        store.add_signal(signal)
        await notification_engine.notify(signal)

    return signals


@app.websocket("/ws/stream")
async def stream(ws: WebSocket) -> None:
    await ws.accept()
    try:
        while True:
            tick = await data_engine.next_tick()
            signals = await process_tick(tick)
            payload = {
                "type": "tick",
                "tick": tick.model_dump(mode="json"),
                "signals": [s.model_dump(mode="json") for s in signals],
            }
            await ws.send_text(json.dumps(payload))
            await asyncio.sleep(0.8)
    except WebSocketDisconnect:
        return


@app.on_event("startup")
async def startup_seed() -> None:
    # prefill with synthetic market history for historical matching
    for _ in range(60):
        for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
            last = store.get_last_price(sym) or random.uniform(100, 70000)
            tick = MarketTick(
                exchange="binance",
                symbol=sym,
                price=round(last * (1 + random.uniform(-0.01, 0.01)), 2),
                volume=round(random.uniform(120, 4200), 3),
                ts=datetime.now(timezone.utc),
            )
            store.add_tick(tick)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("web.main:app", host="0.0.0.0", port=8000, reload=True)
