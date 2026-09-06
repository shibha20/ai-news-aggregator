# Daily AI governance email

Fetches recent AI-governance stories from RSS feeds, writes a short digest, and emails it through Gmail SMTP. GitHub Actions can run the same command every day at 12:00 UTC.

## Local run

```bash
uv sync
cp .env.example .env
```

Edit `.env` with your Gmail address, [Google app password](https://myaccount.google.com/apppasswords), recipient, and OpenAI key. Then:

```bash
uv run ai-news-aggregator
```

`.env` is gitignored. Do not commit it.

If `OPENAI_API_KEY` is missing or the model call fails, the email still goes out as a headline list.

Dry-run (no SMTP):

```bash
uv run ai-news-aggregator --dry-run
```

## Governance

Compliance documents for this system (use policy, data handling, NIST AI RMF mapping, EU AI Act working assessment, official source links, and control mapping) are in [docs/governance/](docs/governance/README.md).

Every email includes a human-review disclaimer. LLM-proposed links are dropped unless they match a fetched RSS URL. Logs record item counts and send/dry-run flags, not secrets or message bodies.

## Gmail app password

1. Turn on 2-Step Verification for the sending Google account.
2. Create an app password at https://myaccount.google.com/apppasswords
3. Use that 16-character password as `GMAIL_APP_PASSWORD`, not your normal login password.

## GitHub Actions

Add these repository secrets (Settings → Secrets and variables → Actions):

- `GMAIL_USER`
- `GMAIL_APP_PASSWORD`
- `TO_EMAIL`
- `OPENAI_API_KEY`

The workflow in `.github/workflows/daily-digest.yml` runs on a schedule (`0 12 * * *`) and can also be started from the Actions tab (Run workflow).

## Feeds

Edit `src/ai_news_aggregator/config.py` to change lookback hours, item cap, model name, or RSS sources. Defaults include Google News (AI governance / regulation / EU AI Act / AI safety policy), Tech Policy Press, NIST, OECD AI, and artificialintelligenceact.eu.
