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
        self._game_folder = None

    def play_game(self, game_path: str):

        while True:
            try:
                root_node, self._game_folder, zip_path = self.game_loader.load_graph(game_path)
            except Exception as e:
                print(f"Failed to load graph from file: {e}")
                return
            # main menu
            progress_node: Node = self.progress_tracker.get_progress_node(self._game_folder, root_node)
            self.audio_player.play_main_menu_audio(self._game_folder, progress_node is not None)

            decision: EnumGesture = self._get_main_menu_decision(progress_node)

            # quit
            if decision == self.settings.get_quit_gesture():
                self.audio_player.play_quit_audio(self._game_folder)
                break

            if decision in self.settings.get_replay_gestures():
                continue

            start_node = self._start_from(root_node, progress_node, decision)

            self._start_game_loop(start_node, zip_path)

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

    def _start_from(self, root_node: Node, saved_node: Node, decision: EnumGesture) -> Node | None:
        """
        If a progress.json exists for this game, ask the player whether to
        resume or restart via a Left/Right gesture.
        """
        if decision == self.settings.get_left_gesture():
            self.audio_player.play_resume_audio(self._game_folder)
            return saved_node
        elif decision == self.settings.get_right_gesture():
            self.audio_player.play_start_new_audio(self._game_folder)
            return root_node
        # for quitting gesture
        return None

    def _get_main_menu_decision(self, progress_node: Node) -> EnumGesture:
        available_gestures: list[EnumGesture] = self.settings.get_replay_gestures() + [self.settings.get_quit_gesture()]

        # right gesture always there to start the game
        available_gestures.append(self.settings.get_right_gesture())

        if progress_node is not None:
            # if progress exists, left gesture to resume the game
            available_gestures.append(self.settings.get_left_gesture())

        decision = self.get_gesture(available_gestures)
        return decision

    def _start_game_loop(self, start_node: Node, zip_path: str):
        """
        Throws TimeoutError if no gesture is detected within TIMEOUT_TIME seconds.
        """
        cur_node: Node = start_node
        while True:
            # Play current scene audio
            self.audio_player.play_audio(self._game_folder, cur_node.get_id())

            # Ask recognizer for a decision
            decision: EnumGesture = self.get_gesture(self._allowed_gestures_for_node(cur_node))

            if decision == self.settings.get_quit_gesture():
                self._handle_quit_from_game(cur_node, zip_path)
                break

            # handle replays
            decision = self._handle_replay(decision, cur_node)

            # handle quit again in case the player decided to quit while replaying
            if decision == self.settings.get_quit_gesture():
                self._handle_quit_from_game(cur_node, zip_path)
                break

            chosen_side: EnumLR | None = self._gesture_to_side(decision)
            if chosen_side is None:
                continue
            cur_node = cur_node.getNode(chosen_side)

            if cur_node.is_win:
                self._handle_win(cur_node)
                break
            if cur_node.is_losing:
                self._handle_lose(cur_node, zip_path)
                break

            time.sleep(1)

    def _handle_replay(self, decision: EnumGesture, cur_node: Node) -> EnumGesture:
        while decision in self.settings.get_replay_gestures():
            if decision == self.settings.get_replay_main_gesture():
                self.audio_player.play_main_audio(self._game_folder, cur_node.get_id())
            elif decision == self.settings.get_replay_options_gesture():
                self.audio_player.play_options_audio(self._game_folder, cur_node.get_id())

            decision: EnumGesture = self.get_gesture(self._allowed_gestures_for_node(cur_node))

        return decision

    def get_gesture(self, gestures_to_spot: list[EnumGesture]) -> EnumGesture:
        """
        A wrapper around the recogniser's get_gesture method to handle timeout exceptions and return the quit gesture if a timeout occurs.
        :param gestures_to_spot:
        :return:
        """
        try:
            return self.recogniser.get_gesture(gestures_to_spot)
        except TimeoutError:
            self.audio_player.play_inactivity_audio(self._game_folder)
            return self.settings.get_quit_gesture()

    def _handle_quit_from_game(self, cur_node: Node, zip_path: str):
        self.progress_tracker.save_progress(zip_path, cur_node.get_id())
        self.audio_player.play_quitting_to_main_menu(self._game_folder)

    def _handle_win(self, cur_node: Node):
        self.audio_player.play_audio(self._game_folder, cur_node.get_id())
        self.audio_player.play_win_audio(self._game_folder)

    def _handle_lose(self, cur_node: Node, zip_path: str):
        self.audio_player.play_audio(self._game_folder, cur_node.get_id())
        self.audio_player.play_lose_audio(self._game_folder)
        self.progress_tracker.clear_progress(zip_path)
