"""Update a Jira issue (status, assignee, priority, labels, summary, description)."""
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from jira_client import api_get, api_put, api_post, get_my_account_id, get_priority_map


def transition_issue(key, target_status):
    """Transition an issue to a new status."""
    transitions = api_get(f'/rest/api/3/issue/{key}/transitions')
    for t in transitions.get('transitions', []):
        if t['name'].lower() == target_status.lower():
            api_post(f'/rest/api/3/issue/{key}/transitions', {
                'transition': {'id': t['id']}
            })
            print(f"  Transitioned to: {t['name']}")
            return True
    available = [t['name'] for t in transitions.get('transitions', [])]
    print(f"  ERROR: Status '{target_status}' not available.", file=sys.stderr)
    print(f"  Available transitions: {', '.join(available)}", file=sys.stderr)
    return False


def main():
    parser = argparse.ArgumentParser(description='Update a Jira issue')
    parser.add_argument('key', help='Issue key (e.g. PROJ-123)')
    parser.add_argument('--status', help='Transition to status (e.g. "In Progress")')
    parser.add_argument('--assignee', help='"me" for self, "none" to unassign, or account ID')
    parser.add_argument('--priority', help='Priority: High, Medium, Low, etc.')
    parser.add_argument('--summary', help='New summary')
    parser.add_argument('--add-labels', help='Comma-separated labels to add')
    parser.add_argument('--description', help='New description text')
    args = parser.parse_args()

    updates = {}
    fields = {}

    if args.assignee:
        if args.assignee == 'me':
            fields['assignee'] = {'accountId': get_my_account_id()}
        elif args.assignee == 'none':
            fields['assignee'] = None
        else:
            fields['assignee'] = {'accountId': args.assignee}

    if args.priority:
        pmap = get_priority_map()
        if args.priority in pmap:
            fields['priority'] = {'id': pmap[args.priority]}

    if args.summary:
        fields['summary'] = args.summary

    if args.description:
        fields['description'] = {
            'type': 'doc',
            'version': 1,
            'content': [{
                'type': 'paragraph',
                'content': [{'type': 'text', 'text': args.description}]
            }]
        }

    if args.add_labels:
        labels = [l.strip() for l in args.add_labels.split(',')]
        updates['labels'] = [{'add': l} for l in labels]

    # Apply field/update changes
    if fields or updates:
        body = {}
        if fields:
            body['fields'] = fields
        if updates:
            body['update'] = updates
        api_put(f'/rest/api/3/issue/{args.key}', body)
        print(f"Updated {args.key}")
        if fields:
            print(f"  Fields changed: {', '.join(fields.keys())}")
        if updates:
            print(f"  Updates applied: {', '.join(updates.keys())}")

    # Transition (separate API call)
    if args.status:
        transition_issue(args.key, args.status)

    if not fields and not updates and not args.status:
        print("Nothing to update. Use --status, --assignee, --priority, --summary, --add-labels, or --description")


if __name__ == '__main__':
    main()
