# Control mapping

| Requirement | Policy | Implementation |
| --- | --- | --- |
| Allowed use is news digest only | ai-use-policy.md | CLI fetch → digest → email; no other side effects |
| No secrets in git | data-handling.md | `.gitignore` `.env`; `.env.example` placeholders |
| No secrets or bodies in logs | data-handling.md | Audit line in `__init__.py`; emailer logs domain only |
| Human review | human-oversight.md | Disclaimer in every email; `--dry-run` |
| Model cannot invent URLs | system-card.md | URL allowlist in `digest.py` |
| Fallback if model fails | human-oversight.md | Headline list without LLM |
| Vendor list | vendor-inventory.md | This table plus config feeds |
| Kill switch | incident-response.md | Disable GitHub Actions workflow; rotate secrets |
| NIST functions | nist-ai-rmf-mapping.md | Documents + controls above |
| EU transparency | eu-ai-act-assessment.md | Disclaimer + AI-assisted flag when LLM used |
