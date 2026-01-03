"""Test Frame buffer to PIL conversion."""
print("Importing...", flush=True)
from windows_capture import WindowsCapture, Frame, InternalCaptureControl
from PIL import Image
import numpy as np
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

    print(f"Frame {frame_count}: {frame.width}x{frame.height}", flush=True)

    # Get frame buffer (already numpy array)
    arr = frame.frame_buffer
    print(f"  Buffer shape: {arr.shape}, dtype: {arr.dtype}", flush=True)
    print(f"  Buffer is C-contiguous: {arr.flags['C_CONTIGUOUS']}", flush=True)

    # Save using built-in method first (known to work)
    if frame_count == 1:
        frame.save_as_image("test_builtin.png")
        print("  Saved with save_as_image -> test_builtin.png", flush=True)

    # Try manual conversion
    try:
        # frame_buffer is BGRA format
        # Convert to RGB by taking first 3 channels and reversing
        rgb = arr[:, :, [2, 1, 0]]  # BGRA -> RGB
        rgb = np.ascontiguousarray(rgb)
        img = Image.fromarray(rgb, mode="RGB")
        if frame_count == 1:
            img.save("test_manual.png")
            print(f"  Saved manual conversion -> test_manual.png", flush=True)
    except Exception as e:
        print(f"  Manual conversion error: {e}", flush=True)

    if frame_count >= 3:
        capture_control.stop()

@capture.event
def on_closed():
    print("Closed", flush=True)

print("Starting...", flush=True)
capture.start()
print("Done!", flush=True)
