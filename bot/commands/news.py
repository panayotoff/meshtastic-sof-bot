# bot/commands/news.py
import ssl
from typing import List
from urllib.request import Request, urlopen

import certifi
from bs4 import BeautifulSoup

from bot.core.text import transliterate_bg_to_en, truncate_ascii_bytes

_RSS_URL = "https://www.svobodnaevropa.bg/api/epiqq"

def _fetch_rss_xml(timeout: float = 10.0) -> bytes:
    req = Request(_RSS_URL, headers={"User-Agent": "meshtastic-bot/1.0"})
    ctx = ssl.create_default_context(cafile=certifi.where())
    with urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read()

def latest_news_title(index_from_last: int = 1) -> str:
    """
    index_from_last:
      1 = latest
      2 = 2nd latest
      ...
      clamped to max 5, and also clamped to available items
    """
    if index_from_last < 1:
        index_from_last = 1
    elif index_from_last > 5:
        index_from_last = 5

    soup = BeautifulSoup(_fetch_rss_xml(), "xml")

    matching_titles: List[str] = []
    for item in soup.find_all("item"):
        categories = [c.get_text(strip=True) for c in item.find_all("category")]
        if "Новини" not in categories:
            continue

        title_tag = item.find("title")
        if not title_tag:
            continue

        raw = title_tag.get_text(strip=True)
        t = truncate_ascii_bytes(transliterate_bg_to_en(raw), 250)
        if t:
            matching_titles.append(t)

    if not matching_titles:
        return ""

    max_valid = min(len(matching_titles), 5)
    if index_from_last > max_valid:
        index_from_last = max_valid

    return matching_titles[index_from_last - 1]