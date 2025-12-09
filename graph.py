class Node:
    def __init__(self, text: str):
        self.text = text
        self.adjacencyList: dict[tuple[str, str], str] = {}

    def addNode(self, gesture: tuple[str, str], newNode):
        self.adjacencyList[gesture] = newNode

    def getNode(self, gesture: tuple[str, str]):
        return self.adjacencyList[gesture]

    def __str__(self):
        return self.text
