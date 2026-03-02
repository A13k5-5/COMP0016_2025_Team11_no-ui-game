import os
import tempfile
import zipfile

from graph import Node
from graph.serial_graph import SerialGraph
from graph.serial_node import SerialNode
from text2speech import Talker


class GameSaver:
    """
    Class responsible for saving the game into a zipped game folder (containing the graph and corresponding audio files).
    """

    def save_game(self, path_to_save: str, game_name: str, root: Node):
        """
        Saves the game to the given path as a zip archive. Only the zip file is written to path_to_save;
        a temporary directory is used for staging and is removed afterwards.
        :param path_to_save: the directory where the game zip should be created
        :param game_name: the name of the game, which will be used as the name of the zip file
        :param root: the root node of the graph representing the game
        :return:
        """
        zip_path: str = os.path.join(path_to_save, game_name + ".zip")

        self._check_zip_path(zip_path)

        with tempfile.TemporaryDirectory() as tmp_dir:
            stage_path: str = os.path.join(tmp_dir, game_name)
            os.makedirs(os.path.join(stage_path, "audio"))

            serialized_graph: SerialGraph = self._serialize_graph(root)
            self.save_graph(stage_path, serialized_graph)
            # self._generate_audio(serialized_graph, stage_path)

            self._zip_folder_to(stage_path, zip_path)


    def _check_zip_path(self, zip_path: str):
        """
        Ensures the destination zip path is available. If a valid game zip already exists it is removed so it can be
        overwritten. If an unrelated file occupies the path, an exception is raised.
        :param zip_path: full path to the target zip file
        :return:
        """
        if os.path.exists(zip_path):
            if not self._is_game_zip(zip_path):
                raise Exception(
                    f"A file '{zip_path}' already exists but is not a valid game zip. "
                    "Please choose a different name or delete the existing file."
                )
            os.remove(zip_path)


    def _zip_folder_to(self, folder_path: str, zip_path: str):
        """
        Writes the contents of folder_path into a new zip archive at zip_path.
        The archive entries are relative to folder_path's parent so the game name
        is preserved as the top-level folder inside the zip.
        :param folder_path: the staging folder to zip
        :param zip_path: destination zip file path
        :return:
        """
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for dirpath, _, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_full_path = os.path.join(dirpath, filename)
                    arcname = os.path.relpath(file_full_path, os.path.dirname(folder_path))
                    zf.write(file_full_path, arcname)

    def _is_game_zip(self, path: str) -> bool:
        """
        Checks if the given path is a valid game zip by verifying the presence of a graph.json entry
        and at least one audio/ entry inside the archive.
        :param path:
        :return: True if the path is a valid game zip, False otherwise
        """
        if not zipfile.is_zipfile(path):
            return False
        with zipfile.ZipFile(path, 'r') as zf:
            names = zf.namelist()
            has_graph = any(n.endswith("graph.json") for n in names)
            has_audio = any("audio/" in n for n in names)
            return has_graph and has_audio


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


    def _serialize_graph(self, root: Node) -> SerialGraph:
        """
        Serializes the graph starting from the root node using DFS. Each node is stored in a dictionary with its ID as
        the key and its details (text, audio path, adjacency list) as the value. The adjacency list is represented as a
        dictionary mapping gesture strings to adjacent node IDs.
        :param root:
        :return: dictionary of serialized nodes
        """
        serial_graph: SerialGraph = SerialGraph(nodes={})

        def dfs(node: Node):
            if node.get_id() in serial_graph.nodes:
                return
            serial_graph.nodes[node.get_id()] = self._serialize_node(node)
            for adjacent_node in node.adjacencyList.values():
                dfs(adjacent_node)

        dfs(root)
        return serial_graph


    def _get_node_audio_filename(self, node_id: int) -> str:
        """
        Generates the file path for the audio file corresponding to a given node.
        :param node_id: the ID of the node for which to generate the audio file path
        :return: the file path for the node's audio file
        """
        return f"node_{node_id}.wav"


    def _serialize_node(self, node: Node) -> SerialNode:
        """
        Serializes a single node into a dictionary format, including its text, audio path, and adjacency list.
        :param node: node to be serialised
        :return: serialised node as a dictionary
        """
        return SerialNode(
            id=node.get_id(),
            text=node.getText(),
            left_option=node.left_option,
            right_option=node.right_option,
            audio_filename=self._get_node_audio_filename(node.get_id()),
            adjacency_list={gesture: adjacent_node.get_id() for gesture, adjacent_node in node.adjacencyList.items()},
            is_win=node.is_win
        )


    def _generate_audio(self, serial_graph: SerialGraph, game_path: str):
        """
        Generates audio files for each node in the graph using the Talker class. The audio files are saved in the specified
        audio directory with filenames corresponding to their node IDs.
        :param serial_graph: the serialized graph containing all nodes for which audio needs to be generated
        :return:
        """
        talker: Talker = Talker()
        description: str = "A calm and soothing narration voice"

        for node_id, serial_node in serial_graph.nodes.items():
            text_parts = [serial_node.text]
            if serial_node.left_option or serial_node.right_option:
                text_parts.append("...You have two options.")
            if serial_node.left_option:
                text_parts.append(f"Do {serial_node.left_option} by raising your left hand.")
            if serial_node.right_option:
                text_parts.append(f"Do {serial_node.right_option} by raising your right hand.")
            
            full_text = " ".join(text_parts).strip()
            output_file: str = os.path.join(game_path, "audio", self._get_node_audio_filename(node_id))

            talker.generate_speech(full_text, description, output_file)
