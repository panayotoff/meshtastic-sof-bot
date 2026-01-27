# bot/core/router.py
import re
from bot.commands.news import latest_news_title
from bot.commands.ping import handle_ping
from bot.commands.weather import handle_weather

def dispatch(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)  # collapse whitespace
    if not text:
        return ""

    parts = text.split(" ")
    cmd = parts[0].lower()
    args = [a.strip() for a in parts[1:] if a.strip()]

    if cmd == "ping":
        return handle_ping(args)

    if cmd == "news":
        n = 1
        if args and args[0].isdigit():
            n = int(args[0])
        return latest_news_title(n) or "No news."

    if cmd == "weather":
        return handle_weather(args)

    return "Unknown command. Try: ping, news [n], weather [tomorrow]"