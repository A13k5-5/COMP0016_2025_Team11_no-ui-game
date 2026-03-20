import os
import shutil
import zipfile

from src.graph import Node
from src.graph.serial_graph import SerialGraph

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

    def load_graph(self, game_zip: str) -> tuple[Node, str, str]:
        """
        Loads the graph from a zipped game folder and reconstructs the game structure.
        The zip should contain a graph.json file and corresponding audio files.
        :param game_zip: path to the zipped game folder
        :return:
        """
        game_folder: str = self._prepare_temp_folder(game_zip)

        # load the serial graph from the graph.json file
        graph_path = os.path.join(game_folder, "graph.json")
        with open(graph_path, 'r') as file:
            serial_graph: SerialGraph = SerialGraph.model_validate_json(file.read().strip())

        # reconstruct the graph structure from the serial graph
        root: Node = SerialGraph.deserialize_graph(serial_graph)

        return root, game_folder, game_zip
