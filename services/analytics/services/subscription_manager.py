import logging
from typing import List
from repository import (
    insert_subscriber,
    select_subscribers,
    delete_subscriber,
    is_subscription_exists
)


class SubscriptionManager:
    def __init__(
        self,
        session_factory
    ) -> None:
        self.session_factory = session_factory

    async def toggle(
        self,
        services: List[int],
        telegram_id: int
    ) -> tuple[List[int], List[int]]:

        to_add, to_remove = [], []

        async with self.session_factory() as session:
            async with session.begin():
                for service_id in services:
                    if await is_subscription_exists(session, service_id, telegram_id):
                        to_remove.append(service_id)
                    else:
                        to_add.append(service_id)

                if to_add:
                    await insert_subscriber(session, to_add, telegram_id)
                if to_remove:
                    await delete_subscriber(session, to_remove, telegram_id)

        logging.debug(
            f"Toggled subscriptions for user <{telegram_id}>: "
            f"added={to_add}, removed={to_remove}"
        )

        return to_add, to_remove

    async def get_recipients(
        self,
        service_id: int
    ) -> List[int]:
        async with self.session_factory() as session:
            return await select_subscribers(session, service_id)
