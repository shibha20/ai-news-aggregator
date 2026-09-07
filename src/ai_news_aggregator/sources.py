from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from time import struct_time
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import feedparser
import httpx

from ai_news_aggregator.config import FEEDS, HTTP_TIMEOUT, LOOKBACK_HOURS, MAX_ITEMS, Feed

logger = logging.getLogger(__name__)

_TRACKING_PARAMS = frozenset(
    {
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "fbclid",
        "gclid",
    }
)


@dataclass(frozen=True)
class Item:
    title: str
    url: str
    source: str
    published: datetime | None
    summary: str


def fetch_items() -> list[Item]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    items: list[Item] = []
    with httpx.Client(timeout=HTTP_TIMEOUT, follow_redirects=True) as client:
        for feed in FEEDS:
            items.extend(_fetch_feed(client, feed, cutoff))
    return _dedupe(items)[:MAX_ITEMS]


def _fetch_feed(client: httpx.Client, feed: Feed, cutoff: datetime) -> list[Item]:
    try:
        response = client.get(feed.url, headers={"User-Agent": "ai-news-aggregator/0.1"})
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Failed to fetch feed %s: %s", feed.name, exc)
        return []

    parsed = feedparser.parse(response.content)
    items: list[Item] = []
    for entry in parsed.entries:
        title = _text(getattr(entry, "title", ""))
        url = _text(getattr(entry, "link", ""))
        if not title or not url:
            continue
        if feed.keywords and not _matches_keywords(f"{title} {_text(getattr(entry, 'summary', ''))}", feed.keywords):
            continue
        published = _entry_datetime(entry)
        if published is None or published < cutoff:
            continue
        items.append(
            Item(
                title=title,
                url=url,
                source=feed.name,
                published=published,
                summary=_strip_tags(_text(getattr(entry, "summary", "")))[:400],
            )
        )
    return items


def _entry_datetime(entry: object) -> datetime | None:
    parsed_struct = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if isinstance(parsed_struct, struct_time):
        return datetime(*parsed_struct[:6], tzinfo=timezone.utc)
    raw = getattr(entry, "published", None) or getattr(entry, "updated", None)
    if isinstance(raw, str) and raw:
        try:
            dt = parsedate_to_datetime(raw)
        except (TypeError, ValueError):
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    return None


def _matches_keywords(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


def _dedupe(items: list[Item]) -> list[Item]:
    items.sort(key=lambda item: item.published or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    unique: list[Item] = []
    for item in items:
        url_key = _normalize_url(item.url)
        title_key = re.sub(r"\s+", " ", item.title).strip().lower()
        if url_key in seen_urls or title_key in seen_titles:
            continue
        seen_urls.add(url_key)
        seen_titles.add(title_key)
        unique.append(item)
    return unique


def _normalize_url(url: str) -> str:
    parts = urlparse(url)
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() not in _TRACKING_PARAMS
    ]
    return urlunparse(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path.rstrip("/"),
            parts.params,
            urlencode(query),
            "",
        )
    )


def _text(value: object) -> str:
    return str(value or "").strip()


def _strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value).strip()
