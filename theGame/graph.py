class Node:
    def __init__(self, text: str, adjacencyList=None):
        if adjacencyList is None:
            adjacencyList = []
        self.text = text
        self.adjacencyList: list[Node] = adjacencyList

    def addNode(self, newNode):
        self.adjacencyList.append(newNode)

    def getNode(self, decisionNumber: int):
        return self.adjacencyList[decisionNumber]

    def __str__(self):
        return self.text
