from typing import Self
from graph.enum_LR import EnumLR


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
        self.adjacencyList: dict[EnumLR, Node] = {}
        self.is_win: bool = False
        self.is_losing: bool = False

    @staticmethod
    def get_main_text_audio_filename(node_id: int) -> str:
        return f"node_{node_id}.wav"

    @staticmethod
    def get_options_audio_filename(node_id: int) -> str:
        return f"node_{node_id}_options.wav"

    def getText(self):
        return self._text

    def get_id(self) -> int:
        return self.id

    def addNode(self, side: EnumLR, newNode: Self):
        self.adjacencyList[side] = newNode

    def getNode(self, side: EnumLR):
        return self.adjacencyList.get(side)

    def get_possible_sides(self) -> list[EnumLR]:
        return [side for side, node in self.adjacencyList.items() if node is not None]

    def __str__(self):
        return f"{self._text}, adjacent to {[node._text for node in self.adjacencyList.values()]}"
