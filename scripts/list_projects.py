"""List Jira projects, optionally filtered by keyword."""
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from jira_client import api_get


def main():
    parser = argparse.ArgumentParser(description='List Jira projects')
    parser.add_argument('--query', help='Filter projects by keyword')
    parser.add_argument('--max', type=int, default=50, help='Max results (default: 50)')
    args = parser.parse_args()

    path = f'/rest/api/3/project/search?maxResults={args.max}'
    if args.query:
        path += f'&query={args.query}'

    result = api_get(path)
    total = result.get('total', 0)
    projects = result.get('values', [])

    print(f"Projects ({total} total, showing {len(projects)}):\n")
    for p in projects:
        lead = p.get('lead', {}).get('displayName', '') if p.get('lead') else ''
        print(f"  {p['key']}: {p['name']}")
        if lead:
            print(f"    Lead: {lead} | Type: {p.get('projectTypeKey', '')}")


if __name__ == '__main__':
    main()
