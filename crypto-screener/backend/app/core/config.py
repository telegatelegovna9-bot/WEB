import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Crypto Screener"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/crypto_screener"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # API Keys (optional)
    BINANCE_API_KEY: str = ""
    BINANCE_SECRET_KEY: str = ""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = ""
    
    # Signal thresholds
    PUMP_THRESHOLD_PERCENT: float = 5.0
    DUMP_THRESHOLD_PERCENT: float = -5.0
    VOLUME_SPIKE_MULTIPLIER: float = 3.0
    ORDER_WALL_MIN_SIZE_USD: float = 100000.0
    
    # Exchanges to monitor
    ENABLED_EXCHANGES: List[str] = ["binance", "okx", "bybit", "mexc", "gate", "bitget"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
