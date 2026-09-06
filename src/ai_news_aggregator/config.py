from __future__ import annotations

import os
from dataclasses import dataclass


GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search?"
    "q=AI+governance+OR+%22AI+regulation%22+OR+%22EU+AI+Act%22"
    "+OR+%22AI+safety+policy%22&hl=en-US&gl=US&ceid=US:en"
)


@dataclass(frozen=True)
class Feed:
    name: str
    url: str
    keywords: tuple[str, ...] = ()


FEEDS: tuple[Feed, ...] = (
    Feed(name="Google News", url=GOOGLE_NEWS_RSS),
    Feed(
        name="Tech Policy Press",
        url="https://www.techpolicy.press/feed/",
        keywords=("ai", "artificial intelligence", "algorithm", "governance"),
    ),
    Feed(
        name="NIST News",
        url="https://www.nist.gov/news-events/news/rss.xml",
        keywords=("ai", "artificial intelligence", "machine learning"),
    ),
    Feed(
        name="OECD AI",
        url="https://wp.oecd.ai/feed/",
    ),
    Feed(
        name="EU AI Act",
        url="https://artificialintelligenceact.eu/feed/",
        keywords=("ai", "act", "regulation", "commission", "standard"),
    ),
)

LOOKBACK_HOURS = int(os.environ.get("LOOKBACK_HOURS", "24"))
MAX_ITEMS = int(os.environ.get("MAX_ITEMS", "15"))
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
HTTP_TIMEOUT = 20.0
