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
        self.transcriber = GroqTranscriber()

    def run(self):
        self.status_update.emit("Processing...")
        try:
            cleaned_text = self.transcriber.process(self.audio_data)
            self.status_update.emit("Pasting...")
            inject_text(cleaned_text)
        except:
            self.status_update.emit("Error!")
        finally:
            self.status_update.emit("Ready")
            self.finished.emit()


class FloatingApp(QWidget):
    start_recording_signal = pyqtSignal()
    stop_recording_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.recorder = AudioRecorder()
        self.setup_ui()
