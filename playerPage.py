import sys
import os
from PySide6 import QtWidgets
from gui.settingsPage import SettingsPage
from gamePlayer.settings_manager import SettingsManager

import gamePlayer


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
        """
        if self._settings.is_keyboard_mode():
            from gamePlayer.keyboard_input_handler import KeyboardInputHandler
            recogniser = KeyboardInputHandler(self._settings)
        else:
            import myGestureRecognizer
            recogniser = myGestureRecognizer.VideoGestureRecogniser()
        player = gamePlayer.GamePlayer(recogniser)
        player.play_game(self.path_edit.text())


def run():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    window = PlayerPage()

    window.show()
    sys.exit(app.exec())
