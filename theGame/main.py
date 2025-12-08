from graph import Node

if __name__ == "__main__":
    start = Node("Start of the game. Make decision and move.")
    leftDecision: Node = Node("ups, you died")
    rightDecision: Node = Node("you win. yey.")

    start.addNode(leftDecision)
    start.addNode(rightDecision)

    curNode: Node = start
    while True:
        print(curNode.text)
        decision = int(input(f"Pick a decision: {[node.text for node in curNode.adjacencyList]}: "))
        curNode = curNode.getNode(decision)
