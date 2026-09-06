from __future__ import annotations

import argparse
import logging

from dotenv import load_dotenv

load_dotenv()

from ai_news_aggregator.digest import build_digest
from ai_news_aggregator.emailer import send_email
from ai_news_aggregator.sources import fetch_items

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Email a daily AI governance news digest.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and build the digest without sending email.",
    )
    args = parser.parse_args(argv)

    items = fetch_items()
    digest = build_digest(items)
    logger.info(
        "audit event=digest_run items=%s used_llm=%s dry_run=%s sent=%s",
        len(items),
        digest.used_llm,
        args.dry_run,
        False,
    )
    if args.dry_run:
        logger.info("dry-run complete; email not sent")
        return
    send_email(digest.subject, digest.html, digest.text)
    logger.info(
        "audit event=digest_run items=%s used_llm=%s dry_run=%s sent=%s",
        len(items),
        digest.used_llm,
        False,
        True,
    )
