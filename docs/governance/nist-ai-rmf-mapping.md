# NIST AI Risk Management Framework mapping

This maps **this digest agent** to NIST AI RMF 1.0 functions. It is a control narrative, not a certification. Primary source: [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework).

## GOVERN

- Written policies live in this directory; README points here.
- Owners: engineering (system), compliance (approval).
- Vendors and secrets are listed; production sends use GitHub secrets, not committed files.

## MAP

- Purpose: internal news awareness ([system card](system-card.md)).
- Users: configured mailbox only; not a public product.
- Risks: misleading summary, secret leakage, unsolicited or misdirected email, over-reliance as legal advice.
- Data: public RSS plus mail/API credentials ([data handling](data-handling.md)).

## MEASURE

- Audit log per run: item count, `used_llm`, `dry_run`, `sent` (no email body, no secrets).
- URL allowlist against fetched items.
- Fallback path when the model fails.
- Operators can `--dry-run` before enabling cron.

## MANAGE

- Disclaimer on every email; human review required.
- Incident steps to disable workflow and rotate keys.
- Change the model, feeds, or vendors only with a policy review.
