import time
from src import Recorder


def main():
    from datetime import datetime
    datetime_str = datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = f"screen/{datetime_str}"

    recorder = Recorder(output_dir)
    try:
        recorder.start()
        print("Recording started... Press Ctrl+C to stop.")
        while True:
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Stopping recording...")
        recorder.stop()


if __name__ == '__main__':
    main()