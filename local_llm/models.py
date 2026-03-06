"""
Pydantic models shared across the local LLM pipeline.
"""
from pydantic import BaseModel, Field

from enum_gesture import EnumGesture


class SerialNode(BaseModel):
    id: int
    text: str
    left_option: str = ""
    right_option: str = ""
    adjacency_list: dict[EnumGesture, int]
    is_win: bool = False


class SerialGraph(BaseModel):
    nodes: dict[int, SerialNode]


class NodeQuantities(BaseModel):
    nodes: int = Field(
        ge=2,
        le=100,
        description="The number of nodes in the game.",
    )


class GraphBlueprint(BaseModel):
    """
    A pre-planned adjacency map for the entire graph, produced before node
    content is written.

    Keys are node IDs (0 … N-1).  Values map the two gesture keys
    '0' (right hand) and '1' (left hand) to the id of the next node.
    Leaf nodes signal no outgoing edges by mapping both gestures to -1.
    """
    adjacency: dict[int, dict[str, int]]
    win_nodes: list[int]

