import os.path
import threading
import time
import numpy as np
from PIL import Image
import cv2

FPS = 20
cursor = Image.open(os.path.join(os.path.dirname(__file__), "resource", "cursor.png"))


def capture_screenshot() -> np.ndarray:
    """ 현재 스크린샷을 찍어서 저장합니다. """
    import mss
    import numpy as np
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        image = sct.grab(monitor)
        return np.array(image)


def draw_cursor(image: np.ndarray) -> np.ndarray:
    """ 포인터를 그립니다. """
    import pyautogui
    # 마우스 포인터 위치 가져오기
    mouse_x, mouse_y = pyautogui.position()
    size = pyautogui.size()
    h, w = image.shape[:2]
    cursor_size = cursor.size
    position = (int(mouse_x * w / size.width - cursor_size[0]//3), int(mouse_y * h / size.height - cursor_size[1]//4))

    # 스크린샷에 마우스 포인터 그리기
    img_pil = Image.fromarray(image)
    img_pil.paste(cursor, position, cursor)
    return np.array(img_pil)

def record_screen(save_path: str, stop_signal: threading.Event):
    """ Record screen to video file. """
    global FPS
    frame_time = 1 / FPS
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    out = None
    next_frame_time = time.time()
    while not stop_signal.is_set():
        image = capture_screenshot()
        frame = draw_cursor(image)

        if out is None:
            screen_size = frame.shape[:2][::-1]
            out = cv2.VideoWriter(save_path, fourcc, FPS, screen_size)

        out.write(frame[..., :3])

        next_frame_time += frame_time
        if sleep_time := max(0., next_frame_time - time.time()):
            time.sleep(sleep_time)
    out.release()
    return save_path
