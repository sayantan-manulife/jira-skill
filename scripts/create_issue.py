"""Create a Jira issue."""
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from jira_client import api_post, api_get, get_my_account_id, get_priority_map, get_issue_types, _load_config


def main():
    parser = argparse.ArgumentParser(description='Create a Jira issue')
    parser.add_argument('--project', required=True, help='Project key (e.g. MYPROJ)')
    parser.add_argument('--type', required=True, help='Issue type (Epic, Story, Task, Sub-task, Bug, etc.)')
    parser.add_argument('--summary', required=True, help='Issue summary/title')
    parser.add_argument('--description', default='', help='Issue description')
    parser.add_argument('--parent', help='Parent issue key (e.g. PROJ-1)')
    parser.add_argument('--assignee', help='"me" for self, or an account ID')
    parser.add_argument('--priority', help='Priority: High, Medium, Low, etc.')
    parser.add_argument('--labels', help='Comma-separated labels')
    args = parser.parse_args()

    # Resolve issue type
    types = get_issue_types(args.project)
    if args.type not in types:
        print(f"ERROR: Issue type '{args.type}' not found in {args.project}.", file=sys.stderr)
        print(f"Available: {', '.join(types.keys())}", file=sys.stderr)
        sys.exit(1)
    type_id = types[args.type]

    # Build fields
    fields = {
        'project': {'key': args.project},
        'issuetype': {'id': type_id},
        'summary': args.summary,
    }

    if args.description:
        fields['description'] = {
            'type': 'doc',
            'version': 1,
            'content': [{
                'type': 'paragraph',
                'content': [{'type': 'text', 'text': args.description}]
            }]
        }

    if args.parent:
        fields['parent'] = {'key': args.parent}

    if args.assignee:
        if args.assignee == 'me':
            fields['assignee'] = {'accountId': get_my_account_id()}
        else:
            fields['assignee'] = {'accountId': args.assignee}

    if args.priority:
        pmap = get_priority_map()
        if args.priority in pmap:
            fields['priority'] = {'id': pmap[args.priority]}
        else:
            print(f"WARNING: Priority '{args.priority}' not found. Available: {', '.join(pmap.keys())}",
                  file=sys.stderr)

    if args.labels:
        fields['labels'] = [l.strip() for l in args.labels.split(',')]

    result = api_post('/rest/api/3/issue', {'fields': fields})
    key = result.get('key', '')
    config = _load_config()
    base_url = config.get('base_url', 'https://your-site.atlassian.net')
    print(f"Created: {key} - {args.summary}")
    print(f"  URL: {base_url}/browse/{key}")


if __name__ == '__main__':
    main()
