from bot.core.mesh import run_bot_dm_only
from bot.core.router import dispatch
from bot.core.text import truncate_ascii_bytes

def on_message(text: str, packet: dict) -> str:
    return truncate_ascii_bytes(dispatch(text), 250)

if __name__ == "__main__":
    run_bot_dm_only(on_message)