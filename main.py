import os
import sys
import queue
import time
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
import pyperclip
from pynput import keyboard
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SAMPLE_RATE = 16000
TEMP_AUDIO_FILE = "temp_dictation.wav"

is_recording = False
audio_queue = queue.Queue()
current_keys = set()


def audio_callback(indata, frames, time_info, status):
    if status:
        print(status, file=sys.stderr)
    if is_recording:
        audio_queue.put(indata.copy())


def process_audio():
    global is_recording
    audio_data = []

    while not audio_queue.empty():
        audio_data.append(audio_queue.get())

    if not audio_data:
        print("No audio recorded.")
        return

    print("Processing audio...")

    audio_concat = np.concatenate(audio_data, axis=0)
    sf.write(TEMP_AUDIO_FILE, audio_concat, SAMPLE_RATE)

    try:
        with open(TEMP_AUDIO_FILE, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=(TEMP_AUDIO_FILE, f.read()),
                model="whisper-large-v3-turbo",
                response_format="text",
            )
            raw_text = transcription
            print(f"Raw text: {raw_text}")

            cleanup_prompt = """
        You are a dictation cleanup engine. Rewrite the raw speech transcript into clean, properly punctuated text. 
        Remove fillers (um, ah, like), fix self-corrections inline, and preserve the original tone. 
        Output ONLY the polished text. Do not add any conversational preamble.
        """

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": cleanup_prompt},
                    {"role": "user", "content": raw_text},
                ],
                model="llama-3.1-8b-instant",
                temperature=0.2,
            )
            cleaned_text = chat_completion.choices[0].message.content
            print(f"cleaned text: {cleaned_text}")

            inject_text(cleaned_text)
    except Exception as e:
        print(f"Error transcribing audio: {e}")
    finally:
        if os.path.exists(TEMP_AUDIO_FILE):
            os.remove(TEMP_AUDIO_FILE)
        print("Ready for next dictation.")


def inject_text(text):
    old_clipboard = pyperclip.paste()
    pyperclip.copy(text)
    time.sleep(0.1)
    keyboard_controller = keyboard.Controller()
    modifier_key = keyboard.Key.cmd if sys.platform == "darwin" else keyboard.Key.ctrl

    with keyboard_controller.pressed(modifier_key):
        keyboard_controller.press("v")
        keyboard_controller.release("v")
