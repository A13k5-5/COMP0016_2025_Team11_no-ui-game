import pystray
from PIL import Image
from personRecognizer import GestureRecognition
import sys
import os

# --- Utility to handle PyInstaller paths ---
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# --- Create gesture recognizer instance ---
gesture_recognition = GestureRecognition(target_fps=10)

# --- Tray callbacks ---
def on_start(icon, item):
    gesture_recognition.start()

def on_stop(icon, item):
    gesture_recognition.stop()

def on_exit(icon, item):
    gesture_recognition.stop()
    icon.stop()

# --- Load tray icon ---
image = Image.open(resource_path("icon.png"))

# --- Build tray menu ---
menu = pystray.Menu(
    pystray.MenuItem("Start monitoring", on_start),
    pystray.MenuItem("Stop monitoring", on_stop),
    pystray.MenuItem("Exit", on_exit)
)

# --- Run tray icon ---
icon = pystray.Icon(
    name="GestureMonitor",
    icon=image,
    title="Gesture Monitor",
    menu=menu
)

icon.run()