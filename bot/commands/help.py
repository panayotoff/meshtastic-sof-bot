# bot/commands/help.py


def handle_help(_: list[str]) -> str:
    return (
        "Commands: "
        "ping, "
        "news [n], "
        "weather [tomorrow], "
        "pi status, "
        "nodes, "
        "help"
    )
