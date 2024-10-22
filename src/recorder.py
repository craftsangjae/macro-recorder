import multiprocessing
import subprocess
import os
from typing import Dict

from src.screen import record_screen
from src.interaction import MouseMonitor, KeyboardMonitor


class Recorder:
    _input_processes: Dict[str, multiprocessing.Process]
    _screen_process: subprocess.Popen

    def __init__(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        self.output_path = os.path.join(output_dir, "output.mp4")
        self._input_processes = {
            'mouse': MouseMonitor(os.path.join(output_dir, "mouse.jsonl")),
            'keyboard': KeyboardMonitor(os.path.join(output_dir, "keyboard.jsonl"))
        }

    def start(self):
        self._screen_process = record_screen(self.output_path)
        for name, process in self._input_processes.items():
            process.start()

    def stop(self):
        for name, process in self._input_processes.items():
            process.terminate()
            process.join(10)
        self._screen_process.terminate()
        self._screen_process.wait(10)


