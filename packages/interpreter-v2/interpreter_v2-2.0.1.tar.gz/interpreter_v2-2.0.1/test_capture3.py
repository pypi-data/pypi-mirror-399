"""Test what Frame object has."""
print("Importing...", flush=True)
from windows_capture import WindowsCapture, Frame, InternalCaptureControl
print("Done", flush=True)

window_title = "Snes9x"
frame_count = 0

capture = WindowsCapture(
    cursor_capture=False,
    draw_border=False,
    window_name=window_title,
)

@capture.event
def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
    global frame_count
    frame_count += 1

    # Print all attributes and methods
    print(f"Frame {frame_count}:", flush=True)
    print(f"  type: {type(frame)}", flush=True)
    print(f"  dir: {[x for x in dir(frame) if not x.startswith('_')]}", flush=True)

    # Check common attributes
    for attr in ['width', 'height', 'frame_buffer', 'raw_buffer', 'buffer', 'data', 'save_as_image']:
        if hasattr(frame, attr):
            val = getattr(frame, attr)
            if callable(val):
                print(f"  {attr}: <method>", flush=True)
            else:
                print(f"  {attr}: {type(val).__name__} = {repr(val)[:100]}", flush=True)

    if frame_count >= 2:
        capture_control.stop()

@capture.event
def on_closed():
    print("Closed", flush=True)

print("Starting...", flush=True)
capture.start()
print("Done!", flush=True)
