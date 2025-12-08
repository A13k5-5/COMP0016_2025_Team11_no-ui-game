class Node:
    def __init__(self, text: str, adjacencyList=None):
        if adjacencyList is None:
            adjacencyList = []
        self.text = text
        self.adjacencyList: list[Node] = adjacencyList
