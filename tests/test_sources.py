from __future__ import annotations

from datetime import datetime, timezone

from ai_news_aggregator.config import Feed
from ai_news_aggregator.sources import _fetch_feed

RSS = b"""<?xml version="1.0"?>
<rss version="2.0"><channel>
<title>Test</title>
<item>
  <title>EU AI Act update</title>
  <link>https://example.com/new</link>
  <pubDate>Sun, 06 Sep 2026 16:00:00 GMT</pubDate>
</item>
<item>
  <title>Old regulation story</title>
  <link>https://example.com/old</link>
  <pubDate>Wed, 01 Jan 2020 12:00:00 GMT</pubDate>
</item>
<item>
  <title>Undated AI Act item</title>
  <link>https://example.com/undated</link>
</item>
</channel></rss>
"""


class _FakeResponse:
    content = RSS

    def raise_for_status(self) -> None:
        return None


class _FakeClient:
    def get(self, url: str, headers: dict[str, str] | None = None) -> _FakeResponse:
        return _FakeResponse()


def test_fetch_drops_undated_and_stale_entries() -> None:
    cutoff = datetime(2026, 9, 5, 18, 0, tzinfo=timezone.utc)
    feed = Feed(name="Test", url="https://example.com/feed")
    items = _fetch_feed(_FakeClient(), feed, cutoff)  # type: ignore[arg-type]
    urls = {item.url for item in items}
    assert urls == {"https://example.com/new"}
