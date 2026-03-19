import os
from playsound3 import playsound
from pathlib import Path
import time

from src.graph import Node

class AudioPlayer:
    @staticmethod
    def play_audio_from_path(file_path: str | Path):
        """
        Play the audio file at the given path.
        """
        print(file_path)
        try:
            playsound(file_path)
        except Exception as e:
            print(f"Error playing audio file {file_path}: {e}")

    def play_main_audio(self, game_folder: str, node_id: int):
        """
        Play the main audio file for the current node.
        """
        self.play_audio_from_path(os.path.join(game_folder, "audio", Node.get_main_text_audio_filename(node_id)))

    def play_options_audio(self, game_folder: str, node_id: int):
        """
        Play the options audio file for the current node.
        """
        self.play_audio_from_path(os.path.join(game_folder, "audio", Node.get_options_audio_filename(node_id)))

    def play_main_menu_audio(self, game_folder: str, progress_exists: bool):
        """
        Play the main menu audio file.
        """
        self.play_audio_from_path(os.path.join(game_folder, "audio", "main_menu_welcome.wav"))
        self.play_audio_from_path(os.path.join(game_folder, "audio", "main_menu_new_game.wav"))
        if progress_exists:
            self.play_audio_from_path(os.path.join(game_folder, "audio", "main_menu_progress.wav"))

    def play_audio(self, game_folder: str, node_id: int):
        """
        Play the main audio followed by the options audio for the current node.
        """
        self.play_main_audio(game_folder, node_id)
        time.sleep(0.5)  # small pause between main text and options
        self.play_options_audio(game_folder, node_id)

    def play_audio_from_file(self, game_folder: str, audio_file: str):
        """
        Play the audio from file name
        """
        self.play_audio_from_path(os.path.join(game_folder, "audio", audio_file))

if __name__ == "__main__":
    AudioPlayer.play_audio_from_path(Path(__file__).parent.parent / "voiceSamples" / "bf_emma.wav")
