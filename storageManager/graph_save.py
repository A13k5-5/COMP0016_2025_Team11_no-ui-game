import json
import os

from graph import Node

class GraphSave:
    def __init__(self, graph):
        self.graph = graph

    def save_graph(self, root: Node, filename: str, audio_dir: str = "audio", game_folder: str = "game"):
        # Create audio directory - if it doesnt exist already
        audio_dir = os.path.join(game_folder, audio_dir)

        self._prep_audio_dir(audio_dir)

        graph_path = os.path.join(game_folder, filename)
        with open(graph_path, 'w') as file:
            json.dump(self._serialize_graph(root), file, indent=4)

        self._generate_audio(self._serialize_graph(root), audio_dir)


    def _prep_audio_dir(self, audio_dir: str):
        # Remove old audio files to avoid duplicates
        if os.path.exists(audio_dir):
            for f in os.listdir(audio_dir):
                os.remove(os.path.join(audio_dir, f))
        os.makedirs(audio_dir, exist_ok=True)


    def _serialize_graph(self, root: Node) -> dict:
        """
        Serializes the graph starting from the root node using DFS. Each node is stored in a dictionary with its ID as
        the key and its details (text, audio path, adjacency list) as the value. The adjacency list is represented as a
        dictionary mapping gesture strings to adjacent node IDs.
        :param root:
        :return: dictionary of serialized nodes
        """
        visited = {}

        def dfs(node: Node):
            if node.get_id() in visited:
                return
            visited[node.get_id()] = self._serialize_node(node)
            for adjacent_node in node.adjacencyList.values():
                dfs(adjacent_node)

        dfs(root)
        return visited


    def _serialize_node(self, node: Node) -> dict:
        """
        Serializes a single node into a dictionary format, including its text, audio path, and adjacency list.
        :param node:
        :return: serialized node as a dictionary
        """
        audio_filename = f"node_{node.get_id()}.wav"
        return {
            "id": node.get_id(),
            "text": node.getText(),
            "audioPath": f"game/audio/{audio_filename}",
            "adjacencyList": {gesture.__str__(): adjacent_node.get_id() for gesture, adjacent_node in node.adjacencyList.items()}
        }
