import logging
from collections import deque
from aiokafka import AIOKafkaConsumer
from services.providers import trade_data_provider, telegram_query_provider
from services.notifications import NotificationManager
from services.subscription_manager import SubscriptionManager
from logic import analyze_price_spike
from blueprints.constants import (
    SERVICE_NAME_TO_ID,
    SERVICE_ID_TO_NAME,
    EVENT_TYPE
)


async def run_telegram_worker(
    telegram_query_consumer: AIOKafkaConsumer,
    manager: SubscriptionManager,
    notificator: NotificationManager
) -> None:
    logging.info("Telegram Worker started. Waiting for queries")

    async for query in telegram_query_provider(telegram_query_consumer):
        service_id: int = query.service_id
        telegram_id: int = query.telegram_id

        logging.info(f"Query received: user <{telegram_id}> wants <{service_id}>")

        assert service_id in SERVICE_NAME_TO_ID.values()

        to_add, to_remove = await manager.toggle([service_id], telegram_id)

        for service_id in to_add:
            await notificator.send(
                telegram_id,
                EVENT_TYPE.SUBSCRIBED,
                {"service": SERVICE_ID_TO_NAME[service_id]}
            )

        for service_id in to_remove:
            await notificator.send(
                telegram_id,
                EVENT_TYPE.UNSUBSCRIBED,
                {"service": SERVICE_ID_TO_NAME[service_id]}
            )


async def run_trades_worker(
    trade_data_consumer: AIOKafkaConsumer,
    manager: SubscriptionManager,
    notificator: NotificationManager
) -> None:
    logging.info("Trades Worker started. Waiting for price data")

    window = deque()

    async for trade_data in trade_data_provider(trade_data_consumer):
        logging.debug(f"Processing trade: {trade_data.symbol} @ {trade_data.price}")

        if await analyze_price_spike(trade_data, window):
            spike_service_id = SERVICE_NAME_TO_ID["SPIKES"]
            recipients = await manager.get_recipients(spike_service_id)
            logging.info(f"SPIKE DETECTED! Alerting {len(recipients)} users.")

            await notificator.broadcast(
                recipients,
                EVENT_TYPE.ALERT
            )
