import json
from threading import Event
from typing import Any, Callable

from openvino_genai import GenerationConfig, LLMPipeline, StructuredOutputConfig, ChatHistory

from src.game_engine.game_generation_local_llm.generation_control import raise_if_cancelled
from src.graph.serial_graph import SerialGraph
from src.graph.serial_node import SerialNode
from src.game_engine.game_generation_local_llm.story_generator.prompts import SYS_MESSAGE, NODE_USER_MESSAGE
from src.game_engine.game_generation_local_llm.graph_blueprint.blueprint import GraphBlueprint


class StoryGenerator:
    def __init__(self, llm: LLMPipeline):
        self.llm: LLMPipeline = llm

    @staticmethod
    def _emit_progress(progress_cb: Callable[[dict[str, Any]], None] | None, **payload: Any) -> None:
        if progress_cb is not None:
            progress_cb(payload)

    def _build_node_config(self) -> GenerationConfig:
        config: GenerationConfig = GenerationConfig()
        config.do_sample = True
        config.temperature = 0.8
        config.structured_output_config = StructuredOutputConfig(
            json_schema=json.dumps(SerialNode.model_json_schema())
        )
        return config

    def _build_node_history(self, node_id: int, adjacency: dict[int, int], is_win: bool, is_losing: bool, theme: str, generated_nodes: dict[int, SerialNode]) -> ChatHistory:
        context: str = (
            "\n".join(node.model_dump_json() for node in generated_nodes.values())
            if generated_nodes
            else "None yet."
        )
        user_message: str = NODE_USER_MESSAGE.format(
            theme=theme,
            node_id=node_id,
            adjacency=json.dumps(adjacency),
            is_win=is_win,
            is_losing=is_losing,
            context=context,
        )
        history: ChatHistory = ChatHistory()
        history.append({"role": "system", "content": SYS_MESSAGE})
        history.append({"role": "user", "content": user_message})
        return history

    def generate_game(
        self,
        user_prompt: str,
        game_blueprint: GraphBlueprint,
        progress_cb: Callable[[dict[str, Any]], None] | None = None,
        cancel_event: Event | None = None,
    ) -> SerialGraph:
        config: GenerationConfig = self._build_node_config()
        generated_nodes: dict[int, SerialNode] = {}
        nodes_total = len(game_blueprint.adjacency)

        # generate each node one-by-one
        for index, (node_id, adjacency) in enumerate(game_blueprint.adjacency.items(), start=1):
            raise_if_cancelled(cancel_event, progress_cb)
            is_win: bool = node_id in game_blueprint.win_nodes
            is_losing: bool = node_id in game_blueprint.lose_nodes

            self._emit_progress(
                progress_cb,
                stage="node_started",
                message=f"Generating node {node_id}",
                node_id=node_id,
                nodes_done=index - 1,
                nodes_total=nodes_total,
            )

            history: ChatHistory = self._build_node_history(
                node_id=node_id,
                adjacency=adjacency,
                is_win=is_win,
                is_losing=is_losing,
                theme=user_prompt,
                generated_nodes=generated_nodes,
            )

            decoded_results = self.llm.generate(history, config)
            raise_if_cancelled(cancel_event, progress_cb)
            serial_node: SerialNode = SerialNode.model_validate_json(decoded_results.texts[0])

            # Enforce blueprint adjacency and terminal/win/lose flags
            serial_node.id = node_id
            serial_node.adjacency_list = adjacency
            serial_node.is_win = is_win
            serial_node.is_losing = is_losing
            if is_win or is_losing:
                serial_node.left_option = ""
                serial_node.right_option = ""

            generated_nodes[node_id] = serial_node
            print(serial_node.model_dump_json(indent=2))

            self._emit_progress(
                progress_cb,
                stage="node_ready",
                message=f"Generated node {node_id}",
                node_id=node_id,
                nodes_done=index,
                nodes_total=nodes_total,
                node=serial_node,
            )


        return SerialGraph(nodes=generated_nodes)
