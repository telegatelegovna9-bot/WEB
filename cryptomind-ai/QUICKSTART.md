# CryptoMind AI - Quick Start Guide

## 🚀 Запуск проекта

### Вариант 1: Docker Compose (Рекомендуется)

```bash
# Перейдите в директорию проекта
cd cryptomind-ai

# Запустите все сервисы
docker-compose up -d

# Проверьте логи
docker-compose logs -f

# Остановите сервисы
docker-compose down
```

**Доступ к сервисам:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

### Вариант 2: Локальная разработка

#### Backend

```bash
cd backend

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt

# Скопируйте .env файл
cp .env.example .env

# Запустите сервер
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Установите зависимости
npm install

# Скопируйте .env файл
cp .env.local.example .env.local

# Запустите dev-сервер
npm run dev
```

---

## 📁 Структура проекта

```
cryptomind-ai/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── core/           # Конфигурация, БД
│   │   ├── engines/        # Signal Detection Engine
│   │   ├── integrations/   # Exchange connectors
│   │   ├── api/            # REST & WebSocket endpoints
│   │   └── models/         # Pydantic & SQLAlchemy models
│   ├── tests/
│   └── requirements.txt
│
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js App Router
│   │   ├── components/    # React компоненты
│   │   ├── hooks/         # Custom hooks
│   │   ├── services/      # API clients
│   │   └── styles/        # Tailwind CSS
│   └── package.json
│
└── docker-compose.yml
```

---

## 🔧 Конфигурация

### Переменные окружения (Backend)

Отредактируйте `backend/.env`:

```env
# База данных
DATABASE_URL=postgresql://cryptomind:cryptomind_secret_2024@localhost:5432/cryptomind

# Redis
REDIS_URL=redis://localhost:6379

# Пороги детекции сигналов
PUMP_THRESHOLD_PERCENT=5.0      # Минимальный рост цены для pump
DUMP_THRESHOLD_PERCENT=-5.0     # Минимальное падение для dump
VOLUME_SPIKE_MULTIPLIER=3.0     # Множитель объема
ORDER_BOOK_WALL_THRESHOLD=100000 # Порог стены в USD
```

---

## 🎯 Основные возможности

### 1. Signal Detection Engine
- **Pump/Dump Detector** - Обнаружение резких движений цены
- **Order Book Detector** - Анализ стаканов и крупных ордеров
- **Volume Spike Detector** - Детекция аномальных объемов

### 2. Intelligence Engine (Ключевая фишка!)
Каждый сигнал включает:
- ✅ **Причины** - Почему сработал сигнал
- ✅ **Тип поведения рынка** - Accumulation, Distribution, Breakout, Manipulation
- ✅ **Вероятность** - Confidence score 0-100%
- ✅ **Исторические аналогии** - Похожие ситуации в прошлом

### 3. Real-time Streaming
- WebSocket подключение для мгновенных уведомлений
- Поддержка множественных подключений
- Автоматическое переподключение

### 4. Multi-Exchange Support
- Binance (активно)
- OKX (готово к подключению)
- Bybit (готово к подключению)
- MEXC (готово к подключению)
- Gate (готово к подключению)
- Bitget (готово к подключению)

---

## 📊 API Endpoints

### REST API

```
GET /health                          # Проверка здоровья
GET /api/v1/status                   # Статус системы
GET /signals                         # Список сигналов
GET /signals/stats                   # Статистика сигналов
GET /signals/{id}                    # Конкретный сигнал
```

### WebSocket

```
ws://localhost:8000/ws/signals       # Поток сигналов
ws://localhost:8000/ws/tickers       # Поток тикеров
```

**Пример WebSocket сообщения:**
```json
{
  "type": "signal",
  "data": {
    "signal_type": "pump",
    "symbol": "BTCUSDT",
    "exchange": "binance",
    "price": 45000.0,
    "confidence_score": 68.0,
    "explanation": {
      "reasons": ["+300% volume spike", "Large buy order detected"],
      "market_behavior": "accumulation",
      "smart_money_activity": true
    },
    "historical_analogies": [...]
  }
}
```

---

## 🧪 Тестирование

### Backend тесты

```bash
cd backend
pytest
```

---

## 🐛 Troubleshooting

### Проблема: Backend не подключается к БД

```bash
# Проверьте, запущен ли PostgreSQL
docker-compose ps

# Перезапустите БД
docker-compose restart postgres
```

### Проблема: Frontend не видит API

Проверьте `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### Проблема: Нет сигналов

1. Проверьте подключение к биржам в логах
2. Убедитесь, что threshold'ы настроены правильно
3. Попробуйте уменьшить `PUMP_THRESHOLD_PERCENT` для тестирования

---

## 📈 Масштабирование

### Production конфигурация

1. Измените `SECRET_KEY` на уникальный
2. Настройте CORS в `backend/app/main.py`
3. Используйте production базу данных
4. Настройте rate limiting
5. Включите HTTPS

### Добавление новой биржи

1. Создайте класс в `backend/app/integrations/`
2. Реализуйте `BaseExchangeConnector`
3. Добавьте в `SignalEngine._initialize_connectors()`

---

## 🤝 Contributing

1. Fork репозиторий
2. Создайте feature branch
3. Внесите изменения
4. Отправьте PR

---

## 📄 License

MIT License

---

## 💡 Пример использования сигнала

```
Signal: BTC Pump

Причины:
- +300% объем
- крупный ордер на покупку
- снята стена продавцов

Тип: Smart Money Accumulation

Вероятность продолжения: 68%

История:
- 3 похожих случая
- 2 дали рост >10%
```

---

**CryptoMind AI** - Не просто скринер, а система анализа и интерпретации рынка.
