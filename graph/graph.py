from typing import Self
from gesture import EnumGesture
from graph.serial_node import SerialNode


class Node:
    def __init__(self, text: str, left_option: str = "", right_option: str = ""):
        """
        :param text: the narrative text describing the current node (e.g., "You stand before an old manor. The gate is locked.")
        :param left_option: the text describing the left option (e.g., "Enter the shed and search")
        :param right_option: the text describing the right option (e.g., "Follow a winding path that leads back toward the gate")
        """
        self.id: int = id(self)
        self._text = text
        self.left_option = left_option
        self.right_option = right_option
        self.adjacencyList: dict[EnumGesture, Node] = {}
        self.is_win: bool = False
        self.is_losing: bool = False

    def getText(self):
        return self._text

    def get_id(self) -> int:
        return self.id

    def addNode(self, gesture: EnumGesture, newNode: Self):
        self.adjacencyList[gesture] = newNode

    def getNode(self, gesture: EnumGesture):
        return self.adjacencyList.get(gesture)

    def get_possible_gestures(self) -> list[EnumGesture]:
        return [gesture for gesture, node in self.adjacencyList.items() if node is not None]

    def __str__(self):
        return f"{self._text}, adjacent to {[node._text for node in self.adjacencyList.values()]}"

    @classmethod
    def deserialize_node(cls, serial_node: SerialNode) -> Self:
        node: Node = Node(
            serial_node.text,
            serial_node.left_option,
            serial_node.right_option
        )
        node.id = serial_node.id
        node.is_win = serial_node.is_win
        node.is_losing = serial_node.is_losing

        return node

