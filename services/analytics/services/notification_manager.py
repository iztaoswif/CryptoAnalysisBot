import logging
from typing import List, Dict, Optional
from aiokafka import AIOKafkaProducer

from blueprints.models import NotificationData
from blueprints.constants import TOPIC

logger = logging.getLogger(__name__)


class NotificationManager:
    def __init__(self, producer: AIOKafkaProducer):
        self.producer = producer

    async def send(
        self,
        telegram_id: int,
        event_type: str,
        payload: Optional[Dict] = None
    ) -> None:
        data = NotificationData(
            telegram_id=telegram_id,
            event_type=event_type,
            payload=payload
        )

        await self.producer.send_and_wait(
            TOPIC.NOTIFICATIONS,
            data.model_dump()
        )

        logger.debug(f"Sent {event_type} to {telegram_id} with payload {payload}")

    async def broadcast(
        self,
        recipients: List[int],
        event_type: str,
        payload: Optional[Dict] = None
    ) -> None:
        logger.info(f"Broadcasting {event_type} to {len(recipients)} recipients")

        for recipient_id in recipients:
            await self.send(recipient_id, event_type, payload)
