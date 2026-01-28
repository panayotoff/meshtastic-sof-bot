# bot/core/router.py
import re
from bot.commands.help import handle_help
from bot.commands.news import latest_news_title
from bot.commands.nodes import handle_nodes
from bot.commands.ping import handle_ping
from bot.commands.pi_status import handle_pi_status
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

    if cmd == "pi" and args and args[0].lower() == "status":
        return handle_pi_status(args[1:])

    if cmd == "nodes":
        return handle_nodes(args)

    if cmd == "help":
        return handle_help(args)

    return "Unknown command. Send 'help' for available commands."