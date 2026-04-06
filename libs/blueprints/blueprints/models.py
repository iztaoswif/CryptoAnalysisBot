from pydantic import BaseModel
from typing import Dict, Optional

class TradeData(BaseModel):
    symbol: str
    price: float
    timestamp: int


class TelegramQueryData(BaseModel):
    service_id: int
    telegram_id: int


class NotificationData(BaseModel):
    event_type: str
    telegram_id: int
    payload: Optional[Dict] = None
