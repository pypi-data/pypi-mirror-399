import threading
from collections import deque
from .config import config
from datetime import datetime, timezone
from .context import get_context

_lock = threading.Lock()
_buffer = deque()

def _timestamp():
    return datetime.now(timezone.utc).isoformat()

def crumb(event: str, **data):
    """
    Record a state breadcrumb.
    Never raises exceptions.
    """
    if not isinstance(event, str) or not event:
        return

    entry = {"event": event}

    if config.include_timestamp:
        entry["ts"] = _timestamp()

    if config.include_thread:
        entry["thread"] = threading.current_thread().name

    try:
        ctx = get_context()
        if ctx:
            entry["context"] = dict(ctx)
    except Exception:
        pass

    for k, v in data.items():
        try:
            entry[k] = repr(v)
        except Exception:
            entry[k] = "<unserializable>"

    with _lock:
        _buffer.append(entry)
        while len(_buffer) > config.max_crumbs:
            _buffer.popleft()

def snapshot():
    with _lock:
        return list(_buffer)

def clear():
    with _lock:
        _buffer.clear()
