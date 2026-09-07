from __future__ import annotations

from ai_news_aggregator.config import LOOKBACK_HOURS
from ai_news_aggregator.digest import _empty_digest


def test_empty_digest_uses_configured_lookback() -> None:
    digest = _empty_digest()
    assert str(LOOKBACK_HOURS) in digest.subject
    assert str(LOOKBACK_HOURS) in digest.text
    assert digest.used_llm is False
    assert digest.highlights == ()
