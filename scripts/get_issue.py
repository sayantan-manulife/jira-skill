"""Get details of a Jira issue, optionally with children and comments."""
import argparse
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from jira_client import api_get, api_post


def main():
    parser = argparse.ArgumentParser(description='Get Jira issue details')
    parser.add_argument('key', help='Issue key (e.g. PROJ-123)')
    parser.add_argument('--children', action='store_true', help='Also list child issues')
    parser.add_argument('--comments', action='store_true', help='Include comments')
    args = parser.parse_args()

    iss = api_get(f'/rest/api/3/issue/{args.key}?expand=renderedFields')
    f = iss.get('fields', {})

    print(f"{'='*60}")
    print(f"{iss['key']}: {f.get('summary', '')}")
    print(f"{'='*60}")
    print(f"  Type: {f.get('issuetype', {}).get('name', '')}")
    print(f"  Status: {f.get('status', {}).get('name', '')}")
    print(f"  Priority: {f.get('priority', {}).get('name', '') if f.get('priority') else 'None'}")

    assignee = f.get('assignee', {})
    print(f"  Assignee: {assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'}")
    reporter = f.get('reporter', {})
    print(f"  Reporter: {reporter.get('displayName', '') if reporter else ''}")
    print(f"  Project: {f.get('project', {}).get('key', '')} - {f.get('project', {}).get('name', '')}")
    print(f"  Created: {f.get('created', '')[:10]}")
    print(f"  Updated: {f.get('updated', '')[:10]}")

    labels = f.get('labels', [])
    if labels:
        print(f"  Labels: {', '.join(labels)}")

    comps = f.get('components', [])
    if comps:
        print(f"  Components: {', '.join(c.get('name', '') for c in comps)}")

    fv = f.get('fixVersions', [])
    if fv:
        print(f"  Fix Versions: {', '.join(v.get('name', '') for v in fv)}")

    # Description (rendered HTML -> plain text)
    desc = iss.get('renderedFields', {}).get('description', '')
    if desc:
        clean = re.sub(r'<[^>]+>', ' ', desc).strip()
        clean = re.sub(r'\s+', ' ', clean)
        print(f"\n  Description:\n    {clean[:1500]}")

    # Sub-tasks
    subs = f.get('subtasks', [])
    if subs:
        print(f"\n  Sub-tasks ({len(subs)}):")
        for s in subs:
            sf = s.get('fields', {})
            print(f"    {s['key']}: {sf.get('summary', '')} | {sf.get('status', {}).get('name', '')}")

    # Links
    links = f.get('issuelinks', [])
    if links:
        print(f"\n  Links ({len(links)}):")
        for l in links:
            lt = l.get('type', {})
            outward = l.get('outwardIssue', {})
            inward = l.get('inwardIssue', {})
            if outward:
                print(f"    {lt.get('outward', '')} -> {outward.get('key', '')}: "
                      f"{outward.get('fields', {}).get('summary', '')}")
            if inward:
                print(f"    {lt.get('inward', '')} <- {inward.get('key', '')}: "
                      f"{inward.get('fields', {}).get('summary', '')}")

    # Children
    if args.children:
        print(f"\n  Children (parent = {args.key}):")
        try:
            result = api_post('/rest/api/3/search/jql', {
                'jql': f'parent = {args.key} ORDER BY key ASC',
                'maxResults': 50,
                'fields': ['summary', 'status', 'issuetype', 'priority', 'assignee'],
            })
            for ch in result.get('issues', []):
                cf = ch.get('fields', {})
                prio = cf.get('priority', {}).get('name', '') if cf.get('priority') else ''
                ca = cf.get('assignee', {})
                can = ca.get('displayName', 'Unassigned') if ca else 'Unassigned'
                print(f"    {ch['key']} [{cf.get('issuetype', {}).get('name', '')}] "
                      f"{cf.get('summary', '')} | {cf.get('status', {}).get('name', '')} | {prio} | {can}")
            if not result.get('issues'):
                print("    (none)")
        except Exception as e:
            print(f"    Error: {e}")

    # Comments
    if args.comments:
        print(f"\n  Comments:")
        try:
            comments = api_get(f'/rest/api/3/issue/{args.key}/comment?maxResults=20')
            for c in comments.get('comments', []):
                author = c.get('author', {}).get('displayName', '')
                created = c.get('created', '')[:10]
                body = c.get('body', {})
                text_parts = []
                for content in body.get('content', []):
                    for inner in content.get('content', []):
                        if inner.get('type') == 'text':
                            text_parts.append(inner.get('text', ''))
                text = ' '.join(text_parts)
                print(f"    [{created}] {author}: {text[:300]}")
            if not comments.get('comments'):
                print("    (none)")
        except Exception as e:
            print(f"    Error: {e}")


if __name__ == '__main__':
    main()
