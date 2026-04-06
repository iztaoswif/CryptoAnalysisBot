from collections import deque
from blueprints.models import TradeData


async def analyze_price_spike(new_data: TradeData, window: deque) -> bool:
    WINDOW_MS = 60000
    SPIKE_THRESHOLD = 0.01

    window.append(new_data)
    
    timestamp_difference = new_data.timestamp - window[0].timestamp
    while len(window) > 1 and timestamp_difference > WINDOW_MS:
        window.popleft()

    old_data = window[0]
    try:
        return abs(new_data.price - old_data.price) / old_data.price > SPIKE_THRESHOLD

    except ZeroDivisionError:
        return True
