from __future__ import annotations

import time
from datetime import datetime
from typing import Optional

from meshtastic.serial_interface import SerialInterface
from pubsub import pub


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Current interface reference for commands that need mesh access
_current_interface: Optional[SerialInterface] = None


def get_interface() -> Optional[SerialInterface]:
    """Get the current Meshtastic interface (if connected)."""
    return _current_interface


def run_bot_dm_only(on_message, dev_path: str | None = None):
    """
    Connects (USB serial), logs all received text messages.
    Responds ONLY to private messages addressed to THIS node.
    Auto-reconnects if the device disconnects.

    on_message(text, packet) -> reply_text (str) or ""
    """

    while True:
        iface: Optional[SerialInterface] = None
        rx_handler = None
        conn_handler = None

        # We only know "my node num" after connect
        my_node_num: Optional[int] = None

        try:
            global _current_interface
            print(f"[{_ts()}] 🔌 Connecting… {dev_path or '(auto)'}")
            iface = SerialInterface(devPath=dev_path)
            _current_interface = iface

            def on_connection_established(interface, **kwargs):
                nonlocal my_node_num
                # In 2.17.x localNode exists; nodeNum becomes valid after handshake
                try:
                    my_node_num = getattr(interface.localNode, "nodeNum", None)
                except Exception:
                    my_node_num = None

                # Sometimes myInfo is populated too
                if my_node_num in (None, -1):
                    try:
                        my_node_num = getattr(interface.myInfo, "my_node_num", None)
                    except Exception:
                        pass

                print(f"[{_ts()}] ✅ Connected. my_node_num={my_node_num}")

            conn_handler = on_connection_established
            pub.subscribe(conn_handler, "meshtastic.connection.established")

            def is_dm_to_me(packet: dict) -> bool:
                if my_node_num is None:
                    return False

                to_val = packet.get("to")  # in your log it's '^all' for channel messages
                return isinstance(to_val, int) and to_val == my_node_num

            def rx(packet, interface):
                decoded = packet.get("decoded", {})
                text = decoded.get("text", "")
                if not text:
                    return

                from_id = packet.get("fromId", packet.get("from", "unknown"))
                to_val = packet.get("toId", packet.get("to", None))
                ch = packet.get("channel", None)
                pid = packet.get("id", None)

                print(
                    f"\n[{_ts()}] 📩 RX"
                    f"\n  from={from_id} to={to_val} ch={ch} id={pid}"
                    f"\n  text={text}"
                )

                if not is_dm_to_me(packet):
                    print(f"[{_ts()}] ↪️  Ignored (not a DM to me)")
                    return

                reply = on_message(text, packet)
                if reply:
                    # Reply to sender as a DM
                    iface.sendText(reply, destinationId=from_id)
                    print(f"[{_ts()}] 📤 TX to={from_id}\n  text={reply}")

            rx_handler = rx
            pub.subscribe(rx_handler, "meshtastic.receive")
            pub.subscribe(rx_handler, "meshtastic.receive.text")

            print(f"[{_ts()}] 👂 Listening (DM-only)… Ctrl+C to stop.")
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print(f"\n[{_ts()}] 🛑 Stopping.")
            return

        except Exception as e:
            print(f"[{_ts()}] ⚠️ Connection/runtime error: {e}")

        finally:
            # Clean up subscriptions to avoid duplicate handlers after reconnect
            try:
                if rx_handler:
                    # pub.unsubscribe(rx_handler, "meshtastic.receive")
                    pub.unsubscribe(rx_handler, "meshtastic.receive.text")
            except Exception:
                pass

            try:
                if conn_handler:
                    pub.unsubscribe(conn_handler, "meshtastic.connection.established")
            except Exception:
                pass

            try:
                if iface:
                    iface.close()
                _current_interface = None
            except Exception:
                pass

            print(f"[{_ts()}] 🔁 Reconnecting in 2s…")
            time.sleep(2)