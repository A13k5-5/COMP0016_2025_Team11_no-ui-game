import sys
from enum import Enum
from typing import Dict, List, Optional, Tuple

from PySide6 import QtWidgets, QtCore, QtGui 
from graph import Node
from myTypes import Gesture
from storageManager import StorageManager

LEFT_GESTURE: Gesture = ("ILoveYou", "Left")
RIGHT_GESTURE: Gesture = ("ILoveYou", "Right")

class OptionSide(str, Enum):
    LEFT = "left"
    RIGHT = "right"

class ZoomableGraphicsView(QtWidgets.QGraphicsView):
    """
    Allows zoom in/out and drag functionality by using a 
    mouse wheel or trackpad - Ctrl+scroll.
    """
    def __init__(self, scene: QtWidgets.QWidget, parent: Optional[QtWidgets.QWidget] = None) -> None:
        print(parent)
        super().__init__(scene, parent)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        # current zoom level
        self._zoom: float = 1.0 
    
    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
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
    def __init__(self, page: "GameCreationPage") -> None:
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
        self.page._create_child_node(self, OptionSide.LEFT)


class GameCreationPage(QtWidgets.QWidget):
    """
    Main page for creating a no-ui game.
    """
    def __init__(self) -> None:
        super().__init__()

        self.game_title: str= ""
        # list of all nodes in the game
        self.nodes: List[NodeWidget] = []
        self.root_node: Optional[NodeWidget] = None
        # node -> (x,y)
        self.node_coords_dict: Dict[NodeWidget, Tuple[float, float]] = {}
        # parent_node -> {"left": child_node, "right": child_node}
        self.node_children: Dict[NodeWidget, Dict[str, NodeWidget]] = {}

        self._setup_window_layout("No-UI-Game Creator")
        self._title_entry()

        self._setup_canvas()
        self._add_root_node()
    
    def _setup_window_layout(self, window_title: str) -> None:
        """
        Set the window title, size and layout.
        """
        self.setWindowTitle(window_title)
        self.resize(800, 600)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        
    def _title_entry(self) -> None:
        # create title entry bar and save button
        self.title_entry = QtWidgets.QLineEdit()
        self.title_entry.setPlaceholderText("Enter game title...")

        self.save_title_button = QtWidgets.QPushButton("Save Title")
        self.save_title_button.clicked.connect(self.save_title)

        #save widgets
        self.layout.addWidget(self.title_entry)
        self.layout.addWidget(self.save_title_button)

    def _setup_canvas(self) -> None:
        self.scene = QtWidgets.QGraphicsScene(self)
        self.view = ZoomableGraphicsView(self.scene)
        self.view.setMinimumHeight(400)
        self.layout.addWidget(self.view)

        self.save_game_button = QtWidgets.QPushButton("Save Game")
        self.save_game_button.clicked.connect(self.save_game)
        self.layout.addWidget(self.save_game_button)

    def _create_node_at(self, x: float, y: float) -> NodeWidget:
        """
        Create a NodeWidget, wrap it in a proxy, and add it to the scene.
        """
        node = NodeWidget(self)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(node)
        proxy.setPos(x,y)
        self.scene.addItem(proxy)

        self.node_coords_dict[node] = (x,y)
        self.nodes.append(node)

        if self.root_node is None:
            self.root_node = node
        
        return node

    def _add_root_node(self) -> None:
        self._create_node_at(50,50)
    
    def _create_child_node(self, parent: NodeWidget, side: OptionSide) -> None:
        parent_coords = self.node_coords_dict.get(parent)
        if not parent:
            return
        
        y_offset = 420
        if side == OptionSide.LEFT: 
            x_offset = -260
        else: #side == OptionSide.RIGHT
            x_offset = 260
        
        new_x = parent_coords[0] + x_offset
        new_y = parent_coords[1] + y_offset
        child = self._create_node_at(new_x, new_y)

        # record connection for saving graph
        if parent not in self.node_children:
            self.node_children[parent] = {}
        self.node_children[parent][side] = child

    def _build_game_graph(self) -> Optional[Node]:
        """
        Build a backend graph tree from the UI nodes.
        """
        if not self.root_node:
            return None
        
        widget_node: Dict[NodeWidget, Node] = {}
        # 1. create backend nodes
        for node_widget in self.nodes:
            text = node_widget.text.toPlainText().strip()
            game_graph_node = Node(text)
            widget_node[node_widget] = game_graph_node


        # 2. loop through the node widgets 
        # for each node create connections to their children as Node objects
        for parent_widget, children in self.node_children.items():
            parent_node = widget_node[parent_widget]

            left_child = children.get("left")
            right_child = children.get("right")

            if left_child:
                parent_node.addNode(LEFT_GESTURE, widget_node[left_child])
            if right_child:
                parent_node.addNode(RIGHT_GESTURE, widget_node[right_child])
        return widget_node[self.root_node]
    
    def save_title(self) -> None:
        self.game_title = self.title_entry.text().strip()
        print(f"Title: {self.game_title}")

    def save_game(self) -> None:
        root = self._build_game_graph()
        if not root:
            return

        # TODO - right now we save all games into graph.json for test purposes
        # later update so that the game is saved into the "title".json
        title = self.title_entry.text().strip() or "untitled"
        filename = "graph.json" #f"{title}.json"

        StorageManager().save_graph(root, filename=filename)
        print(f"Saved game to {filename}")


def run():
    app = QtWidgets.QApplication([])

    widget = GameCreationPage()
    widget.setBackgroundRole(QtGui.QPalette.Base)
    widget.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    run()