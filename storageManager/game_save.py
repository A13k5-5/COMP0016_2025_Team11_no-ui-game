import os
import tempfile
import zipfile
import json

from multipledispatch import dispatch
from . import config
from graph import Node
from graph.serial_graph import SerialGraph
from text2speech import Talker


class GameSaver:
    """
    Class responsible for saving the game into a zipped game folder (containing the graph and corresponding audio files).
    """

    @dispatch(str, str, Node)
    def save_game(self, path_to_save: str, game_name: str, root: Node):
        serialized_graph: SerialGraph = SerialGraph.serialize_graph(root)
        self.save_game(path_to_save, game_name, serialized_graph)

    @dispatch(str, str, SerialGraph)
    def save_game(self, path_to_save: str, game_name: str, serialized_graph: SerialGraph):
        """
        Saves the game to the given path as a zip archive. Only the zip file is written to path_to_save;
        a temporary directory is used for staging and is removed afterwards.
        :param path_to_save: the directory where the game zip should be created
        :param game_name: the name of the game, which will be used as the name of the zip file
        :param serialized_graph: the graph in a serialized format (dictionary) to be saved as JSON
        :return:
        """
        zip_path: str = os.path.join(path_to_save, game_name + config.FILE_EXTENSION)

        self._check_zip_path(zip_path)

        with tempfile.TemporaryDirectory() as tmp_dir:
            stage_path: str = os.path.join(tmp_dir, game_name)
            os.makedirs(os.path.join(stage_path, "audio"))

            self.save_graph(stage_path, serialized_graph)
            self._generate_audio(serialized_graph, stage_path)

            self._zip_folder_to(stage_path, zip_path)

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

    def _get_node_audio_filename(self, node_id: int) -> str:
        """
        Generates the file path for the audio file corresponding to a given node.
        :param node_id: the ID of the node for which to generate the audio file path
        :return: the file path for the node's audio file
        """
        return f"node_{node_id}.wav"

    def _generate_audio(self, serial_graph: SerialGraph, game_path: str):
        """
        Generates audio files for each node in the graph using the Talker class. The audio files are saved in the specified
        audio directory with filenames corresponding to their node IDs.
        :param serial_graph: the serialized graph containing all nodes for which audio needs to be generated
        :return:
        """
        talker: Talker = Talker()

        for node_id, serial_node in serial_graph.nodes.items():
            # generate the main text audio
            main_text_audio_file: str = os.path.join(game_path, "audio", Node.get_main_text_audio_filename(node_id))
            talker.generate_speech(serial_node.text, main_text_audio_file)

            # generate the options audio
            options_audio_file: str = serial_node.get_options_text()
            output_file = os.path.join(game_path, "audio", Node.get_options_audio_filename(node_id))
            talker.generate_speech(options_audio_file, output_file)

        # generate win/lose outcome audio
        talker.generate_speech("You win!", os.path.join(game_path, "audio", "win.wav"))
        talker.generate_speech("Game over!", os.path.join(game_path, "audio", "lose.wav"))

        # generate progress instructions
        talker.generate_speech(
            "A saved game was found. Raise your left hand to resume, or your right to restart.",
            os.path.join(game_path, "audio", "progress.wav")
        )
        talker.generate_speech("Resuming your game", os.path.join(game_path, "audio", "resume.wav") )
        talker.generate_speech("Starting a new game", os.path.join(game_path, "audio", "start_new.wav"))
        talker.generate_speech("Quitting game. Your progress has been saved.", os.path.join(game_path, "audio", "quit.wav"))


    def save_progress(self, zip_path: str, node_id: int) -> None:
        """
        Write progress.json into the .noui zip with the current node ID.
        """
        with zipfile.ZipFile(zip_path, 'r') as zf:
            top_level = {name.split('/')[0] for name in zf.namelist() if '/' in name}
            game_name = next(iter(top_level))

        arcname = f"{game_name}/progress.json"
        progress_content = json.dumps({"node_id": node_id})
        self._update_zip_entry(zip_path, arcname, progress_content)
    
    def clear_progress(self, zip_path: str) -> None:
        """
        Remove progress.json from the .noui zip if it exists.
        """
        self._remove_zip_entry(zip_path, "progress.json")

    def _update_zip_entry(self, zip_path: str, arcname: str, content: str) -> None:
        """
        Add or replace a text entry inside an existing zip file in place.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(tmp_dir)

            full_path = os.path.join(tmp_dir, arcname)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for dirpath, _, filenames in os.walk(tmp_dir):
                    for filename in filenames:
                        file_full_path = os.path.join(dirpath, filename)
                        arc = os.path.relpath(file_full_path, tmp_dir)
                        zf.write(file_full_path, arc)

    def _remove_zip_entry(self, zip_path: str, filename: str) -> None:
        """
        Remove all entries whose name ends with filename from the zip.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                members = [m for m in zf.namelist() if not m.endswith(filename)]
                zf.extractall(tmp_dir)

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for dirpath, _, filenames in os.walk(tmp_dir):
                    for fn in filenames:
                        file_full_path = os.path.join(dirpath, fn)
                        arc = os.path.relpath(file_full_path, tmp_dir)
                        if arc in members:
                            zf.write(file_full_path, arc)

