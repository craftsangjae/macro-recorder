import multiprocessing
import time
import json
from typing import Tuple

from pynput.keyboard import KeyCode


class MouseMonitor(multiprocessing.Process):
    def __init__(self, output_path: str):
        super().__init__()
        self.output_path = output_path

    def run(self):
        from pynput import mouse
        s_time = time.time()
        s_w, s_h = get_screen_size()

        def write_log(x: float, y: float, action: str):
            row = [s_time - time.time(), x / s_w, y / s_h, action]
            with open(self.output_path, encoding="utf-8", mode='a') as f:
                json.encoder.FLOAT_REPR = lambda o: lambda f: ("%.4f" % f)
                f.write(json.dumps(row, ensure_ascii=False) + '\n')

        def on_move(x, y):
            write_log(x, y, 'move')

        def on_click(x, y, button, pressed):
            if pressed:
                write_log(x, y, f'{button.name} press')
            else:
                write_log(x, y, f'{button.name} release')

        def on_scroll(x, y, dx, dy):
            write_log(x, y, "scroll")

        with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
            print('Mouse monitor started.')
            listener.join()


class KeyboardMonitor(multiprocessing.Process):
    def __init__(self, output_path: str):
        super().__init__()
        self.output_path = output_path

    def run(self):
        from pynput import keyboard
        s_time = time.time()

        def write_log(action: str, key: KeyCode):
            try:
                row = [s_time - time.time(), action, key.char]
            except AttributeError:
                row = [s_time - time.time(), action, str(key)]

            with open(self.output_path, encoding="utf-8", mode='a') as f:
                f.write(json.dumps(row, ensure_ascii=False) + '\n')

        with keyboard.Listener(
            on_press=lambda key: write_log('press', key),
            on_release=lambda key: write_log('release', key)
        ) as listener:
            print('Keyboard Monitor started.')
            try:
                listener.join()
            except KeyboardInterrupt:
                print('Keyboard Monitor ended.')
                return


def get_screen_size() -> Tuple[int, int]:
    import screeninfo
    monitors = screeninfo.get_monitors()
    for m in monitors:
        if m.is_primary:
            return m.width, m.height

    if monitors:
        m = monitors[0]
        return m.width, m.height

