from typing import Self

from pydantic import BaseModel

from gesture import EnumGesture
from graph import Node


class SerialNode(BaseModel):
    id: int
    text: str
    left_option: str = ""
    right_option: str = ""
    adjacency_list: dict[EnumGesture, int]
    is_win: bool = False
    is_losing: bool = False

    @classmethod
    def serialize_node(cls, node: Node) -> Self:
        """
        Serializes a single node into a dictionary format, including its text, audio path, and adjacency list.
        :param node: node to be serialised
        :return: serialised node as a dictionary
        """
        return SerialNode(
            id=node.get_id(),
            text=node.getText(),
            left_option=node.left_option,
            right_option=node.right_option,
            adjacency_list={gesture: adjacent_node.get_id() for
                            gesture, adjacent_node in
                            node.adjacencyList.items()},
            is_win=node.is_win
        )
