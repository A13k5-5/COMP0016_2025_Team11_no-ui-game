import sys
from PySide6 import QtWidgets, QtCore, QtGui

class HomePage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # set title, size and layout type (vertical box)
        self.setWindowTitle("No-UI-Game Editor")
        self.resize(800, 600)
        self.layout = QtWidgets.QVBoxLayout(self)
        
        # create widgets
        self.new_game_button = QtWidgets.QPushButton("Create a New Game")
        self.edit_game_button = QtWidgets.QPushButton("Edit Game")
        self.text = QtWidgets.QLabel("Hello World", alignment=QtCore.Qt.AlignCenter)

        # add widgets
        self.layout.addWidget(self.text)

        # horizontal box layout for the 2 buttons
        self.button_row = QtWidgets.QHBoxLayout()
        self.button_row.addWidget(self.new_game_button)
        self.button_row.addWidget(self.edit_game_button)

        self.layout.addLayout(self.button_row)


def run():
    app = QtWidgets.QApplication([])

    widget = HomePage()
    widget.setBackgroundRole(QtGui.QPalette.Base)
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run()

    