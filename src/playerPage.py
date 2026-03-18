import sys
import os
from PySide6 import QtWidgets

from src.gui.settingsPage import SettingsPage
from src.gamePlayer.settings_manager import SettingsManager

from src import gamePlayer


class PlayerPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._settings = SettingsManager()
        self.setWindowTitle("No-UI Game")
        self.resize(400, 120)

        layout = QtWidgets.QVBoxLayout(self)

        # Folder selection row
        folder_row = QtWidgets.QHBoxLayout()
        self.path_edit = QtWidgets.QLineEdit()
        self.path_edit.setPlaceholderText("Select a game…")
        self.path_edit.setReadOnly(True)
        browse_btn = QtWidgets.QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse)
        folder_row.addWidget(self.path_edit)
        folder_row.addWidget(browse_btn)
        layout.addLayout(folder_row)

        # Run button
        btn_row = QtWidgets.QHBoxLayout()
        self.run_btn = QtWidgets.QPushButton("Run")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run)

        settings_btn = QtWidgets.QPushButton("⚙ Settings")
        settings_btn.clicked.connect(self._open_settings)
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(settings_btn)
        layout.addLayout(btn_row)

    def _browse(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Game Zip", os.path.expanduser("~"),
            "Game files (*.noui)"
        )
        if path:
            self.path_edit.setText(os.path.abspath(path))
            self.run_btn.setEnabled(True)
    
    def _open_settings(self):
        dlg = SettingsPage(self._settings, parent=self)
        dlg.exec()

    def _run(self):
        """
        Depending on settings configuration, call gamePlayer with keyboard or video recognizer
        Run the game loop in a background thread so the Qt main thread stays
        free to process keypresses via keyPressEvent.
        """
        import threading
        if self._settings.is_keyboard_mode():
            from src.gamePlayer.keyboard_input_handler import KeyboardInputHandler
            self._recogniser = KeyboardInputHandler(self._settings)
        else:
            from src import myGestureRecognizer
            self._recogniser = myGestureRecognizer.VideoGestureRecogniser()

        player = gamePlayer.GamePlayer(self._recogniser, self._settings)
        thread = threading.Thread(
            target=player.play_game,
            args=(self.path_edit.text(),),
            daemon=True
        )
        # daemon thread = background thread that dies when the main program exits
        thread.start()

    def keyPressEvent(self, event) -> None:
        """
        Forward keypresses to KeyboardInputHandler when in keyboard mode.
        """
        print("key pressed:", event.key(), "has recogniser:", hasattr(self, "_recogniser"))
        if self._settings.is_keyboard_mode() and hasattr(self, "_recogniser"):
            self._recogniser.register_key(event.key())
        super().keyPressEvent(event)

def run(path: str = None):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    window = PlayerPage()

    window.show()
    if path is not None:
        window.path_edit.setText(os.path.abspath(path))
        window.run_btn.setEnabled(True)
        window._run()

    sys.exit(app.exec())
