import json
import os
from graph import Node
from text2speech.text2speech import Talker

class StorageManager:
    def save_graph(self, root: Node, filename: str, audio_dir: str = "audio", game_folder: str = "game"):
        # Create audio directory - if it doesnt exist already
        audio_dir = os.path.join(game_folder, audio_dir)

        # Remove old audio files to avoid duplicates
        if os.path.exists(audio_dir):
            for f in os.listdir(audio_dir):
                print(f)
                os.remove(os.path.join(audio_dir, f))
        
        os.makedirs(audio_dir, exist_ok=True)

        graph_path = os.path.join(game_folder, filename)
        with open(graph_path, 'w') as file:
            json.dump(self._serialize_graph(root), file, indent=4)
        
        self._generate_audio(self._serialize_graph(root), audio_dir)

    def _serialize_graph(self, root: Node) -> dict:
        visited = {}

        def dfs(node: Node):
            if node.id in visited:
                return
            visited[node.id] = self._serialize_node(node)
            for adjacent_node in node.adjacencyList.values():
                dfs(adjacent_node)

        dfs(root)
        return visited

    def _serialize_node(self, node: Node) -> dict:
        audio_filename = f"node_{node.id}.wav"
        return {
            "id": node.id,
            "text": node.getText(),
            "audioPath": f"game/audio/{audio_filename}",
            "adjacencyList": {gesture.__str__(): adjacent_node.id for gesture, adjacent_node in node.adjacencyList.items()}
        }

    def load_graph(self, filename: str, game_folder: str = "game") -> Node:
        graph_path = os.path.join(game_folder, filename)
        with open(graph_path, 'r') as file:
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
            node.audioPath = node_data.get("audioPath")
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
    
    def _generate_audio(self, data: dict, audio_dir: str):
        """
        Generate audio files for all nodes in the graph using Talker class.
        """
        talker = Talker()
        description = "A calm and soothing narration voice"

        for node_id, node_data in data.items():
            text = node_data["text"]
            output_file = os.path.join(audio_dir, f"node_{node_id}.wav")

            talker.generate_speech(text, description, output_file)
            
    
    def build_default_story_graph(self) -> Node:
        # Story nodes with clear choice descriptions that reference handedness
        start = Node(
            "You find yourself at the ruined gate of an old manor. Two paths lie ahead:"
            "Options:"
            " - Left: Go through the garden (leads to the shed)."
            " - Right: Go down the cellar stairs (leads to the cellar)."
        )
        garden = Node(
            "You slip through the garden, tangled roses parting around you. Moonlight reveals a hidden tool shed."
            "Options:"
            " - Left: Enter the shed and search (leads to finding a lantern and rope)."
            " - Right: Follow a winding path that leads back toward the gate."
        )
        cellar = Node(
            "You descend the stone stair into a cold cellar. The air smells of dust and old paper; something moves in the corner."
            "Options:"
            " - Left: Retreat and head back toward the gate."
            " - Right: Approach the corner (may reveal an encounter)."
        )
        shed_find = Node(
            "Inside the shed you find a lantern and rope. This may help later."
            "Options:"
            " - Left: Leave the shed and return toward the gate."
            " - Right: Take a different path that leads toward the cellar encounter."
        )
        cellar_encounter = Node(
            "A shadow rustles — a friendly stray dog wags its tail, offering companionship."
            "Options:"
            " - Left: Escort the dog back toward the gate."
            " - Right: Continue on a path that also leads back toward the gate."
        )
        loop_back = Node(
            "The path leads back to the gate. You may choose again."
            "Options:"
            " - Left: Reattempt the gate choices (Left -> garden)."
            " - Right: Reattempt the gate choices (Right -> cellar)."
        )

        # All connections use the same gesture key `ILoveYou`; handedness decides the branch
        start.addNode(("ILoveYou", "Left"), garden)
        start.addNode(("ILoveYou", "Right"), cellar)

        garden.addNode(("ILoveYou", "Left"), shed_find)
        garden.addNode(("ILoveYou", "Right"), loop_back)

        cellar.addNode(("ILoveYou", "Left"), loop_back)
        cellar.addNode(("ILoveYou", "Right"), cellar_encounter)

        shed_find.addNode(("ILoveYou", "Left"), loop_back)
        shed_find.addNode(("ILoveYou", "Right"), cellar_encounter)

        cellar_encounter.addNode(("ILoveYou", "Left"), loop_back)
        cellar_encounter.addNode(("ILoveYou", "Right"), loop_back)

        loop_back.addNode(("ILoveYou", "Left"), start)
        loop_back.addNode(("ILoveYou", "Right"), start)

        return start

    def test_game(self):
        root = Node("Start")
        nodeA = Node("Node A")
        nodeB = Node("Node B")
        root.addNode(("ILoveYou", "Left"), nodeA)
        root.addNode(("ILoveYou", "Right"), nodeB)
        
        return root


if __name__ == "__main__":
    storage_manager = StorageManager()

    # load demo game graph
    root = storage_manager.test_game()
    storage_manager.save_graph(root, "graph.json")

    loaded_root = storage_manager.load_graph("graph.json")
    print(loaded_root)
    print(loaded_root.adjacencyList)
    print(loaded_root.adjacencyList[("ILoveYou", "Left")])
    print(loaded_root.adjacencyList[("ILoveYou", "Right")])
