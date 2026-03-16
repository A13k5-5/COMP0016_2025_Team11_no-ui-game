import json

from openvino_genai import GenerationConfig, LLMPipeline, StructuredOutputConfig, ChatHistory

from .blueprint import GraphBlueprint
from .prompts import BLUEPRINT_MESSAGE

class BlueprintGenerator:
    """
    Before generating the game itself, blueprint of the game is created. This is
    a pre-planned adjacency map of the entire graph of the game.
    """
    def __init__(self, llm: LLMPipeline):
        self.llm: LLMPipeline = llm
        self.config: GenerationConfig = GenerationConfig()
        self.history: ChatHistory = ChatHistory()

    def _build_config(self):
        self.config: GenerationConfig = GenerationConfig()
        self.config.do_sample = True
        self.config.temperature = 0.7
        self.config.structured_output_config = StructuredOutputConfig(
            json_schema=json.dumps(GraphBlueprint.model_json_schema())
        )

    def _build_history(self, user_prompt: str):
        self.history: ChatHistory = ChatHistory()
        self.history.append({"role": "system", "content": BLUEPRINT_MESSAGE})
        self.history.append({"role": "user", "content": user_prompt})

    def generate_blueprint(self, user_prompt: str) -> GraphBlueprint:
        self._build_config()
        self._build_history(user_prompt)

        decoded_results = self.llm.generate(self.history, self.config)
        print(decoded_results.texts[0])
        generated_blueprint: GraphBlueprint = GraphBlueprint.model_validate_json(decoded_results.texts[0])
        return generated_blueprint
