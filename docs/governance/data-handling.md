# Data handling

## Data in scope

| Data | Source | Retention in this app |
| --- | --- | --- |
| Headlines, links, snippets | Public RSS feeds | In memory for one run only |
| Recipient and sender addresses | Environment / GitHub secrets | Not written to disk by the app |
| Gmail app password, OpenAI API key | `.env` or GitHub Actions secrets | Never logged; never committed |
| Model output | OpenAI API response | In memory, then inserted into the email |

The application does not use a database. GitHub Actions logs retain **audit fields only** (item count, LLM vs fallback, send/dry-run). Do not enable debug logging that dumps request or email bodies.

## Secrets

- Local: `.env` (gitignored). Use `.env.example` as a template with no real values.
- CI: repository secrets `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `TO_EMAIL`, `OPENAI_API_KEY`.
- Rotate credentials after suspected exposure (see [incident response](incident-response.md)).

## Logging rules

Allowed: counts, booleans (`used_llm`, `dry_run`, `sent`), redacted recipient (domain only).

Forbidden: passwords, API keys, full email HTML/text, raw SMTP transcripts.
