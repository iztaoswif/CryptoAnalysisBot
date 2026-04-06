from enum import StrEnum


class TOPIC(StrEnum):
    TRADES = "raw-trades"
    NOTIFICATIONS = "notifications"
    TELEGRAM_QUERY = "tg-query"


class GROUP_ID(StrEnum):
    ANALYTICS = "analytics-group"
    BOT = "bot-group"
    COLLECTOR = "collector-group"


class EVENT_TYPE(StrEnum):
    ALERT = "alert"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"


SERVICE_NAME_TO_ID = {
    "SPIKES": 1
}


SERVICE_ID_TO_NAME = {
    1: "SPIKES"
}
