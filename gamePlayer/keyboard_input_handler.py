from PySide6 import QtWidgets, QtCore, QtGui
from gesture import EnumGesture
from gamePlayer.settings_manager import SettingsManager

class KeyboardInputHandler:
    """
    Waits for a keypress and maps it to an EnumGesture using the configured keyboard bindings.
    """
    def __init__(self, settings: SettingsManager):
        self._last_key: int | None = None

        self._key_to_gesture: dict[int, EnumGesture] = {}
        # for every game action:
        # 1) get the configured key string from settings
        # 2) convert key string to Qt code ("A" -> QtCore.Qt.Key_A)
        # 3) map it to the corresponding EnumGesture
        for action in ("option_left", "option_right", "replay_main", "replay_options", "quit"):
            key_str = settings.get_key(action).upper()
            qt_key = getattr(QtCore.Qt, f"Key_{key_str}", None)
            if qt_key is not None:
                self._key_to_gesture[qt_key] = settings.get_gesture(action)

    def get_gesture(self, gestures_to_spot: list[EnumGesture]) -> EnumGesture:
        """
        Blocks until the user presses a key mapped to one of gestures_to_spot.
        The quit gesture is always accepted regardless of gestures_to_spot.
        """
        while True:
            QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents, 100)
            key = self._last_key
            self._last_key = None
            if key is None:
                continue
            gesture = self._key_to_gesture.get(key)
            if gesture is None:
                continue
            if gesture in gestures_to_spot:
                return gesture
    
    def register_key(self, key: int) -> None:
        """
        Called by PlayerPage.keyPressEvent when a key is pressed.
        """
        self._last_key = key