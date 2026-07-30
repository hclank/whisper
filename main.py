import os
import sys
import queue
import threading
import sounddevice as sd
import soundfile as sf
import pyperclip
from pynput import keyboard
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
