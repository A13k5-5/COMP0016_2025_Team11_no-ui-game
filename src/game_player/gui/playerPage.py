import sys
import os
from PySide6 import QtWidgets, QtCore
from src.game_player.gui.settingsPage import SettingsPage
from src.game_player.model.settings_manager import SettingsManager
from src.game_player.gui.file_association_popup import show_noui_registration_popup_if_needed

from src.game_player.model import game_player
from src.game_player import myGestureRecognizer

class WorkerSignal(QtCore.QObject):
    finished = QtCore.Signal()

class Worker(QtCore.QRunnable):
    def __init__(self, recogniser, settings, path):
        super().__init__()
        self.recogniser = recogniser
        self.settings = settings
        self.path = path
        self.signals = WorkerSignal()

    @QtCore.Slot()
    def run(self):
        try:
            player = game_player.GamePlayer(self.recogniser, self.settings)
            player.play_game(self.path)
        finally:
            self.signals.finished.emit()


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

    def _quit(self):
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        app.quit()

    def _run(self):
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

        worker = Worker(self._recogniser, self._settings, self.path_edit.text())
        worker.signals.finished.connect(self._quit)
        # run method of the worker starts (the game loop)
        QtCore.QThreadPool.globalInstance().start(worker)

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

    window.show()
    show_noui_registration_popup_if_needed(parent=window)
    if path is not None:
        window.path_edit.setText(os.path.abspath(path))
        window.run_btn.setEnabled(True)
        window._run()

    app.exec()
