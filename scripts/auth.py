"""
Re-authenticate with Jira via OAuth 2.0 (3LO) browser flow.
Run this for initial setup or if the refresh token has expired.
"""
import http.server
import urllib.request
import urllib.parse
import json
import webbrowser
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description='Authenticate with Jira OAuth 2.0')
    parser.add_argument('--config', default=None,
                        help='Path to config.json (default: ../config.json or JIRA_SKILL_CONFIG env)')
    args = parser.parse_args()

    config_path = args.config or os.environ.get('JIRA_SKILL_CONFIG',
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json'))

    if not os.path.exists(config_path):
        print(f"ERROR: Config not found at {config_path}", file=sys.stderr)
        print("Create config.json with client_id, client_secret, callback_url, cloud_id, base_url",
              file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    client_id = config['client_id']
    client_secret = config['client_secret']
    callback_url = config.get('callback_url', 'http://localhost:8080/callback')
    scopes = 'read:jira-work read:jira-user write:jira-work offline_access'

    auth_code = None

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal auth_code
            p = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            auth_code = p.get('code', [None])[0] or f"ERROR:{p.get('error', ['unknown'])[0]}"
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h2>Authorization complete! You can close this tab.</h2>')
        def log_message(self, *a):
            pass

    # Parse port from callback URL
    port = int(callback_url.split(':')[-1].split('/')[0])
    srv = http.server.HTTPServer(('localhost', port), Handler)
    srv.timeout = 180

    url = 'https://auth.atlassian.com/authorize?' + urllib.parse.urlencode({
        'audience': 'api.atlassian.com',
        'client_id': client_id,
        'scope': scopes,
        'redirect_uri': callback_url,
        'response_type': 'code',
        'prompt': 'consent',
        'state': 'jira-auth',
    })

    print(f"Opening browser for Jira authorization...")
    print(f"Callback: {callback_url}")
    print(f"\nIf the browser doesn't open, visit:\n  {url}\n")
    webbrowser.open(url)

    while auth_code is None:
        srv.handle_request()
    srv.server_close()

    if auth_code.startswith('ERROR:'):
        print(f"Authorization failed: {auth_code}")
        sys.exit(1)

    print("Exchanging authorization code for token...")
    data = json.dumps({
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'redirect_uri': callback_url,
    }).encode()

    req = urllib.request.Request('https://auth.atlassian.com/oauth/token',
        data=data, headers={'Content-Type': 'application/json'})
    try:
        resp = urllib.request.urlopen(req)
        td = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"Token exchange failed ({e.code}): {e.read().decode()[:500]}")
        sys.exit(1)

    print(f"Scopes granted: {td.get('scope', '')}")

    if 'refresh_token' in td:
        config['jira_refresh_token'] = td['refresh_token']
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"\nRefresh token saved to {config_path}")
        print("Authentication complete! You can now use all Jira skill scripts.")
    else:
        print("\nWARNING: No refresh token received.")
        print("Make sure 'offline_access' is in your app's scopes.")


if __name__ == '__main__':
    main()
