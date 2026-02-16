import sys
from typing import Optional

from PySide6 import QtWidgets, QtCore, QtGui 
from graph import Node
from storageManager import StorageManager
from . import config
from .zoomableGraphicsView import ZoomableGraphicsView
from .nodeWidget import NodeWidget
from .optionSide import OptionSide


class GameCreationPage(QtWidgets.QWidget):
    """
    Main page for creating a no-ui game.
    """
    def __init__(self) -> None:
        super().__init__()

        self.game_title: str= ""
        # list of all nodes in the game
        self.nodes: list[NodeWidget] = []
        self.root_node: Optional[NodeWidget] = None
        # node -> (x,y)
        self.node_coords_dict: dict[NodeWidget, tuple[float, float]] = {}
        # parent_node -> {"left": child_node, "right": child_node}
        self.node_children: dict[NodeWidget, dict[str, NodeWidget]] = {}

        self._setup_window_layout("No-UI-Game Creator")
        self._title_entry()

        self._setup_canvas()
        self._add_root_node()
    
    def _setup_window_layout(self, window_title: str) -> None:
        """
        Set the window title, size and layout.
        """
        self.setWindowTitle(window_title)
        self.resize(config.WINDOW_HEIGHT, config.WINDOW_WIDTH)
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
        self.view.setMinimumHeight(config.CANVAS_HEIGHT)
        self.layout.addWidget(self.view)

        self.save_game_button = QtWidgets.QPushButton("Save Game")
        self.save_game_button.clicked.connect(self.save_game)
        self.layout.addWidget(self.save_game_button)

    def _create_node_at(self, x: float, y: float) -> NodeWidget:
        """
        Create a NodeWidget, wrap it in a proxy, and add it to the scene.
        A proxy (QGraphicsProxyWidget) is a wrapper that allows a widget to be placed 
        inside a scene (QGraphicsScene).
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

    def _write_node_text(self, node_widget: NodeWidget) -> str:
        """
        Build spoken text including the two options, if present.
        """
        main_text = node_widget.text.toPlainText().strip()
        left_text = node_widget.left_option.text().strip()
        right_text = node_widget.right_option.text().strip()

        parts = [main_text]
        if left_text or right_text:
            parts.append("...You have two options.")
        if left_text:
            parts.append(f"Do {left_text} by raising your left hand.")
        if right_text:
            parts.append(f"Do {right_text} by raising your right hand.")
        return " ".join(parts).strip()

    def _build_game_graph(self) -> Optional[Node]:
        """
        Build a backend graph tree from the UI nodes.
        """
        if not self.root_node:
            return None
        
        widget_node: dict[NodeWidget, Node] = {}
        # 1. create backend nodes
        for node_widget in self.nodes:
            text = self._write_node_text(node_widget)
            game_graph_node = Node(text)
            widget_node[node_widget] = game_graph_node


        # 2. loop through the node widgets 
        # for each node create connections to their children as Node objects
        for parent_widget, children in self.node_children.items():
            parent_node = widget_node[parent_widget]

            left_child = children.get("left")
            right_child = children.get("right")

            if left_child:
                parent_node.addNode(config.LEFT_GESTURE, widget_node[left_child])
            if right_child:
                parent_node.addNode(config.RIGHT_GESTURE, widget_node[right_child])
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