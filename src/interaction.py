import threading
import time

import ujson as json


def record_mouse_events(output_path: str, stop_signal: threading.Event):
    """Log mouse events with timestamps."""
    from pynput import mouse
    s_time = time.time()
    mouse_log = []

    def on_move(x, y):
        # skip to log mouse move event to reduce log size
        # mouse_log.append((time.time() - s_time, 'move', x, y))
        return

    def on_click(x, y, button, pressed):
        action = 'pressed' if pressed else 'released'
        mouse_log.append((time.time() - s_time, f'{action} {button}', x, y))

    def on_scroll(x, y, dx, dy):
        mouse_log.append((time.time() - s_time, 'scroll', dx, dy))

    with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
        while not stop_signal.is_set():
            time.sleep(0.0001)
        listener.stop()

    with open(output_path, 'w') as f:
        json.dump(mouse_log, f, ensure_ascii=False, indent=2)


def record_keyboard_events(output_path: str, stop_signal: threading.Event):
    """Log keyboard events with timestamps."""
    from pynput import keyboard
    s_time = time.time()
    keyboard_log = []

    def on_press(key):
        try:
            keyboard_log.append((time.time() - s_time, 'press', key.char))
        except AttributeError:
            keyboard_log.append((time.time() - s_time, 'press', str(key)))

    def on_release(key):
        try:
            keyboard_log.append((time.time() - s_time, 'release', key.char))
        except AttributeError:
            keyboard_log.append((time.time() - s_time, 'release', str(key)))
        if stop_signal.is_set():
            return False  # Stop listener

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        while not stop_signal.is_set():
            time.sleep(0.0001)
        listener.stop()

    with open(output_path, 'w') as f:
        json.dump(keyboard_log, f, ensure_ascii=False, indent=2)
