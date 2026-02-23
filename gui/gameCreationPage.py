import os.path
import sys
from typing import Optional

from PySide6 import QtWidgets, QtCore, QtGui

from gesture import EnumGesture
from graph import Node
from storageManager import GameLoader, GameSaver
from . import config
from .zoomableGraphicsView import ZoomableGraphicsView
from .nodeWidget import NodeWidget
from .optionSide import OptionSide


class GameCreationPage(QtWidgets.QWidget):
    """
    Main page for creating a no-ui game.
    """
    def __init__(self, game_folder: Optional[str] = None) -> None:
        super().__init__()

        self.game_title: str= ""

        self.game_loader: GameLoader = GameLoader()
        self.game_saver: GameSaver = GameSaver()

        # list of all nodes in the game
        self.nodes: list[NodeWidget] = []
        self.root_node: Optional[NodeWidget] = None
        # node -> (x,y)
        self.node_coords_dict: dict[NodeWidget, tuple[float, float]] = {}
        # parent_node -> {"left": child_node, "right": child_node}
        self.node_children: dict[NodeWidget, dict[str, NodeWidget]] = {}
        # node -> (depth, position)
        self.node_depth_pos: dict[NodeWidget, tuple[int, int]] = {}

        self._setup_window_layout("No-UI-Game Creator")
        self._title_entry()

        self._setup_canvas()

        if game_folder:
            self._load_game(game_folder)
        else:
            self._add_root_node()
    
    def _setup_window_layout(self, window_title: str) -> None:
        """
        Set the window title, size and layout.
        """
        self.setWindowTitle(window_title)
        self.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
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

        # store proxy for deletion later
        node._proxy = proxy  

        self.node_coords_dict[node] = (x,y)
        self.nodes.append(node)

        if self.root_node is None:
            self.root_node = node
        
        return node

    def _add_root_node(self) -> None:
        x, y = self._get_node_position(0, 0)
        node = self._create_node_at(x, y)
        self.node_depth_pos[node] = (0, 0)
    
    def _create_child_node(self, parent: NodeWidget, side: OptionSide) -> None:
        parent_coords = self.node_coords_dict.get(parent)
        if not parent_coords:
            return
        
        parent_depth, parent_pos = self.node_depth_pos.get(parent, (0, 0))
        child_depth = parent_depth + 1
        child_pos = parent_pos * 2 if side == OptionSide.LEFT else parent_pos * 2 + 1
        
        new_x, new_y = self._get_node_position(child_depth, child_pos)
        child = self._create_node_at(new_x, new_y)
        self.node_depth_pos[child] = (child_depth, child_pos)

        # record connection for saving graph
        if parent not in self.node_children:
            self.node_children[parent] = {}
        self.node_children[parent][side] = child

        self._update_delete_buttons()
    
    def _update_delete_buttons(self) -> None:
        """
        Update the delete buttons on nodes as tree grows.
        So that only leaf nodes can be deleted (not root).
        """
        for node in self.nodes:
            is_leaf: bool = len(self.node_children.get(node, {})) == 0
            is_root: bool = (node == self.root_node)
            node.set_delete_visible(is_leaf and not is_root)

    def delete_leaf_node(self, node: NodeWidget) -> None:
        """
        Delete leaf node.
        """
        # find parent and remove from the children
        for parent, children in self.node_children.items():
            for side, child in list(children.items()):
                if child == node:
                    del self.node_children[parent][side]
                    break
        
        # remove from all node tracking
        self.nodes.remove(node)
        self.node_coords_dict.pop(node, None)
        self.node_children.pop(node, None)

        # remove from proxy (the canvas)
        proxy = getattr(node, "_proxy", None)
        if proxy:
            self.scene.removeItem(proxy)
            proxy.deleteLater()
        node.deleteLater()

        self._update_delete_buttons()

    def _build_game_graph(self) -> Optional[Node]:
        """
        Build a backend graph tree from the UI nodes.
        """
        if not self.root_node:
            return None
        
        widget_node: dict[NodeWidget, Node] = {}
        # 1. create backend nodes
        for node_widget in self.nodes:
            main_text = node_widget.text.toPlainText().strip()
            left_text = node_widget.left_option.text().strip()
            right_text = node_widget.right_option.text().strip()
            
            game_graph_node = Node(main_text, left_text, right_text)
            game_graph_node.is_win = node_widget.win_button.isChecked()
            widget_node[node_widget] = game_graph_node


        # 2. loop through the node widgets 
        # for each node create connections to their children as Node objects
        for parent_widget, children in self.node_children.items():
            parent_node = widget_node[parent_widget]

            left_child = children.get(OptionSide.LEFT)
            right_child = children.get(OptionSide.RIGHT)

            if left_child:
                parent_node.addNode(EnumGesture.ILoveYou_Left, widget_node[left_child])
            if right_child:
                parent_node.addNode(EnumGesture.ILoveYou_Right, widget_node[right_child])
        return widget_node[self.root_node]
    
    def save_title(self) -> None:
        self.game_title = self.title_entry.text().strip()
        print(f"Title: {self.game_title}")

    def save_game(self) -> None:
        root = self._build_game_graph()
        if not root:
            return

        title = self.title_entry.text().strip() or "untitled"
        game_path = os.path.join(os.path.dirname(__file__), os.pardir, "saved_games")

        progress = self._show_saving_popup()

        self.game_saver.save_game(game_path, title, root)
        progress.close()
        QtWidgets.QMessageBox.information(self, "Success", f"Game saved to {game_path}/{title}")
    
    def _show_saving_popup(self):
        progress = QtWidgets.QProgressDialog("Saving game...", None, 0, 0, self)
        progress.setWindowTitle("Saving")
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setCancelButton(None)
        progress.show()
        QtWidgets.QApplication.processEvents()

        return progress

    def _load_game(self, game_folder: str) -> None:
        """
        Load an existing game onto the creation page and populate the graph nodes.
        """
        print(f"load game from {game_folder}")
        try:
            root_node = self.game_loader.load_graph(game_folder)
            
            game_name = os.path.basename(game_folder)
            self.game_title = game_name
            self.title_entry.setText(game_name)

            self._populate_graph(root_node)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load game: {e}")

    def _get_node_position(self, depth: int, position: int, total_width: int = config.GAME_TREE_WIDTH) -> tuple[float, float]:
        """
        Total window width is divided into 2^depth equal slots(/sections) at each depth level,
        and the node is centered in its slot.
        So nodes do not overlap as tree grows.
        """
        slots = 2 ** depth
        slot_width = total_width / slots
        x = slot_width * position + slot_width / 2
        y = depth * config.CHILD_NODE_Y_OFFSET + config.TREE_Y_OFFSET
        return x, y

    def _populate_graph(self, root_node: Node):
        """
        Recursively build UI widgets from loaded Node graph.
        """
        queue = [(root_node, 0, 0, None, None)]  # (node, depth, pos, parent_widget, side)
        self.root_node = None

        while queue:
            node, depth, pos, parent_widget, side = queue.pop(0)

            x, y = self._get_node_position(depth, pos)
            node_widget: NodeWidget = self._create_node_at(x, y)
            self._populate_widget_from_node(node_widget, node)
            self.node_depth_pos[node_widget] = (depth, pos)

            if not self.root_node:
                self.root_node = node_widget

            if parent_widget is not None and side is not None:
                if parent_widget not in self.node_children:
                    self.node_children[parent_widget] = {}
                self.node_children[parent_widget][side] = node_widget

            for gesture, child_node in node.adjacencyList.items():
                if gesture == EnumGesture.ILoveYou_Left:
                    queue.append((child_node, depth + 1, pos * 2, node_widget, OptionSide.LEFT))
                elif gesture == EnumGesture.ILoveYou_Right:
                    queue.append((child_node, depth + 1, pos * 2 + 1, node_widget, OptionSide.RIGHT))

        self._update_delete_buttons()

    def _populate_widget_from_node(self, node_widget: NodeWidget, node: Node) -> None:
        """
        Fill in the main text and the options of a node widget from the node object
        """
        node_widget.text.setPlainText(node.getText())
        node_widget.left_option.setText(node.left_option)
        node_widget.right_option.setText(node.right_option)
        node_widget.win_button.setChecked(node.is_win)
        node_widget.win_button.setStyleSheet("background-color: #f0c040;" if node.is_win else "")
        

def run():
    app = QtWidgets.QApplication([])

    widget = GameCreationPage()
    widget.setBackgroundRole(QtGui.QPalette.Base)
    widget.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    run()