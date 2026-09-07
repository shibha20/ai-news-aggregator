from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from html import escape

from openai import OpenAI

from ai_news_aggregator.config import LOOKBACK_HOURS, OPENAI_MODEL
from ai_news_aggregator.governance import attach_disclaimer
from ai_news_aggregator.sources import Item

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You write a daily AI governance email digest.
Focus on regulation, agency action, legislation, standards, and policy.
Ignore product launches unless they have a clear policy angle.
Return JSON only with this shape:
{
  "subject": "short subject line starting with AI Governance:",
  "highlights": [{"title": "", "summary": "", "source": "", "url": ""}],
  "watch_this": [{"title": "", "summary": "", "source": "", "url": ""}]
}
Use 5-8 highlights. Use watch_this for bills, agency actions, and standards work.
Every item must include a real url from the provided sources.
"""


@dataclass(frozen=True)
class Digest:
    subject: str
    html: str
    text: str
    used_llm: bool
    highlights: tuple[dict[str, str], ...] = ()
    watch: tuple[dict[str, str], ...] = ()


def build_digest(items: list[Item]) -> Digest:
    if not items:
        return _empty_digest()
    if os.environ.get("OPENAI_API_KEY"):
        try:
            return _llm_digest(items)
        except Exception:
            logger.exception("LLM digest failed; using headline fallback")
    return _fallback_digest(items)


def _llm_digest(items: list[Item]) -> Digest:
    client = OpenAI()
    payload = [
        {
            "title": item.title,
            "url": item.url,
            "source": item.source,
            "published": item.published.isoformat() if item.published else None,
            "summary": item.summary,
        }
        for item in items
    ]
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": "Stories from the last day:\n" + json.dumps(payload, indent=2),
            },
        ],
    )
    content = response.choices[0].message.content or "{}"
    data = json.loads(content)
    allowed_urls = {item.url for item in items}
    highlights = _allowlisted(_normalize_entries(data.get("highlights")), allowed_urls)
    watch = _allowlisted(_normalize_entries(data.get("watch_this")), allowed_urls)
    if not highlights:
        return _fallback_digest(items)
    subject = str(data.get("subject") or "").strip() or _default_subject()
    html, text = attach_disclaimer(
        _render_html(highlights, watch),
        _render_text(highlights, watch),
        used_llm=True,
    )
    return Digest(
        subject=subject,
        html=html,
        text=text,
        used_llm=True,
        highlights=tuple(highlights),
        watch=tuple(watch),
    )


def _fallback_digest(items: list[Item]) -> Digest:
    highlights = [
        {
            "title": item.title,
            "summary": item.summary or "Open the link for details.",
            "source": item.source,
            "url": item.url,
        }
        for item in items[:8]
    ]
    html, text = attach_disclaimer(
        _render_html(highlights, []),
        _render_text(highlights, []),
        used_llm=False,
    )
    return Digest(
        subject=_default_subject(),
        html=html,
        text=text,
        used_llm=False,
        highlights=tuple(highlights),
    )


def _empty_digest() -> Digest:
    subject = f"AI Governance: no notable items in the last {LOOKBACK_HOURS} hours"
    body = (
        "No recent AI governance stories were found in the configured feeds "
        f"for the last {LOOKBACK_HOURS} hours."
    )
    html, text = attach_disclaimer(f"<p>{escape(body)}</p>", body, used_llm=False)
    return Digest(subject=subject, html=html, text=text, used_llm=False)


def _allowlisted(entries: list[dict[str, str]], allowed_urls: set[str]) -> list[dict[str, str]]:
    return [entry for entry in entries if entry["url"] in allowed_urls]


def _normalize_entries(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    entries: list[dict[str, str]] = []
    for raw in value:
        if not isinstance(raw, dict):
            continue
        title = str(raw.get("title") or "").strip()
        url = str(raw.get("url") or "").strip()
        if not title or not url:
            continue
        entries.append(
            {
                "title": title,
                "summary": str(raw.get("summary") or "").strip(),
                "source": str(raw.get("source") or "").strip(),
                "url": url,
            }
        )
    return entries


def _render_html(highlights: list[dict[str, str]], watch: list[dict[str, str]]) -> str:
    parts = ["<h2>Highlights</h2>", "<ul>"]
    parts.extend(_html_items(highlights))
    parts.append("</ul>")
    if watch:
        parts.extend(["<h2>Watch this</h2>", "<ul>"])
        parts.extend(_html_items(watch))
        parts.append("</ul>")
    return "\n".join(parts)


def _html_items(entries: list[dict[str, str]]) -> list[str]:
    lines: list[str] = []
    for entry in entries:
        source = f" ({escape(entry['source'])})" if entry["source"] else ""
        summary = f"<br>{escape(entry['summary'])}" if entry["summary"] else ""
        lines.append(
            "<li>"
            f'<a href="{escape(entry["url"], quote=True)}">{escape(entry["title"])}</a>'
            f"{source}{summary}"
            "</li>"
        )
    return lines


def _render_text(highlights: list[dict[str, str]], watch: list[dict[str, str]]) -> str:
    lines = ["Highlights", ""]
    lines.extend(_text_items(highlights))
    if watch:
        lines.extend(["", "Watch this", ""])
        lines.extend(_text_items(watch))
    return "\n".join(lines)


def _text_items(entries: list[dict[str, str]]) -> list[str]:
    lines: list[str] = []
    for entry in entries:
        source = f" ({entry['source']})" if entry["source"] else ""
        lines.append(f"- {entry['title']}{source}")
        if entry["summary"]:
            lines.append(f"  {entry['summary']}")
        lines.append(f"  {entry['url']}")
        lines.append("")
    return lines


def _default_subject() -> str:
    return "AI Governance daily digest"
