# Jira Cloud MCP — AI-Powered Jira Cloud Administration

[![MCP](https://img.shields.io/badge/MCP-Model_Context_Protocol-blue)](https://modelcontextprotocol.io)
[![Jira Cloud](https://img.shields.io/badge/Jira_Cloud-Atlassian-0052CC)](https://www.atlassian.com/software/jira)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-brightgreen)](LICENSE)

> **MCP server** that gives AI assistants full read/write access to your Jira Cloud instance — issues, workflows, screens, schemes, permissions, security levels, users, groups, automation rules, and audit logs. **86 tools** via Jira Cloud REST API v3.

## What is this?

A **Model Context Protocol (MCP) server** for **Jira Cloud** that allows AI assistants like **Claude Desktop**, **Claude Code**, **n8n**, **Open WebUI**, **Cursor**, **Windsurf**, or any MCP-compatible client to **analyze and modify your Jira Cloud configuration**.

Instead of clicking through dozens of admin screens:
- *"Which projects use the default workflow scheme?"*
- *"Show me all custom fields unused in any screen"*
- *"What permission schemes grant Browse Projects to anonymous?"*
- *"Create a new issue type and add it to project X"*
- *"Disable automation rule #42 in project SOS"*

## Key Features

- **86 tools** — read + write in a single MCP (no separate analyst/admin)
- **Zero plugins** — works directly with Jira Cloud REST API v3
- **Rate-limit aware** — automatic retry with backoff on 429 responses
- **Issue CRUD** — create, update, transition, assign, comment, link, delete, bulk transition
- **Full scheme inspection** — permission, notification, workflow, screen, field config, issue security, issue type schemes
- **Security levels** — read security schemes with level members
- **Project roles & access** — view/modify role membership
- **Automation rules** — list, inspect, enable, disable (native Jira automation)
- **Audit log** — read admin actions with date/user filtering
- **Works with any MCP client** — Claude Desktop, Claude Code, n8n, Open WebUI (MCPO), OpenCode, Cursor, Windsurf

## Companion: Jira DC MCP Servers

For **Jira Data Center** (on-premise), use the companion servers:
- 👉 **[jira-analyst-mcp](https://github.com/aforbco/Jira-DC-MCP-analyst)** — 79 read-only analysis tools
- 👉 **[jira-admin-mcp](https://github.com/aforbco/Jira-DC-MCP-admin)** — 91 write/admin tools

## Architecture

```
Claude / AI Agent → MCP Server (Python/stdio or SSE) → Jira Cloud REST API v3
```

No Groovy, no ScriptRunner, no plugins — pure REST API.

## Tools (86 total)

| Domain | Tools | Capabilities |
|---|---|---|
| Issues | `jql_search`, `get_issue`, `create_issue`, `update_issue`, `transition_issue`, `assign_issue`, `add_comment`, `get_issue_comments`, `get_issue_changelog`, `get_issue_transitions`, `get_issue_worklogs`, `add_worklog`, `link_issues`, `delete_issue`, `bulk_transition` | Full CRUD, JQL, transitions, comments, changelog, worklogs, links |
| Custom Fields | `list_custom_fields`, `get_custom_field`, `get_field_options`, `create_custom_field`, `update_custom_field`, `delete_custom_field`, `add_field_option`, `list_system_fields` | CRUD, contexts, options |
| Workflows | `list_workflows`, `get_workflow`, `list_statuses`, `list_workflow_schemes`, `get_workflow_scheme`, `list_priorities`, `list_resolutions`, `list_issue_types`, `list_issue_link_types` | Workflows, statuses, priorities, resolutions |
| Schemes | `list/get_permission_schemes`, `create_permission_scheme`, `add_permission_grant`, `list/get_notification_schemes`, `list/get_issue_security_schemes`, `list/get_issue_type_schemes`, `list/get_field_configurations`, `list_field_config_schemes` | All scheme types with grants/levels |
| Projects | `create_project`, `list_project_templates`, `list_projects`, `get_project`, `get_project_config`, `get_project_roles`, `add/remove_project_role_member`, `list_project_roles_global`, `create/list_components`, `create/list_versions` | Create projects, full management |
| Screens | `list_screens`, `get_screen`, `create_screen`, `add/remove_field_to/from_screen`, `list_screen_schemes`, `list_issue_type_screen_schemes` | Screen CRUD, field management |
| Users & Groups | `search_users`, `get_user`, `list_groups`, `get_group_members`, `create_group`, `add/remove_user_to/from_group`, `get_myself` | User lookup, group management |
| Automation | `list_automation_rules`, `get_automation_rule`, `enable_automation_rule`, `disable_automation_rule` | Native Jira automation |
| Admin | `get_server_info`, `get_audit_log`, `list_shared_filters`, `get_filter`, `list/get_dashboards`, `list_project_categories`, `list_event_types`, `get_global_permissions`, `get_application_properties` | Server info, audit, filters, dashboards |

## Setup

### 1. Get API Token

Go to [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens) and create a token.

### 2. Install

```bash
git clone https://github.com/aforbco/Jira-cloud-mcp.git
cd Jira-cloud-mcp
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Jira URL, email, and API token
```

### 3. Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "jira-cloud": {
      "command": "/path/to/Jira-cloud-mcp/.venv/bin/python",
      "args": ["/path/to/Jira-cloud-mcp/server.py"],
      "env": {
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your-email@company.com",
        "JIRA_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

### 4. Docker

```bash
docker-compose up -d
```

### 5. Claude Code

Create `.mcp.json` in your project:

```json
{
  "mcpServers": {
    "jira-cloud": {
      "command": "/path/to/Jira-cloud-mcp/.venv/bin/python",
      "args": ["/path/to/Jira-cloud-mcp/server.py"],
      "env": {
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your-email@company.com",
        "JIRA_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

## Jira Cloud vs DC — Feature Comparison

| Feature | Cloud MCP | DC Analyst + Admin |
|---|---|---|
| Tools | 86 | 170 (79 + 91) |
| Plugins needed | None | ScriptRunner |
| Deployment | Python only | Python + Groovy endpoint |
| Workflow internals | Full (post-functions, validators, conditions via REST API) | Full (Java API — conditions, validators, post-functions) |
| ScriptRunner config | N/A | Listeners, behaviours, scripted fields, fragments, jobs |
| Assets/CMDB | Via REST API | Via Java OSGi API |
| Automation | Native rules | A4J plugin rules |
| Security levels | Full REST API | Full Java API |
| Audit log | REST API | REST API + system log |

## License

MIT
