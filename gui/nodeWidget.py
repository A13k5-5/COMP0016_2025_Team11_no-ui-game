from PySide6 import QtWidgets, QtCore
from .optionSide import OptionSide
from . import config


class NodeWidget(QtWidgets.QFrame):
    """
    UI widget for a story node with text and two options.
    Each node has:
      - a text field for the gesture label
      - a "+" button to create a new child node in the tree
      - a "🔗" button to enter link mode and connect to an existing node
    """
    def __init__(self, page) -> None:  # page: GameCreationPage
        super().__init__()

        self.page = page
        self._setup_frame()
        self._create_widgets()
        self._build_layout()
        self._assign_button_functions()

    def _setup_frame(self) -> None:
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setLineWidth(2)
        self.setFixedSize(config.NODE_WIDTH, config.NODE_HEIGHT)

    def _create_widgets(self) -> None:
        self.text = QtWidgets.QPlainTextEdit()
        self.text.setPlaceholderText("Write the node text here...")

        # Left option row
        self.left_option = QtWidgets.QLineEdit()
        self.left_option.setPlaceholderText("Left option text")
        self.left_plus = QtWidgets.QPushButton("+")
        self.left_plus.setFixedWidth(config.PLUS_BUTTON_WIDTH)

        self.left_link = QtWidgets.QPushButton("🔗")
        self.left_link.setFixedWidth(config.PLUS_BUTTON_WIDTH)
        self.left_link.setToolTip("Link this option to an existing node")

        # Right option row
        self.right_option = QtWidgets.QLineEdit()
        self.right_option.setPlaceholderText("Right option text")
        self.right_plus = QtWidgets.QPushButton("+")
        self.right_plus.setFixedWidth(config.PLUS_BUTTON_WIDTH)

        self.right_link = QtWidgets.QPushButton("🔗")
        self.right_link.setFixedWidth(config.PLUS_BUTTON_WIDTH)
        self.right_link.setToolTip("Link this option to an existing node")

        self.delete_button = QtWidgets.QPushButton("Delete")
        self.delete_button.setVisible(False)
        self.delete_button.setStyleSheet("background-color: #ff6b6b; color: white;")

        self.win_button = QtWidgets.QPushButton("⭐ Set as Win")
        self.win_button.setCheckable(True)
        self.win_button.clicked.connect(self._set_win)

        self.lose_button = QtWidgets.QPushButton("❌ Set as Loss")
        self.lose_button.setVisible(False)
        self.lose_button.setCheckable(True)
        self.lose_button.clicked.connect(self._set_loss)

    def _build_layout(self) -> None:
        options_row = QtWidgets.QHBoxLayout()
        left_col = QtWidgets.QVBoxLayout()
        right_col = QtWidgets.QVBoxLayout()

        # Left: text field, then + and 🔗 side by side
        left_col.addWidget(self.left_option)
        left_buttons = QtWidgets.QHBoxLayout()
        left_buttons.addWidget(self.left_plus)
        left_buttons.addWidget(self.left_link)
        left_col.addLayout(left_buttons)

        # Right: text field, then + and 🔗 side by side
        right_col.addWidget(self.right_option)
        right_buttons = QtWidgets.QHBoxLayout()
        right_buttons.addWidget(self.right_plus)
        right_buttons.addWidget(self.right_link)
        right_col.addLayout(right_buttons)

        options_row.addLayout(left_col)
        options_row.addLayout(right_col)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.text)
        layout.addLayout(options_row)
        layout.addWidget(self.win_button, alignment=QtCore.Qt.AlignLeft)
        layout.addWidget(self.lose_button,  alignment=QtCore.Qt.AlignLeft)
        layout.addWidget(self.delete_button, alignment=QtCore.Qt.AlignRight)

    def _assign_button_functions(self) -> None:
        self.left_plus.clicked.connect(self._create_left_child)
        self.right_plus.clicked.connect(self._create_right_child)
        self.left_link.clicked.connect(self._start_left_link)
        self.right_link.clicked.connect(self._start_right_link)
        self.delete_button.clicked.connect(self._delete_self)

    def _create_left_child(self) -> None:
        self.page._create_child_node(self, OptionSide.LEFT)

    def _create_right_child(self) -> None:
        self.page._create_child_node(self, OptionSide.RIGHT)

    def _start_left_link(self) -> None:
        self.page.enter_link_mode(self, OptionSide.LEFT)

    def _start_right_link(self) -> None:
        self.page.enter_link_mode(self, OptionSide.RIGHT)

    def _delete_self(self) -> None:
        self.page.delete_leaf_node(self)

    def set_delete_visible(self, visible: bool) -> None:
        self.delete_button.setVisible(visible)

    def set_link_mode_highlight(self, active: bool) -> None:
        """
        Highlight this node as a valid link target while in link mode.
        """
        if active:
            self.setStyleSheet("NodeWidget { background-color: #fffbcc; border: 2px solid #f0a000; }")
        else:
            self.setStyleSheet("")

    def _set_win(self) -> None:
        is_win = self.win_button.isChecked()
        self.win_button.setStyleSheet("background-color: #f0c040;" if is_win else "")

    def set_lose_visible(self, visible: bool) -> None:
        self.lose_button.setVisible(visible)
    
    def _set_loss(self) -> None:
        is_loss = self.lose_button.isChecked()
        self.lose_button.setStyleSheet("background-color: #fc3d3d;" if is_loss else "")