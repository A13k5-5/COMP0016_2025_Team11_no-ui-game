from pydantic import BaseModel
from typing import Self

from graph import Node
from graph.serial_node import SerialNode


class SerialGraph(BaseModel):
    nodes: dict[int, SerialNode]

    @classmethod
    def serialize_graph(cls, root: Node) -> Self:
        """
        Serializes the graph starting from the root node using DFS. Each node is stored in a dictionary with its ID as
        the key and its details (text, audio path, adjacency list) as the value. The adjacency list is represented as a
        dictionary mapping gesture strings to adjacent node IDs.
        :param root:
        :return: dictionary of serialized nodes
        """
        serial_graph: SerialGraph = SerialGraph(nodes={})

        def dfs(node: Node):
            if node.get_id() in serial_graph.nodes:
                return
            serial_graph.nodes[node.get_id()] = SerialNode.serialize_node(node)
            for adjacent_node in node.adjacencyList.values():
                dfs(adjacent_node)

        dfs(root)
        return serial_graph
