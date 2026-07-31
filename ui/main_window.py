from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QThread
from core.audio import AudioRecorder
from core.transcriber import GroqTranscriber
from core.injector import inject_text


class DictationWorker(QObject):
    finished = pyqtSignal()
    status_update = pyqtSignal(str)

    def __init__(self, audio_data):
        super().__init__()
        self.audio_data = audio_data
        self.transcriber = GroqTranscriber
