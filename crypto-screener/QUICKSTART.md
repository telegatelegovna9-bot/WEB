# 🚀 QUICK START GUIDE

## Установка и запуск за 2 минуты

### Шаг 1: Клонирование/Переход в директорию
```bash
cd /workspace/crypto-screener
```

### Шаг 2: Запуск через Docker (Рекомендуется)
```bash
docker-compose up -d
```

### Шаг 3: Откройте браузер
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Локальная разработка

### Backend (Terminal 1)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```

---

## Проверка работы

### 1. Проверьте Backend
Откройте http://localhost:8000/api/health

Должны увидеть:
```json
{
  "status": "healthy",
  "tickers_count": 50,
  "signals_count": 5,
  "websocket_clients": 0
}
```

### 2. Проверьте Frontend
Откройте http://localhost:3000

Должны увидеть:
- ✅ Статус подключения (зеленая точка "Live")
- ✅ Stats Panel с цифрами
- ✅ Top Gainers/Losers/Volume
- ✅ Ленту сигналов
- ✅ Таблицу тикеров

### 3. Протестируйте фильтры
1. Выберите биржи в dropdown
2. Введите символ в поиск (например, "BTC")
3. Измените Min Probability slider
4. Переключите Grid/List view

---

## Troubleshooting

### Backend не запускается
```bash
# Проверьте Python версию (нужна 3.11+)
python --version

# Переустановите зависимости
pip uninstall -y -r requirements.txt
pip install -r requirements.txt
```

### Frontend не запускается
```bash
# Очистите кэш
rm -rf node_modules .next
npm install
npm run dev
```

### WebSocket не подключается
- Убедитесь что backend запущен на порту 8000
- Проверьте консоль браузера на ошибки
- Попробуйте обновить страницу

### Нет данных от бирж
- Проверьте интернет соединение
- Биржевые API могут быть временно недоступны
- В демо режиме данные генерируются автоматически

---

## Структура проекта

```
crypto-screener/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI приложение
│   │   ├── core/config.py       # Настройки
│   │   ├── models/schemas.py    # Pydantic модели
│   │   └── services/
│   │       ├── exchange_connector.py  # Binance, OKX, Bybit
│   │       └── signal_engine.py       # AI анализ
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Dashboard
│   │   │   └── layout.tsx       # Root layout
│   │   ├── components/
│   │   │   ├── Header.tsx       # Навигация
│   │   │   ├── SignalCard.tsx   # Карточка сигнала
│   │   │   ├── TickerTable.tsx  # Таблица
│   │   │   ├── StatsPanel.tsx   # Статистика
│   │   │   └── Filters.tsx      # Фильтры
│   │   ├── lib/
│   │   │   ├── types.ts         # TypeScript типы
│   │   │   └── api.ts           # API client
│   │   └── styles/globals.css   # Стили
│   └── package.json
└── docker-compose.yml
```

---

## API Examples

### Получить тикеры
```bash
curl http://localhost:8000/api/tickers?limit=10
```

### Получить сигналы
```bash
curl http://localhost:8000/api/signals?min_probability=70
```

### WebSocket подключение (JavaScript)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

---

## Следующие шаги

1. Настройте API ключи бирж (опционально)
2. Изучите код signal_engine.py для понимания логики
3. Добавьте свои стратегии в backend/app/services/
4. Кастомизируйте UI под свои нужды

**Удачного трейдинга! 🚀**
