# AI governance (this project)

This folder is the compliance pack for **ai-news-aggregator**: an internal daily digest that fetches public RSS items, optionally summarizes them with a hosted LLM, and emails the result.

It is **not** a substitute for legal sign-off, a DPIA, vendor DPAs, or your organization’s official policy library. Engineering owns the code; the compliance team owns approval of these documents.

## Documents

| Document | What it is |
| --- | --- |
| [AI use policy](ai-use-policy.md) | Allowed and prohibited uses of the agent |
| [Data handling](data-handling.md) | What data is processed, stored, and logged |
| [Vendor inventory](vendor-inventory.md) | Third parties and data leaving the environment |
| [Human oversight](human-oversight.md) | Who reviews output; dry-run and fallback |
| [System card](system-card.md) | Model, prompt intent, known limits, evaluation gates |
| [Incident response](incident-response.md) | How to shut off keys and the daily job |
| [NIST AI RMF mapping](nist-ai-rmf-mapping.md) | GOVERN / MAP / MEASURE / MANAGE for this system |
| [EU AI Act assessment](eu-ai-act-assessment.md) | Working classification and transparency steps |
| [Official references](official-references.md) | Links to NIST, EU, and related primary sources |
| [Control mapping](control-mapping.md) | Policy claims mapped to code |

## Owners

- **System owner:** engineering (this repository)
- **Policy owner:** compliance team
- **Review cadence:** at least when the model, vendors, or data flows change
