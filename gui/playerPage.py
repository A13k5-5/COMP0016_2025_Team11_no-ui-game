import sys
import os
from PySide6 import QtWidgets


class PlayerPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("No-UI Game")
        self.resize(400, 120)

        layout = QtWidgets.QVBoxLayout(self)

        # Folder selection row
        folder_row = QtWidgets.QHBoxLayout()
        self.path_edit = QtWidgets.QLineEdit()
        self.path_edit.setPlaceholderText("Select a game folder…")
        self.path_edit.setReadOnly(True)
        browse_btn = QtWidgets.QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse)
        folder_row.addWidget(self.path_edit)
        folder_row.addWidget(browse_btn)
        layout.addLayout(folder_row)

        # Run button
        self.run_btn = QtWidgets.QPushButton("Run")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run)
        layout.addWidget(self.run_btn)

    def _browse(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Game Folder", os.path.expanduser("~"),
            QtWidgets.QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.path_edit.setText(os.path.abspath(folder))
            self.run_btn.setEnabled(True)

    def _run(self):
        import gamePlayer
        player = gamePlayer.GamePlayer()
        player.playGame(self.path_edit.text())


def run():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    window = PlayerPage()
    window.show()
    sys.exit(app.exec())

