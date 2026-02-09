import json
import os

from graph import Node

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
            data = json.load(file)

        root, nodes = self._load_nodes(data)
        self._establish_connections(data, nodes)

        return root


    def _load_nodes(self, data: dict) -> (Node, dict[int, Node]):
        """
        Load nodes without connections. Gives back the root node and a dictionary of all nodes.
        :param data:
        :return:
        """
        root: Node | None = None
        nodes: dict[int, Node] = {}
        for node_id, node_data in data.items():
            node = Node(node_data["text"])
            node.id = int(node_id)
            node.audioPath = node_data.get("audioPath")
            nodes[node.id] = node
            if root is None:
                root = node
        return root, nodes


    def _establish_connections(self, data: dict, nodes: dict[int, Node]) -> None:
        """
        Establish connections between nodes based on adjacency lists. Makes sure that all the nodes have their adjacency
        lists properly filled in, so that the game can be played.
        :param data:
        :param nodes:
        """
        for node_id, node_data in data.items():
            node = nodes[int(node_id)]
            for gesture_str, adjacent_node_id in node_data["adjacencyList"].items():
                # reconstruct the gesture tuple
                gesture = eval(gesture_str)
                adjacent_node = nodes[int(adjacent_node_id)]
                node.addNode(gesture, adjacent_node)
