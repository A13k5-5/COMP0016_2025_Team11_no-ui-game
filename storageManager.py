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

if __name__ == "__main__":
    storage_manager = StorageManager()
    root = Node("Root Node")
    child1 = Node("Child Node 1")
    child2 = Node("Child Node 2")
    root.addNode(("Gesture1", "Left"), child1)
    root.addNode(("Gesture2", "Right"), child2)
    child1.addNode(("Gesture3", "Left"), root)
    storage_manager.save_graph(root, "graph.json")
