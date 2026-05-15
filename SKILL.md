---
name: jira
description: >
  Query, create, and manage Jira issues on any Atlassian Cloud instance
  via OAuth 2.0 (3LO). Supports searching issues, creating epics/stories/tasks,
  reading issue details, updating issues, and listing projects. Use when the user
  mentions Jira, issues, epics, sprints, boards, or wants to interact with
  Atlassian Jira Cloud projects.
---

# Jira Skill for Copilot CLI

Interact with any Atlassian Jira Cloud instance via REST API using OAuth 2.0 (3LO) tokens.

## When to Use

- User asks about Jira issues, epics, stories, tasks, sprints, or boards
- User wants to search issues (JQL or full-text)
- User wants to create, update, or read issues
- User mentions Jira project keys
- User wants to check status of work items

## Setup

Full setup instructions are in [README.md](README.md). Summary:

### 1. Register an OAuth 2.0 App

1. Go to **https://developer.atlassian.com/console/myapps/**
2. Click **Create** > **OAuth 2.0 integration**
3. Under **Permissions**, add Jira scopes: `read:jira-work`, `write:jira-work`, `read:jira-user`
4. Under **Authorization**, add OAuth 2.0 (3LO) with callback URL: `http://localhost:8080/callback`
5. Under **Settings**, copy your **Client ID** and **Secret**

> The `offline_access` scope is requested automatically by `auth.py` to enable refresh tokens.

### 2. Find Your Cloud ID

Visit `https://YOUR-SITE.atlassian.net/_edge/tenant_info` and copy the `cloudId` value.

### 3. Configure

```bash
cp config.example.json config.json
# Edit config.json with your client_id, client_secret, cloud_id, and base_url
```

Or set `JIRA_SKILL_CONFIG` env var pointing to a config file stored elsewhere.

### 4. Authenticate (One-Time)

```bash
python scripts/auth.py
```

Opens a browser for OAuth consent. After approving, the refresh token is saved to `config.json`. You only need to do this once - tokens auto-rotate on every API call and last ~90 days without use.

## Available Scripts

All scripts auto-refresh the OAuth token on each call. No manual re-authentication needed.

### Search Issues

```bash
python scripts/search.py --jql "project = MYPROJ ORDER BY updated DESC" --max 20
python scripts/search.py --text "search term" --project MYPROJ --max 50
```

### Get Issue Details

```bash
python scripts/get_issue.py PROJ-123
python scripts/get_issue.py PROJ-123 --children
python scripts/get_issue.py PROJ-123 --comments
```

### Create Issue

```bash
python scripts/create_issue.py --project MYPROJ --type Epic --summary "My Epic" --description "Details" --priority High
python scripts/create_issue.py --project MYPROJ --type Story --summary "My Story" --parent PROJ-1 --assignee me
```

### Update Issue

```bash
python scripts/update_issue.py PROJ-123 --status "In Progress"
python scripts/update_issue.py PROJ-123 --assignee me --priority High
python scripts/update_issue.py PROJ-123 --add-labels "label1,label2"
```

### List Projects

```bash
python scripts/list_projects.py
python scripts/list_projects.py --query "keyword"
```

## How It Works

1. **Token Refresh**: On every API call, `jira_client.py` reads the refresh token from config, exchanges it for a fresh 1-hour access token, and rotates the refresh token.
2. **No Re-auth Needed**: The refresh token is valid for ~90 days. Only re-run `auth.py` if you need new scopes or the token expires from non-use.
3. **New Search API**: Uses the current `/rest/api/3/search/jql` POST endpoint (the old GET endpoint is deprecated).

## Troubleshooting

### Token Expired (403/401)
Run `python scripts/auth.py` to re-authenticate via browser.

### "App not installed" Error
This means you're using a client_credentials token instead of a user-scoped token. Run `auth.py` to get a proper 3LO user token.

### Search API 410 Error
The old `/rest/api/3/search` GET endpoint is removed. All scripts here use the new `/rest/api/3/search/jql` POST endpoint.

### Board/Sprint API 401
Board and sprint APIs require `read:board-scope:jira-software` scope. Add it in your OAuth app settings and re-authenticate.

## Requirements

- Python 3.8+ (uses only stdlib: `urllib`, `json`, `http.server`, `argparse`)
- No pip dependencies required
