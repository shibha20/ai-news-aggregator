from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage

from ai_news_aggregator.config import SMTP_HOST, SMTP_PORT
from ai_news_aggregator.governance import recipient_log_label

logger = logging.getLogger(__name__)


def send_email(subject: str, html: str, text: str) -> None:
    user = os.environ.get("GMAIL_USER", "").strip()
    password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
    to_email = os.environ.get("TO_EMAIL", "").strip()
    missing = [
        name
        for name, value in (
            ("GMAIL_USER", user),
            ("GMAIL_APP_PASSWORD", password),
            ("TO_EMAIL", to_email),
        )
        if not value
    ]
    if missing:
        raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = user
    message["To"] = to_email
    message.set_content(text)
    message.add_alternative(html, subtype="html")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(message)
    logger.info("audit event=email_sent recipient=%s", recipient_log_label(to_email))
