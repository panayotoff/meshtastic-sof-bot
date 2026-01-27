# bot/commands/weather.py
from __future__ import annotations

import json
import ssl
from datetime import date
from urllib.request import Request, urlopen

import certifi

from bot.core.text import truncate_ascii_bytes

# Sofia (center)
SOFIA_LAT = 42.6977
SOFIA_LON = 23.3219
TZ = "Europe/Sofia"


def _http_get_json(url: str, timeout: float = 10.0) -> dict:
    req = Request(url, headers={"User-Agent": "meshtastic-bot/1.0"})
    ctx = ssl.create_default_context(cafile=certifi.where())
    with urlopen(req, timeout=timeout, context=ctx) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_daily_forecast() -> dict:
    # Daily forecast for today + tomorrow
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={SOFIA_LAT}&longitude={SOFIA_LON}"
        f"&timezone={TZ}"
        "&daily=temperature_2m_min,temperature_2m_max,precipitation_probability_max"
        "&forecast_days=2"
    )
    return _http_get_json(url)


def _format_day(label: str, d: dict, idx: int) -> str:
    daily = d.get("daily", {})
    tmin = daily.get("temperature_2m_min", [None, None])[idx]
    tmax = daily.get("temperature_2m_max", [None, None])[idx]
    pop = daily.get("precipitation_probability_max", [None, None])[idx]

    parts = [f"Sofia {label}:"]
    if tmin is not None and tmax is not None:
        # keep it short
        parts.append(f"{int(round(tmin))}-{int(round(tmax))}C")
    if pop is not None:
        parts.append(f"rain {int(round(pop))}%")

    return " ".join(parts)


def handle_weather(args: list[str]) -> str:
    """
    Commands:
      weather
      weather tomorrow
    """
    want_tomorrow = bool(args) and args[0].strip().lower() == "tomorrow"

    try:
        data = _fetch_daily_forecast()
        # Index 0 = today, 1 = tomorrow (because forecast_days=2)
        idx = 1 if want_tomorrow else 0
        label = "tomorrow" if want_tomorrow else "today"
        msg = _format_day(label, data, idx)
        return truncate_ascii_bytes(msg, 250)
    except Exception:
        return truncate_ascii_bytes("Weather unavailable.", 250)