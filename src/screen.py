import subprocess
import re
from typing import Tuple, List
import ffmpeg


def pick_audio_device():
    """ 오디오 디바이스를 선택합니다. """
    device_list = get_audio_devices()
    return select_best_audio_device(device_list)


def get_audio_devices() -> List[Tuple[str, str]]:
    """ 모든 오디오 장치 정보를 가져옵니다. """
    ffmpeg_command = ['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', '""']
    process = subprocess.Popen(ffmpeg_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    output, error = process.communicate()
    error = error.decode('utf-8')
    return re.findall(r'\[(\d+)\] (.*)', error.split('audio devices:')[-1])


def select_best_audio_device(devices: List[Tuple[str, str]]) -> str:
    priority_keywords = ['airpods', 'macbook', 'microphone']
    for keyword in priority_keywords:
        keyword = keyword.lower()
        for device_id, device_name in devices:
            if keyword in device_name.lower():
                return device_id

    if devices:
        return devices[0][0]


def pick_capture_screen():
    device_list = get_video_devices()
    return select_capture_screen(device_list)


def get_video_devices() -> List[Tuple[str, str]]:
    """ 모든 비디오 장치 정보를 가져옵니다.
    """
    ffmpeg_command = ['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', '""']
    process = subprocess.Popen(ffmpeg_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    output, error = process.communicate()
    error = error.decode('utf-8')
    return re.findall(r'\[(\d+)\] (.*)', error.split('audio devices:')[0].split('video devices:')[-1])


def select_capture_screen(devices: List[Tuple[str, str]]):
    priority_keywords = ['Capture screen']
    for keyword in priority_keywords:
        keyword = keyword.lower()
        for device_id, device_name in devices:
            if keyword in device_name.lower():
                return device_id
    if devices:
        return devices[0][0]


def record_screen(output_path: str) -> subprocess.Popen:
    """ 화면을 녹화합니다 """
    video_device_id = pick_capture_screen()
    audio_device_id = pick_audio_device()

    ffmpeg_command = (
        ffmpeg
        .input(f'{video_device_id}:{audio_device_id}',
               format='avfoundation',
               capture_cursor=1,
               capture_mouse_clicks=1)
        .output(output_path,
                vcodec='libx264',
                acodec='aac')
        .overwrite_output()
        .compile()
    )
    return subprocess.Popen(
        ffmpeg_command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )