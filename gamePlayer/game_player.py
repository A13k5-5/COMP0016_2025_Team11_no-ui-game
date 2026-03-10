import time

from gamePlayer.audio_player import AudioPlayer
from graph import Node
import myGestureRecognizer

from gesture import EnumGesture
import storageManager.game_load

ALWAYS_GESTURES = [EnumGesture.PointingUp_Left, EnumGesture.PointingUp_Right]

class GamePlayer:
    """
    Class to play the interactive story game.
    """
    def __init__(self):
        self.game_loader: storageManager.game_load.GameLoader = storageManager.game_load.GameLoader()
        self.audio_player: AudioPlayer = AudioPlayer()
        self.recogniser: myGestureRecognizer.VideoGestureRecogniser = myGestureRecognizer.VideoGestureRecogniser()

    def play_game(self, game_path: str):
        try:
            root_node, game_folder = self.game_loader.load_graph(game_path)
        except Exception as e:
            print(f"Failed to load graph from file: {e}")
            return

        self._start_game_loop(root_node, game_folder)

    def _start_game_loop(self, start_node: Node, game_folder: str):
        """
        Throws TimeoutError if no gesture is detected within TIMEOUT_TIME seconds.
        """
        cur_node: Node = start_node
        while True:
            # Play current scene audio
            self.audio_player.play_audio(game_folder, cur_node.get_id())

            # Ask recognizer for a decision (expects a tuple like ("ILoveYou", "Left"))
            decision: EnumGesture = self.recogniser.get_gesture(cur_node.get_possible_gestures() + ALWAYS_GESTURES)
            if decision == EnumGesture.Victory:
                break

            while decision in ALWAYS_GESTURES:
                if decision == EnumGesture.PointingUp_Left:
                    self.audio_player.play_main_audio(game_folder, cur_node.get_id())
                elif decision == EnumGesture.PointingUp_Right:
                    self.audio_player.play_options_audio(game_folder, cur_node.get_id())

                decision: EnumGesture = self.recogniser.get_gesture(cur_node.get_possible_gestures() + ALWAYS_GESTURES)


            cur_node = cur_node.getNode(decision)

            if cur_node.is_win:
                self.audio_player.play_audio(game_folder, cur_node.get_id())
                self.audio_player.play_win_audio(game_folder)
                break
            if cur_node.is_losing:
                self.audio_player.play_audio(game_folder, cur_node.get_id())
                self.audio_player.play_lose_audio(game_folder)
                break

            time.sleep(2)
