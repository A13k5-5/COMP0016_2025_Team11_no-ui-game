from myTypes import Gesture


class Node:
    def __init__(self, text: str):
        self.id = id(self)
        self._text = text
        self.adjacencyList: dict[Gesture, Node] = {}

    def getText(self):
        return self._text

    def addNode(self, gesture: Gesture, newNode):
        self.adjacencyList[gesture] = newNode

    def getNode(self, gesture: Gesture):
        return self.adjacencyList.get(gesture)

    def __str__(self):
        return f"{self._text}, adjacent to {[node._text for node in self.adjacencyList.values()]}"
