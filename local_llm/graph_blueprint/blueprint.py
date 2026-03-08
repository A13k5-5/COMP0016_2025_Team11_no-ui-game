from pydantic import BaseModel

class GraphBlueprint(BaseModel):
    """
    A pre-planned adjacency map for the entire graph, produced before node generation.

    :arg adjacency: Keys are node IDs (0 … N-1).  Values map the two gesture keys to the id of the next node.
    Leaf nodes signal no outgoing edges by mapping both gestures to -1.
    """
    adjacency: dict[int, dict[int, int]]
    win_nodes: list[int]
