import os
import json
import time

from gamePlayer.audio_player import AudioPlayer
from graph import Node

from gesture import EnumGesture
import storageManager.game_load
import storageManager.progress_tracker
from gamePlayer.settings_manager import SettingsManager

class GamePlayer:
    """
    Class to play the interactive story game.
    """
    def __init__(self, recogniser, settings: SettingsManager):
        self.game_loader: storageManager.game_load.GameLoader = storageManager.game_load.GameLoader()
        self.progress_tracker: storageManager.progress_tracker.ProgressTracker = storageManager.progress_tracker.ProgressTracker()
        self.audio_player: AudioPlayer = AudioPlayer()
        self.recogniser = recogniser
        self.settings = settings

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

        start_node = self._start_from(root_node, game_folder, zip_path)
        self._start_game_loop(start_node, game_folder, zip_path)

    def _start_from(self, root_node: Node, game_folder: str, zip_path: str) -> Node:
        """
        If a progress.json exists for this game, ask the player whether to
        resume or restart via a Left/Right gesture.
        """
        progress_path = os.path.join(game_folder, "progress.json")
        if not os.path.exists(progress_path):
            return root_node

        try:
            with open(progress_path, "r") as f:
                data = json.load(f)
            saved_id = data.get("node_id")
            saved_node = self._find_node_by_id(root_node, saved_id)
        except Exception:
            return root_node

        if saved_node is None:
            return root_node

        self.audio_player.play_audio_from_file(game_folder, "progress.wav")
        decision = self.recogniser.get_gesture(self._progress_gestures())

        if decision == EnumGesture.ILoveYou_Left:
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
            decision: EnumGesture = self.recogniser.get_gesture(cur_node.get_possible_gestures() + self._replay_gestures())
            if decision == EnumGesture.Victory:
                self.progress_tracker.save_progress(zip_path, cur_node.get_id())
                self.audio_player.play_audio_from_file(game_folder, "quit.wav")
                break

            while decision in self._replay_gestures():
                if decision == EnumGesture.PointingUp_Left:
                    self.audio_player.play_main_audio(game_folder, cur_node.get_id())
                elif decision == EnumGesture.PointingUp_Right:
                    self.audio_player.play_options_audio(game_folder, cur_node.get_id())

                decision: EnumGesture = self.recogniser.get_gesture(cur_node.get_possible_gestures() + self._replay_gestures())


            cur_node = cur_node.getNode(decision)

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

            time.sleep(2)

    
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
