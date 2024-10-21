import threading
import os
from typing import Dict

from src.audio import record_audio
from src.interaction import record_mouse_events, record_keyboard_events
from src.screen import record_screen


class Recorder:
    threads: Dict[str, threading.Thread]

    def __init__(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        self.stop_event = threading.Event()

        self.video_path = os.path.join(output_dir, "screen.avi")
        self.audio_path = os.path.join(output_dir, "audio.wav")
        self.output_path = os.path.join(output_dir, "output.mp4")

        mouse_log_path = os.path.join(output_dir, "mouse.json")
        keyboard_path = os.path.join(output_dir, "keyboard.json")

        self.threads = {
            'screen': threading.Thread(target=record_screen, args=(self.video_path, self.stop_event,)),
            'audio': threading.Thread(target=record_audio, args=(self.audio_path, self.stop_event,)),
            'mouse': threading.Thread(target=record_mouse_events, args=(mouse_log_path, self.stop_event,)),
            'keyboard': threading.Thread(target=record_keyboard_events, args=(keyboard_path, self.stop_event,))
        }

    def start(self):
        for name, thread in self.threads.items():
            thread.start()

    def stop(self):
        self.stop_event.set()
        for name, thread in self.threads.items():
            thread.join()

        merge_video(self.output_path, self.video_path, self.audio_path)
        # os.remove(self.video_path)
        # os.remove(self.audio_path)


def merge_video(output_path:str, video_path:str, audio_path:str):
    from moviepy.editor import VideoFileClip, AudioFileClip
    return (
        VideoFileClip(video_path)
        .set_audio(AudioFileClip(audio_path))
        .write_videofile(output_path, codec="libx264", audio_codec="aac")
    )

