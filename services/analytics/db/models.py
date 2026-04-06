from sqlalchemy import (
    MetaData,
    Table,
    Column,
    BigInteger,
    Integer,
    String,
    Index
)


metadata = MetaData()

subscriptions = Table(
    "subscriptions",
    metadata,
    Column(
        "telegram_id",
        BigInteger,
        primary_key=True
    ),
    Column(
        "service_id",
        Integer,
        primary_key=True
    ),

    Index("idx_service_id", "service_id")
)

spikes_subscriptions = Table(
    "spikes_subscriptions",
    metadata,
    Column(
        "telegram_id",
        BigInteger,
        primary_key=True
    ),
    Column(
        "symbol",
        String,
        primary_key=True
    )
)
