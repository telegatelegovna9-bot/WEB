from enum import Enum


class Exchange(str, Enum):
    BINANCE = "binance"
    OKX = "okx"
    BYBIT = "bybit"
    MEXC = "mexc"
    GATE = "gate"
    BITGET = "bitget"


class SignalType(str, Enum):
    PUMP = "pump"
    DUMP = "dump"
    ORDER_BOOK_WALL = "order_book_wall"
    LISTING = "listing"
    BREAKOUT = "breakout"
    CONSOLIDATION = "consolidation"
    FLAG_PATTERN = "flag_pattern"
    TRIANGLE_PATTERN = "triangle_pattern"


class MarketBehavior(str, Enum):
    ACCUMULATION = "accumulation"
    DISTRIBUTION = "distribution"
    BREAKOUT = "breakout"
    MANIPULATION = "manipulation"
    NORMAL = "normal"


class Timeframe(str, Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
