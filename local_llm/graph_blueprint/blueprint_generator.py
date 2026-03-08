from openvino_genai import GenerationConfig, LLMPipeline, StructuredOutputConfig, ChatHistory

class BlueprintGenerator:
    """
    Before generating the game itself, blueprint of the game is created. This is
    a pre-planned adjacency map of the entire graph of the game.
    """
    def __init__(self, llm: LLMPipeline):
        self.llm: LLMPipeline = llm
        self.config: GenerationConfig = GenerationConfig()
        self.history: ChatHistory = ChatHistory()

    def generate_blueprint(self, task_description):
        pass
