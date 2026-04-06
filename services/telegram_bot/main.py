import asyncio
import logging
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from contextlib import AsyncExitStack
from typing import AsyncGenerator

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.exceptions import TelegramRetryAfter

from blueprints.models import TelegramQueryData, NotificationData
from blueprints.constants import (
    TOPIC,
    GROUP_ID,
    SERVICE_NAME_TO_ID,
    EVENT_TYPE
)
from config.kafka import (
    BOOTSTRAP_SERVERS,
    VALUE_SERIALIZER,
    VALUE_DESERIALIZER
)
from config.telegram import BOT_TOKEN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TelegramBot")


MESSAGES = {
    EVENT_TYPE.ALERT:
        lambda p: "Alert triggered!",
    EVENT_TYPE.SUBSCRIBED:
        lambda p: f"Subscribed to {p['service']}",
    EVENT_TYPE.UNSUBSCRIBED:
        lambda p: f"Unsubscribed from {p['service']}",
}


async def send_to_analyzer(
    producer: AIOKafkaProducer,
    telegram_data: TelegramQueryData
) -> None:
    topic = TOPIC.TELEGRAM_QUERY
    logger.info(f"KAFKA: Sending query to analyzer on topic '{topic}'")
    await producer.send_and_wait(topic, telegram_data.model_dump())
    logger.info("KAFKA: Query successfully delivered.")


async def get_from_analyzer(
    consumer: AIOKafkaConsumer
) -> AsyncGenerator[NotificationData, None]:
    logger.info("KAFKA: Notification generator started.")
    async for message in consumer:
        yield NotificationData(**message.value)


async def run_bot(
    producer: AIOKafkaProducer,
    consumer: AIOKafkaConsumer
) -> None:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp["producer"] = producer

    async def process_notifications() -> None:
        logger.info("TASK: Notification loop started.")
        try:
            async for data in get_from_analyzer(consumer):
                text = MESSAGES[data.event_type](data.payload)
                logger.info(f"TASK: Sending {data.event_type} to {data.telegram_id}")
                try:
                    await bot.send_message(data.telegram_id, text)
                except TelegramRetryAfter as e:
                    logger.warning(f"TASK: Flood control, retrying after {e.retry_after}s")
                    await asyncio.sleep(e.retry_after)
                    await bot.send_message(data.telegram_id, text)
        except Exception as e:
            logger.error(f"TASK: Notification loop error: {e}", exc_info=True)

    asyncio.create_task(process_notifications())

    @dp.message(CommandStart())
    async def cmd_start(message: Message) -> None:
        logger.info(f"BOT: User {message.from_user.id} triggered /start")
        commands = ", ".join(f"/{s.lower()}" for s in SERVICE_NAME_TO_ID)
        await message.answer(f"Hello! Available services: {commands}")

    for service_name, service_id in SERVICE_NAME_TO_ID.items():
        async def make_handler(sid: int = service_id):
            async def handler(
                message: Message,
                producer: AIOKafkaProducer
            ) -> None:
                telegram_data = TelegramQueryData(
                    service_id=sid,
                    telegram_id=message.from_user.id
                )
                await send_to_analyzer(producer, telegram_data)

            return handler

        dp.message.register(
            await make_handler(service_id),
            Command(service_name.lower())
        )

    logger.info("BOT: Starting polling...")
    await dp.start_polling(bot, skip_updates=True)


async def main() -> None:
    logger.info("SYSTEM: Initializing Telegram Bot Service...")

    async with AsyncExitStack() as stack:
        producer = await stack.enter_async_context(
            AIOKafkaProducer(
                bootstrap_servers=BOOTSTRAP_SERVERS,
                value_serializer=VALUE_SERIALIZER
            )
        )
        logger.info("SYSTEM: Kafka Producer connected.")

        notifications_consumer = await stack.enter_async_context(
            AIOKafkaConsumer(
                TOPIC.NOTIFICATIONS,
                bootstrap_servers=BOOTSTRAP_SERVERS,
                group_id=GROUP_ID.BOT,
                value_deserializer=VALUE_DESERIALIZER,
                auto_offset_reset="latest"
            )
        )
        logger.info("SYSTEM: Kafka Consumer connected.")

        await run_bot(producer, notifications_consumer)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"SYSTEM: Telegram bot crashed! Error: {e}", exc_info=True)