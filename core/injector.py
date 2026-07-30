import sys
import time
import pyperclip
from pynput import keyboard


def inject_text(text):
    pyperclip.copy(text)
    time.sleep(0.1)

    keyboard_controller = keyboard.Controller()
    modifier = keyboard.Key.cmd if sys.platform == "darwin" else keyboard.Key.ctrl

    with keyboard_controller.pressed(modifier):
        keyboard_controller.press("v")
        keyboard_controller.release("v")
