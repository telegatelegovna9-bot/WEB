from app.models.schemas import Exchange


class BaseExchangeConnector:
    """Base class for all exchange connectors"""
    
    def __init__(self):
        self.name: str = ""
        self.ws_url: str = ""
        self.api_url: str = ""
        self.is_connected: bool = False
        self.subscribed_symbols: list = []
    
    async def connect(self) -> bool:
        """Establish WebSocket connection"""
        raise NotImplementedError
    
    async def disconnect(self):
        """Close WebSocket connection"""
        raise NotImplementedError
    
    async def subscribe_ticker(self, symbol: str) -> bool:
        """Subscribe to ticker updates"""
        raise NotImplementedError
    
    async def subscribe_orderbook(self, symbol: str, depth: int = 20) -> bool:
        """Subscribe to order book updates"""
        raise NotImplementedError
    
    async def subscribe_trades(self, symbol: str) -> bool:
        """Subscribe to trade updates"""
        raise NotImplementedError
    
    def normalize_ticker(self, data: dict) -> dict:
        """Normalize ticker data to common format"""
        raise NotImplementedError
    
    def normalize_orderbook(self, data: dict) -> dict:
        """Normalize order book data to common format"""
        raise NotImplementedError
    
    def normalize_trade(self, data: dict) -> dict:
        """Normalize trade data to common format"""
        raise NotImplementedError
