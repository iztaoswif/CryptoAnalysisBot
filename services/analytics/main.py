import asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from contextlib import AsyncExitStack
import logging
from services.subscription_manager import SubscriptionManager
from services.notification_manager import NotificationManager
from workers import run_telegram_worker, run_trades_worker

from db.engine import async_session_factory

from blueprints.constants import TOPIC, GROUP_ID
from config.kafka import (
    BOOTSTRAP_SERVERS,
    VALUE_SERIALIZER,
    VALUE_DESERIALIZER
)

logging.basicConfig(
    filename='analytics.log',
    filemode='w', 
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

async def main() -> None:
    logging.info(f"Starting Analytics Service. Connecting to {BOOTSTRAP_SERVERS}")
    async with AsyncExitStack() as stack:
        notification_producer = await stack.enter_async_context(
            AIOKafkaProducer(
                bootstrap_servers=BOOTSTRAP_SERVERS,
                value_serializer=VALUE_SERIALIZER
            )
        )
        logging.info("Notification Producer connected.")

        trade_data_consumer = await stack.enter_async_context(
            AIOKafkaConsumer(
                TOPIC.TRADES,
                bootstrap_servers=BOOTSTRAP_SERVERS,
                group_id=GROUP_ID.ANALYTICS,
                value_deserializer=VALUE_DESERIALIZER
                #, auto_offset_reset="earliest"
            )
        )
        logging.info(f"Trade Consumer connected to group: {trade_data_consumer._group_id}")

        telegram_query_consumer = await stack.enter_async_context(
            AIOKafkaConsumer(
                TOPIC.TELEGRAM_QUERY,
                bootstrap_servers=BOOTSTRAP_SERVERS,
                group_id=GROUP_ID.ANALYTICS,
                value_deserializer=VALUE_DESERIALIZER
            )
        )
        logging.info(f"Telegram Consumer connected to group: {telegram_query_consumer._group_id}")

        manager = SubscriptionManager(async_session_factory)
        notificator = NotificationManager(notification_producer)

        async with asyncio.TaskGroup() as task_group:

            task_group.create_task(run_telegram_worker(
                telegram_query_consumer,
                manager,
                notificator
            ))

            task_group.create_task(run_trades_worker(
                trade_data_consumer,
                manager,
                notificator
            ))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"SYSTEM: Analytics crashed! Error: {e}", exc_info=True)
