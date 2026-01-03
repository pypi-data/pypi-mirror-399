import json
from .core import snapshot

def export_json(path):
    with open(path, "w") as f:
        json.dump(snapshot(), f, indent=2)