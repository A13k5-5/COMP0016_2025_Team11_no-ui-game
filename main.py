import time

from graph import Node
from myGestureRecognizer.gestureRecogniserRefactor import GestureRecognizerApp

if __name__ == "__main__":
    start = Node("Start of the game. Make decision and move.")
    leftDecision: Node = Node("ups, you died")
    rightDecision: Node = Node("you win. yey.")

    start.addNode(("ILoveYou", "Left"), leftDecision)
    start.addNode(("ILoveYou", "Right"), rightDecision)

    rightDecision.addNode(("ILoveYou", "Right"), start)

    curNode: Node = start
    recogniser: GestureRecognizerApp = GestureRecognizerApp()
    while True:
        print(curNode.text)
        print(f"Pick a decision: {[node.text for node in curNode.adjacencyList.values()]}: ")
        decision = recogniser.run()
        curNode = curNode.getNode(decision)
        time.sleep(5)
