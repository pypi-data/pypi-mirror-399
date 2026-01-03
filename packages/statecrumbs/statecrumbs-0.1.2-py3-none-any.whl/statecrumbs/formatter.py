import json

def format_json(crumbs):
    return json.dumps(crumbs, indent=2)

def format_text(crumbs):
    lines = ["Statecrumbs (most recent first):"]
    for c in crumbs:
        lines.append(str(c))
    return "\n".join(lines)
