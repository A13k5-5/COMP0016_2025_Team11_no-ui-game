from PySide6 import QtWidgets, QtCore, QtGui 
from .optionSide import OptionSide


class NodeWidget(QtWidgets.QFrame):
    """
    UI widget for a story node with text and two options.
    """
    def __init__(self, page) -> None: # page: GameCreationWindow
        super().__init__()

        # the page the node belongs to
        self.page = page
        self._setup_frame()
        self._create_widgets()
        self._build_layout()
        self._assign_button_functions()

    def _setup_frame(self) -> None:
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setLineWidth(2)
    
    def _create_widgets(self) -> None:
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
    
    def _build_layout(self) -> None:
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

    def _assign_button_functions(self) -> None:
        self.left_plus.clicked.connect(self._create_left_option)
        self.right_plus.clicked.connect(self._create_right_option)

    def _create_left_option(self) -> None:
        """
        Tell the GameCreationPage to create a new node on the left.
        """
        self.page._create_child_node(self, OptionSide.LEFT)

    def _create_right_option(self) -> None:
        """
        Tell the GameCreationPage to create a new node on the right.
        """
        self.page._create_child_node(self, OptionSide.RIGHT)

