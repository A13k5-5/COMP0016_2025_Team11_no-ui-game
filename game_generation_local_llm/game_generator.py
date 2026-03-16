import os

from openvino_genai import LLMPipeline

from graph.serial_graph import SerialGraph
from game_generation_local_llm.graph_blueprint.blueprint import GraphBlueprint
from game_generation_local_llm.graph_blueprint.blueprint_generator import BlueprintGenerator
from game_generation_local_llm.story_generator.story_generator import StoryGenerator


class GameGenerator:
    def __init__(self):
        model_path: str = os.path.join(os.path.dirname(__file__), "models", "TinyLlama-1.1B-Chat-v1.0_ov")
        self.pipe: LLMPipeline = LLMPipeline(model_path, "GPU")
        self.blueprint_generator: BlueprintGenerator = BlueprintGenerator(self.pipe)
        self.game_generator: StoryGenerator = StoryGenerator(self.pipe)

    def generate_game(self, prompt: str, blueprint: GraphBlueprint = None) -> SerialGraph:
        """
        Generates the game graph based on users prompt. If the blueprint not provided,
        it will be generated based on the prompt.
        :param prompt:
        :param blueprint:
        :return:
        """
        # sanitise blueprint
        if blueprint is None:
            blueprint: GraphBlueprint = self.blueprint_generator.generate_blueprint(prompt)

        story: SerialGraph = self.game_generator.generate_game(prompt, blueprint)
        return story
