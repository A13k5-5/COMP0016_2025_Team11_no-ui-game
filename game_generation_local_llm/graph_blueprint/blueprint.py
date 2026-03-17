from pydantic import BaseModel

from graph import EnumLR


class GraphBlueprint(BaseModel):
    """
    A pre-planned adjacency map for the entire graph, produced before node generation.

    :arg adjacency: Keys are node IDs (0 … N-1).  Values map the two gesture keys to the id of the next node.
    Win/lose nodes signal a terminal state by mapping both gestures back to themselves.
    """
    adjacency: dict[int, dict[EnumLR, int]]
    win_nodes: list[int]
    lose_nodes: list[int]
