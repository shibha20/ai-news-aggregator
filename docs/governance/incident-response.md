# Incident response

Use this when secrets leak, mail goes to the wrong person, or the model behaves outside policy.

1. **Stop sending** — in GitHub, disable `.github/workflows/daily-digest.yml` (or disable Actions for the repo).
2. **Revoke Google access** — delete the Gmail app password and create a new one if needed.
3. **Revoke OpenAI** — rotate or disable `OPENAI_API_KEY`.
4. **Rotate GitHub secrets** — update `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `TO_EMAIL`, `OPENAI_API_KEY`.
5. **Check the last run** — Actions log should show audit fields only; if a body or secret was printed, treat logs as sensitive and restrict access.
6. **Notify compliance** — include time, what was sent (not a paste of secrets), and whether a third party could have received mail or API data.
7. **Resume** — only after secrets are rotated and the workflow is re-approved.
