# 🚀 CryptoMind AI

**Advanced Crypto Screener with Intelligent Signals & Market Behavior Explanation**

---

## 🎯 Что это?

CryptoMind AI — это не просто скринер. Это **интеллектуальная платформа**, которая:

1. ✅ Автоматически анализирует рынок криптовалют в реальном времени
2. ✅ Обнаруживает торговые возможности (pump, dump, volume spikes, order book walls)
3. ✅ **Объясняет причины сигналов** (ключевая фишка!)
4. ✅ Оценивает вероятность отработки (0-100%)
5. ✅ Находит исторические аналогии
6. ✅ Отслеживает активность "умных денег"

---

## 🏗️ Архитектура

```
┌─────────────────┐         ┌──────────────────┐
│   Frontend      │◄───────►│   Backend        │
│   Next.js 14    │  WS/REST│   FastAPI        │
└─────────────────┘         └────────┬─────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
            │   Signal    │ │ Intelligence│ │  Exchange   │
            │   Engine    │ │   Engine    │ │ Connectors  │
            └─────────────┘ └─────────────┘ └─────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
            │ PostgreSQL  │ │   Redis     │ │  Binance    │
            │ TimescaleDB │ │   Cache     │ │  WebSocket  │
            └─────────────┘ └─────────────┘ └─────────────┘
```

---

## 🔥 Уникальные возможности

### 1. Объясняющие сигналы
Не просто "pump detected", а подробное объяснение **ПОЧЕМУ**:
- +300% volume spike
- Крупный ордер на покупку
- Снята стена продавцов

### 2. Probability Score
Оценка вероятности отработки сигнала от 0 до 100%

### 3. Исторические аналогии
Поиск похожих ситуаций в прошлом с указанием результата

### 4. Smart Money Detection
Отслеживание активности крупных игроков

### 5. Market Behavior Classification
- Accumulation
- Distribution
- Breakout
- Manipulation

---

## 📦 Компоненты

### Backend (Python/FastAPI)
- **Data Engine**: WebSocket интеграция с биржами (Binance готов, другие по шаблону)
- **Signal Detection Engine**:
  - Pump/Dump Detector
  - Volume Spike Detector
  - Order Book Detector
- **Intelligence Engine**: Анализ и объяснение сигналов
- **REST API + WebSocket** для real-time данных
- **PostgreSQL + TimescaleDB** для хранения
- **Redis** для кэширования

### Frontend (Next.js 14/React)
- Современный темный UI с glassmorphism
- Real-time дашборд через WebSocket
- Карточки сигналов с полной информацией
- Фильтрация по типам сигналов
- Адаптивный дизайн

---

## 🚀 Быстрый старт

### Вариант 1: Docker Compose (рекомендуется)

```bash
cd /workspace

# Запуск всех сервисов
docker-compose up -d

# Доступ:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Вариант 2: Локальный запуск

#### Backend
```bash
cd backend

# Установка зависимостей
pip install -r requirements.txt

# Копирование .env
cp .env.example .env

# Запуск
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend

# Установка зависимостей
npm install

# Запуск
npm run dev
```

---

## 📊 Пример сигнала

```json
{
  "signal_id": "uuid...",
  "signal_type": "pump",
  "symbol": "BTCUSDT",
  "exchange": "binance",
  "price": 45000.0,
  "price_change_percent": 5.2,
  "confidence_score": 78.5,
  "explanation": {
    "reasons": [
      "+5.2% price increase in 5min",
      "3.5x volume spike",
      "Strong volume confirms genuine buying pressure"
    ],
    "market_behavior": "accumulation",
    "smart_money_activity": true,
    "large_orders_detected": true,
    "recommendation": "Consider long position with tight stop-loss"
  },
  "historical_analogies": [
    {
      "similarity_score": 0.85,
      "outcome": "success",
      "price_change_after": 8.5,
      "symbol": "BTCUSDT",
      "timeframe": "5m"
    }
  ],
  "probability_assessment": {
    "success_probability": 72.3,
    "outlook": "bullish",
    "risk_level": "medium"
  }
}
```

---

## 🛠️ Технологии

| Компонент | Технология |
|-----------|------------|
| Backend | Python 3.11, FastAPI |
| Frontend | Next.js 14, React, TypeScript |
| Database | PostgreSQL + TimescaleDB |
| Cache | Redis |
| Charts | Recharts |
| Styling | Tailwind CSS |
| Real-time | WebSockets |

---

## 📈 Расширение

### Добавление новой биржи

1. Создайте файл `backend/exchanges/{exchange}_connector.py`
2. Унаследуйтесь от `BaseExchangeConnector`
3. Реализуйте абстрактные методы
4. Добавьте в `main.py`

### Добавление нового детектора

1. Создайте файл `backend/signals/{name}_detector.py`
2. Реализуйте метод `detect()`
3. Добавьте в `SignalDetector`

---

## ⚙️ Конфигурация

Основные параметры в `backend/config.py`:

```python
PUMP_THRESHOLD_PERCENT = 3.0      # % роста для pump
DUMP_THRESHOLD_PERCENT = -3.0     # % падения для dump
VOLUME_SPIKE_MULTIPLIER = 3.0     # множитель объема
ORDER_BOOK_WALL_SIZE = 100000     # $ размер стены
```

---

## 📝 Лицензия

MIT License

---

## 💡 Roadmap

- [ ] Telegram Bot для уведомлений
- [ ] Поддержка OKX, Bybit, MEXC
- [ ] Pattern Detection (треугольники, флаги)
- [ ] Listing Detector
- [ ] Backtesting engine
- [ ] User authentication
- [ ] Custom strategies

---

**CryptoMind AI** — ваш интеллектуальный помощник в мире крипто-трейдинга! 🚀
