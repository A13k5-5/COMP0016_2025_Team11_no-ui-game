import json
from threading import Event
from typing import Any, Callable

from openvino_genai import GenerationConfig, LLMPipeline, StructuredOutputConfig, ChatHistory

from src.game_generation_local_llm.generation_control import raise_if_cancelled
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

    @staticmethod
    def _emit_progress(progress_cb: Callable[[dict[str, Any]], None] | None, **payload: Any) -> None:
        if progress_cb is not None:
            progress_cb(payload)

    def generate_blueprint(
        self,
        user_prompt: str,
        progress_cb: Callable[[dict[str, Any]], None] | None = None,
        cancel_event: Event | None = None,
    ) -> GraphBlueprint:

        raise_if_cancelled(cancel_event, progress_cb)
        self._build_config()
        self._build_history(user_prompt)
        self._emit_progress(progress_cb, stage="blueprint_started", message="Generating blueprint structure")

        # decoded_results = self.llm.generate(self.history, self.config)
        # print(decoded_results.texts[0])
        # generated_blueprint: GraphBlueprint = GraphBlueprint.model_validate_json(decoded_results.texts[0])
        # generated_blueprint.sanitize_references()

        # stubbed generated blueprint
        adjacency = {
                        "0":  {"0": 1,  "1": 3},
                        "1":  {"0": 2,  "1": 2},
                        "2":  {"0": 2,  "1": 2},
                        "3":  {"0": 3,  "1": 3}
        }

        generated_blueprint: GraphBlueprint = GraphBlueprint(adjacency=adjacency, win_nodes=[3], lose_nodes=[2])

        raise_if_cancelled(cancel_event, progress_cb)
        self._emit_progress(
            progress_cb,
            stage="blueprint_ready",
            message="Blueprint generated",
            nodes_total=len(generated_blueprint.adjacency),
            blueprint=generated_blueprint,
        )
        return generated_blueprint
