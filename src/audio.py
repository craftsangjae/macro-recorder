import struct
import threading
import wave

from pvrecorder import PvRecorder


def record_audio(save_path: str, stop_signal: threading.Event):
    """ Record Microphone to wave file. """
    recorder = PvRecorder(device_index=-1, frame_length=512)
    audio = []

    recorder.start()
    while not stop_signal.is_set():
        frame = recorder.read()
        audio.extend(frame)

    recorder.stop()
    with wave.open(save_path, 'w') as f:
        f.setparams((1, 2, 16000, 512, "NONE", "NONE"))
        f.writeframes(struct.pack("h" * len(audio), *audio))
    recorder.delete()
