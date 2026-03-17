import os.path
import sys
from typing import Any, Optional

from PySide6 import QtWidgets, QtCore, QtGui

from gesture import EnumGesture
from graph import Node
from graph.serial_graph import SerialGraph
from graph.serial_node import SerialNode
from storageManager import GameLoader, GameSaver
from . import config
from .zoomableGraphicsView import ZoomableGraphicsView
from .nodeWidget import NodeWidget
from .optionSide import OptionSide


# Colours for the connector lines
LINE_COLOR_LEFT  = QtGui.QColor("#2a7ae2") # left opt = blue
LINE_COLOR_RIGHT = QtGui.QColor("#e22d2a") # right opt = red


class _GameGenerationWorker(QtCore.QObject):
    """Background worker that keeps heavy LLM generation off the GUI thread."""
    progress = QtCore.Signal(dict)
    finished = QtCore.Signal(object)
    failed = QtCore.Signal(str)
    done = QtCore.Signal()

    def __init__(self, prompt: str) -> None:
        super().__init__()
        self.prompt = prompt

    @QtCore.Slot()
    def run(self) -> None:
        from game_generation_local_llm.game_generator import GameGenerator

        try:
            generator = GameGenerator()
            serial_graph = generator.generate_game(self.prompt, progress_cb=self._emit_progress)
            self.finished.emit(serial_graph)
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            self.done.emit()

    def _emit_progress(self, payload: dict[str, Any]) -> None:
        self.progress.emit(payload)


