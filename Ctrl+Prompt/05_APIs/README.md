# 05_APIs — What's live vs mocked

> Source: brief §7, §11 (fully answered). ⚠️ Confirm the dev/sandbox **Jira token** is actually
> available before build day.

## Decision

- **Ticket source:** **Jira** is the primary, in-scope source. The team has no easy ServiceNow
  access, so Jira is the guaranteed live integration.
- **For the demo:** connect **LIVE** to a dev/sandbox Jira board via an API token. Do **not**
  mock Jira as the default path.
- **LLM backend:** clustering / RCA / playbook generation runs on an LLM (e.g. **Amazon Bedrock**
  or similar).

## Multi-source `connect` layer (kept in scope)

Jira is live and primary, but the core pain is **cross-source blindness** — the same root cause
surfacing in Jira, Zendesk and PagerDuty without anyone noticing. So the integration is built as
a **source-agnostic `connect` layer**, not a hardcoded Jira client:

| Source | Mode | How |
|---|---|---|
| **Jira** | **live** | `jira_rest` descriptor + API token (primary demo path). Implemented via `urllib` — real HTTP, Basic auth, offset pagination. |
| Zendesk / PagerDuty | descriptor / mock | Copy `jira_rest.json`, edit paths + normalize tables |
| In-house / legacy | file | `jira_csv.json` descriptor — CSV/JSON/NDJSON export (implemented) |
| Any (demo fallback) | `--mock` | canonical JSON loaded as if a collector produced it |

Onboarding a new source = **writing a descriptor (config), not code**. The engine never talks to
a source — only `connect` does, and everything downstream runs over the canonical JSON.

> **Config format:** JSON is the shipped default (`connections.json`, `descriptors/*.json`,
> `taxonomy.json`) so the tool runs on the stdlib with zero installs. YAML is auto-detected and
> used if PyYAML is present.

## Live Jira config (shape)

```jsonc
// connections.json — identity + auth only, NO secrets in cleartext. chmod 600.
{
  "version": 1,
  "connections": [
    { "name": "jira-sre",
      "descriptor": "descriptors/jira_rest.json",
      "base_url": "${JIRA_BASE_URL}",                 // e.g. https://<org>.atlassian.net
      "auth": {"method": "basic",                     // Jira Cloud: email + API token
               "user_env": "JIRA_EMAIL",
               "token_env": "JIRA_API_TOKEN"},         // variable NAME, never the value
      "vars": {"JIRA_PROJECT": "SRE", "SINCE": "90d"} }
  ]
}
```

## Multiple accounts / companies

Each connection is an **independent account/company**: its own `base_url`, its own credential env
vars, and its own Jira project. Two ways to set the project:

```jsonc
{ "name": "acme-jira", "base_url": "https://acme.atlassian.net",
  "auth": {"method":"basic","user_env":"ACME_JIRA_EMAIL","token_env":"ACME_JIRA_TOKEN"},
  "query": {"jql": "project = OPS AND created >= -30d"} }   // project via JQL override
{ "name": "globex-jira", "base_url": "https://globex.atlassian.net",
  "auth": {"method":"basic","user_env":"GLOBEX_JIRA_EMAIL","token_env":"GLOBEX_JIRA_TOKEN"},
  "vars": {"JIRA_PROJECT": "SUPPORT"} }                     // project via a variable
```

`agent connect --test <name>` prints the resolved URL + JQL before any network call, so you can
confirm the right company and project. `${VAR}` lookup order: environment → connection `vars` → default.

## Secret-handling rules

| Rule | Reason |
|---|---|
| Secrets referenced by **variable name**, never value | No leaks in git, logs, demo screenshots |
| `agent connect --test jira-sre` before extracting | Fails early (401 vs network vs permissions) |
| Secrets never in canonical JSON or report | Output is shareable |
| `600` on `connections.json`, verified at startup | World-readable credentials = incident |

## Failure handling (demo resilience)

| Failure | Behavior |
|---|---|
| Invalid token (401/403) | Abort, suggest `--test`, do **not** retry |
| Rate limit (429) | Backoff on `Retry-After`, resume from cursor |
| Network down / timeout | 3 retries → suggest `--mock` so the demo isn't blocked |
| Unknown priority value | Map to `default`, **log it** for the normalize table |

**Source:** brief §7, §11.
