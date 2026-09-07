from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from html import escape
from urllib.parse import urlparse

from ai_news_aggregator.config import LOOKBACK_HOURS, MAX_ITEMS
from ai_news_aggregator.digest import Digest
from ai_news_aggregator.governance import disclaimer_text
from ai_news_aggregator.sources import Item

_GOVERNANCE_TERMS = (
    "ai",
    "artificial intelligence",
    "algorithm",
    "governance",
    "regulation",
    "eu ai act",
    "nist",
    "oecd",
    "policy",
    "legislation",
    "legislative",
    "commission",
    "standard",
    "safety",
    "oversight",
    "compliance",
    "executive order",
    "copyright",
    "privacy",
)

_ALLOWED_SCHEMES = frozenset({"http", "https"})


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    severity: str
    detail: str


@dataclass(frozen=True)
class EvalReport:
    checks: tuple[Check, ...]

    @property
    def critical_passed(self) -> bool:
        return all(check.passed for check in self.checks if check.severity == "critical")

    @property
    def warning_count(self) -> int:
        return sum(1 for check in self.checks if check.severity == "warning" and not check.passed)


def evaluate(digest: Digest, items: list[Item], *, now: datetime | None = None) -> EvalReport:
    """Score a digest against fetch invariants and governance rules."""
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=LOOKBACK_HOURS)
    checks = (
        *_item_checks(items, cutoff),
        *_digest_checks(digest, items),
    )
    return EvalReport(checks=checks)


def format_report(report: EvalReport) -> str:
    lines = []
    for check in report.checks:
        status = "PASS" if check.passed else check.severity.upper()
        lines.append(f"{status} {check.name}: {check.detail}")
    lines.append(f"critical_passed={report.critical_passed} warnings={report.warning_count}")
    return "\n".join(lines)


def _item_checks(items: list[Item], cutoff: datetime) -> tuple[Check, ...]:
    undated = [item.url for item in items if item.published is None]
    stale = [
        item.url
        for item in items
        if item.published is not None and item.published < cutoff
    ]
    return (
        Check(
            name="item_dates",
            passed=not undated,
            severity="critical",
            detail="all fetched items have a publish time"
            if not undated
            else f"undated items: {len(undated)}",
        ),
        Check(
            name="lookback_window",
            passed=not stale,
            severity="critical",
            detail=f"all items are within {LOOKBACK_HOURS} hours"
            if not stale
            else f"stale items: {len(stale)}",
        ),
        Check(
            name="item_cap",
            passed=len(items) <= MAX_ITEMS,
            severity="critical",
            detail=f"{len(items)} items (cap {MAX_ITEMS})",
        ),
    )


def _digest_checks(digest: Digest, items: list[Item]) -> tuple[Check, ...]:
    entries = (*digest.highlights, *digest.watch)
    allowed_urls = {item.url for item in items}
    by_url = {item.url: item for item in items}
    notice = disclaimer_text(used_llm=digest.used_llm)
    invented = [entry["url"] for entry in entries if entry["url"] not in allowed_urls]
    bad_schemes = [
        entry["url"]
        for entry in entries
        if urlparse(entry["url"]).scheme.lower() not in _ALLOWED_SCHEMES
    ]
    ungrounded = [
        entry["url"]
        for entry in entries
        if entry["url"] in by_url and not _grounded(entry, by_url[entry["url"]])
    ]
    relevant = [entry for entry in entries if _governance_related(entry)]
    relevance_ok = not entries or (len(relevant) / len(entries) >= 0.5)
    return (
        Check(
            name="disclaimer",
            passed=notice in digest.text and escape(notice) in digest.html,
            severity="critical",
            detail="human-review disclaimer present with matching LLM/fallback wording",
        ),
        Check(
            name="subject",
            passed=digest.subject.startswith("AI Governance"),
            severity="critical",
            detail=digest.subject or "(empty subject)",
        ),
        Check(
            name="url_allowlist",
            passed=not invented,
            severity="critical",
            detail="all digest URLs came from the fetch"
            if not invented
            else f"invented URLs: {len(invented)}",
        ),
        Check(
            name="url_scheme",
            passed=not bad_schemes,
            severity="critical",
            detail="digest links are http(s)"
            if not bad_schemes
            else f"non-http URLs: {len(bad_schemes)}",
        ),
        Check(
            name="groundedness",
            passed=not ungrounded,
            severity="warning",
            detail="digest titles overlap the source headlines"
            if not ungrounded
            else f"weak title match: {len(ungrounded)}",
        ),
        Check(
            name="governance_relevance",
            passed=relevance_ok,
            severity="warning",
            detail=(
                "no digest entries to score"
                if not entries
                else f"{len(relevant)}/{len(entries)} entries look like governance news"
            ),
        ),
    )


def _grounded(entry: dict[str, str], item: Item) -> bool:
    title = entry["title"].lower()
    source = item.title.lower()
    if source in title or title in source:
        return True
    if SequenceMatcher(None, title, source).ratio() >= 0.4:
        return True
    title_tokens = _tokens(entry["title"])
    source_tokens = _tokens(f"{item.title} {item.summary}")
    if not title_tokens:
        return False
    return len(title_tokens & source_tokens) / len(title_tokens) >= 0.3


def _governance_related(entry: dict[str, str]) -> bool:
    blob = f"{entry['title']} {entry['summary']}".lower()
    for term in _GOVERNANCE_TERMS:
        if " " in term or len(term) > 3:
            if term in blob:
                return True
        elif re.search(rf"\b{re.escape(term)}\b", blob):
            return True
    return False


def _tokens(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", value.lower()) if len(token) > 3}
