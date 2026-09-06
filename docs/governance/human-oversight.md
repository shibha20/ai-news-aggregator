# Human oversight

This agent **sends mail**. It does not close tickets, change access, or file regulatory notices.

## Controls

1. **Human recipient** — a person must read the digest and check original links before acting.
2. **Disclaimer** — every message states that the content is not legal advice and is AI-assisted when the LLM ran.
3. **Headline fallback** — if the model is down or the key is missing, the email is a list of fetched headlines, not a model narrative.
4. **URL allowlist** — model-proposed links are dropped unless they match a URL from the fetch step.
5. **Dry-run** — `uv run ai-news-aggregator --dry-run` builds the digest and writes audit logs without SMTP.
6. **Manual run** — GitHub Actions `workflow_dispatch` can be used instead of or in addition to the cron schedule.
7. **Kill switch** — disable the workflow and revoke secrets (see [incident response](incident-response.md)).

## Roles

- **Operator:** runs or schedules the job; keeps secrets.
- **Recipient:** reviews the email.
- **Compliance:** approves this pack and any change in purpose, vendors, or model.
