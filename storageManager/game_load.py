import os
import shutil
import zipfile

from graph import Node
from graph.serial_graph import SerialGraph

TEMP_FOLDER = os.path.join(os.path.dirname(__file__), "temporary")


class GameLoader:
    """
    Class responsible for loading a game from a zipped game folder (containing the graph and corresponding audio files).
    """

    def _prepare_temp_folder(self, zip_path: str) -> str:
        """
        Wipes and recreates the 'temporary' folder, then extracts the given zip archive into it.
        :param zip_path: path to the zipped game folder
        :return: path to the extracted game folder inside 'temporary'
        """
        if os.path.exists(TEMP_FOLDER):
            shutil.rmtree(TEMP_FOLDER)
        os.makedirs(TEMP_FOLDER)

        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(TEMP_FOLDER)

        # If the zip contained a single top-level folder, return that folder
        extracted = os.listdir(TEMP_FOLDER)
        if len(extracted) == 1 and os.path.isdir(os.path.join(TEMP_FOLDER, extracted[0])):
            return os.path.join(TEMP_FOLDER, extracted[0])
        return TEMP_FOLDER

    def load_graph(self, game_zip: str) -> tuple[Node, str]:
        """
        Loads the graph from a zipped game folder and reconstructs the game structure.
        The zip should contain a graph.json file and corresponding audio files.
        :param game_zip: path to the zipped game folder
        :return:
        """
        game_folder = self._prepare_temp_folder(game_zip)

        graph_path = os.path.join(game_folder, "graph.json")
        with open(graph_path, 'r') as file:
            serial_graph: SerialGraph = SerialGraph.model_validate_json(file.read().strip())

        root, nodes = self._load_nodes(serial_graph)
        self._establish_connections(serial_graph, nodes)

        return root, game_folder


    def _load_nodes(self, serial_graph: SerialGraph) -> tuple[Node, dict[int, Node]]:
        """
        Load nodes without connections. Gives back the root node and a dictionary of all nodes.
        :param serial_graph:
        :return:
        """
        root: Node | None = None
        nodes: dict[int, Node] = {}
        for node_id, serial_node in serial_graph.nodes.items():
            node: Node = Node(
                serial_node.text,
                serial_node.left_option,
                serial_node.right_option
            )
            node.id = int(node_id)
            node.audio_filename = serial_node.audio_filename
            node.is_win = serial_node.is_win
            nodes[node.id] = node
            if root is None:
                root = node
        return root, nodes


    def _establish_connections(self, serial_graph: SerialGraph, nodes: dict[int, Node]) -> None:
        """
        Establish connections between nodes based on adjacency lists. Makes sure that all the nodes have their adjacency
        lists properly filled in, so that the game can be played.
        :param serial_graph:
        :param nodes:
        """
        for node_id, serial_node in serial_graph.nodes.items():
            node = nodes[int(node_id)]
            for gesture, adjacent_node_id in serial_node.adjacency_list.items():
                adjacent_node = nodes[int(adjacent_node_id)]
                node.addNode(gesture, adjacent_node)

