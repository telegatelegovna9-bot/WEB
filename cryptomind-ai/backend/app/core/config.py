from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "CryptoMind AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "postgresql://cryptomind:cryptomind_secret_2024@localhost:5432/cryptomind"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Exchanges
    BINANCE_WS_URL: str = "wss://stream.binance.com:9443/ws"
    BINANCE_API_URL: str = "https://api.binance.com"
    
    OKX_WS_URL: str = "wss://ws.okx.com:8443/ws/v5/public"
    OKX_API_URL: str = "https://www.okx.com"
    
    BYBIT_WS_URL: str = "wss://stream.bybit.com/v5/public/linear"
    BYBIT_API_URL: str = "https://api.bybit.com"
    
    MEXC_WS_URL: str = "wss://wbs.mexc.com/ws"
    MEXC_API_URL: str = "https://api.mexc.com"
    
    GATE_WS_URL: str = "wss://fx-ws.gateio.ws/v4/ws"
    GATE_API_URL: str = "https://api.gateio.ws/api/v4"
    
    BITGET_WS_URL: str = "wss://ws.bitget.com/v2/ws/public"
    BITGET_API_URL: str = "https://api.bitget.com"

    # Signal Detection Thresholds
    PUMP_THRESHOLD_PERCENT: float = 5.0  # Price increase %
    DUMP_THRESHOLD_PERCENT: float = -5.0  # Price decrease %
    VOLUME_SPIKE_MULTIPLIER: float = 3.0  # Volume multiplier
    ORDER_BOOK_WALL_THRESHOLD: float = 100000  # USD value

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_RECONNECT_DELAY: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
