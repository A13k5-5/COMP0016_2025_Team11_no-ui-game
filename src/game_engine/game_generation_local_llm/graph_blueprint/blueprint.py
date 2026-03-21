from pydantic import BaseModel

from src.graph import EnumLR
from src.graph.serial_graph import SerialGraph


class GraphBlueprint(BaseModel):
    """
    A pre-planned adjacency map for the entire graph, produced before node generation.

    :arg adjacency: Keys are node IDs (0 … N-1).  Values map the two gesture keys to the id of the next node.
    Win/lose nodes signal a terminal state by mapping both gestures back to themselves.
    """
    adjacency: dict[int, dict[EnumLR, int]]
    win_nodes: list[int]
    lose_nodes: list[int]

    def sanitize_references(self):
        """
        Normalize adjacency so every node has both LEFT/RIGHT edges and every target points
        to an existing node. Missing/invalid targets fall back to a self-loop.
        """
        # Allowed target IDs are the nodes that actually exist in this blueprint.
        valid_nodes: set[int] = set(self.adjacency.keys())

        normalized_adjacency: dict[int, dict[EnumLR, int]] = {}
        for node_id, node_adjacency in self.adjacency.items():
            normalized_node: dict[EnumLR, int] = {}

            # Force a complete 2-choice map (RIGHT then LEFT) for every node.
            for side in (EnumLR.RIGHT, EnumLR.LEFT):
                target_node: int | None = node_adjacency.get(side)
                if target_node is None:
                    # If LLM omitted a side, keep graph playable with a self-loop.
                    normalized_node[side] = node_id
                    continue
                if target_node not in valid_nodes:
                    # Prevent dangling references (e.g., edge to a non-existent node ID).
                    normalized_node[side] = node_id
                    continue

                normalized_node[side] = target_node

            normalized_adjacency[node_id] = normalized_node

        # Replace raw adjacency with sanitized adjacency used downstream.
        self.adjacency = normalized_adjacency

    def convert_to_serial_graph(self) -> SerialGraph:
        """
        Placeholder serial graph.
        :return:
        """
        pass
