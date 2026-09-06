# AI use policy

## Purpose

This system produces an **internal awareness digest** of public AI-governance news. It does not make legal determinations, grant access, score people, or enforce policy.

## Allowed

- Fetching public RSS/Atom headlines, links, and short snippets
- Calling a configured LLM to summarize those items for an approved recipient
- Sending the digest through the approved email account
- Running on a schedule or on demand (`workflow_dispatch`, local CLI)

## Prohibited

- Collecting or sending personal data other than the configured sender and recipient mailboxes
- Using digest output as legal advice, an official compliance decision, or an enforcement action
- Training or fine-tuning a model on repository secrets, mailbox contents, or unpublished internal documents
- Prompting the model to invent sources or URLs that were not fetched
- Logging API keys, Gmail app passwords, or full email bodies

## Output status

Every email must include a human-review disclaimer. Recipients must verify primary sources before acting.
