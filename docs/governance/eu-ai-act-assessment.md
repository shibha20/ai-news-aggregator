# EU AI Act assessment (working)

This is an internal working classification for **ai-news-aggregator**, not legal advice. Official text: [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj).

## What the system is

A scheduled internal tool that summarizes **public news** and emails it to a designated person. The LLM does not decide on people’s access, credit, jobs, or legal status.

## Working classification

| Question | This system |
| --- | --- |
| Prohibited AI (e.g. social scoring, untargeted scraping of faces for a recognition database)? | No |
| Annex III high-risk (biometrics, critical infrastructure, employment, essential services, law enforcement, etc.)? | **No — not in those use cases** |
| GPAI model provider? | No — we are a **deployer** of a third-party model API |
| Consumer-facing chatbot? | No |

Treat the digest as **low / transparency-oriented** use: tell the recipient when content is AI-generated, keep a human in the loop, and do not use output as an automated decision.

If product scope changes (public app, HR screening, customer decisions), **re-open this assessment** before shipping.

## Transparency steps implemented in product

- Email disclaimer: not legal advice; AI-assisted when the LLM ran; human review required
- Headline fallback if the model is unused or fails
- Links restricted to fetched sources

## Documentation we keep (Art. 11-style, scaled down)

System card, data handling, vendor inventory, and this file. We do not maintain Annex IV-level technical documentation because we do not treat this as a high-risk system.
