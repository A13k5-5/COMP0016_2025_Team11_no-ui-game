import os
import json
import time

from src.gamePlayer.audio_player import AudioPlayer
from src.graph import Node

from src.gesture import EnumGesture
from src.graph.enum_LR import EnumLR
from src.storageManager import game_load
from src.storageManager import progress_tracker
from src.gamePlayer.settings_manager import SettingsManager

class GamePlayer:
    """
    Class to play the interactive story game.
    """
    def __init__(self, recogniser, settings: SettingsManager):
        self.game_loader: game_load.GameLoader = game_load.GameLoader()
        self.progress_tracker: progress_tracker.ProgressTracker = progress_tracker.ProgressTracker()
        self.audio_player: AudioPlayer = AudioPlayer()
        self.recogniser = recogniser
        self.settings = settings

    def play_game(self, game_path: str):
        try:
            root_node, game_folder, zip_path = self.game_loader.load_graph(game_path)
        except Exception as e:
            print(f"Failed to load graph from file: {e}")
            return

        # before starting the game loop, show the menu
        progress_node: Node = self.progress_tracker.get_progress_node(game_folder, root_node)
        self.audio_player.play_main_menu_audio(game_folder, progress_node is not None)
        start_node = self._start_from(root_node, progress_node, game_folder)

        self._start_game_loop(start_node, game_folder, zip_path)

    def _gesture_to_side(self, gesture: EnumGesture) -> EnumLR | None:
        if gesture == self.settings.get_left_gesture():
            return EnumLR.LEFT
        if gesture == self.settings.get_right_gesture():
            return EnumLR.RIGHT
        return None

    def _side_to_gesture(self, side: EnumLR) -> EnumGesture:
        if side == EnumLR.LEFT:
            return self.settings.get_left_gesture()
        return self.settings.get_right_gesture()
    
    def _allowed_gestures_for_node(self, node: Node) -> list[EnumGesture]:
        option_gestures = [self._side_to_gesture(side) for side in node.get_possible_sides()]
        return option_gestures + self.settings.get_replay_gestures() + [self.settings.get_quit_gesture()]

    def _start_from(self, root_node: Node, saved_node: Node, game_folder: str) -> Node:
        """
        If a progress.json exists for this game, ask the player whether to
        resume or restart via a Left/Right gesture.
        """
        available_gestures = [self.settings.get_right_gesture()]
        if saved_node is not None:
            available_gestures.append(self.settings.get_left_gesture())

        decision = self.recogniser.get_gesture(available_gestures + [self.settings.get_quit_gesture()])

        if decision == self.settings.get_left_gesture():
            self.audio_player.play_audio_from_file(game_folder, "resume.wav")
            return saved_node
        else:
            self.audio_player.play_audio_from_file(game_folder, "start_new.wav")
            return root_node

    def _start_game_loop(self, start_node: Node, game_folder: str, zip_path: str):
        """
        Throws TimeoutError if no gesture is detected within TIMEOUT_TIME seconds.
        """
        cur_node: Node = start_node
        while True:
            # Play current scene audio
            self.audio_player.play_audio(game_folder, cur_node.get_id())

            # Ask recognizer for a decision (expects a tuple like ("ILoveYou", "Left"))
            decision: EnumGesture = self.recogniser.get_gesture(self._allowed_gestures_for_node(cur_node))

            if decision == self.settings.get_quit_gesture():
                self._handle_quit(cur_node, game_folder, zip_path)
                break

            decision = self._handle_replay(decision, cur_node, game_folder)

            # handle quit again in case the player decided to quit while replaying
            if decision == self.settings.get_quit_gesture():
                self._handle_quit(cur_node, game_folder, zip_path)
                break

            chosen_side = self._gesture_to_side(decision)
            if chosen_side is None:
                continue
            cur_node = cur_node.getNode(chosen_side)

            if cur_node.is_win:
                self._handle_win(cur_node, game_folder, zip_path)
                break
            if cur_node.is_losing:
                self._handle_lose(cur_node, game_folder, zip_path)
                break

            time.sleep(1)

    def _handle_replay(self, decision: EnumGesture, cur_node: Node, game_folder: str) -> EnumGesture:
        while decision in self.settings.get_replay_gestures():
            if decision == self.settings.get_replay_main_gesture():
                self.audio_player.play_main_audio(game_folder, cur_node.get_id())
            elif decision == self.settings.get_replay_options_gesture():
                self.audio_player.play_options_audio(game_folder, cur_node.get_id())

            decision: EnumGesture = self.recogniser.get_gesture(self._allowed_gestures_for_node(cur_node))

        return decision

    def _handle_quit(self, cur_node: Node, game_folder: str, zip_path: str):
        self.progress_tracker.save_progress(zip_path, cur_node.get_id())
        self.audio_player.play_audio_from_file(game_folder, "quit.wav")

    def _handle_win(self, cur_node: Node, game_folder: str, zip_path: str):
        self.audio_player.play_audio(game_folder, cur_node.get_id())
        self.audio_player.play_audio_from_file(game_folder, "win.wav")
        self.progress_tracker.clear_progress(zip_path)

    def _handle_lose(self, cur_node: Node, game_folder: str, zip_path: str):
        self.audio_player.play_audio(game_folder, cur_node.get_id())
        self.audio_player.play_audio_from_file(game_folder, "lose.wav")
        self.progress_tracker.clear_progress(zip_path)
