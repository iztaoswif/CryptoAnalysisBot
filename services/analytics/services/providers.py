import logging
import pprint
from aiokafka import AIOKafkaConsumer
from typing import AsyncGenerator
from blueprints.models import TradeData, TelegramQueryData

logger = logging.getLogger(__name__)


async def trade_data_provider(
    consumer: AIOKafkaConsumer
) -> AsyncGenerator[TradeData, None]:
    async for message in consumer:
        try:
            logger.debug(f"Got message: <{pprint.pformat(message.value)}> from collector")
            yield TradeData(**message.value)

        except Exception:
            logger.error(f"Failed to parse trade data. Raw: {message.value}")


async def telegram_query_provider(
    consumer: AIOKafkaConsumer
) -> AsyncGenerator[TelegramQueryData, None]:
    async for message in consumer:
        try:
            logger.debug(f"Got message: <{pprint.pformat(message.value)}> from telegram")
            yield TelegramQueryData(**message.value)

        except Exception:
            logger.error(f"Failed to parse query data. Raw: {message.value}")
