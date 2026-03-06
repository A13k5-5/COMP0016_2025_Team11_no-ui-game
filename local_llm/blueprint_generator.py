"""
BlueprintGenerator: wraps Step 2 of the pipeline — planning the full graph
structure BEFORE any story text is written.
"""
import json

from openvino_genai import GenerationConfig, LLMPipeline, \
    StructuredOutputConfig, ChatHistory

from models import GraphBlueprint
from prompts import SYS_BLUEPRINT, BLUEPRINT_CORRECTION

# Minimum fraction of non-leaf nodes that must have more than one incoming edge.
_MIN_CONVERGENCE_RATIO = 0.3
_MAX_RETRIES = 3


class BlueprintGenerator:
    """
    Generates and sanitises a :class:`GraphBlueprint` for a game of a given
    size.  The blueprint is produced in a single LLM call so the full directed
    graph structure (including converging paths) is planned before any story
    content is written.

    If the model produces a binary-tree / funnel pattern, a corrective follow-up
    is sent (up to :data:`_MAX_RETRIES` times) before falling back to the last
    sanitised result.
    """

    def __init__(self, pipe: LLMPipeline) -> None:
        self._pipe = pipe

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        total_num_nodes: int,
        user_prompt: str,
        temperature: float = 0.7,
    ) -> GraphBlueprint:
        """
        Ask the LLM to produce a graph blueprint, validate convergence, and
        retry with a corrective prompt if the result looks like a binary tree.

        :param total_num_nodes: exact number of nodes the game must have.
        :param user_prompt:     the original story description from the user.
        :param temperature:     sampling temperature for the LLM call.
        :returns:               sanitised :class:`GraphBlueprint`.
        """
        history = self._build_initial_history(total_num_nodes, user_prompt)
        config = self._build_config(temperature)

        blueprint: GraphBlueprint | None = None

        for attempt in range(1, _MAX_RETRIES + 1):
            raw = self._call_llm(history, config)
            blueprint = self._sanitise(raw, total_num_nodes)

            violations = self._convergence_violations(blueprint, total_num_nodes)
            if not violations:
                print(f"[BlueprintGenerator] Valid blueprint on attempt {attempt}.")
                return blueprint

            # Blueprint failed — append the assistant response and a corrective
            # user message, then try again.
            print(
                f"[BlueprintGenerator] Attempt {attempt} failed convergence check: "
                f"{violations}. Sending correction prompt."
            )
            history.append({"role": "assistant", "content": raw.model_dump_json()})
            history.append({
                "role": "user",
                "content": BLUEPRINT_CORRECTION.format(violations="\n".join(f"  - {v}" for v in violations)),
            })

        print("[BlueprintGenerator] Max retries reached; returning best available blueprint.")
        return blueprint

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_initial_history(self, total_num_nodes: int, user_prompt: str) -> ChatHistory:
        history = ChatHistory()
        history.append({"role": "system", "content": SYS_BLUEPRINT})
        history.append({
            "role": "user",
            "content": (
                f"Design a graph blueprint for a {total_num_nodes}-node text adventure. "
                f"Story description: {user_prompt}"
            ),
        })
        return history

    def _build_config(self, temperature: float) -> GenerationConfig:
        config = GenerationConfig()
        config.do_sample = True
        config.temperature = temperature
        config.structured_output_config = StructuredOutputConfig(
            json_schema=json.dumps(GraphBlueprint.model_json_schema())
        )
        return config

    def _call_llm(self, history: ChatHistory, config: GenerationConfig) -> GraphBlueprint:
        result = self._pipe.generate(history, config)
        return GraphBlueprint.model_validate_json(result.texts[0])

    @staticmethod
    def _convergence_violations(blueprint: GraphBlueprint, total_num_nodes: int) -> list[str]:
        """
        Return a list of human-readable violation strings.  An empty list means
        the blueprint passes all convergence checks.
        """
        violations: list[str] = []

        # Count incoming edges for every node.
        incoming: dict[int, int] = {n: 0 for n in range(total_num_nodes)}
        for edges in blueprint.adjacency.values():
            for target in edges.values():
                if target != -1 and target in incoming:
                    incoming[target] += 1

        # Identify leaf nodes (both gestures map to -1).
        leaves = {
            node_id
            for node_id, edges in blueprint.adjacency.items()
            if all(t == -1 for t in edges.values())
        }
        non_leaves = [n for n in range(total_num_nodes) if n not in leaves]

        # Check convergence ratio among non-leaf nodes.
        if non_leaves:
            converging = [n for n in non_leaves if incoming[n] > 1]
            ratio = len(converging) / len(non_leaves)
            if ratio < _MIN_CONVERGENCE_RATIO:
                violations.append(
                    f"Only {len(converging)}/{len(non_leaves)} non-leaf nodes have more than "
                    f"one incoming edge ({ratio:.0%}); at least {_MIN_CONVERGENCE_RATIO:.0%} required. "
                    f"Nodes with multiple incoming edges: {converging}."
                )

        # Detect funnel anti-pattern: a single non-leaf node that receives edges
        # from the majority of other non-leaf nodes.
        if non_leaves:
            max_incoming = max(incoming[n] for n in non_leaves)
            if max_incoming > len(non_leaves) * 0.6:
                funnel_node = max(non_leaves, key=lambda n: incoming[n])
                violations.append(
                    f"Node {funnel_node} receives edges from {incoming[funnel_node]} other nodes "
                    f"({incoming[funnel_node]/len(non_leaves):.0%} of non-leaf nodes) — "
                    "this looks like the forbidden funnel anti-pattern."
                )

        return violations

    @staticmethod
    def _sanitise(blueprint_raw: GraphBlueprint, total_num_nodes: int) -> GraphBlueprint:
        """
        Post-process the raw blueprint to guarantee:

        * Every node id 0 … N-1 appears exactly once as a key in ``adjacency``.
        * No adjacency target is outside the valid range (clamped to -1).
        * At least one win node exists.
        """
        adjacency: dict[int, dict[str, int]] = {}
        for node_id in range(total_num_nodes):
            if node_id in blueprint_raw.adjacency:
                raw_edges: dict = blueprint_raw.adjacency[node_id]
                adjacency[node_id] = {
                    gesture: (
                        target
                        if target == -1 or 0 <= target < total_num_nodes
                        else -1
                    )
                    for gesture, target in raw_edges.items()
                }
            else:
                # Missing node — treat as leaf
                adjacency[node_id] = {"0": -1, "1": -1}

        win_nodes: list[int] = [
            n for n in blueprint_raw.win_nodes
            if 0 <= n < total_num_nodes
        ]
        if not win_nodes:
            win_nodes = [total_num_nodes - 1]

        return GraphBlueprint(adjacency=adjacency, win_nodes=win_nodes)

