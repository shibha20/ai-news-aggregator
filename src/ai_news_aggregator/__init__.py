from __future__ import annotations

import argparse
import logging

from dotenv import load_dotenv

load_dotenv()

from ai_news_aggregator.digest import build_digest
from ai_news_aggregator.emailer import send_email
from ai_news_aggregator.evaluation import evaluate, format_report
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
    parser.add_argument(
        "--eval",
        action="store_true",
        help="Fetch, build, and print an evaluation report without sending email.",
    )
    args = parser.parse_args(argv)

    items = fetch_items()
    digest = build_digest(items)
    report = evaluate(digest, items)
    logger.info(
        "audit event=digest_eval critical_passed=%s warnings=%s used_llm=%s items=%s",
        report.critical_passed,
        report.warning_count,
        digest.used_llm,
        len(items),
    )
    if args.eval:
        print(format_report(report))
        if not report.critical_passed:
            raise SystemExit(1)
        return
    logger.info(
        "audit event=digest_run items=%s used_llm=%s dry_run=%s sent=%s eval_passed=%s",
        len(items),
        digest.used_llm,
        args.dry_run,
        False,
        report.critical_passed,
    )
    if not report.critical_passed:
        logger.error("digest failed evaluation; email not sent\n%s", format_report(report))
        raise SystemExit(1)
    if args.dry_run:
        logger.info("dry-run complete; email not sent")
        return
    send_email(digest.subject, digest.html, digest.text)
    logger.info(
        "audit event=digest_run items=%s used_llm=%s dry_run=%s sent=%s eval_passed=%s",
        len(items),
        digest.used_llm,
        False,
        True,
        True,
    )
