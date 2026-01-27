# bot/core/text.py
import re
from typing import Dict

_BG2LAT: Dict[str, str] = {
    "А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D", "Е": "E", "Ж": "Zh",
    "З": "Z", "И": "I", "Й": "Y", "К": "K", "Л": "L", "М": "M", "Н": "N",
    "О": "O", "П": "P", "Р": "R", "С": "S", "Т": "T", "У": "U", "Ф": "F",
    "Х": "H", "Ц": "Ts", "Ч": "Ch", "Ш": "Sh", "Щ": "Sht", "Ъ": "A",
    "Ь": "Y", "Ю": "Yu", "Я": "Ya",
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ж": "zh",
    "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n",
    "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f",
    "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sht", "ъ": "a",
    "ь": "y", "ю": "yu", "я": "ya",
}

def transliterate_bg_to_en(text: str) -> str:
    out = "".join(_BG2LAT.get(ch, ch) for ch in text)
    out = re.sub(r"\s+", " ", out).strip()
    return out

def truncate_ascii_bytes(text: str, limit_bytes: int = 250) -> str:
    """
    ASCII only. If truncates, adds '...' and keeps total <= limit_bytes.
    """
    ascii_text = text.encode("ascii", errors="ignore").decode("ascii", errors="ignore")
    b = ascii_text.encode("ascii")

    if len(b) <= limit_bytes:
        return ascii_text

    ellipsis = b"..."
    max_body = limit_bytes - len(ellipsis)
    if max_body <= 0:
        return "..."

    truncated = b[:max_body].decode("ascii", errors="ignore").rstrip()
    return (truncated + "...").rstrip()