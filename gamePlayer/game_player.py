import time

from gamePlayer.audio_player import AudioPlayer
from graph import Node
import myGestureRecognizer

from gesture import EnumGesture
import storageManager.game_load


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
            # Display current scene and available choices (explicit about handedness)
            print("\n" + cur_node.getText() + "\n")

            self._list_options(cur_node)
            
            # Play current scene audio
            self.audio_player.play_audio(game_folder, cur_node.get_id())

            # Ask recognizer for a decision (expects a tuple like ("ILoveYou", "Left"))
            decision: EnumGesture = self.recogniser.get_gesture(cur_node.get_possible_gestures())
            if decision == EnumGesture.Victory:
                break

            cur_node = cur_node.getNode(decision)

            time.sleep(2)

    def _list_options(self, cur_node: Node):
        options = list(cur_node.adjacencyList.items())
        print("Choices (perform a gesture with the shown hand):")
        for idx, (gesture, node) in enumerate(options, start=1):
            # show a short preview of the destination and the required handedness
            print(f" {idx}. Gesture: {gesture.__str__()} -> {node.getText().split('.')[0]}")
