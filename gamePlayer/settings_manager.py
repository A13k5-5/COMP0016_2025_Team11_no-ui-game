import os
import json
from gesture import EnumGesture

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "..", "settings.json")

DEFAULT_SETTINGS = {
    "input_device": "webcam",  # "webcam" or "keyboard"
    "gestures": {
        "option_left":    EnumGesture.ILoveYou_Left.value,
        "option_right":   EnumGesture.ILoveYou_Right.value,
        "replay_main":    EnumGesture.PointingUp_Left.value,
        "replay_options": EnumGesture.PointingUp_Right.value,
        "quit":           EnumGesture.Victory.value,
    },
    "keyboard": {
        "option_left":    "Left",
        "option_right":   "Right",
        "replay_main":    "R",
        "replay_options": "F",
        "quit":           "Q",
    }
}
 

class SettingsManager:
    """
    Loads and saves player settings to settings.json at the project root.
    """
    def __init__(self):
        self._data: dict = self._load()

    def _load(self) -> dict:
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r") as f:
                    loaded = json.load(f)
                data = dict(loaded)

                return data
            except Exception:
                pass
        return dict(DEFAULT_SETTINGS)