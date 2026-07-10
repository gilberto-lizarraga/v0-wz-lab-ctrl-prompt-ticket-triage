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
| **Jira** | **live** | `jira_rest` descriptor + API token (primary demo path) |
| Zendesk | descriptor / mock | `generic_rest` descriptor |
| PagerDuty | descriptor / mock | `generic_rest` descriptor |
| In-house / legacy | file / mock | `generic_file` descriptor (CSV/JSON export) |
| Any (demo fallback) | `--mock` | canonical JSON loaded as if a collector produced it |

Onboarding a new source = **writing a descriptor (config), not code**. The engine never talks to
a source — only `connect` does, and everything downstream runs over the canonical JSON.

## Live Jira config (shape)

```yaml
# connections.yaml — identity + auth only, NO secrets in cleartext
version: 1
connections:
  - name: jira-sre
    descriptor: descriptors/jira_rest.yaml
    base_url: ${JIRA_BASE_URL}          # e.g. https://<org>.atlassian.net
    auth:
      method: basic                     # Jira Cloud: email + API token (basic)
      user_env: JIRA_EMAIL
      token_env: JIRA_API_TOKEN         # variable NAME, never the value
```

```yaml
# descriptors/jira_rest.yaml (excerpt)
kind: rest
transport:
  list_path: /rest/api/3/search
  query: { jql: "project = SRE AND created >= -90d" }
  record_selector: "$.issues[*]"
pagination: { style: offset, page_size_param: maxResults, page_size: 100 }
mapping:
  id:                "$.key"
  title:             "$.fields.summary"
  body:              "$.fields.description"
  created_at:        "$.fields.created"
  declared_priority: "$.fields.priority.name"
  status:            "$.fields.status.name"
  reporter:          "$.fields.reporter.displayName"
normalize:
  declared_priority: { P1: 0, P2: 1, P3: 2, P4: 3, default: 2 }  # 0 = most severe
  status:            { Open: open, "In Progress": in_progress, Done: resolved, default: open }
```

## Secret-handling rules

| Rule | Reason |
|---|---|
| Secrets referenced by **variable name**, never value | No leaks in git, logs, demo screenshots |
| `agent connect --test jira-sre` before extracting | Fails early (401 vs network vs permissions) |
| Secrets never in canonical JSON or report | Output is shareable |
| `600` on `connections.yaml`, verified at startup | World-readable credentials = incident |

## Failure handling (demo resilience)

| Failure | Behavior |
|---|---|
| Invalid token (401/403) | Abort, suggest `--test`, do **not** retry |
| Rate limit (429) | Backoff on `Retry-After`, resume from cursor |
| Network down / timeout | 3 retries → suggest `--mock` so the demo isn't blocked |
| Unknown priority value | Map to `default`, **log it** for the normalize table |

**Source:** brief §7, §11.
