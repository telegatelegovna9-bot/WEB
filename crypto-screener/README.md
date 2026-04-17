# 🚀 CryptoScreener Pro

Профессиональная платформа для крипто-трейдинга с интеллектуальными сигналами и AI-анализом рынка.

## ✨ Возможности

### 🔍 Signal Detection Engine
- **Pump/Dump Detector** - Обнаружение резких движений цены
- **Volume Spike Detector** - Аномалии объема торгов
- **Order Book Density** - Анализ крупных лимитных ордеров и "стен"
- **Pattern Recognition** - Распознавание графических паттернов

### 🧠 Signal Intelligence Engine (Ключевая фишка!)
Каждый сигнал сопровождается подробным анализом:
- **Причины сигнала** - объем, цена, действия крупных игроков
- **Тип поведения рынка** - Smart Money Accumulation, Distribution, FOMO, Manipulation
- **Probability Score** - Оценка вероятности отработки (0-100%)
- **Исторические аналогии** - Похожие ситуации в прошлом с результатами

### 📊 Real-time Data
- Подключение к биржам: **Binance**, **OKX**, **Bybit**
- WebSocket для данных в реальном времени
- REST API fallback

### 🎨 Premium UI/UX
- Современный темный интерфейс в стиле TradingView
- Fully customizable dashboard
- Grid/List view для сигналов
- Расширенные фильтры (биржи, типы сигналов, вероятность)
- Поиск по символам
- Top Gainers/Losers/Volume виджеты

## 🏗️ Архитектура

```
crypto-screener/
├── backend/                 # FastAPI (Python)
│   ├── app/
│   │   ├── main.py         # API + WebSocket
│   │   ├── core/config.py  # Конфигурация
│   │   ├── models/         # Типы данных
│   │   └── services/
│   │       ├── exchange_connector.py  # Binance, OKX, Bybit
│   │       └── signal_engine.py       # Intelligence Engine
│   └── requirements.txt
├── frontend/                # Next.js 14 (React/TypeScript)
│   ├── src/
│   │   ├── app/            # Pages
│   │   ├── components/     # UI Components
│   │   └── lib/            # Utils & API
│   └── package.json
└── docker-compose.yml       # Docker orchestration
```

## 🚀 Быстрый старт

### Вариант 1: Docker (Рекомендуется)

```bash
cd crypto-screener
docker-compose up -d
```

### Вариант 2: Локальная разработка

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📊 API Endpoints

| Endpoint | Описание |
|----------|----------|
| `GET /api/tickers` | Получить все тикеры |
| `GET /api/signals` | Получить сигналы с фильтрами |
| `GET /api/stats` | Статистика скринера |
| `GET /api/exchanges` | Список бирж |
| `GET /api/orderbook/{exchange}/{symbol}` | Стакан цен |
| `WS /ws` | WebSocket для real-time обновлений |

## 🔧 Конфигурация

Создайте файл `.env` в папке backend:

```env
# Опционально - для расширенных функций
BINANCE_API_KEY=your_key
BINANCE_SECRET=your_secret
OKX_API_KEY=your_key
OKX_SECRET=your_secret
BYBIT_API_KEY=your_key
BYBIT_SECRET=your_secret

# Пороги для сигналов
PUMP_THRESHOLD_PERCENT=5.0
DUMP_THRESHOLD_PERCENT=-5.0
VOLUME_SPIKE_MULTIPLIER=3.0
WALL_SIZE_THRESHOLD_USDT=100000
```

## 📱 Интерфейс

### Dashboard
- Live статистика (сигналы,tracked symbols, accuracy)
- Top Gainers/Losers/Volume
- Лента сигналов с интеллектуальным анализом
- Таблица рыночных данных

### Фильтры
- Выбор бирж (Binance, OKX, Bybit)
- Типы сигналов (Pump, Dump, Volume Spike)
- Минимальная вероятность (%)
- Поиск по символам

### Signal Card
Каждая карточка сигнала показывает:
- Тип сигнала и символ
- Текущую цену и изменение %
- Probability Score с визуальной шкалой
- Market Behavior классификацию
- Key Factors (причины)
- Historical Analogies с результатами
- Теги (smart_money, high_probability, etc.)

## 🎯 Уникальные возможности

1. **Объясняющие сигналы** - Не просто "pump detected", а ПОЧЕМУ это происходит
2. **Probability Score** - Машинное обучение для оценки вероятности
3. **Market Behavior Classification** - Определение намерений крупных игроков
4. **Historical Pattern Matching** - Поиск похожих ситуаций в истории
5. **Real-time Intelligence** - Мгновенный анализ при поступлении данных

## 🛠️ Технологии

**Backend:**
- Python 3.11
- FastAPI
- WebSockets
- aiohttp
- pandas/numpy (для анализа)

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Lucide Icons

**Infrastructure:**
- Docker & Docker Compose
- WebSocket для real-time
- REST API

## 📈 Roadmap

- [ ] Telegram Bot уведомления
- [ ] Пользовательские стратегии
- [ ] Backtesting engine
- [ ] Machine Learning модели
- [ ] Дополнительные биржи (MEXC, Gate, Bitget)
- [ ] Графики (TradingView integration)
- [ ] Heatmap рынка
- [ ] Портфельный трекинг

## ⚠️ Disclaimer

Это инструмент для анализа рынка, а не финансовый советник. Всегда проводите собственное исследование (DYOR) перед принятием торговых решений.

## 📄 License

MIT License

---

**CryptoScreener Pro** - Не просто показываем рынок, а объясняем его.
