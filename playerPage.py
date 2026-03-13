import sys
import os
from PySide6 import QtWidgets
from PySide6.QtCore import QThread

import gamePlayer


class GameThread(QThread):
    def __init__(self, game_path):
        super().__init__()
        self.game_path = game_path

    def run(self):
        player = gamePlayer.GamePlayer()
        player.play_game(self.game_path)


class PlayerPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("No-UI Game")
        self.resize(400, 120)

        layout = QtWidgets.QVBoxLayout(self)

        # Folder selection row
        folder_row = QtWidgets.QHBoxLayout()
        self.path_edit = QtWidgets.QLineEdit()
        self.path_edit.setPlaceholderText("Select a game…")
        self.path_edit.setReadOnly(True)
        self.browse_btn = QtWidgets.QPushButton("Browse…")
        self.browse_btn.clicked.connect(self._browse)
        folder_row.addWidget(self.path_edit)
        folder_row.addWidget(self.browse_btn)
        layout.addLayout(folder_row)

        # Run button
        self.run_btn = QtWidgets.QPushButton("Run")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run)
        layout.addWidget(self.run_btn)

    def _browse(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Game Zip", os.path.expanduser("~"),
            "Game files (*.noui)"
        )
        if path:
            self.path_edit.setText(os.path.abspath(path))
            self.run_btn.setEnabled(True)

    def _run(self):
        self.run_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)

        self.thread = GameThread(self.path_edit.text())
        self.thread.finished.connect(self._on_game_finished)
        self.thread.start()

    def _on_game_finished(self):
        self.run_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)


def run():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    window = PlayerPage()

    window.show()
    sys.exit(app.exec())
