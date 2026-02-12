from playsound3 import playsound
import time

from graph import Node
import myGestureRecognizer
import storageManager

from gesture import Gesture


class GamePlayer:
    """
    Class to play the interactive story game.
    """
    def __init__(self):
        self.game_loader: storageManager.GameLoader = storageManager.GameLoader()
        self.recogniser: myGestureRecognizer.VideoGestureRecogniser = myGestureRecognizer.VideoGestureRecogniser()

    def _playAudio(self, audioPath: str):
        """
        Play the audio file.
        """
        try:
            playsound(audioPath)
        except Exception as e:
            print(f"Error playing audio file {audioPath}: {e}")

    def playGame(self, gameFilePath: str):
        try:
            root_node: Node = self.game_loader.load_graph(gameFilePath)
        except Exception as e:
            print(f"Failed to load graph from file: {e}")
            return

        self._startGameLoop(root_node)

    def _startGameLoop(self, startNode: Node):
        """
        Throws TimeoutError if no gesture is detected within TIMEOUT_TIME seconds.
        """
        curNode: Node = startNode
        while True:
            # Display current scene and available choices (explicit about handedness)
            print("\n" + curNode.getText() + "\n")

            self._listOptions(curNode)
            
            # Play current scene audio
            self._playAudio(curNode.audioPath)

            # Ask recognizer for a decision (expects a tuple like ("ILoveYou", "Left"))
            decision: Gesture = self.recogniser.get_gesture(list(curNode.adjacencyList.keys()))
            curNode = curNode.getNode(decision)

            time.sleep(3)

    def _listOptions(self, curNode: Node):
        options = list(curNode.adjacencyList.items())
        print("Choices (perform a gesture with the shown hand):")
        for idx, (gesture, node) in enumerate(options, start=1):
            # show a short preview of the destination and the required handedness
            print(f" {idx}. Gesture: {gesture.gesture} Hand: {gesture.handedness} -> {node.getText().split('.')[0]}")
