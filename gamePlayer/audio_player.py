import os
from playsound3 import playsound
import time

from graph import Node

class AudioPlayer:
    def _play_audio_from_path(self, file_path: str):
        """
        Play the audio file at the given path.
        """
        try:
            playsound(file_path)
        except Exception as e:
            print(f"Error playing audio file {file_path}: {e}")

    def play_main_audio(self, game_path: str, node_id: int):
        """
        Play the main audio file for the current node.
        """
        self._play_audio_from_path(os.path.join(game_path, "audio", Node.get_main_text_audio_filename(node_id)))

    def play_options_audio(self, game_path: str, node_id: int):
        """
        Play the options audio file for the current node.
        """
        self._play_audio_from_path(os.path.join(game_path, "audio", Node.get_options_audio_filename(node_id)))

    def play_audio(self, game_path: str, node_id: int):
        """
        Play the main audio followed by the options audio for the current node.
        """
        self.play_main_audio(game_path, node_id)
        time.sleep(0.5)  # small pause between main text and options
        self.play_options_audio(game_path, node_id)

    def play_audio_from_file(self, game_path: str, audio_file: str):
        """
        Play the audio from file name
        """
        self._play_audio_from_path(os.path.join(game_path, "audio", audio_file))