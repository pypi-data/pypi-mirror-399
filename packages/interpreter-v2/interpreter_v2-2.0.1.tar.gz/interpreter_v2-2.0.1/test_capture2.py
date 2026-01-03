"""Test Windows Graphics Capture with numpy conversion."""
import threading
import time

print("Importing libraries...", flush=True)
from windows_capture import WindowsCapture, Frame, InternalCaptureControl
from PIL import Image
import numpy as np
print("Imports done", flush=True)

window_title = "Snes9x"
frame_count = 0
latest_frame = None
frame_lock = threading.Lock()

print(f"Creating capture for: {window_title}", flush=True)
capture = WindowsCapture(
    cursor_capture=False,
    draw_border=False,
    window_name=window_title,
)
print("Capture created", flush=True)

@capture.event
def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
    global frame_count, latest_frame
    frame_count += 1

    try:
        # Get frame as numpy array
        arr = frame.to_numpy(copy=False)
        print(f"Frame {frame_count}: shape={arr.shape}, dtype={arr.dtype}", flush=True)

        # Convert BGRA to RGB
        rgb = arr[:, :, [2, 1, 0]]  # Reorder: BGRA -> RGB
        rgb = np.ascontiguousarray(rgb)

        # Create PIL image
        img = Image.fromarray(rgb, mode="RGB")
        print(f"  PIL image: {img.size}, mode={img.mode}", flush=True)

        # Save first frame
        if frame_count == 1:
            img.save("test_numpy_frame.png")
            print("  Saved to test_numpy_frame.png", flush=True)

        with frame_lock:
            latest_frame = img

    except Exception as e:
        print(f"  Error: {e}", flush=True)

    if frame_count >= 5:
        capture_control.stop()

@capture.event
def on_closed():
    print("Capture closed", flush=True)

print("Starting capture...", flush=True)
capture.start()
print("Done!", flush=True)
