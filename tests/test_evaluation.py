from __future__ import annotations  # allow list[Item] style type hints

from datetime import datetime, timedelta, timezone  # build a frozen "now" and item ages

from ai_news_aggregator.digest import Digest, _fallback_digest  # email shape + no-LLM headline path
from ai_news_aggregator.evaluation import evaluate  # the scoring function under test
from ai_news_aggregator.governance import attach_disclaimer  # adds the required human-review footer
from ai_news_aggregator.sources import Item  # one fetched RSS story

# Frozen clock so lookback (default 24h) does not depend on when pytest runs.
NOW = datetime(2026, 9, 6, 18, 0, tzinfo=timezone.utc)


def _item(
    *,
    title: str = "EU AI Act guidance published",  # on-topic default headline
    url: str = "https://example.com/eu-ai-act",  # default fetched URL
    hours_ago: int = 2,  # default: inside the 24h window
) -> Item:
    # One fake RSS item tests can tweak (title, url, age).
    return Item(
        title=title,
        url=url,
        source="Test Feed",
        published=NOW - timedelta(hours=hours_ago),  # timestamp relative to NOW
        summary="The Commission published new AI Act guidance.",  # on-topic blurb
    )


def test_fallback_digest_passes_critical_checks() -> None:
    # Happy path: a real governance story should be allowed to send.
    items = [_item()]  # one in-window, on-topic fetch
    digest = _fallback_digest(items)  # headline email, no LLM
    report = evaluate(digest, items, now=NOW)  # score digest vs fetch
    assert report.critical_passed  # SMTP would be allowed
    by_name = {check.name: check for check in report.checks}  # look up checks by name
    assert by_name["disclaimer"].passed  # footer is present
    assert by_name["url_allowlist"].passed  # links match the fetch
    assert by_name["governance_relevance"].passed  # text looks like policy news


def test_invented_url_fails_allowlist() -> None:
    # The model (or a bug) linked a URL that was never fetched.
    items = [_item()]  # fetch only has example.com/eu-ai-act
    highlights = (
        {
            "title": "EU AI Act guidance published",
            "summary": "Policy update.",
            "source": "Test Feed",
            "url": "https://evil.example/not-fetched",  # not in items → must fail allowlist
        },
    )
    html, text = attach_disclaimer("<p>x</p>", "x", used_llm=True)  # valid disclaimer so only URL fails
    digest = Digest(
        subject="AI Governance: test",  # valid subject prefix
        html=html,
        text=text,
        used_llm=True,
        highlights=highlights,  # digest entries with the invented URL
    )
    report = evaluate(digest, items, now=NOW)
    assert not report.critical_passed  # send must be blocked
    assert not next(check for check in report.checks if check.name == "url_allowlist").passed


def test_missing_disclaimer_fails() -> None:
    # Same good story, but the email body omitted the required disclaimer.
    items = [_item()]
    digest = Digest(
        subject="AI Governance: test",
        html="<p>no disclaimer</p>",  # missing required footer in HTML
        text="no disclaimer",  # missing required footer in plain text
        used_llm=True,
        highlights=(
            {
                "title": items[0].title,  # title matches fetch
                "summary": items[0].summary,
                "source": items[0].source,
                "url": items[0].url,  # URL matches fetch (allowlist OK)
            },
        ),
    )
    report = evaluate(digest, items, now=NOW)
    assert not report.critical_passed  # send must be blocked
    assert not next(check for check in report.checks if check.name == "disclaimer").passed


def test_product_launch_warns_on_relevance() -> None:
    # Off-topic product news: warn, but do not block send.
    items = [
        Item(
            title="Acme Phone 17 goes on sale tomorrow",  # not governance
            url="https://example.com/phone",
            source="Test Feed",
            published=NOW - timedelta(hours=2),  # still in the lookback window
            summary="Preorder the new flagship camera phone.",  # no policy terms
        )
    ]
    digest = _fallback_digest(items)  # still has disclaimer + allowlisted URL
    report = evaluate(digest, items, now=NOW)
    assert report.critical_passed  # email is still allowed
    relevance = next(check for check in report.checks if check.name == "governance_relevance")
    assert not relevance.passed  # relevance check should fail
    assert report.warning_count >= 1  # that failure is a warning, not critical


def test_undated_and_stale_items_fail() -> None:
    # Fetch quality: old and undated RSS items must fail critical item checks.
    stale = _item(url="https://example.com/old", hours_ago=48)  # older than 24h lookback
    undated = Item(
        title="EU AI Act guidance published",
        url="https://example.com/undated",
        source="Test Feed",
        published=None,  # no timestamp → must fail item_dates
        summary="Policy update.",
    )
    digest = _fallback_digest([stale, undated])
    report = evaluate(digest, [stale, undated], now=NOW)
    assert not report.critical_passed  # send must be blocked
    by_name = {check.name: check for check in report.checks}
    assert not by_name["item_dates"].passed  # undated item
    assert not by_name["lookback_window"].passed  # 48h-old item
