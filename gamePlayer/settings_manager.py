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

    def _merge_with_defaults(self, candidate: dict) -> dict:
        """
        Recursively merge candidate onto defaults, keeping defaults' schema.
        """
        if not isinstance(candidate, dict):
            return dict(DEFAULT_SETTINGS)

        merged = {}
        for key, default_value in DEFAULT_SETTINGS.items():
            candidate_value = candidate.get(key)

            if isinstance(default_value, dict):
                merged[key] = self._merge_with_defaults(default_value, candidate_value)
            elif candidate_value is None:
                merged[key] = default_value
            else:
                merged[key] = candidate_value

        return merged

    def _load(self) -> dict:
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r") as f:
                    loaded = json.load(f)
                return self._merge_with_defaults(loaded)
            except Exception:
                pass
        return dict(DEFAULT_SETTINGS)
    
    def save(self) -> None:
        """
        Persist current settings to settings.json.
        """
        with open(SETTINGS_PATH, "w") as f:
            json.dump(self._data, f, indent=4)