from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from web.models import Signal


class NotificationEngine:
    """Telegram-ready notifier with anti-spam throttling."""

    def __init__(self, cooldown_seconds: int = 25) -> None:
        self.cooldown_seconds = cooldown_seconds
        self._last_sent: dict[str, datetime] = defaultdict(lambda: datetime.min.replace(tzinfo=timezone.utc))

    async def notify(self, signal: Signal) -> bool:
        key = f"{signal.exchange}:{signal.symbol}:{signal.signal_type}"
        now = datetime.now(timezone.utc)
        if now - self._last_sent[key] < timedelta(seconds=self.cooldown_seconds):
            return False

        # Place for Telegram Bot API integration.
        self._last_sent[key] = now
        return True
