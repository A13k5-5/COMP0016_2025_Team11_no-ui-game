from graph import Node
from myGestureRecognizer import VideoGestureRecogniser
from storageManager import StorageManager
import time

if __name__ == "__main__":
    graph_file = "graph.json"
    storage_manager = StorageManager()

    try:
        root_node = storage_manager.load_graph(graph_file)
        print("Graph loaded from file.")
    except Exception as e:
        print(f"Failed to load graph from file: {e}")

    curNode: Node = root_node
    print(root_node)
    recogniser: VideoGestureRecogniser = VideoGestureRecogniser()

    while True:
        # Display current scene and available choices (explicit about handedness)
        print("\n" + curNode.getText() + "\n")
        # Build readable option list for console preview
        options = list(curNode.adjacencyList.items())
        print("Choices (perform `ILoveYou` gesture with the shown hand):")
        for idx, (key, node) in enumerate(options, start=1):
            gesture, handedness = key
            # show a short preview of the destination and the required handedness
            print(f" {idx}. Hand: {handedness} -> {node._text.split('.')[0]}")

        # Ask recognizer for a decision (expects a tuple like ("ILoveYou", "Left"))
        decision = recogniser.get_gesture(list(curNode.adjacencyList.keys()))
        print(f"_______________Recognised gesture: {decision}")

        if not decision:
            print("Unrecognised input from recogniser. Please try again.")
            continue

        next_node = curNode.getNode(decision)
        if not next_node:
            print("That gesture/hand combination is not valid here. Try again.")
            continue

        curNode = next_node
        time.sleep(3)
