from PySide6 import QtWidgets, QtCore
from gesture import EnumGesture

ACTIONS = [
    ("option_left",    "Option Left"),
    ("option_right",   "Option Right"),
    ("replay_main",    "Replay Main Text"),
    ("replay_options", "Replay Options Text"),
    ("quit",           "Quit / Save Progress"),
]

GESTURE_OPTIONS = [g for g in EnumGesture if g != EnumGesture.INVALID]


class SettingsPage(QtWidgets.QDialog):
    """
    Settings dialog for the game player.
    Allows the user to configure the input device (webcam / keyboard)
    and the gesture binding for each game action.
    Keyboard bindings are predetermined and shown read-only.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dropdowns: dict[str, QtWidgets.QComboBox] = {}

        self._setup_window_layout()
        self._input_selection()
        self._gesture_bindings()
        self._keyboard_bindings()
        self._buttons()

    def _setup_window_layout(self) -> None:
        """Set the window title, size and layout."""
        self.setWindowTitle("Player Settings")
        self.setMinimumWidth(420)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(12)
        self.layout.setContentsMargins(20, 20, 20, 20)

    def _input_selection(self) -> None:
        """Create the input device toggle."""
        device_group = QtWidgets.QGroupBox("Input Device")
        device_layout = QtWidgets.QHBoxLayout(device_group)
        self._webcam_radio = QtWidgets.QRadioButton("Webcam (gesture)")
        self._keyboard_radio = QtWidgets.QRadioButton("Keyboard")
        device_layout.addWidget(self._webcam_radio)
        device_layout.addWidget(self._keyboard_radio)
        self._webcam_radio.setChecked(True)
        self.layout.addWidget(device_group)

    def _gesture_bindings(self) -> None:
        """Create gesture binding dropdowns, one per action."""
        gesture_group = QtWidgets.QGroupBox("Gesture Bindings")
        gesture_layout = QtWidgets.QFormLayout(gesture_group)
        gesture_layout.setSpacing(8)
        for action, label in ACTIONS:
            combo = QtWidgets.QComboBox()
            for g in GESTURE_OPTIONS:
                combo.addItem(g.name, userData=g)
            combo.setCurrentIndex(0)
            self._dropdowns[action] = combo
            gesture_layout.addRow(label + ":", combo)
        self.layout.addWidget(gesture_group)

    def _keyboard_bindings(self) -> None:
        """Show predetermined keyboard bindings as read-only labels."""
        kb_group = QtWidgets.QGroupBox("Keyboard Bindings (fixed)")
        kb_layout = QtWidgets.QFormLayout(kb_group)
        kb_layout.setSpacing(8)
        for action, label in ACTIONS:
            key_label = QtWidgets.QLabel("—")  # TODO: populated from SettingsManager
            key_label.setStyleSheet("color: #555;")
            kb_layout.addRow(label + ":", key_label)
        self.layout.addWidget(kb_group)

    def _buttons(self) -> None:
        """Add Save and Cancel buttons."""
        btn_row = QtWidgets.QHBoxLayout()
        save_btn = QtWidgets.QPushButton("Save")
        save_btn.clicked.connect(self._save)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        self.layout.addLayout(btn_row)

    def _save(self) -> None:
        # TODO: wire into SettingsManager
        self.accept()