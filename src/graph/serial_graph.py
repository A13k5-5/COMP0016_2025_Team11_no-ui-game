from pydantic import BaseModel
from typing import Self

from src.graph import Node
from src.graph.serial_node import SerialNode


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

    @classmethod
    def deserialize_graph(cls, serial_graph: Self) -> Node:
        root, nodes = SerialGraph._load_nodes(serial_graph)
        SerialGraph._establish_connections(serial_graph, nodes)

        return root

    @classmethod
    def _load_nodes(cls, serial_graph: Self) -> tuple[Node, dict[int, Node]]:
        """
        Load nodes without connections. Gives back the root node and a dictionary of all nodes.
        :param serial_graph:
        :return:
        """
        root: Node | None = None
        nodes: dict[int, Node] = {}
        for node_id, serial_node in serial_graph.nodes.items():
            node: Node = SerialNode.deserialize_node(serial_node)

            nodes[node.id] = node
            if root is None:
                root = node
        return root, nodes

    @classmethod
    def _establish_connections(cls, serial_graph: Self, nodes: dict[int, Node]) -> None:
        """
        Establish connections between nodes based on adjacency lists. Makes sure that all the nodes have their adjacency
        lists properly filled in, so that the game can be played.
        :param serial_graph:
        :param nodes:
        """
        for node_id, serial_node in serial_graph.nodes.items():
            node = nodes[int(node_id)]
            for side, adjacent_node_id in serial_node.adjacency_list.items():
                adjacent_node = nodes[int(adjacent_node_id)]
                node.addNode(side, adjacent_node)
