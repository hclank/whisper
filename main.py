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

current_keys = set()


def should_stop(key):
    if key == keyboard.Key.esc:
        return True
    if hasattr(key, "char") and key.char and key.char.lower() == "q":
        return True
    return False


def on_press(key):
    global is_recording
    current_keys.add(key)

    has_ctrl = any(
        k in current_keys
        for k in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r)
    )
    has_shift = any(
        k in current_keys
        for k in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r)
    )

    if has_ctrl and has_shift and not is_recording:
        print("Recording started (Ctrl + Shift held)...")
        is_recording = True
        while not audio_queue.empty():
            audio_queue.get()


def on_release(key):
    global is_recording

    if key in current_keys:
        current_keys.remove(key)

    if is_recording:
        has_ctrl = any(
            k in current_keys
            for k in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r)
        )
        has_shift = any(
            k in current_keys
            for k in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r)
        )

        if not (has_ctrl and has_shift):
            print("Recording stopped (key released).")
            is_recording = False
            threading.Thread(target=process_audio).start()

    if should_stop(key):
        print("Exiting...")
        return False


if __name__ == "__main__":
    print("Dictation script running.")
    print("Press and hold Control + Shift to record.")
    print("Release either key to process and paste.")
    print("Press Q or ESC to quit.")

    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=audio_callback)
    with stream:
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
