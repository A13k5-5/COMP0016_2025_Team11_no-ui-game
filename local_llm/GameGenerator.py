import json

from openvino_genai import GenerationConfig, LLMPipeline, StructuredOutputConfig, ChatHistory

from graph.serial_graph import SerialGraph
from local_llm.prompts import SYS_MESSAGE


class GameGenerator:
    def __init__(self, llm: LLMPipeline):
        self.llm: LLMPipeline = llm
        self.config: GenerationConfig = GenerationConfig()
        # self.config.structured_output_config = StructuredOutputConfig(
        #     json_schema=json.dumps(SerialGraph.model_json_schema())
        # )
        self.history: ChatHistory = ChatHistory()

    def generate_game(self, user_prompt: str) -> str:
        history = ChatHistory()
        history.append({"role": "system", "content": SYS_MESSAGE})

        self.config.structured_output_config = StructuredOutputConfig(
            json_schema=json.dumps(SerialGraph.model_json_schema())
        )
        self.config.do_sample = True
        self.config.temperature = 0.8

        history.append({"role": "user", "content": user_prompt})

        decoded_results = self.llm.generate(history, self.config)
        json_response = decoded_results.texts[0]
        return json_response
