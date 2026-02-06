import sys
from PySide6 import QtWidgets, QtCore, QtGui

class GameCreationPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.game_title = ""
        self._setup_window_layout("No-UI-Game Creator")
        self._title_entry()
    
    def _setup_window_layout(self, window_title : str):
        """
        Set the window title, size and layout.
        """
        self.setWindowTitle(window_title)
        self.resize(800, 600)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        
    def _title_entry(self):
        # create title entry bar and save button
        self.title_entry = QtWidgets.QLineEdit()
        self.title_entry.setPlaceholderText("Enter game title...")

        self.save_title_button = QtWidgets.QPushButton("Save Title")
        self.save_title_button.clicked.connect(self.save_title)

        #save widgets
        self.layout.addWidget(self.title_entry)
        self.layout.addWidget(self.save_title_button)

    def save_title(self):
        self.game_title = self.title_entry.text().strip()
        print(f"Saved title: {self.game_title}")

def run():
    app = QtWidgets.QApplication([])

    widget = GameCreationPage()
    widget.setBackgroundRole(QtGui.QPalette.Base)
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run()