class GameCreationPage(QtWidgets.QWidget):
    """
    Main page for creating a no-ui game.

    Nodes are arranged in a tree by default (using the + buttons).

    The 🔗 buttons enter link mode: click any existing node to wire
    that option to it instead of creating a new child. A coloured line
    is drawn between connected nodes so the graph structure is visible.
    """
    def __init__(self, game_path: Optional[str] = None) -> None:
        super().__init__()

        self.game_title: str = ""
        self.game_loader: GameLoader = GameLoader()
        self.game_saver: GameSaver = GameSaver()

        # Ordered list of all node widgets
        self.nodes: list[NodeWidget] = []
        self.root_node: Optional[NodeWidget] = None
        # node -> (x, y) scene position
        self.node_coords_dict: dict[NodeWidget, tuple[float, float]] = {}
        # parent -> {OptionSide: child}   (covers both tree-created and linked children)
        self.node_children: dict[NodeWidget, dict[OptionSide, NodeWidget]] = {}
        # node -> (depth, position)  — used for tree layout only
        self.node_depth_pos: dict[NodeWidget, tuple[int, int]] = {}

        # Drawn connector lines: (parent, side) -> QGraphicsLineItem
        self._lines: dict[tuple[NodeWidget, OptionSide], QtWidgets.QGraphicsLineItem] = {}

        # Link-mode state: None when inactive
        self._link_source: Optional[tuple[NodeWidget, OptionSide]] = None

        # AI generation state
        self._generation_thread: Optional[QtCore.QThread] = None
        self._generation_worker: Optional[_GameGenerationWorker] = None
        self._stream_blueprint: Optional[dict[str, Any]] = None
        self._stream_nodes: dict[int, dict[str, Any]] = {}

        self._setup_window_layout("No-UI-Game Creator")
        self._title_entry()

        self._setup_canvas()

        if game_path:
            self._load_game(game_path)
        else:
            self._add_root_node()
    
    def _setup_window_layout(self, window_title: str) -> None:
        """
        Set the window title, size and layout.
        Top level is a horizontal split: left side is the canvas, right side is AI helper.
        """
        self.setWindowTitle(window_title)
        self.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        h_layout = QtWidgets.QHBoxLayout(self)

        canvas = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(canvas)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        h_layout.addWidget(canvas, stretch=1)

        h_layout.addWidget(self._build_ai_panel())

    def _title_entry(self) -> None:
        # create title entry bar and save button
        self.title_entry = QtWidgets.QLineEdit()
        self.title_entry.setPlaceholderText("Enter game title...")

        #save widgets
        self.layout.addWidget(self.title_entry)

    def _setup_canvas(self) -> None:
        self.scene = QtWidgets.QGraphicsScene(self)
        self.view = ZoomableGraphicsView(self.scene)
        self.view.setMinimumHeight(config.CANVAS_HEIGHT)

        # intercept mouse-press on the scene to handle link-mode clicks
        self.scene.installEventFilter(self)

        self.layout.addWidget(self.view)

        self.save_game_button = QtWidgets.QPushButton("Save Game")
        self.save_game_button.clicked.connect(self.save_game)
        self.layout.addWidget(self.save_game_button)

    def _build_ai_panel(self) -> QtWidgets.QWidget:
        """
        AI helper side panel — white background, grey border, title and hint
        pinned to the top, prompt box and button pinned to the bottom.
        """
        panel = QtWidgets.QWidget()
        panel.setFixedWidth(config.AI_PANEL_WIDTH)
        panel.setStyleSheet(
            "QWidget#aiPanel {"
            "  border-left: 1px;"
            "}"
        )
        panel.setObjectName("aiPanel")

        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        # top: title, hint
        header = QtWidgets.QLabel("AI Game Generator")
        header.setStyleSheet("font-size: 22px; font-weight: bold; background: transparent;")
        header.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        layout.addWidget(header)

        hint = QtWidgets.QLabel("Describe your game and click Generate. The current canvas will be replaced.")
        hint.setWordWrap(True)
        hint.setStyleSheet("font-size: 16px; background: transparent;")
        hint.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        layout.addWidget(hint)

        # middle whitespace
        layout.addStretch(1)

        # bottom: label, prompt box, button
        prompt_label = QtWidgets.QLabel("Describe your game:")
        prompt_label.setStyleSheet("font-size: 16px; background: transparent;")
        layout.addWidget(prompt_label)

        self._ai_prompt = QtWidgets.QTextEdit()
        self._ai_prompt.setPlaceholderText("e.g. A horror story set in an abandoned hospital...")
        self._ai_prompt.setFixedHeight(80)
        self._ai_prompt.setStyleSheet(
            "QTextEdit {"
            "  border: 1px solid #c0c0c0;"
            "  border-radius: 4px;"
            "  padding: 4px;"
            "  font-size: 11px;"
            "}"
        )
        layout.addWidget(self._ai_prompt)

        self._ai_generate_btn = QtWidgets.QPushButton("Generate Game")
        self._ai_generate_btn.setStyleSheet(
            "QPushButton {"
            "  border: 1px solid #c0c0c0;"
            "  border-radius: 4px;"
            "  padding: 6px;"
            "  font-size: 12px;"
            "}"
            "QPushButton:disabled { color: #aaa; }"
        )
        self._ai_generate_btn.clicked.connect(self._on_AIgenerate_clicked)
        layout.addWidget(self._ai_generate_btn)

        self._ai_progress = QtWidgets.QProgressBar()
        self._ai_progress.setVisible(False)
        self._ai_progress.setRange(0, 1)
        self._ai_progress.setValue(0)
        layout.addWidget(self._ai_progress)

        self._ai_status = QtWidgets.QLabel("")
        self._ai_status.setWordWrap(True)
        self._ai_status.setStyleSheet("font-size: 11px; background: transparent;")
        layout.addWidget(self._ai_status)

        return panel

    def _on_AIgenerate_clicked(self) -> None:
        """
        Start generation on a worker thread and stream progress into the UI.
        """
        if self._generation_thread is not None and self._generation_thread.isRunning():
            self._ai_status.setText("Generation is already in progress.")
            return

        prompt = self._ai_prompt.toPlainText().strip()
        if not prompt:
            self._ai_status.setText("Please enter a prompt first.")
            return

        self._stream_blueprint = None
        self._stream_nodes.clear()
        self._set_generation_running(True)
        self._ai_status.setText("Starting game generation...")

        thread = QtCore.QThread(self)
        worker = _GameGenerationWorker(prompt)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.progress.connect(self._on_generation_progress)
        worker.finished.connect(self._on_generation_finished)
        worker.failed.connect(self._on_generation_failed)
        worker.done.connect(self._on_generation_done)
        worker.done.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(self._on_generation_thread_finished)
        thread.finished.connect(thread.deleteLater)

        self._generation_thread = thread
        self._generation_worker = worker
        thread.start()

    @QtCore.Slot(dict)
    def _on_generation_progress(self, payload: dict[str, Any]) -> None:
        stage = payload.get("stage", "")
        message = payload.get("message", "")

        if stage == "blueprint_ready":
            self._stream_blueprint = payload.get("blueprint")
            total = int(payload.get("nodes_total", 0) or 0)
            self._ai_progress.setRange(0, max(1, total))
            self._ai_progress.setValue(0)
            self._render_streaming_preview()

        if stage == "story_started":
            total = int(payload.get("nodes_total", 0) or 0)
            self._ai_progress.setRange(0, max(1, total))

        if stage in {"node_started", "node_ready"}:
            done = int(payload.get("nodes_done", 0) or 0)
            total = int(payload.get("nodes_total", 0) or 0)
            if total > 0:
                self._ai_progress.setRange(0, total)
                self._ai_progress.setValue(min(done, total))

        if stage == "node_ready":
            node_id = payload.get("node_id")
            node_payload = payload.get("node")
            if node_id is not None and isinstance(node_payload, dict):
                self._stream_nodes[int(node_id)] = node_payload
                self._render_streaming_preview()

        if message:
            self._ai_status.setText(message)

    @QtCore.Slot(object)
    def _on_generation_finished(self, serial_graph: SerialGraph) -> None:
        self._clear_canvas()
        self._populate_graph_from_serial(serial_graph)
        self._ai_status.setText("Generation complete.")
        if self._ai_progress.maximum() > 0:
            self._ai_progress.setValue(self._ai_progress.maximum())

    @QtCore.Slot(str)
    def _on_generation_failed(self, error_message: str) -> None:
        self._ai_status.setText(f"Error: {error_message}")

    @QtCore.Slot()
    def _on_generation_done(self) -> None:
        self._set_generation_running(False)

    @QtCore.Slot()
    def _on_generation_thread_finished(self) -> None:
        self._generation_thread = None
        self._generation_worker = None

    def _set_generation_running(self, running: bool) -> None:
        self._ai_generate_btn.setEnabled(not running)
        self._ai_prompt.setEnabled(not running)
        self._ai_progress.setVisible(running)
        if not running:
            self._ai_progress.setRange(0, 1)
            self._ai_progress.setValue(0)

    def _clear_canvas(self) -> None:
        """Remove all nodes, lines, and graph tracking state from the canvas."""
        self.scene.clear()
        self.nodes.clear()
        self.node_coords_dict.clear()
        self.node_children.clear()
        self.node_depth_pos.clear()
        self._lines.clear()
        self.root_node = None

    def _render_streaming_preview(self) -> None:
        """Render the current blueprint with generated/placeholder node text while generation runs."""
        blueprint = self._stream_blueprint
        if not blueprint:
            return

        adjacency = blueprint.get("adjacency")
        if not isinstance(adjacency, dict) or not adjacency:
            return

        win_nodes = {int(node_id) for node_id in blueprint.get("win_nodes", [])}
        lose_nodes = {int(node_id) for node_id in blueprint.get("lose_nodes", [])}
        serial_nodes: dict[int, SerialNode] = {}

        for raw_node_id, raw_adjacency in adjacency.items():
            node_id = int(raw_node_id)
            is_win = node_id in win_nodes
            is_losing = node_id in lose_nodes
            payload = self._stream_nodes.get(node_id)

            if payload is None:
                payload = {
                    "id": node_id,
                    "text": f"[Generating node {node_id}...]",
                    "left_option": "" if (is_win or is_losing) else "Working...",
                    "right_option": "" if (is_win or is_losing) else "Working...",
                    "adjacency_list": raw_adjacency,
                    "is_win": is_win,
                    "is_losing": is_losing,
                }
            else:
                payload = dict(payload)
                payload["id"] = node_id
                payload["adjacency_list"] = raw_adjacency
                payload["is_win"] = is_win
                payload["is_losing"] = is_losing

            serial_nodes[node_id] = SerialNode.model_validate(payload)

        self._clear_canvas()
        self._populate_graph_from_serial(SerialGraph(nodes=serial_nodes))

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key_Escape:
            self._cancel_link_mode()
        super().keyPressEvent(event)

    def eventFilter(self, watched, event) -> bool:
        """
        When in link mode, a mouse-press on the scene checks whether the user
        clicked on a node proxy and completes (or cancels) the link.
        """
        if (self._link_source is not None
                and watched is self.scene
                and event.type() == QtCore.QEvent.GraphicsSceneMousePress):

            # Find which proxy (if any) was clicked
            items = self.scene.items(event.scenePos())
            clicked_node = self._proxy_to_node(items)

            if clicked_node is not None:
                source_node, side = self._link_source
                if clicked_node is not source_node:          # can't link to yourself
                    self._complete_link(source_node, side, clicked_node)
                    return True                               # consume the event
            # Clicked on empty space → cancel
            self._cancel_link_mode()
            return True

        return super().eventFilter(watched, event)

    def _proxy_to_node(self, items) -> Optional[NodeWidget]:
        """
        Return the NodeWidget for the topmost proxy in the item list, or None.
        """
        for item in items:
            if isinstance(item, QtWidgets.QGraphicsProxyWidget):
                widget = item.widget()
                if isinstance(widget, NodeWidget):
                    return widget
                # click landed on a child widget inside the proxy
                if widget is not None:
                    parent = widget.parent()
                    while parent is not None:
                        if isinstance(parent, NodeWidget):
                            return parent
                        parent = parent.parent()
        return None

    def enter_link_mode(self, source: NodeWidget, side: OptionSide) -> None:
        """
        Activate link mode: highlight all other nodes as targets and wait
        for the user to click one (or press Escape to cancel).
        """
        # Cancel any active link mode first
        self._cancel_link_mode()
        self._link_source = (source, side)

        for node in self.nodes:
            if node is not source:
                node.set_link_mode_highlight(True)

        # Visual feedback on the source node's link button
        btn = source.left_link if side == OptionSide.LEFT else source.right_link
        btn.setStyleSheet("background-color: #f0a000; color: white;")

        self.view.setFocus()   # so Escape is captured

    def _cancel_link_mode(self) -> None:
        if self._link_source is None:
            return
        source, side = self._link_source
        btn = source.left_link if side == OptionSide.LEFT else source.right_link
        btn.setStyleSheet("")
        for node in self.nodes:
            node.set_link_mode_highlight(False)
        self._link_source = None

    def _complete_link(self, source: NodeWidget, side: OptionSide, target: NodeWidget) -> None:
        """
        Wire source → target on the given side, replacing any previous connection,
        draw a line between them, and exit link mode.
        """
        # Remove any existing connection on this side (line + child record)
        self._remove_connection(source, side)

        # Record the new connection
        if source not in self.node_children:
            self.node_children[source] = {}
        self.node_children[source][side] = target

        # Draw the connector line
        self._draw_line(source, side, target)

        self._cancel_link_mode()
        self._update_buttons()


    def _create_node_at(self, x: float, y: float) -> NodeWidget:
        node = NodeWidget(self)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(node)
        proxy.setPos(x, y)
        self.scene.addItem(proxy)

        node._proxy = proxy
        self.node_coords_dict[node] = (x, y)
        self.nodes.append(node)

        if self.root_node is None:
            self.root_node = node

        return node

    def _add_root_node(self) -> None:
        x, y = self._get_node_position(0, 0)
        node = self._create_node_at(x, y)
        self.node_depth_pos[node] = (0, 0)
    
    def _create_child_node(self, parent: NodeWidget, side: OptionSide) -> None:
        """
        Create a brand-new child node in the tree, connect it, then
        re-layout the whole tree so nothing overlaps.
        """
        if not self.node_coords_dict.get(parent):
            return

        self._remove_connection(parent, side)

        child = self._create_node_at(0, 0)

        if parent not in self.node_children:
            self.node_children[parent] = {}
        self.node_children[parent][side] = child

        self._relayout_tree()
        self._update_buttons()

    def _relayout_tree(self) -> None:
        """
        Recompute positions for all nodes using the subtree-width algorithm
        and move their proxies. Redraws all lines.
        """
        if self.root_node is None:
            return

        H_GAP = 60
        slot = max(
            config.NODE_WIDTH + H_GAP,
            config.GAME_TREE_WIDTH / max(1, self._widget_subtree_width(self.root_node, set()))
        )

        positions: dict[NodeWidget, tuple[float, float]] = {}
        self._assign_widget_x(self.root_node, 0.0, slot, 0, set(), positions)

        for nw, (x, y) in positions.items():
            self.node_coords_dict[nw] = (x, y)
            nw._proxy.setPos(x, y)

        for key in list(self._lines):
            self.scene.removeItem(self._lines.pop(key))
        for par, children in self.node_children.items():
            for s, child in children.items():
                self._draw_line(par, s, child)

    def _widget_subtree_width(self, node: NodeWidget, visited: set) -> int:
        """
        Number of leaves in this widget subtree (minimum 1).
        """
        if id(node) in visited:
            return 1
        visited.add(id(node))
        children = list(self.node_children.get(node, {}).values())
        if not children:
            return 1
        return sum(self._widget_subtree_width(c, visited) for c in children)

    def _assign_widget_x(self, node: NodeWidget, x_start: float, slot: float,
                         depth: int, visited: set,
                         positions: dict) -> None:
        """
        Recursively assign x positions based on subtree leaf counts.
        """
        if id(node) in visited:
            return
        visited.add(id(node))

        children = self.node_children.get(node, {})
        ordered = [(s, c) for s, c in [
            (OptionSide.LEFT,  children.get(OptionSide.LEFT)),
            (OptionSide.RIGHT, children.get(OptionSide.RIGHT)),
        ] if c is not None]

        if not ordered:
            x = x_start + slot / 2
        else:
            widths = [self._widget_subtree_width(c, set()) for _, c in ordered]
            x = x_start + sum(widths) * slot / 2
            cursor = x_start
            for (_, child), w in zip(ordered, widths):
                self._assign_widget_x(child, cursor, slot, depth + 1, visited, positions)
                cursor += w * slot

        y = depth * config.CHILD_NODE_Y_OFFSET + config.TREE_Y_OFFSET
        positions[node] = (x, y)

    def _update_buttons(self) -> None:
        """
        Update the buttons on nodes as tree grows.
        So that only leaf nodes can be deleted (not root).
        And only leaf nodes can be set as losing nodes.
        """
        for node in self.nodes:
            is_leaf: bool = len(self.node_children.get(node, {})) == 0
            is_root: bool = (node == self.root_node)
            node.set_delete_visible(is_leaf and not is_root)
            node.set_lose_visible(is_leaf and not is_root)

    def delete_leaf_node(self, node: NodeWidget) -> None:
        """
        Delete leaf node.
        """
        # find parent and remove from the children
        for parent, children in self.node_children.items():
            for side, child in list(children.items()):
                if child == node:
                    self._remove_connection(parent, side)
                    break

        self.nodes.remove(node)
        self.node_coords_dict.pop(node, None)
        self.node_children.pop(node, None)
        self.node_depth_pos.pop(node, None)

        proxy = getattr(node, "_proxy", None)
        if proxy:
            self.scene.removeItem(proxy)
            proxy.deleteLater()
        node.deleteLater()

        self._update_buttons()

    def _node_centre_bottom(self, node: NodeWidget) -> QtCore.QPointF:
        """Scene coordinates of the bottom-centre of a node's proxy."""
        x, y = self.node_coords_dict[node]
        w = node.width()
        h = node.height()
        return QtCore.QPointF(x + w / 2, y + h)

    def _node_centre_top(self, node: NodeWidget) -> QtCore.QPointF:
        """Scene coordinates of the top-centre of a node's proxy."""
        x, y = self.node_coords_dict[node]
        w = node.width()
        return QtCore.QPointF(x + w / 2, y)

    def _draw_line(self, parent: NodeWidget, side: OptionSide, child: NodeWidget) -> None:
        """Draw (or redraw) the connector line for this parent-side pair."""
        key = (parent, side)
        # Remove old line if present
        if key in self._lines:
            self.scene.removeItem(self._lines[key])

        p1 = self._node_centre_bottom(parent)
        p2 = self._node_centre_top(child)

        line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(p1, p2))
        color = LINE_COLOR_LEFT if side == OptionSide.LEFT else LINE_COLOR_RIGHT
        pen = QtGui.QPen(color, config.LINE_WIDTH)
        pen.setStyle(QtCore.Qt.SolidLine)
        line.setPen(pen)
        line.setZValue(-1)   # draw behind node widgets

        self.scene.addItem(line)
        self._lines[key] = line

    def _remove_connection(self, parent: NodeWidget, side: OptionSide) -> None:
        """Remove the visual line and child record for a given parent-side."""
        key = (parent, side)
        if key in self._lines:
            self.scene.removeItem(self._lines.pop(key))
        children = self.node_children.get(parent, {})
        children.pop(side, None)

    def _build_game_graph(self) -> Optional[Node]:
        """
        Build a backend graph tree from the UI nodes.
        """
        if not self.root_node:
            return None

        widget_node: dict[NodeWidget, Node] = {}
        for nw in self.nodes:
            n = Node(
                nw.text.toPlainText().strip(),
                nw.left_option.text().strip(),
                nw.right_option.text().strip(),
            )
            n.is_win = nw.win_button.isChecked()
            n.is_losing = nw.lose_button.isChecked()
            widget_node[nw] = n

        for parent_widget, children in self.node_children.items():
            parent_node = widget_node[parent_widget]
            left_child  = children.get(OptionSide.LEFT)
            right_child = children.get(OptionSide.RIGHT)
            if left_child:
                parent_node.addNode(EnumGesture.ILoveYou_Left,  widget_node[left_child])
            if right_child:
                parent_node.addNode(EnumGesture.ILoveYou_Right, widget_node[right_child])

        return widget_node[self.root_node]

    def save_game(self) -> None:
        root = self._build_game_graph()
        if not root:
            return

        title = self.title_entry.text().strip() or "untitled"
        game_path = os.path.join(os.path.dirname(__file__), os.pardir, "saved_games")

        progress = self._show_saving_popup()
        try:
            self.game_saver.save_game(game_path, title, root)
        except Exception as e:
            progress.close()
            QtWidgets.QMessageBox.critical(self, "Save failed", str(e))
            return
        progress.close()
        QtWidgets.QMessageBox.information(self, "Success", f"Game saved to {game_path}/{title}")

    def _show_saving_popup(self) -> QtWidgets.QProgressDialog:
        progress = QtWidgets.QProgressDialog("Saving game...", None, 0, 0, self)
        progress.setWindowTitle("Saving")
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setCancelButton(None)
        progress.show()
        QtWidgets.QApplication.processEvents()

        return progress

    def _load_game(self, game_path: str) -> None:
        """
        Load an existing game onto the creation page and populate the graph nodes.
        """
        try:
            root_node, game_folder, _ = self.game_loader.load_graph(game_path)
            game_name = os.path.basename(game_folder)
            self.game_title = game_name
            self.title_entry.setText(game_name)

            self._populate_graph(root_node)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load game: {e}")

    def _get_node_position(self, depth: int, position: int,
                           total_width: int = config.GAME_TREE_WIDTH) -> tuple[float, float]:
        slots = 2 ** depth
        slot_width = total_width / slots
        x = slot_width * position + slot_width / 2
        y = depth * config.CHILD_NODE_Y_OFFSET + config.TREE_Y_OFFSET
        return x, y

    def _populate_graph(self, root_node: Node) -> None:
        """
        BFS over the loaded backend graph, creating NodeWidgets.

        At shallow depths nodes are placed using the standard binary tree slot
        formula. Once slot_width < NODE_WIDTH + gap, nodes at that depth are
        assigned x positions using a sequential counter so they never overlap,
        regardless of how many nodes share a depth level.
        """
        H_GAP = 60
        MIN_SLOT = config.NODE_WIDTH + H_GAP

        backend_to_widget: dict[int, NodeWidget] = {}
        depth_counter: dict[int, int] = {}  # tracks how many nodes placed per depth

        queue: list[tuple[Node, int, int, Optional[NodeWidget], Optional[OptionSide]]] = [
            (root_node, 0, 0, None, None)
        ]
        self.root_node = None
        visited: set[int] = set()

        while queue:
            node, depth, pos, parent_widget, side = queue.pop(0)
            node_id = node.get_id()

            if node_id in visited:
                if parent_widget is not None and side is not None:
                    target_widget = backend_to_widget[node_id]
                    if parent_widget not in self.node_children:
                        self.node_children[parent_widget] = {}
                    self.node_children[parent_widget][side] = target_widget
                    self._draw_line(parent_widget, side, target_widget)
                continue

            visited.add(node_id)

            slot_width = config.GAME_TREE_WIDTH / (2 ** depth)
            if slot_width >= MIN_SLOT:
                x = slot_width * pos + slot_width / 2
            else:
                idx = depth_counter.get(depth, 0)
                depth_counter[depth] = idx + 1
                x = idx * MIN_SLOT + MIN_SLOT / 2

            y = depth * config.CHILD_NODE_Y_OFFSET + config.TREE_Y_OFFSET

            nw = self._create_node_at(x, y)
            self._populate_widget_from_node(nw, node)
            self.node_depth_pos[nw] = (depth, pos)
            backend_to_widget[node_id] = nw

            if self.root_node is None:
                self.root_node = nw

            if parent_widget is not None and side is not None:
                if parent_widget not in self.node_children:
                    self.node_children[parent_widget] = {}
                self.node_children[parent_widget][side] = nw
                self._draw_line(parent_widget, side, nw)

            for gesture, child_node in node.adjacencyList.items():
                if gesture == EnumGesture.ILoveYou_Left:
                    queue.append((child_node, depth + 1, pos * 2,     nw, OptionSide.LEFT))
                elif gesture == EnumGesture.ILoveYou_Right:
                    queue.append((child_node, depth + 1, pos * 2 + 1, nw, OptionSide.RIGHT))

        self._update_buttons()

    def _populate_graph_from_serial(self, serial: SerialGraph) -> None:
        """Rebuild widget graph from a serialized graph payload."""
        root, nodes = self.game_loader._load_nodes(serial)
        self.game_loader._establish_connections(serial, nodes)
        self._populate_graph(root)

    def _populate_widget_from_node(self, nw: NodeWidget, node: Node) -> None:
        nw.text.setPlainText(node.getText())
        nw.left_option.setText(node.left_option)
        nw.right_option.setText(node.right_option)
        nw.win_button.setChecked(node.is_win)
        nw.win_button.setStyleSheet("background-color: #f0c040;" if node.is_win else "")
        nw.lose_button.setChecked(node.is_losing)
        nw.lose_button.setStyleSheet("background-color: #fc3d3d;" if node.is_losing else "")


def run():
    app = QtWidgets.QApplication([])

    widget = GameCreationPage()
    widget.setBackgroundRole(QtGui.QPalette.Base)
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run()

