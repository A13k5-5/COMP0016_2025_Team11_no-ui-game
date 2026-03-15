from PySide6 import QtWidgets, QtCore, QtGui
from gesture import EnumGesture

# pre-set Qt-key codes to actions
_KEY_TO_GESTURE: dict[int, EnumGesture] = {
    QtCore.Qt.Key_Left:  EnumGesture.ILoveYou_Left,
    QtCore.Qt.Key_Right: EnumGesture.ILoveYou_Right,
    QtCore.Qt.Key_R:     EnumGesture.PointingUp_Left,
    QtCore.Qt.Key_F:     EnumGesture.PointingUp_Right,
    QtCore.Qt.Key_Q:     EnumGesture.Victory,
}

_last_key: int | None = None

class KeyboardInputHandler:
    """
    Waits for a keypress and maps it to an EnumGesture using the configured keyboard bindings.
    """

    def get_gesture(self, gestures_to_spot: list[EnumGesture]) -> EnumGesture:
        """
        Blocks until the user presses a key mapped to one of gestures_to_spot.
        The quit gesture is always accepted regardless of gestures_to_spot.
        """
        global _last_key

        while True:
            QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents, 100)
            key = _last_key
            _last_key = None
            if key is None:
                continue
            gesture = _KEY_TO_GESTURE.get(key)
            if gesture is None:
                continue
            if gesture in gestures_to_spot or gesture == self._quit_gesture:
                return gesture
    
    @staticmethod
    def register_key(key: int) -> None:
        """
        Called by PlayerPage.keyPressEvent when a key is pressed.
        """
        global _last_key
        _last_key = key