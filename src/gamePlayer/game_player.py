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

    def _quit_gesture(self) -> EnumGesture:
        return self.settings.get_gesture("quit")

    def _replay_gestures(self) -> list[EnumGesture]:
        return [self.settings.get_gesture("replay_main"), self.settings.get_gesture("replay_options")]
 
    def _progress_gestures(self) -> list[EnumGesture]:
        return [self.settings.get_gesture("option_left"), self.settings.get_gesture("option_right")]

    def play_game(self, game_path: str):
        try:
            root_node, game_folder, zip_path = self.game_loader.load_graph(game_path)
        except Exception as e:
            print(f"Failed to load graph from file: {e}")
            return

        # before starting the game loop, show the menu
        progress_node: Node = self._get_progress_node(game_folder, root_node)
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
            return self.settings.get_gesture("option_left")
        return self.settings.get_gesture("option_right")
    
    def _allowed_gestures_for_node(self, node: Node) -> list[EnumGesture]:
        option_gestures = [self._side_to_gesture(side) for side in node.get_possible_sides()]
        return option_gestures + self._replay_gestures() + [self._quit_gesture()]

    def _get_progress_node(self, game_folder: str, root_node: Node) -> Node | None:
        """
        Gives the progress node if a progress.json file exists and is valid, otherwise returns None.
        :param game_folder:
        :param root_node:
        :return:
        """
        progress_path = os.path.join(game_folder, "progress.json")

        # if doesn't exist, return None
        if not os.path.exists(progress_path):
            return None

        try:
            # if error, return None
            with open(progress_path, "r") as f:
                data = json.load(f)
            saved_id = data.get("node_id")
            saved_node = self._find_node_by_id(root_node, saved_id)
        except Exception:
            return None

        if saved_node is None:
            return None

        return saved_node

    def _start_from(self, root_node: Node, saved_node: Node, game_folder: str) -> Node:
        """
        If a progress.json exists for this game, ask the player whether to
        resume or restart via a Left/Right gesture.
        """
        available_gestures = [self.settings.get_right_gesture()]
        if saved_node is not None:
            available_gestures.append(self.settings.get_left_gesture())

        decision = self.recogniser.get_gesture(available_gestures + [self._quit_gesture()])

        if decision == self.settings.get_gesture("option_left"):
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
            if decision == self._quit_gesture():
                self.progress_tracker.save_progress(zip_path, cur_node.get_id())
                self.audio_player.play_audio_from_file(game_folder, "quit.wav")
                break

            while decision in self._replay_gestures():
                if decision == self.settings.get_gesture("replay_main"):
                    self.audio_player.play_main_audio(game_folder, cur_node.get_id())
                elif decision == self.settings.get_gesture("replay_options"):
                    self.audio_player.play_options_audio(game_folder, cur_node.get_id())

                decision: EnumGesture = self.recogniser.get_gesture(self._allowed_gestures_for_node(cur_node))

            chosen_side = self._gesture_to_side(decision)
            if chosen_side is None:
                continue
            cur_node = cur_node.getNode(chosen_side)

            if cur_node.is_win:
                self.audio_player.play_audio(game_folder, cur_node.get_id())
                self.audio_player.play_audio_from_file(game_folder, "win.wav")
                self.progress_tracker.clear_progress(zip_path)
                break
            if cur_node.is_losing:
                self.audio_player.play_audio(game_folder, cur_node.get_id())
                self.audio_player.play_audio_from_file(game_folder, "lose.wav")
                self.progress_tracker.clear_progress(zip_path)
                break

            time.sleep(1)

    
    def _find_node_by_id(self, root: Node, target_id: int) -> Node | None:
        """
        BFS from root to find the node with the given ID
        """
        visited: set[int] = set()
        queue: list[Node] = [root]
        while queue:
            node = queue.pop(0)
            node_id = node.get_id()
            if node_id in visited:
                continue
            visited.add(node_id)
            if node_id == target_id:
                return node
            queue.extend(node.adjacencyList.values())
        return None
