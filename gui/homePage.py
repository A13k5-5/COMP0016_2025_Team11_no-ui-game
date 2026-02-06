import sys
from gameCreationPage import GameCreationPage
from PySide6 import QtWidgets, QtCore, QtGui

class HomePage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self._setup_window_layout("No-UI-Game")
        self._create_widgets()
        self._add_widgets()
           
    def _setup_window_layout(self, window_title : str):
        """
        Set the window title, size and layout.
        """
        self.setWindowTitle(window_title)
        self.resize(800, 600)
        self.layout = QtWidgets.QVBoxLayout(self)

    def _create_widgets(self):
        self.new_game_button = QtWidgets.QPushButton("Create a New Game")
        self.new_game_button.clicked.connect(self.open_game_creator)
        self._creation_window = None

        self.edit_game_button = QtWidgets.QPushButton("Edit Game")
        self.text = QtWidgets.QLabel("No-UI Game", alignment=QtCore.Qt.AlignCenter)

    def _add_widgets(self):
        self.layout.addWidget(self.text)

        # horizontal box layout for the 2 buttons
        self.button_row = QtWidgets.QHBoxLayout()
        self.button_row.addWidget(self.new_game_button)
        self.button_row.addWidget(self.edit_game_button)

        self.layout.addLayout(self.button_row)

    def open_game_creator(self):
        self._creation_window = GameCreationPage()
        self._creation_window.show()



def run():
    app = QtWidgets.QApplication([])

    widget = HomePage()
    widget.setBackgroundRole(QtGui.QPalette.Base)
    widget.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    run()

    