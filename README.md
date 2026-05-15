# jira-skill

A [GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli) skill for interacting with Atlassian Jira Cloud via OAuth 2.0.

Search, create, update, and read Jira issues directly from your terminal agent - no pip dependencies required.

## Features

- **Search** issues by JQL or full-text
- **Create** epics, stories, tasks, bugs with parent linking
- **Update** status, assignee, priority, labels
- **Read** issue details with children and comments
- **List** projects by keyword
- **Auto-refresh** OAuth tokens (no re-authentication needed day-to-day)

## Quick Start

1. Clone this repo into your skills directory:
   ```bash
   git clone https://github.com/sayantan-manulife/jira-skill.git ~/.agents/skills/jira
   ```

2. Create `config.json` with your OAuth app credentials (see [SKILL.md](SKILL.md) for setup).

3. Run initial auth:
   ```bash
   python scripts/auth.py
   ```

4. Use from Copilot CLI:
   ```
   > search jira for issues about "authentication"
   > create a story in PROJECT-X about fixing the login bug
   > what's the status of PROJ-42?
   ```

## Config

Create a `config.json` in the repo root:

```json
{
  "client_id": "YOUR_OAUTH_CLIENT_ID",
  "client_secret": "YOUR_OAUTH_CLIENT_SECRET",
  "callback_url": "http://localhost:8080/callback",
  "cloud_id": "YOUR_ATLASSIAN_CLOUD_ID",
  "base_url": "https://YOUR-SITE.atlassian.net",
  "jira_refresh_token": ""
}
```

> **Note:** `config.json` is gitignored. Never commit credentials.

## Scripts

| Script | Description |
|--------|-------------|
| `scripts/jira_client.py` | Shared OAuth client with auto token refresh |
| `scripts/auth.py` | Browser-based OAuth 2.0 (3LO) authentication |
| `scripts/search.py` | Search issues by JQL or text |
| `scripts/get_issue.py` | Get issue details, children, comments |
| `scripts/create_issue.py` | Create issues with full field support |
| `scripts/update_issue.py` | Update status, fields, and labels |
| `scripts/list_projects.py` | List/search accessible projects |

## Requirements

- Python 3.8+
- No external dependencies (stdlib only)

## License

MIT
