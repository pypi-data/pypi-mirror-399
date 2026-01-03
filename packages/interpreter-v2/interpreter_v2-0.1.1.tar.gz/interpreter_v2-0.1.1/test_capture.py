"""Test Windows Graphics Capture API."""
import sys
import time
import threading

print("Importing windows_capture...", flush=True)
from windows_capture import WindowsCapture, Frame, InternalCaptureControl
print("Imported successfully", flush=True)

from PIL import Image

window_title = "Snes9x"
frame_count = 0

# Create capture
print(f"Creating capture for window: {window_title}", flush=True)
capture = WindowsCapture(
    cursor_capture=False,
    draw_border=False,
    window_name=window_title,
)
print("Capture created", flush=True)

@capture.event
def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
    global frame_count
    frame_count += 1
    print(f"Frame {frame_count}: {frame.width}x{frame.height}", flush=True)

    # Try to save as image directly
    if frame_count == 1:
        frame.save_as_image("test_frame.png")
        print("Saved first frame to test_frame.png", flush=True)

    # Stop after 5 frames
    if frame_count >= 5:
        capture_control.stop()

@capture.event
def on_closed():
    print("Capture closed", flush=True)

print("Starting capture (this blocks until stopped)...", flush=True)
capture.start()
print("Done!", flush=True)
