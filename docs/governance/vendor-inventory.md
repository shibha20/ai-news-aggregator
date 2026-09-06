# Vendor inventory

| Vendor | Role | Data sent | Notes |
| --- | --- | --- | --- |
| RSS publishers (Google News, Tech Policy Press, NIST, OECD AI, EU AI Act site, others in config) | News sources | HTTP GET from the runner; publishers see the runner IP and User-Agent | Public web content |
| OpenAI | Optional summarization | Titles, URLs, snippets, system prompt | Disabled if `OPENAI_API_KEY` is unset; headline fallback still sends |
| Google (Gmail SMTP) | Email delivery | Digest subject and body, sender/recipient | App password, not the account login password |
| GitHub | Schedule, secrets, audit logs | Workflow metadata and the audit log lines we print | Disable the workflow to stop sends |

Compliance should keep separate DPAs / SCCs with OpenAI and Google as required by your organization. This inventory only describes **this repository’s** data flow.
