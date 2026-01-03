import sys
from .core import snapshot
from .formatter import format_json
from .config import config

_original_hook = sys.excepthook

def _excepthook(exc_type, exc, tb):
    crumbs = snapshot()

    if crumbs:
        try:
            output = format_json(crumbs)

            if config.on_crash == "stderr":
                sys.stderr.write("\n" + output + "\n")

            elif config.on_crash == "file":
                with open(config.output_file, "w") as f:
                    f.write(output)

            elif callable(config.on_crash):
                config.on_crash(crumbs)

        except Exception:
            pass  # never block the real exception

    _original_hook(exc_type, exc, tb)

def install():
    sys.excepthook = _excepthook
