"""
GameGenerator: orchestrates the full three-step LLM pipeline.

  Step 1 – NodeQuantityResolver  →  decide how many nodes to create
  Step 2 – BlueprintGenerator    →  plan the full directed-graph structure
  Step 3 – NodeContentWriter     →  write story content for every node
"""
import json

from openvino_genai import GenerationConfig, LLMPipeline, \
    StructuredOutputConfig, ChatHistory

from models import NodeQuantities, SerialNode, GraphBlueprint
from prompts import (
    SYS_QUANTITIES,
    SYS_NODE_WRITER,
    NODE_WRITER_PRIMER,
    build_node_prompt,
)
from blueprint_generator import BlueprintGenerator


class NodeQuantityResolver:
    """
    Step 1: given a free-text description, ask the LLM how many nodes the
    game should have.
    """

    def __init__(self, pipe: LLMPipeline) -> None:
        self._pipe = pipe

    def resolve(self, user_prompt: str) -> int:
        """Return the number of nodes (always ≥ 2)."""
        history: ChatHistory = ChatHistory()
        history.append({"role": "system", "content": SYS_QUANTITIES})
        history.append({"role": "user", "content": user_prompt})

        config = GenerationConfig()
        config.do_sample = False
        # this action should be almost deterministic
        config.temperature = 0.0
        config.structured_output_config = StructuredOutputConfig(
            json_schema=json.dumps(NodeQuantities.model_json_schema())
        )

        result = self._pipe.generate(history, config)
        parsed = json.loads(result.texts[0])
        return max(2, parsed["nodes"])


class NodeContentWriter:
    """
    Step 3: given a blueprint and a story theme, generate a :class:`SerialNode`
    JSON object for every node in order.

    The full conversation history is kept across nodes so the model can
    maintain story consistency.
    """

    def __init__(self, pipe: LLMPipeline) -> None:
        self._pipe = pipe

    def write_all(
        self,
        total_num_nodes: int,
        user_prompt: str,
        blueprint: GraphBlueprint,
        temperature: float = 0.8,
    ) -> list[SerialNode]:
        """
        Generate story content for every node and return a list of raw
        SerialNode dicts in node-id order.

        :param total_num_nodes: exact node count (must match blueprint).
        :param user_prompt:     original story description from the user.
        :param blueprint:       sanitised :class:`GraphBlueprint` produced by
                                :class:`BlueprintGenerator`.
        :param temperature:     sampling temperature for story generation.
        :returns:               list of raw node dicts (validated against
                                :class:`SerialNode`).
        """
        config = GenerationConfig()
        config.do_sample = True
        config.temperature = temperature
        config.structured_output_config = StructuredOutputConfig(
            json_schema=json.dumps(SerialNode.model_json_schema())
        )

        history: ChatHistory = self._build_initial_history(total_num_nodes, user_prompt)
        generated_nodes: list[SerialNode] = []

        for cur_node_num in range(total_num_nodes):
            node_prompt = build_node_prompt(total_num_nodes, cur_node_num, blueprint)
            history.append({"role": "user", "content": node_prompt})

            result = self._pipe.generate(history, config)
            json_response: str = result.texts[0]

            # Validate against the schema (raises if malformed)
            node: SerialNode = SerialNode.model_validate(json.loads(json_response))
            print(node.model_dump_json(indent=2))

            generated_nodes.append(node)
            history.append({"role": "assistant", "content": json_response})

        return generated_nodes

    def _build_initial_history(
        self, total_num_nodes: int, user_prompt: str
    ) -> ChatHistory:
        history = ChatHistory()
        history.append({
            "role": "system",
            "content": (
                f"{SYS_NODE_WRITER} "
                f"The game has exactly {total_num_nodes} nodes "
                f"(ids 0 to {total_num_nodes - 1})."
            ),
        })
        history.append({"role": "user", "content": f"Story theme: {user_prompt}"})
        history.append({"role": "assistant", "content": NODE_WRITER_PRIMER})
        return history


class GameGenerator:
    """
    High-level facade that wires together all three pipeline steps and
    returns the complete list of generated `SerialGraph`.

    Usage::
        pipe = LLMPipeline(model_dir, "CPU")
        generator = GameGenerator(pipe)
        nodes = generator.generate("A dark fantasy dungeon crawler with 12 nodes")
    """

    def __init__(self, pipe: LLMPipeline) -> None:
        self._pipe = pipe
        self._quantity_resolver = NodeQuantityResolver(pipe)
        self._blueprint_generator = BlueprintGenerator(pipe)
        self._node_writer = NodeContentWriter(pipe)

    def generate(self, user_prompt: str) -> list[SerialNode]:
        """
        Run the full pipeline and return a list of raw node dicts.

        :param user_prompt: free-text description of the game to create.
        :returns:           list of validated SerialNode dicts.
        """
        # Step 1 — how many nodes?
        total_num_nodes = self._quantity_resolver.resolve(user_prompt)
        print(f"[GameGenerator] Nodes to generate: {total_num_nodes}")

        # Step 2 — graph structure
        blueprint: GraphBlueprint = self._blueprint_generator.generate(total_num_nodes, user_prompt)
        print(f"[GameGenerator] Blueprint:\n{blueprint.model_dump_json(indent=2)}")

        # Step 3 — story content
        nodes: list[SerialNode] = self._node_writer.write_all(total_num_nodes, user_prompt, blueprint)
        print(f"[GameGenerator] Generation complete ({len(nodes)} nodes).")

        return nodes
