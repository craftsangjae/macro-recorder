from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,
    QLabel, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import QTimer
import sys
from src.recorder import Recorder
import os
import json  # JSON 로그 파싱을 위해 추가


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("화면 녹화 프로그램")

        self.recorder = None
        self.output_dir = ""

        layout = QVBoxLayout()

        self.select_folder_button = QPushButton("저장할 폴더 선택")
        self.select_folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.select_folder_button)

        self.folder_label = QLabel("선택된 폴더: 없음")
        layout.addWidget(self.folder_label)

        self.start_button = QPushButton("녹화 시작")
        self.start_button.clicked.connect(self.start_recording)
        self.start_button.setEnabled(False)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("녹화 종료")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        # 로그 표시를 위한 탭 위젯 추가
        self.tabs = QTabWidget()

        # 마우스 로그 테이블 설정
        self.mouse_log_table = QTableWidget()
        self.mouse_log_table.setColumnCount(4)
        self.mouse_log_table.setHorizontalHeaderLabels(["시간", "X 좌표", "Y 좌표", "동작"])
        self.mouse_log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabs.addTab(self.mouse_log_table, "마우스 로그")

        # 키보드 로그 테이블 설정
        self.keyboard_log_table = QTableWidget()
        self.keyboard_log_table.setColumnCount(3)
        self.keyboard_log_table.setHorizontalHeaderLabels(["시간", "동작", "키"])
        self.keyboard_log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabs.addTab(self.keyboard_log_table, "키보드 로그")

        layout.addWidget(self.tabs)

        self.setLayout(layout)

        # 타이머 설정하여 로그 파일 업데이트
        self.timer = QTimer()
        self.timer.setInterval(200)  # 0.2초마다 업데이트
        self.timer.timeout.connect(self.update_logs)

        # 로그 파일의 마지막 읽은 위치 추적
        self.mouse_log_position = 0
        self.keyboard_log_position = 0

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "저장할 폴더 선택")
        if folder:
            self.output_dir = folder
            self.folder_label.setText(f"선택된 폴더: {self.output_dir}")
            self.start_button.setEnabled(True)

    def start_recording(self):
        if self.output_dir:
            # 로그 테이블 초기화
            self.mouse_log_table.setRowCount(0)
            self.keyboard_log_table.setRowCount(0)
            self.mouse_log_position = 0
            self.keyboard_log_position = 0

            self.recorder = Recorder(self.output_dir)
            self.recorder.start()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.timer.start()  # 녹화 시작 시 타이머 시작

    def stop_recording(self):
        if self.recorder:
            self.recorder.stop()
            self.recorder = None
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.timer.stop()  # 녹화 종료 시 타이머 정지

    def update_logs(self):
        if self.output_dir:
            mouse_log_path = os.path.join(self.output_dir, "mouse.jsonl")
            keyboard_log_path = os.path.join(self.output_dir, "keyboard.jsonl")

            # 마우스 로그 업데이트
            if os.path.exists(mouse_log_path):
                with open(mouse_log_path, 'r', encoding="utf-8") as f:
                    f.seek(self.mouse_log_position)
                    new_logs = f.read()
                    self.mouse_log_position = f.tell()
                    if new_logs:
                        for line in new_logs.strip().split('\n'):
                            try:
                                log = json.loads(line)
                                time_str = f"{log[0]:.3f}"
                                x = f"{log[1]:.3f}"
                                y = f"{log[2]:.3f}"
                                action = log[3]
                                row_position = self.mouse_log_table.rowCount()
                                self.mouse_log_table.insertRow(row_position)
                                self.mouse_log_table.setItem(row_position, 0, QTableWidgetItem(time_str))
                                self.mouse_log_table.setItem(row_position, 1, QTableWidgetItem(x))
                                self.mouse_log_table.setItem(row_position, 2, QTableWidgetItem(y))
                                self.mouse_log_table.setItem(row_position, 3, QTableWidgetItem(action))
                            except json.JSONDecodeError:
                                continue

            # 키보드 로그 업데이트
            if os.path.exists(keyboard_log_path):
                with open(keyboard_log_path, 'r', encoding="utf-8") as f:
                    f.seek(self.keyboard_log_position)
                    new_logs = f.read()
                    self.keyboard_log_position = f.tell()
                    if new_logs:
                        for line in new_logs.strip().split('\n'):
                            try:
                                log = json.loads(line)
                                time_str = f"{log[0]:.3f}"
                                action = log[1]
                                key = log[2]
                                row_position = self.keyboard_log_table.rowCount()
                                self.keyboard_log_table.insertRow(row_position)
                                self.keyboard_log_table.setItem(row_position, 0, QTableWidgetItem(time_str))
                                self.keyboard_log_table.setItem(row_position, 1, QTableWidgetItem(action))
                                self.keyboard_log_table.setItem(row_position, 2, QTableWidgetItem(key))
                            except json.JSONDecodeError:
                                continue


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
