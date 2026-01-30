import json
from graph import Node

class StorageManager:
    def save_graph(self, root: Node, filename: str):
        with open(filename, 'w') as file:
            json.dump(self.serialize_graph(root), file, indent=4)

    def serialize_node(self, node: Node) -> dict:
        serialized = {
            "id": node.id,
            "text": node.getText(),
            "adjacencyList": {gesture.__str__(): adjacent_node.id for gesture, adjacent_node in node.adjacencyList.items()}
        }
        return serialized

    def serialize_graph(self, root: Node) -> dict:
        visited = {}

        def dfs(node: Node):
            if node.id in visited:
                return
            visited[node.id] = self.serialize_node(node)
            for adjacent_node in node.adjacencyList.values():
                dfs(adjacent_node)

        dfs(root)
        return visited

    def load_graph(self, filename: str) -> Node:
        with open(filename, 'r') as file:
            data = json.load(file)

        root, nodes = self._load_nodes(data)
        self._establish_connections(data, nodes)

        return root

    def _load_nodes(self, data: dict):
        """
        Load nodes without connections. Gives back the root node and a dictionary of all nodes.
        """
        root: Node | None = None
        nodes = {}
        for node_id, node_data in data.items():
            node = Node(node_data["text"])
            node.id = int(node_id)
            nodes[node.id] = node
            if root is None:
                root = node
        return root, nodes

    def _establish_connections(self, data: dict, nodes: dict[int, Node]):
        """
        Establish connections between nodes based on adjacency lists.
        """
        for node_id, node_data in data.items():
            node = nodes[int(node_id)]
            for gesture_str, adjacent_node_id in node_data["adjacencyList"].items():
                # reconstruct the gesture tuple
                gesture = eval(gesture_str)
                adjacent_node = nodes[int(adjacent_node_id)]
                node.addNode(gesture, adjacent_node)

if __name__ == "__main__":
    storage_manager = StorageManager()
    # root = Node("Root Node")
    # child1 = Node("Child Node 1")
    # child2 = Node("Child Node 2")
    # root.addNode(("Gesture1", "Left"), child1)
    # root.addNode(("Gesture2", "Right"), child2)
    # child1.addNode(("Gesture3", "Left"), root)
    # storage_manager.save_graph(root, "graph.json")
    loaded_root = storage_manager.load_graph("graph.json")
    print(loaded_root)
    print(loaded_root.adjacencyList)
    print(loaded_root.adjacencyList[("Gesture1", "Left")])
    print(loaded_root.adjacencyList[("Gesture2", "Right")])
