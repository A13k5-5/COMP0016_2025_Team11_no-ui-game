import sys
from PySide6 import QtWidgets, QtCore, QtGui

class ZoomableGraphicsView(QtWidgets.QGraphicsView):
    """
    Allows zoom in/out and drag functionality by using a 
    mouse wheel or trackpad - Ctrl+scroll.
    """
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        # current zoom level
        self._zoom = 1.0 
    
    def wheelEvent(self, event):
        if event.modifiers() & QtCore.Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self._zoom *= 1.15
            else:
                self._zoom /= 1.15

            # limit zooming too far out/in
            self._zoom = max(0.2, min(self._zoom, 3.0)) 
            self.setTransform(QtGui.QTransform().scale(self._zoom, self._zoom))
            event.accept()
        else:
            super().wheelEvent(event)


class NodeWidget(QtWidgets.QFrame):
    """
    UI widget for a story node with text and two options.
    """
    def __init__(self):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setLineWidth(2)

        self.text = QtWidgets.QPlainTextEdit()
        self.text.setPlaceholderText("Write the node text here...")

        self.left_option = QtWidgets.QLineEdit()
        self.left_option.setPlaceholderText("Left option text")
        self.left_plus = QtWidgets.QPushButton("+")
        self.left_plus.setFixedWidth(22)

        self.right_option = QtWidgets.QLineEdit()
        self.right_option.setPlaceholderText("Right option text")
        self.right_plus = QtWidgets.QPushButton("+")
        self.right_plus.setFixedWidth(22)

        options_row = QtWidgets.QHBoxLayout()
        left_col = QtWidgets.QVBoxLayout()
        right_col = QtWidgets.QVBoxLayout()

        left_col.addWidget(self.left_option)
        left_col.addWidget(self.left_plus, alignment=QtCore.Qt.AlignCenter)

        right_col.addWidget(self.right_option)
        right_col.addWidget(self.right_plus, alignment=QtCore.Qt.AlignCenter)

        options_row.addLayout(left_col)
        options_row.addLayout(right_col)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.text)
        layout.addLayout(options_row)

        # placeholder hooks for arrow creation
        self.left_plus.clicked.connect(lambda: print("Left + clicked"))
        self.right_plus.clicked.connect(lambda: print("Right + clicked"))


class GameCreationPage(QtWidgets.QWidget):
    """
    Main page for creating a no-ui game.
    """
    def __init__(self):
        super().__init__()

        self.game_title = ""
        self._setup_window_layout("No-UI-Game Creator")
        self._title_entry()

        self._setup_canvas()
        self._add_root_node()
    
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

    def _setup_canvas(self):
        self.scene = QtWidgets.QGraphicsScene(self)
        self.view = ZoomableGraphicsView(self.scene)
        self.view.setMinimumHeight(400)
        self.layout.addWidget(self.view)

    def _add_root_node(self):
        root_widget = NodeWidget()
        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(root_widget)
        proxy.setPos(50, 50)
        self.scene.addItem(proxy)

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