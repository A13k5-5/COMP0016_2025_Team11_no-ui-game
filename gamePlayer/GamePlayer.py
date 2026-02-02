import myGestureRecognizer
import storageManager
import time

class GamePlayer:
    def __init__(self):
        self.storage_manager = storageManager.StorageManager()
        self.recogniser = myGestureRecognizer.VideoGestureRecogniser()

    def playGame(self, gameFilePath: str):
        try:
            root_node = self.storage_manager.load_graph(gameFilePath)
        except Exception as e:
            print(f"Failed to load graph from file: {e}")
            return

        curNode = root_node

        while True:
            # Display current scene and available choices (explicit about handedness)
            print("\n" + curNode.getText() + "\n")

            self.listOptions(curNode)

            # Ask recognizer for a decision (expects a tuple like ("ILoveYou", "Left"))
            decision = self.recogniser.get_gesture(list(curNode.adjacencyList.keys()))
            print(f"_______________Recognised gesture: {decision}")

            if not decision:
                print("Unrecognised input from recogniser. Please try again.")
                continue

            curNode = curNode.getNode(decision)

            time.sleep(3)

    def listOptions(self, curNode):
        options = list(curNode.adjacencyList.items())
        print("Choices (perform a gesture with the shown hand):")
        for idx, ((gesture, handedness), node) in enumerate(options, start=1):
            # show a short preview of the destination and the required handedness
            print(f" {idx}. Gesture: {gesture} Hand: {handedness} -> {node._text.split('.')[0]}")
