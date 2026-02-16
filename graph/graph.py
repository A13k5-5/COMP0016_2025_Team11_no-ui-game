from gesture import EnumGesture


class Node:
    def __init__(self, text: str):
        self.id: int = id(self)
        self._text = text
        self.audioPath = None
        self.adjacencyList: dict[EnumGesture, Node] = {}

    def getText(self):
        return self._text

    def get_id(self) -> int:
        return self.id

    def addNode(self, gesture: EnumGesture, newNode: 'Node'):
        self.adjacencyList[gesture] = newNode

    def getNode(self, gesture: EnumGesture):
        return self.adjacencyList.get(gesture)

    def __str__(self):
        return f"{self._text}, adjacent to {[node._text for node in self.adjacencyList.values()]}"
