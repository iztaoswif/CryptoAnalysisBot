from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    select,
    insert,
    delete,
    exists
)
from typing import List
from db.models import subscriptions


async def is_subscription_exists(
    session: AsyncSession,
    service_id: int,
    telegram_id: int
) -> bool:
    stmt = (
        select(
            exists()
            .where(subscriptions.c.service_id == service_id)
            .where(subscriptions.c.telegram_id == telegram_id)
        )
    )

    result = await session.execute(stmt)
    return result.scalar()



async def select_subscribers(
    session: AsyncSession,
    service_id: int
) -> List[int]:
    stmt = (
        select(subscriptions.c.telegram_id)
        .where(subscriptions.c.service_id == service_id)
    )

    result = await session.execute(stmt)
    return result.scalars().all()


async def insert_subscriber(
    session: AsyncSession,
    service_ids: List[int],
    telegram_id: int
) -> None:
    data = [
        {
            "telegram_id": telegram_id,
            "service_id": service_id
        }
        for service_id in service_ids
    ]

    stmt = (
        insert(subscriptions)
        .values(data)
    )

    await session.execute(stmt)


async def delete_subscriber(
    session: AsyncSession,
    service_ids: List[int],
    telegram_id: int
) -> None:
    stmt = (
        delete(subscriptions)
        .where(subscriptions.c.telegram_id == telegram_id)
        .where(subscriptions.c.service_id.in_(service_ids))
    )

    await session.execute(stmt)
