import subprocess
import sys
import textwrap

def test_crash_dump():
    code = textwrap.dedent("""
        from statecrumbs import enable, crumb
        enable(on_crash="stderr")

        crumb("before_crash", value=42)
        1 / 0
    """)

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True
    )

    assert "before_crash" in result.stderr
    assert "ZeroDivisionError" in result.stderr
