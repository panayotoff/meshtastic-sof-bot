# bot/commands/nodes.py
from bot.core.mesh import get_interface


def handle_nodes(_: list[str]) -> str:
    iface = get_interface()
    if iface is None:
        return "Not connected"
    try:
        nodes = iface.nodes
        if nodes:
            count = len(nodes)
            return f"Nodes found: {count}"
        return "Nodes: 0"
    except Exception:
        return "Could not get nodes"
