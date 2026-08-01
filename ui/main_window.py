from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QThread
from core.audio import AudioRecorder
from core.transcriber import GroqTranscriber
from core.injector import inject_text
from main import is_recording


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

    def setup_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setFixedSize(200, 80)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        self.status_label = QLabel("Ready (Hold Ctrl+Shift)")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            """
            color: white; 
            font-weight: bold; 
            font-family: Arial;
        """
        )

        self.stop_button = QPushButton("Stop & Process")
        self.stop_button.setStyleSheet(
            """
            QPushButton {
                background-color: #ff4757;
                color: white;
                border-radius: 10px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6b81;
            }
        """
        )
        self.stop_button.hide()

        self.stop_button.clicked.connect(self._handle_stop)

        layout.addWidget(self.status_label)
        layout.addWidget(self.stop_button)

        self.setStyleSheet(
            """
            FloatingApp {
                background-color: rgba(30, 30, 30, 220);
                border-radius: 15px;
            }
        """
        )

        self.setLayout(layout)

        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() // 2 - 100, screen.height() - 150)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, "oldPos"):
            delta = event.globalPosition().toPoint() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    def _handle_start(self):
        if self.recorder.is_recording():
            return

        self.recorder.start()

        self.status_label.setText("🎙️ Listening...")
        self.status_label.setStyleSheet(
            "color: #2ed573; font-weight: bold; font-family: Arial;"
        )
        self.stop_button.show()

    def _handle_stop(self):
        if not self.recorder.is_recording:
            return

        audio_data = self.recorder.stop()

        self.stop_button.hide()
        self.status_label.setStyleSheet(
            "color: #ffa502; font-weight: bold; font-family: Arial;"
        )

        if not audio_data:
            self.update_status("No audio.")
            return

        from PyQt6.QtCore import QThread

        self.thread = QThread()
        self.worker = DictationWorker(audio_data)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.status_update.connect(self.update_status)

        self.thread.start()
