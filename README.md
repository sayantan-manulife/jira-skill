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

## Prerequisites

- Python 3.8+ (stdlib only, no pip installs)
- A Jira Cloud instance (e.g. `https://yourcompany.atlassian.net`)
- Permission to create an OAuth app at [developer.atlassian.com](https://developer.atlassian.com)

## Setup Guide

### Step 1: Register an OAuth 2.0 App

1. Go to **https://developer.atlassian.com/console/myapps/**
2. Click **Create** > **OAuth 2.0 integration**
3. Give it a name (e.g. "Copilot Jira Skill") and click **Create**
4. In the left sidebar, click **Permissions** and add these Jira scopes:
   - `read:jira-work` - read issues, projects, boards
   - `write:jira-work` - create and update issues
   - `read:jira-user` - read user profiles (for assignee lookups)
5. In the left sidebar, click **Authorization** > **Add** next to "OAuth 2.0 (3LO)"
6. Set the **Callback URL** to: `http://localhost:8080/callback`
7. Click **Save changes**
8. In the left sidebar, click **Settings** and copy your **Client ID** and **Secret**

### Step 2: Find Your Cloud ID

Visit this URL (replace `YOUR-SITE` with your Atlassian subdomain):

```
https://YOUR-SITE.atlassian.net/_edge/tenant_info
```

The JSON response contains your `cloudId`. Copy it.

### Step 3: Clone and Configure

```bash
# Clone into your skills directory
git clone https://github.com/sayantan-manulife/jira-skill.git ~/.agents/skills/jira
cd ~/.agents/skills/jira

# Create your config file
cp config.example.json config.json
```

Edit `config.json` with your values:

```json
{
  "client_id": "YOUR_CLIENT_ID_FROM_STEP_1",
  "client_secret": "YOUR_CLIENT_SECRET_FROM_STEP_1",
  "callback_url": "http://localhost:8080/callback",
  "cloud_id": "YOUR_CLOUD_ID_FROM_STEP_2",
  "base_url": "https://YOUR-SITE.atlassian.net",
  "jira_refresh_token": ""
}
```

> **Note:** `config.json` is gitignored and will never be committed.

Alternatively, set the `JIRA_SKILL_CONFIG` environment variable to point to a config file stored elsewhere.

### Step 4: Authenticate

```bash
python scripts/auth.py
```

This will:
1. Start a local HTTP server on port 8080
2. Open your browser to Atlassian's consent page
3. After you click **Accept**, capture the authorization code
4. Exchange it for access + refresh tokens
5. Save the refresh token to `config.json`

**You only need to do this once.** After the initial authentication, every API call automatically refreshes the token. Refresh tokens are valid for ~90 days of inactivity, so regular usage means you never re-authenticate.

### Step 5: Use It

From Copilot CLI (or run scripts directly):

```
> search jira for issues about "authentication"
> create a story in PROJECT-X about fixing the login bug
> what's the status of PROJ-42?
```

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
