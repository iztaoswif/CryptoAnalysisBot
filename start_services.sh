#!/bin/bash
uv run services/collector/main.py && uv run services/analytics/main.py && uv run services/telegram_bot/main.py
