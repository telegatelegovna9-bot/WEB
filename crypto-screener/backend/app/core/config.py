from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Crypto Screener"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/crypto_screener"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Exchanges
    BINANCE_WS_URL: str = "wss://stream.binance.com:9443/ws"
    OKX_WS_URL: str = "wss://ws.okx.com:8443/ws/v5/public"
    BYBIT_WS_URL: str = "wss://stream.bybit.com/v5/public/linear"
    MEXC_WS_URL: str = "wss://wbs.mexc.com/ws"
    GATE_WS_URL: str = "wss://ws.gate.io/v4"
    BITGET_WS_URL: str = "wss://ws.bitget.com/mix/v1/stream"
    
    # Signal Engine
    SIGNAL_MIN_CONFIDENCE: float = 0.6
    SIGNAL_COOLDOWN_SECONDS: int = 300
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    
    # Rate Limits
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
