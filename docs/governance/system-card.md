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

Operators should periodically dry-run and spot-check that highlights match source titles and that disclaimers appear. There is no automated factuality benchmark in this repo.
