import sys
from .gameCreationPage import GameCreationPage
from PySide6 import QtWidgets, QtCore, QtGui
from . import config

class HomePage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self._setup_window_layout("No-UI-Game")
        self._create_widgets()
        self._add_widgets()
           
    def _setup_window_layout(self, window_title: str) -> None:
        """
        Set the window title, size and layout.
        """
        self.setWindowTitle(window_title)
        self.resize(config.WINDOW_HEIGHT, config.WINDOW_WIDTH)
        self.layout = QtWidgets.QVBoxLayout(self)

    def _create_widgets(self) -> None:
        self.new_game_button = QtWidgets.QPushButton("Create a New Game")
        self.new_game_button.clicked.connect(self.open_game_creator)
        self._creation_window = None

        self.edit_game_button = QtWidgets.QPushButton("Edit Game")
        self.edit_game_button.clicked.connect(self.open_file_dialog)
        self.text = QtWidgets.QLabel("No-UI Game", alignment=QtCore.Qt.AlignCenter)

    def _add_widgets(self) -> None:
        self.layout.addWidget(self.text)

        # horizontal box layout for the 2 buttons
        self.button_row = QtWidgets.QHBoxLayout()
        self.button_row.addWidget(self.new_game_button)
        self.button_row.addWidget(self.edit_game_button)

        self.layout.addLayout(self.button_row)

    def open_game_creator(self) -> None:
        self._creation_window = GameCreationPage()
        self._creation_window.show()

    def open_file_dialog(self) -> None:
        """
        Open Finder file picker. No file handling yet.
        """
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Game File",
            "",
            "All Files (*.*)"
        )
        if file_path:
            print(f"Selected file: {file_path}")


def run():
    app = QtWidgets.QApplication([])

    widget = HomePage()
    widget.setBackgroundRole(QtGui.QPalette.Base)
    widget.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    run()

    