"""Search Jira issues by JQL or full-text."""
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from jira_client import api_post


def main():
    parser = argparse.ArgumentParser(description='Search Jira issues')
    parser.add_argument('--jql', help='JQL query string')
    parser.add_argument('--text', help='Full-text search across all issues')
    parser.add_argument('--project', help='Limit search to a project key')
    parser.add_argument('--max', type=int, default=20, help='Max results (default: 20)')
    parser.add_argument('--fields',
                        default='summary,status,assignee,issuetype,priority,updated,labels,project',
                        help='Comma-separated field list')
    args = parser.parse_args()

    if not args.jql and not args.text:
        print("ERROR: Provide --jql or --text", file=sys.stderr)
        sys.exit(1)

    if args.jql:
        jql = args.jql
    else:
        jql = f'text ~ "{args.text}"'
        if args.project:
            jql = f'project = {args.project} AND {jql}'
        jql += ' ORDER BY updated DESC'

    result = api_post('/rest/api/3/search/jql', {
        'jql': jql,
        'maxResults': args.max,
        'fields': args.fields.split(','),
    })

    total = result.get('total', 0)
    issues = result.get('issues', [])
    print(f"Found {total} issues (showing {len(issues)})\n")

    for iss in issues:
        f = iss.get('fields', {})
        proj = f.get('project', {}).get('key', '')
        status = f.get('status', {}).get('name', '')
        itype = f.get('issuetype', {}).get('name', '')
        assignee = f.get('assignee', {})
        aname = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
        priority = f.get('priority', {}).get('name', '') if f.get('priority') else ''
        labels = ', '.join(f.get('labels', []))
        updated = f.get('updated', '')[:10]

        print(f"  {iss['key']} [{proj}] [{itype}] {f.get('summary', '')}")
        print(f"    Status: {status} | Priority: {priority} | Assignee: {aname} | Updated: {updated}")
        if labels:
            print(f"    Labels: {labels}")


if __name__ == '__main__':
    main()
