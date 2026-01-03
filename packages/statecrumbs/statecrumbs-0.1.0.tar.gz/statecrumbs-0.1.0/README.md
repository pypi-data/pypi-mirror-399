## statecrumbs 🧩

Lightweight runtime state breadcrumbs for crash debugging, observability, and post‑mortem analysis. Capture small, structured “crumbs” of state as your code executes - thread‑safe, context‑aware, and bounded in memory.


### Features

- Bounded ring buffer (no log spam) via `max_crumbs`
- Zero‑overhead crash hook that never blocks the real exception
- Context propagation with scoped values (`request_id`, `pipeline_id`, etc.)
- Thread‑safe recording
- Structured output as JSON or readable text


### Installation

From PyPI:

```bash
pip install statecrumbs
```

From source (editable):

```bash
pip install -e .
```


### Quick start

```python
from statecrumbs import enable, crumb

# Install crash hook and set a small buffer
enable(on_crash="stderr", max_crumbs=5)

crumb("start", user="alice")
crumb("before_error", x=10)

1 / 0  # On crash, recent crumbs are dumped to stderr as JSON
```

Example crash output (shape):

```json
[
  {
    "event": "start",
    "ts": "2025-12-30T10:23:45.123456+00:00",
    "thread": "MainThread"
  },
  {
    "event": "before_error",
    "ts": "2025-12-30T10:23:45.234567+00:00",
    "thread": "MainThread",
    "x": "10"
  }
]
```


### Core API

- `enable(**kwargs)`: Configure and install the crash hook.
  - Supported config keys (defaults shown):
    - `max_crumbs: int = 50`
    - `on_crash: str = "stderr"`  (one of `"stderr" | "file" | "none" | callable`)
    - `output_file: str = "statecrumbs.json"` (used when `on_crash == "file"`)
    - `include_timestamp: bool = True` (adds ISO‑8601 `ts` field)
    - `include_thread: bool = True` (adds `thread` field)

- `crumb(event: str, **data)`: Record a breadcrumb.
  - Adds fields:
    - `event`: required string
    - `ts`: ISO‑8601 UTC timestamp (e.g. `2025-12-30T10:23:45.123456+00:00`) if enabled
    - `thread`: current thread name if enabled
    - `context`: dict of scoped values if any (see Context below)
    - any `**data` you pass, stored via `repr(value)`
  - Never raises; no‑op for empty/invalid events.

- `snapshot() -> list[dict]`: Return a copy of the current crumb buffer (oldest to newest).

- `clear()`: Clear the buffer.

- `dump()`: Print current crumbs as pretty JSON to stdout.


### Crash behavior

When the crash hook is installed (via `enable()`), an unhandled exception will trigger a dump of `snapshot()` according to `on_crash`:
- `"stderr"`: write JSON to stderr (default)
- `"file"`: write to `output_file`
- `"none"`: do nothing
- `callable`: a callable receiving the `crumbs` list

The hook is defensive and won’t block or replace the real exception.


### Context

Use the context manager to add scoped metadata automatically to all crumbs recorded within the scope:

```python
from statecrumbs import crumb, snapshot, clear
from statecrumbs.context import context

clear()

with context(request_id="req-999", user="bob"):
    crumb("request_start")
    with context(step="db_query"):
        crumb("query_started")
        crumb("query_finished")
    crumb("request_end")

for c in snapshot():
    print(c)
```

Each crumb within the `context(...)` scope includes a `context` field containing the merged key/values active at capture time.

Available context helpers:
- `context(**kwargs)`: context manager that merges keys for the duration of the block.
- `get_context()`: returns the current context dict (for advanced use).


### Formatting and export

- `formatter.format_json(crumbs) -> str`: pretty JSON string.
- `formatter.format_text(crumbs) -> str`: simple text format.
- `export.export_json(path)`: write the current `snapshot()` to a file as pretty JSON.


### Thread‑safety and buffer semantics

- All crumb operations are protected by a lock; concurrent `crumb()` calls are safe.
- The buffer is a ring with capacity `max_crumbs`. When full, oldest crumbs are dropped.


### Examples in repo

- `examples/basic_crumb.py`: minimal breadcrumbs + crash behavior.
- `examples/data_ingest.py`: staged pipeline with success/failure paths, context scoping, and JSON export.
- `examples/web_request.py`: request‑scoped context and nested steps.
- `examples/basic_context.py`: simple request‑scoped context.
- `examples/nested_context.py`: nested contexts across multiple steps.
- `examples/prod_scale_pipeline.py`: large batch pipeline with many crumbs and buffer tuning.

Run an example:

```bash
python examples/basic_crumb.py
```


### Testing

The project includes a small test suite:

```bash
pip install -e .[test]  # or just ensure pytest is available
pytest
```


### Data model

A typical crumb looks like:

```json
{
  "event": "transform_completed",
  "ts": "2025-12-30T10:23:45.987654+00:00",
  "thread": "MainThread",
  "context": {"pipeline_id": "ingest-42", "stage": "transform"},
  "records": "4"
}
```

Notes:
- `ts` is ISO‑8601 UTC with timezone offset.
- Arbitrary fields come from `**data` and are stored using `repr(value)` to avoid serialization errors.


### FAQ

- Why both context and ad‑hoc fields?
  - Use `context(...)` for durable, cross‑cutting metadata (request IDs, stages). Use `**data` for event‑specific details.
- What happens if values aren’t JSON‑serializable?
  - Values from `**data` are stored via `repr(value)`. If `repr` fails, the value falls back to `"<unserializable>"`.
- Can I disable timestamps or thread names?
  - Yes, set `include_timestamp=False` or `include_thread=False` in `enable(...)`.


### License

MIT © Hemapriya N

