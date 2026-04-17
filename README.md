# Crypto Intelligence Screener (SaaS Prototype)

Интерпретирующий крипто-скринер: не только обнаружение событий, но и объяснение сигналов, оценка вероятности и сравнение с историческими кейсами.

## Реализованные компоненты

- **Data Engine**
  - Мульти-биржевой слой: Binance, OKX, Bybit, MEXC, Gate, Bitget.
  - Нормализация данных в `MarketTick`.
  - WebSocket stream (MVP: mock connectors) + архитектурный задел под REST fallback.

- **Signal Detection Engine**
  - Pump/Dump detector.
  - Order Book Density proxy detector.
  - Listing detector (MVP heuristic).
  - Pattern breakout detector.

- **Signal Intelligence Engine**
  - Причины сигнала.
  - Тип поведения рынка: Accumulation / Distribution / Breakout / Manipulation.
  - Probability score 0–100.
  - Исторические совпадения.

- **Strategy Engine**
  - Модульная модель стратегий с расширяемым интерфейсом.

- **Notification Engine**
  - Telegram-ready слой с антиспам-кулдауном.

- **Frontend (screener UI)**
  - Hero + вход в скринер.
  - Мозаика мульти-чартов (6 карт) и правая таблица монет с метриками.
  - Фильтры бирж, таймфрейм-панель, live-обновление через WS.
  - Список интеллектуальных сигналов и панель объяснения.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn web.main:app --reload
```

Откройте: `http://localhost:8000`

## API

- `GET /api/markets` — snapshot скринера (ранг, natr-like, объем 24h, изменения цены).
- `GET /api/signals` — последние интеллектуальные сигналы.
- `POST /api/simulate/tick` — инжект тестового тика.
- `WS /ws/stream` — realtime ticks + signals.
