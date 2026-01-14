import pystray
from PIL import Image
from gestureRecognizer import GestureRecognition
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

gesture_recognition = GestureRecognition(
    model_path=resource_path("gesture_recognizer.task"),
    target_fps=10
)

def on_start(icon, item):
    gesture_recognition.start()

def on_stop(icon, item):
    gesture_recognition.stop()

def on_exit(icon, item):
    gesture_recognition.stop()
    icon.stop()

image = Image.open(resource_path("icon.png"))

menu = pystray.Menu(
    pystray.MenuItem("Start monitoring", on_start),
    pystray.MenuItem("Stop monitoring", on_stop),
    pystray.MenuItem("Exit", on_exit)
)

icon = pystray.Icon(
    name="GestureMonitor",
    icon=image,
    title="Gesture Monitor",
    menu=menu
)

icon.run()
