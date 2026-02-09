import json
import os

from graph import Node
from text2speech import Talker

class GraphSave:
    """
    Class responsible for saving the game into a game 'folder' (containing the graph and corresponding audio files).
    """

    def save_game(self, path_to_save: str, game_name: str, root: Node):
        """
        Saves the game to the given path.
        :param path_to_save:
        :param root:
        :return:
        """
        game_path: str = os.path.join(path_to_save, game_name)
        self._prepare_game_folder(game_path)
        audio_dir: str = os.path.join(game_path, "audio")
        serialized_graph: dict = self._serialize_graph(root, audio_dir)
        print(serialized_graph)
        self.save_graph(game_path, serialized_graph)
        self._generate_audio(serialized_graph, audio_dir)


    def _prepare_game_folder(self, game_path: str):
        """
        Prepares the game folder by creating the necessary directory structure. If a folder with the same name already exists,
        an exception is raised to prevent overwriting existing data.
        :param game_path:
        :return:
        """
        audio_dir: str = os.path.join(game_path, "audio")
        if os.path.exists(audio_dir):
            raise Exception("Game folder already exists. Please choose a different name or delete the existing folder.")
        os.makedirs(audio_dir)


    def save_graph(self, path_to_save: str, serialized_graph: dict):
        """
        Saves the graph to a JSON file.
        :param path_to_save: path to the directory where the graph should be saved
        :param serialized_graph: the graph in a serialized format (dictionary) to be saved as JSON
        :return:
        """
        graph_path: str = os.path.join(path_to_save, "graph.json")
        with open(graph_path, 'w') as file:
            json.dump(serialized_graph, file, indent=4)


    def _serialize_graph(self, root: Node, audio_dir: str) -> dict:
        """
        Serializes the graph starting from the root node using DFS. Each node is stored in a dictionary with its ID as
        the key and its details (text, audio path, adjacency list) as the value. The adjacency list is represented as a
        dictionary mapping gesture strings to adjacent node IDs.
        :param root:
        :param audio_dir: directory where audio files will be stored
        :return: dictionary of serialized nodes
        """
        visited = {}

        def dfs(node: Node):
            if node.get_id() in visited:
                return
            visited[node.get_id()] = self._serialize_node(node, audio_dir)
            for adjacent_node in node.adjacencyList.values():
                dfs(adjacent_node)

        dfs(root)
        return visited


    def _get_node_audio_path(self, node_id: int, audio_dir: str) -> str:
        """
        Generates the file path for the audio file corresponding to a given node.
        :param node_id: the ID of the node for which to generate the audio file path
        :param audio_dir: the directory where audio files are stored
        :return: the file path for the node's audio file
        """
        return os.path.join(audio_dir, f"node_{node_id}.wav")


    def _serialize_node(self, node: Node, audio_dir: str) -> dict:
        """
        Serializes a single node into a dictionary format, including its text, audio path, and adjacency list.
        :param node: node to be serialized
        :param audio_dir: directory where audio files will be stored
        :return: serialized node as a dictionary
        """
        return {
            "id": node.get_id(),
            "text": node.getText(),
            "audioPath": self._get_node_audio_path(node.get_id(), audio_dir),
            "adjacencyList": {gesture.__str__(): adjacent_node.get_id() for gesture, adjacent_node in node.adjacencyList.items()}
        }


    def _generate_audio(self, data: dict, audio_dir: str):
        """
        Generates audio files for each node in the graph using the Talker class. The audio files are saved in the specified
        audio directory with filenames corresponding to their node IDs.
        :param data:
        :param audio_dir:
        :return:
        """
        talker = Talker()
        description = "A calm and soothing narration voice"

        for node_id, node_data in data.items():
            text = node_data["text"]
            output_file = self._get_node_audio_path(node_id, audio_dir)

            talker.generate_speech(text, description, output_file)
