import sys
from PySide6 import QtWidgets, QtCore

class HomePage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CYOA Game Editor")

        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("Hello World", alignment=QtCore.Qt.AlignCenter)

        # set layout type and place widgets
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)

def run():
    app = QtWidgets.QApplication([])

    widget = HomePage()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run()

    