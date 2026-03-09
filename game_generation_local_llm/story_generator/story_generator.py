import json

from openvino_genai import GenerationConfig, LLMPipeline, StructuredOutputConfig, ChatHistory

from graph.serial_graph import SerialGraph
from game_generation_local_llm.story_generator.prompts import SYS_MESSAGE
from game_generation_local_llm.graph_blueprint.blueprint import GraphBlueprint


class StoryGenerator:
    def __init__(self, llm: LLMPipeline):
        self.llm: LLMPipeline = llm
        self.config: GenerationConfig = GenerationConfig()
        self.history: ChatHistory = ChatHistory()

    def _build_config(self):
        self.config: GenerationConfig = GenerationConfig()
        self.config.do_sample = True
        self.config.temperature = 0.8
        self.config.structured_output_config = StructuredOutputConfig(
            json_schema=json.dumps(SerialGraph.model_json_schema())
        )

    def _build_history(self, user_prompt: str, game_blueprint: GraphBlueprint):
        blueprint_json: str = game_blueprint.model_dump_json(indent=2)
        full_prompt: str = (
            f"BLUEPRINT:\n{blueprint_json}\n\n"
            f"THEME:\n{user_prompt}"
        )
        self.history: ChatHistory = ChatHistory()
        self.history.append({"role": "system", "content": SYS_MESSAGE})
        self.history.append({"role": "user", "content": full_prompt})

    def generate_game(self, user_prompt: str, game_blueprint: GraphBlueprint) -> SerialGraph:
        self._build_config()
        self._build_history(user_prompt, game_blueprint)

        decoded_results = self.llm.generate(self.history, self.config)
        generated_graph: SerialGraph = SerialGraph.model_validate_json(decoded_results.texts[0])
        sanitised_graph: SerialGraph = self._sanitise_generated_graph(generated_graph)
        return sanitised_graph

    def _sanitise_generated_graph(self, graph: SerialGraph) -> SerialGraph:
        """
        Checks that every node referenced in adjacency lists actually exists in the graph.
        Any reference to a non-existent node is replaced with a self-loop (the node's own ID).
        """
        existing_ids = set(graph.nodes.keys())
        for node_id, node in graph.nodes.items():
            node.adjacency_list = {
                gesture: target if target in existing_ids else node_id
                for gesture, target in node.adjacency_list.items()
            }
        return graph
