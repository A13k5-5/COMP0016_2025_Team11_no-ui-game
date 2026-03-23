import os
import json
from src.game_player.gesture import EnumGesture
from pathlib import Path

SETTINGS_PATH: Path = Path(__file__).parent.parent / "settings.json"

DEFAULT_SETTINGS: dict = {
    "input_device": "webcam",  # "webcam" or "keyboard"
    "gestures": {
        "option_left":    EnumGesture.Thumb_Up_Left.value,
        "option_right":   EnumGesture.Thumb_Up_Right.value,
        "replay_main":    EnumGesture.PointingUp_Left.value,
        "replay_options": EnumGesture.PointingUp_Right.value,
        "quit":           EnumGesture.Victory_Left.value,
    },
    "keyboard": {
        "option_left":    "A",
        "option_right":   "D",
        "replay_main":    "R",
        "replay_options": "F",
        "quit":           "Q",
    },
    "recogniser_timeout": 30.0 # seconds to wait for gesture recognizer before timeout
}
 

class SettingsManager:
    """
    Loads and saves player settings to settings.json at the project root.
    """
    def __init__(self):
        self._data: dict = self._load()

    def _merge_with_defaults(self, candidate: dict, defaults: dict = None) -> dict:
        """
        Recursively merge candidate onto defaults, keeping defaults' schema.
        """
        if not isinstance(candidate, dict):
            return dict(DEFAULT_SETTINGS)
        
        if defaults is None:
            defaults = DEFAULT_SETTINGS

        merged = {}
        for key, default_value in defaults.items():
            candidate_value = candidate.get(key)

            if isinstance(default_value, dict):
                merged[key] = self._merge_with_defaults(candidate_value, default_value)
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

    def is_keyboard_mode(self) -> bool:
        return self._data["input_device"] == "keyboard"
    
    def get_input_device(self) -> str:
        return self._data["input_device"]
 
    def set_input_device(self, device: str) -> None:
        assert device in ("webcam", "keyboard")
        self._data["input_device"] = device

    def get_left_gesture(self) -> EnumGesture:
        return self.get_gesture("option_left")

    def get_right_gesture(self) -> EnumGesture:
        return self.get_gesture("option_right")

    def get_quit_gesture(self) -> EnumGesture:
        return self.get_gesture("quit")

    def get_replay_gestures(self) -> list[EnumGesture]:
        return [self.get_gesture("replay_main"), self.get_gesture("replay_options")]

    def get_progress_gestures(self) -> list[EnumGesture]:
        return [self.get_gesture("option_left"), self.get_gesture("option_right")]

    def get_replay_main_gesture(self) -> EnumGesture:
        return self.get_gesture("replay_main")

    def get_replay_options_gesture(self) -> EnumGesture:
        return self.get_gesture("replay_options")

    def get_gesture(self, action: str) -> EnumGesture:
        return EnumGesture(self._data["gestures"][action])
 
    def set_gesture(self, action: str, gesture: EnumGesture) -> None:
        self._data["gestures"][action] = gesture
    
    def get_key(self, action: str) -> str:
        return self._data["keyboard"][action]

    def set_key(self, action: str, key: str) -> None:
        self._data["keyboard"][action] = key

    def get_recogniser_timeout(self) -> float:
        return self._data["recogniser_timeout"]

    def set_recogniser_timeout(self, timeout: float) -> None:
        self._data["recogniser_timeout"] = timeout
