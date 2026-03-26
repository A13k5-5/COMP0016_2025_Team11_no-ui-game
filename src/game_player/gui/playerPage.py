import os
import sys
import threading
from PySide6 import QtWidgets
from src.game_player.gui.settingsPage import SettingsPage
from src.game_player.model.settings_manager import SettingsManager
from src.game_player.gui.file_association_popup import show_noui_registration_popup_if_needed

from src.game_player.model import game_player, GamePlayer
from src.game_player import myGestureRecognizer


class PlayerPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._settings = SettingsManager()
        self.setWindowTitle("No-UI Game")
        self.resize(400, 120)
        # keyboard or video recogniser
        self._recogniser = None

        self.ran_standalone: bool | None = False

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

        self.gesture_hint_label = QtWidgets.QLabel(
            "Tip: You can view your current gesture bindings in Settings."
        )
        self.gesture_hint_label.setWordWrap(True)
        hint_font = self.gesture_hint_label.font()
        hint_font.setPointSize(max(8, hint_font.pointSize() - 1))
        self.gesture_hint_label.setFont(hint_font)
        self.gesture_hint_label.setStyleSheet("color: #6e6e6e;")
        layout.addWidget(self.gesture_hint_label)

        # Run button
        btn_row = QtWidgets.QHBoxLayout()
        self.run_btn = QtWidgets.QPushButton("Run")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self.run)

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

    def _optional_quit(self):
        # if ran with a file argument, quit the app
        if not self.ran_standalone:
            app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
            app.quit()

    def _play_game(self, player: GamePlayer):
        """
        Runs the game and optionally quits.
        :param player:
        :return:
        """
        player.play_game(self.path_edit.text())
        self._optional_quit()

    def run(self):
        """
        Depending on settings configuration, call gamePlayer with keyboard or video recognizer
        Run the game loop in a background thread so the Qt main thread stays
        free to process keypresses via keyPressEvent.
        """
        if self._settings.is_keyboard_mode():
            from src.game_player.model.keyboard_input_handler import KeyboardInputHandler
            self._recogniser = KeyboardInputHandler(self._settings)
        else:
            self._recogniser = myGestureRecognizer.VideoGestureRecogniser(self._settings)

        player = game_player.GamePlayer(self._recogniser, self._settings)
        thread = threading.Thread(target=self._play_game, args=(player,), daemon=True)
        thread.start()

    def keyPressEvent(self, event) -> None:
        """
        Forward keypresses to KeyboardInputHandler when in keyboard mode.
        """
        if self._settings.is_keyboard_mode() and hasattr(self, "_recogniser"):
            self._recogniser.register_key(event.key())
        super().keyPressEvent(event)

def run(path: str = None):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    window = PlayerPage()
    window.ran_standalone = path is None

    window.show()
    show_noui_registration_popup_if_needed(parent=window)
    if not window.ran_standalone:
        window.path_edit.setText(os.path.abspath(path))
        window.run_btn.setEnabled(False)
        window.run()

    sys.exit(app.exec())
