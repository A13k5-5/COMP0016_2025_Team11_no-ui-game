class Node:
    def __init__(self, text: str):
        self._text = text
        self.adjacencyList: dict[tuple[str, str], Node] = {}

    def getText(self):
        return self._text

    def addNode(self, gesture: tuple[str, str], newNode):
        self.adjacencyList[gesture] = newNode

    def getNode(self, gesture: tuple[str, str]):
        return self.adjacencyList.get(gesture)

    def __str__(self):
        return self._text
