"""
CryptoMind AI - Configuration Settings
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/cryptomind"
    TIMESCALE_URL: str = "postgresql://postgres:postgres@localhost:5432/timescale"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API Keys (optional)
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_SECRET_KEY: Optional[str] = None
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # WebSocket
    WS_HOST: str = "0.0.0.0"
    WS_PORT: int = 8765
    
    # Signal Detection Thresholds
    PUMP_THRESHOLD_PERCENT: float = 3.0  # Price increase % to detect pump
    DUMP_THRESHOLD_PERCENT: float = -3.0  # Price decrease % to detect dump
    VOLUME_SPIKE_MULTIPLIER: float = 3.0  # Volume multiplier for spike detection
    ORDER_BOOK_WALL_SIZE: float = 100000  # USD value for wall detection
    
    # Intelligence Engine
    MIN_CONFIDENCE_SCORE: float = 0.5
    HISTORICAL_ANALOGIES_COUNT: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
