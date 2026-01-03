"""Check available methods on WindowsCapture."""
print("Importing...", flush=True)
from windows_capture import WindowsCapture
print("Done", flush=True)

capture = WindowsCapture(
    cursor_capture=False,
    draw_border=False,
    window_name="Snes9x",
)

print("Methods:", flush=True)
for attr in dir(capture):
    if not attr.startswith('_'):
        val = getattr(capture, attr)
        if callable(val):
            print(f"  {attr}()", flush=True)
        else:
            print(f"  {attr} = {val}", flush=True)
