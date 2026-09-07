# System card

## System

Internal CLI `ai-news-aggregator`: fetch public RSS → optional LLM digest → Gmail SMTP.

## Model

- Default: `gpt-4o-mini` via the OpenAI API (`OPENAI_MODEL` can override)
- Task: JSON digest (subject, highlights, “watch this”) from supplied items only
- Not used for: classification of people, biometrics, credit, employment, or law-enforcement decisions

## Intended behavior

- Prefer regulation, agency action, legislation, standards, and policy news
- Ignore product launches unless they have a policy angle
- Use only URLs present in the fetched item list

## Known limits

- RSS and Google News include irrelevant or duplicate items; keyword filters are coarse
- The model can mis-summarize; recipients must open the source
- Feeds can 404 or block the runner; those sources are skipped for that run
- No persistent memory across days, so the digest can repeat stories if feeds do

## Evaluation

Deterministic checks in `src/ai_news_aggregator/evaluation.py` run on every digest (including before SMTP send):

- **Critical (block send):** every fetched item is dated and inside the lookback window; item count ≤ cap; disclaimer present; subject starts with `AI Governance`; digest URLs match the fetch and use `http(s)`.
- **Warnings (logged, do not block):** digest titles overlap source headlines; at least half of entries look like governance/policy news.

`uv run pytest` covers these rules with fixtures. `uv run ai-news-aggregator --eval` scores a live fetch. There is still no automated factuality benchmark; recipients must open source links.
