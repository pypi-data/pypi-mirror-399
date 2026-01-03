from contextlib import contextmanager
from contextvars import ContextVar

_context = ContextVar("statecrumbs_context", default={})

@contextmanager
def context(**kwargs):
    current = _context.get()
    merged = {**current, **kwargs}
    token = _context.set(merged)
    try:
        yield
    finally:
        _context.reset(token)

def get_context():
    return _context.get()
