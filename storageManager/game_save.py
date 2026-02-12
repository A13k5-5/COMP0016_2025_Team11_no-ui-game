import os
import shutil

from graph import Node
from graph.serial_graph import SerialGraph
from graph.serial_node import SerialNode
from text2speech import Talker


class GameSaver:
    """
    Class responsible for saving the game into a game 'folder' (containing the graph and corresponding audio files).
    """

    def save_game(self, path_to_save: str, game_name: str, root: Node):
        """
        Saves the game to the given path.
        :param path_to_save: the directory where the game folder should be created
        :param game_name: the name of the game, which will be used as the name of the game folder
        :param root: the root node of the graph representing the game
        :return:
        """
        game_path: str = os.path.join(path_to_save, game_name)
        audio_dir: str = os.path.join(game_path, "audio")

        self._prepare_game_folder(game_path)

        serialized_graph: SerialGraph = self._serialize_graph(root, audio_dir)
        self.save_graph(game_path, serialized_graph)

        # self._generate_audio(serialized_graph, audio_dir)


    def _prepare_game_folder(self, game_path: str):
        """
        Prepares the game folder by creating the necessary directory structure. If a folder with the same name already exists,
        an exception is raised to prevent overwriting existing data.
        :param game_path:
        :return:
        """
        if os.path.exists(game_path):
            if not self._is_game_folder(game_path):
                raise Exception(f"A folder {game_path} already exists, but it not a valid game folder. Please choose a different name or delete the existing folder.")
            # if a game folder, we can proceed to overwrite it
            shutil.rmtree(game_path)
        audio_dir: str = os.path.join(game_path, "audio")
        os.makedirs(audio_dir)

    def _is_game_folder(self, path: str) -> bool:
        """
        Checks if the given path is a valid game folder by verifying the presence of the graph.json file and the audio directory.
        :param path:
        :return: True if the path is a valid game folder, False otherwise
        """
        graph_path: str = os.path.join(path, "graph.json")
        audio_dir: str = os.path.join(path, "audio")
        return os.path.isfile(graph_path) and os.path.isdir(audio_dir)


    def save_graph(self, path_to_save: str, serialized_graph: SerialGraph):
        """
        Saves the graph to a JSON file.
        :param path_to_save: path to the directory where the graph should be saved
        :param serialized_graph: the graph in a serialized format (dictionary) to be saved as JSON
        :return:
        """
        graph_path: str = os.path.join(path_to_save, "graph.json")
        with open(graph_path, 'w') as file:
            file.write(serialized_graph.model_dump_json(indent=4))


    def _serialize_graph(self, root: Node, audio_dir: str) -> SerialGraph:
        """
        Serializes the graph starting from the root node using DFS. Each node is stored in a dictionary with its ID as
        the key and its details (text, audio path, adjacency list) as the value. The adjacency list is represented as a
        dictionary mapping gesture strings to adjacent node IDs.
        :param root:
        :param audio_dir: directory where audio files will be stored
        :return: dictionary of serialized nodes
        """
        serial_graph: SerialGraph = SerialGraph(nodes={})

        def dfs(node: Node):
            if node.get_id() in serial_graph.nodes:
                return
            serial_graph.nodes[node.get_id()] = self._serialize_node(node, audio_dir)
            for adjacent_node in node.adjacencyList.values():
                dfs(adjacent_node)

        dfs(root)
        return serial_graph


    def _get_node_audio_path(self, node_id: int, audio_dir: str) -> str:
        """
        Generates the file path for the audio file corresponding to a given node.
        :param node_id: the ID of the node for which to generate the audio file path
        :param audio_dir: the directory where audio files are stored
        :return: the file path for the node's audio file
        """
        return os.path.join(audio_dir, f"node_{node_id}.wav")


    def _serialize_node(self, node: Node, audio_dir: str) -> SerialNode:
        """
        Serializes a single node into a dictionary format, including its text, audio path, and adjacency list.
        :param node: node to be serialized
        :param audio_dir: directory where audio files will be stored
        :return: serialized node as a dictionary
        """
        return SerialNode(
            id=node.get_id(),
            text=node.getText(),
            audio_path=self._get_node_audio_path(node.get_id(), audio_dir),
            adjacency_list={gesture: adjacent_node.get_id() for gesture, adjacent_node in node.adjacencyList.items()}
        )
        return {
            "id": node.get_id(),
            "text": node.getText(),
            "audioPath": self._get_node_audio_path(node.get_id(), audio_dir),
            "adjacencyList": {gesture.__str__(): adjacent_node.get_id() for gesture, adjacent_node in node.adjacencyList.items()}
        }


    def _generate_audio(self, serial_graph: SerialGraph, audio_dir: str):
        """
        Generates audio files for each node in the graph using the Talker class. The audio files are saved in the specified
        audio directory with filenames corresponding to their node IDs.
        :param serial_graph: the serialized graph containing all nodes for which audio needs to be generated
        :param audio_dir:
        :return:
        """
        talker: Talker = Talker()
        description: str = "A calm and soothing narration voice"

        for node_id, serial_node in serial_graph.nodes.items():
            text: str = serial_node.text
            output_file: str = self._get_node_audio_path(node_id, audio_dir)

            talker.generate_speech(text, description, output_file)
