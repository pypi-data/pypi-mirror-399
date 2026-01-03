"""Test threaded capture approach."""
import threading
import time

print("Importing...", flush=True)
from windows_capture import WindowsCapture, Frame, InternalCaptureControl
from PIL import Image
import numpy as np
print("Done", flush=True)

window_title = "Snes9x"
latest_frame = None
frame_lock = threading.Lock()
frame_count = 0

print(f"Creating capture for: {window_title}", flush=True)
capture = WindowsCapture(
    cursor_capture=False,
    draw_border=False,
    window_name=window_title,
)
print("Capture created", flush=True)

@capture.event
def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
    global latest_frame, frame_count
    frame_count += 1
    print(f"[CALLBACK] Frame {frame_count}: {frame.width}x{frame.height}", flush=True)

    try:
        arr = frame.frame_buffer
        rgb = arr[:, :, [2, 1, 0]]
        rgb = np.ascontiguousarray(rgb)
        img = Image.fromarray(rgb, mode="RGB")

        with frame_lock:
            latest_frame = img
        print(f"[CALLBACK] Frame stored", flush=True)
    except Exception as e:
        print(f"[CALLBACK] Error: {e}", flush=True)

    if frame_count >= 10:
        capture_control.stop()

@capture.event
def on_closed():
    print("[CALLBACK] Closed", flush=True)

# Start in background thread
print("Starting capture thread...", flush=True)
thread = threading.Thread(target=capture.start, daemon=True)
thread.start()
print("Thread started", flush=True)

# Wait and poll for frames
for i in range(50):
    time.sleep(0.1)
    with frame_lock:
        if latest_frame:
            print(f"[MAIN] Got frame: {latest_frame.size}", flush=True)
            latest_frame.save("test_threaded.png")
            print("[MAIN] Saved to test_threaded.png", flush=True)
            break
    print(f"[MAIN] Waiting... ({i+1}/50)", flush=True)
else:
    print("[MAIN] No frame received!", flush=True)

print("Done!", flush=True)
