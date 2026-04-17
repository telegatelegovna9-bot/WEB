from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from app.core.config import settings
from app.core.database import init_db
from app.api.websocket import router as websocket_router, setup_signal_engine
from app.api.signals import router as signals_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting CryptoMind AI...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Setup signal engine
    signal_engine = setup_signal_engine()
    
    # Start signal engine with popular symbols
    symbols = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
        "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "TRXUSDT", "LINKUSDT"
    ]
    
    asyncio.create_task(signal_engine.start(symbols))
    logger.info(f"Signal engine started with {len(symbols)} symbols")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CryptoMind AI...")
    await signal_engine.stop()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Advanced crypto screener with intelligent signals and market behavior analysis",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(websocket_router)
app.include_router(signals_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "description": "Advanced crypto screener with intelligent signals"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/api/v1/status")
async def api_status():
    """Get API status and configuration"""
    return {
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "exchanges": {
            "binance": "connected",
            "okx": "available",
            "bybit": "available",
            "mexc": "available",
            "gate": "available",
            "bitget": "available"
        },
        "features": {
            "signal_detection": True,
            "intelligence_engine": True,
            "historical_analogies": True,
            "websocket_streaming": True,
            "multi_exchange": True
        }
    }


# For development/testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
