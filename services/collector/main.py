import asyncio
import websockets
from typing import AsyncGenerator
import json
from aiokafka import AIOKafkaProducer
from contextlib import AsyncExitStack
import logging
import pprint

from blueprints.constants import TOPIC
from blueprints.models import TradeData
from config.kafka import (
    BOOTSTRAP_SERVERS,
    VALUE_SERIALIZER
)

logging.basicConfig(
    #filename='collector.log',
    #filemode='w',
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


async def send_to_analytics(
    producer: AIOKafkaProducer,
    trade_data: TradeData) -> None:
    
    trade_topic = TOPIC.TRADES.value

    await producer.send_and_wait(
        trade_topic,
        trade_data.model_dump()
    )



async def receive_from_binance() -> AsyncGenerator[TradeData, None]:
    uri = "wss://stream.binance.com:9443/ws/btcusdt@trade"
    logging.debug(f"Got URI: <{uri}>")

    async with websockets.connect(uri) as websocket:
        logging.info("Connected to Binance Websocket API")

        async for message in websocket:
            logging.info("New message received!")

            data = json.loads(message)

            trade_data = TradeData(
                symbol=data["s"],
                price=float(data["p"]),
                timestamp=data["T"]
            )

            yield trade_data


async def main() -> None:
    async with AsyncExitStack() as stack:
        logging.debug("Entered AsyncExitStack")
        producer = await stack.enter_async_context(
            AIOKafkaProducer(
                bootstrap_servers=BOOTSTRAP_SERVERS,
                value_serializer=VALUE_SERIALIZER
            )
        )

        logging.debug("Initialized producer with value serializer")

        async for trade in receive_from_binance():
            await send_to_analytics(producer, trade)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"SYSTEM: Collector crashed! Error: {e}", exc_info=True)
