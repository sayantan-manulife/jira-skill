"""
Shared Jira API client with automatic OAuth 2.0 token refresh.
All skill scripts import this module.
"""
import urllib.request
import urllib.parse
import json
import os
import sys

# Config resolution: env var > local config.json > skill-level config
CONFIG_PATH = os.environ.get('JIRA_SKILL_CONFIG',
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json'))

TOKEN_URL = 'https://auth.atlassian.com/oauth/token'


def _load_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"ERROR: Config not found at {CONFIG_PATH}", file=sys.stderr)
        print("Create config.json or set JIRA_SKILL_CONFIG env var.", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)


def _save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)


def _get_base_url():
    config = _load_config()
    cloud_id = config.get('cloud_id', '')
    if not cloud_id:
        print("ERROR: 'cloud_id' missing from config.", file=sys.stderr)
        sys.exit(1)
    return f'https://api.atlassian.com/ex/jira/{cloud_id}'


def get_access_token():
    """Get a fresh access token using the stored refresh token."""
    config = _load_config()
    refresh = config.get('jira_refresh_token')
    if not refresh:
        print("ERROR: No jira_refresh_token in config. Run auth.py first.", file=sys.stderr)
        sys.exit(1)

    data = json.dumps({
        'grant_type': 'refresh_token',
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'refresh_token': refresh,
    }).encode()

    req = urllib.request.Request(TOKEN_URL, data=data,
                                headers={'Content-Type': 'application/json'})
    try:
        resp = urllib.request.urlopen(req)
        td = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        print(f"ERROR: Token refresh failed ({e.code}): {body}", file=sys.stderr)
        print("Try running: python scripts/auth.py", file=sys.stderr)
        sys.exit(1)

    # Rotate refresh token (Atlassian uses rotating refresh tokens)
    if 'refresh_token' in td:
        config['jira_refresh_token'] = td['refresh_token']
        _save_config(config)

    return td['access_token']


def headers():
    """Return auth headers for Jira API calls."""
    token = get_access_token()
    return {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }


def api_get(path):
    """GET request to Jira REST API."""
    base = _get_base_url()
    req = urllib.request.Request(f'{base}{path}', headers=headers())
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        print(f"API GET error {e.code}: {body}", file=sys.stderr)
        raise


def api_post(path, body):
    """POST request to Jira REST API."""
    base = _get_base_url()
    data = json.dumps(body).encode()
    req = urllib.request.Request(f'{base}{path}', data=data, headers=headers())
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()[:500]
        print(f"API POST error {e.code}: {body_text}", file=sys.stderr)
        raise


def api_put(path, body):
    """PUT request to Jira REST API."""
    base = _get_base_url()
    data = json.dumps(body).encode()
    req = urllib.request.Request(f'{base}{path}', data=data, headers=headers(), method='PUT')
    try:
        resp = urllib.request.urlopen(req)
        raw = resp.read()
        return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()[:500]
        print(f"API PUT error {e.code}: {body_text}", file=sys.stderr)
        raise


def get_my_account_id():
    """Get the current user's Jira account ID."""
    me = api_get('/rest/api/3/myself')
    return me['accountId']


def get_priority_map():
    """Return a dict of priority name -> id."""
    prios = api_get('/rest/api/3/priority')
    return {p['name']: p['id'] for p in prios}


def get_issue_types(project_key):
    """Return issue types for a project as {name: id}."""
    result = api_get(f'/rest/api/3/issue/createmeta/{project_key}/issuetypes')
    types = result.get('issueTypes', result.get('values', []))
    return {t['name']: t['id'] for t in types if isinstance(t, dict)}
