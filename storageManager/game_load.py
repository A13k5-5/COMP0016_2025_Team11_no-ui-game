import os

from graph import Node
from graph.serial_graph import SerialGraph


class GameLoader:
    """
    Class responsible for loading a game from a game 'folder' (containing the graph and corresponding audio files).
    """
    def load_graph(self, game_folder: str) -> Node:
        """
        Loads the graph from a JSON file and reconstructs the game structure. The JSON file should contain the serialized graph.
        :param game_folder: path to the game folder containing the graph.json file
        :return:
        """
        graph_path = os.path.join(game_folder, "graph.json")
        with open(graph_path, 'r') as file:
            serial_graph: SerialGraph = SerialGraph.model_validate_json(file.read().strip())

        root, nodes = self._load_nodes(serial_graph)
        self._establish_connections(serial_graph, nodes)

        return root


    def _load_nodes(self, serial_graph: SerialGraph) -> tuple[Node, dict[int, Node]]:
        """
        Load nodes without connections. Gives back the root node and a dictionary of all nodes.
        :param serial_graph:
        :return:
        """
        root: Node | None = None
        nodes: dict[int, Node] = {}
        for node_id, serial_node in serial_graph.nodes.items():
            node: Node = Node(serial_node.text)
            node.id = int(node_id)
            node.audioPath = serial_node.audio_path
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

