"""Test Frame crop method."""
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

    print(f"Frame {frame_count}: {frame.width}x{frame.height}", flush=True)

    # Check crop method signature
    import inspect
    try:
        sig = inspect.signature(frame.crop)
        print(f"  crop signature: {sig}", flush=True)
    except Exception as e:
        print(f"  crop inspect error: {e}", flush=True)

    # Try to crop (guessing parameters)
    if frame_count == 1:
        try:
            # Try cropping top 70 pixels (title bar)
            cropped = frame.crop(0, 70, frame.width, frame.height)
            print(f"  Cropped: {cropped.width}x{cropped.height}", flush=True)
            cropped.save_as_image("test_cropped.png")
            print("  Saved to test_cropped.png", flush=True)
        except Exception as e:
            print(f"  crop error: {e}", flush=True)

        # Also save original for comparison
        frame.save_as_image("test_original.png")
        print("  Saved original to test_original.png", flush=True)

    if frame_count >= 2:
        capture_control.stop()

@capture.event
def on_closed():
    print("Closed", flush=True)

print("Starting...", flush=True)
capture.start()
print("Done!", flush=True)
