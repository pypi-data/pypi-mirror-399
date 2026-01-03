from .core import crumb, clear, snapshot
from .crash import install
from .config import config

def enable(**kwargs):
    """
    Enable statecrumbs and install crash hook.
    """
    for k, v in kwargs.items():
        if hasattr(config, k):
            setattr(config, k, v)
    install()

def dump():
    """
    Print current crumbs to stdout.
    """
    from .formatter import format_json
    print(format_json(snapshot()))

__all__ = ["enable", "crumb", "dump", "clear", "snapshot"]
