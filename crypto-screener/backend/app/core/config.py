import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys (optional - can work without for public data)
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
    BINANCE_SECRET = os.getenv("BINANCE_SECRET", "")
    OKX_API_KEY = os.getenv("OKX_API_KEY", "")
    OKX_SECRET = os.getenv("OKX_SECRET", "")
    BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "")
    BYBIT_SECRET = os.getenv("BYBIT_SECRET", "")
    
    # WebSocket URLs
    BINANCE_WS = "wss://stream.binance.com:9443/ws"
    BINANCE_WS_TESTNET = "wss://testnet.binance.vision/ws"
    OKX_WS = "wss://ws.okx.com:8443/ws/v5/public"
    BYBIT_WS = "wss://stream.bybit.com/v5/public/linear"
    
    # REST API URLs
    BINANCE_REST = "https://api.binance.com"
    OKX_REST = "https://www.okx.com"
    BYBIT_REST = "https://api.bybit.com"
    
    # App settings
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/crypto_screener")
    
    # Signal thresholds
    PUMP_THRESHOLD_PERCENT = 5.0  # % price increase
    DUMP_THRESHOLD_PERCENT = -5.0  # % price decrease
    VOLUME_SPIKE_MULTIPLIER = 3.0  # x times average volume
    WALL_SIZE_THRESHOLD_USDT = 100000  # $ value for wall detection
    
    # Update intervals
    TICKER_UPDATE_MS = 1000
    ORDERBOOK_UPDATE_MS = 500
    TRADES_UPDATE_MS = 100
    
settings = Settings()
