from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QThread
from core.audio import AudioRecorder
from core.transcriber import GroqTranscriber
from core.injector import inject_text
