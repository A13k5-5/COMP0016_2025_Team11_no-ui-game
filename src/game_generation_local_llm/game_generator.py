import os
from typing import Any, Callable

from openvino_genai import LLMPipeline

from src.graph.serial_graph import SerialGraph
from src.game_generation_local_llm.graph_blueprint.blueprint import GraphBlueprint
from src.game_generation_local_llm.graph_blueprint.blueprint_generator import BlueprintGenerator
from src.game_generation_local_llm.story_generator.story_generator import StoryGenerator


class GameGenerator:
    def __init__(self):
        model_path: str = os.path.join(os.path.dirname(__file__), "models", "model_path")
        self.pipe: LLMPipeline = LLMPipeline(model_path, "CPU")
        self.blueprint_generator: BlueprintGenerator = BlueprintGenerator(self.pipe)
        self.game_generator: StoryGenerator = StoryGenerator(self.pipe)

    @staticmethod
    def _emit_progress(progress_cb: Callable[[dict[str, Any]], None] | None, **payload: Any) -> None:
        if progress_cb is not None:
            progress_cb(payload)

    def generate_game(
        self,
        prompt: str,
        blueprint: GraphBlueprint = None,
        progress_cb: Callable[[dict[str, Any]], None] | None = None,
    ) -> SerialGraph:
        """
        Generates the game graph based on users prompt. If the blueprint not provided,
        it will be generated based on the prompt.
        :param prompt:
        :param blueprint:
        :return:
        """
        self._emit_progress(progress_cb, stage="started", message="Starting game generation")

        try:
            if blueprint is None:
                self._emit_progress(progress_cb, stage="blueprint_started", message="Generating blueprint")
                blueprint = self.blueprint_generator.generate_blueprint(prompt, progress_cb=progress_cb)

            self._emit_progress(
                progress_cb,
                stage="story_started",
                message="Generating story nodes",
                nodes_total=len(blueprint.adjacency),
            )

            story: SerialGraph = self.game_generator.generate_game(prompt, blueprint, progress_cb=progress_cb)

            self._emit_progress(
                progress_cb,
                stage="completed",
                message="Generation complete",
                nodes_total=len(story.nodes),
            )
            return story
        except Exception as exc:
            self._emit_progress(progress_cb, stage="error", message=str(exc))
            raise
