"""
BlueprintGenerator: wraps Step 2 of the pipeline — planning the full graph
structure BEFORE any story text is written.
"""
import json
from dataclasses import dataclass, field

from openvino_genai import GenerationConfig, LLMPipeline, \
    StructuredOutputConfig, ChatHistory

from models import GraphBlueprint
from prompts import SYS_BLUEPRINT, BLUEPRINT_CORRECTION

# Minimum fraction of non-leaf nodes that must have more than one incoming edge.
_MIN_CONVERGENCE_RATIO = 0.35
_MAX_FUNNEL_RATIO = 0.6
_MAX_RETRIES = 3


# ---------------------------------------------------------------------------
# Internal data-holder: pre-computed graph metrics used by all checks
# ---------------------------------------------------------------------------

@dataclass
class _BlueprintAnalysis:
    """
    Pre-computes and exposes the structural properties of a :class:`GraphBlueprint`
    that are needed by the convergence checks.  Constructed once per blueprint
    so every check reads from the same consistent snapshot.
    """
    adj: dict[int, dict[str, int]]
    total_num_nodes: int

    # Derived fields — populated in __post_init__
    incoming: dict[int, int] = field(init=False)
    leaves: set[int] = field(init=False)
    non_leaves: list[int] = field(init=False)

    def __post_init__(self) -> None:
        self.incoming = self._count_incoming()
        self.leaves = self._find_leaves()
        self.non_leaves = [
            n for n in range(self.total_num_nodes) if n not in self.leaves
        ]

    def _count_incoming(self) -> dict[int, int]:
        counts: dict[int, int] = {n: 0 for n in range(self.total_num_nodes)}
        for edges in self.adj.values():
            for target in edges.values():
                if target != -1 and target in counts:
                    counts[target] += 1
        return counts

    def _find_leaves(self) -> set[int]:
        return {
            node_id
            for node_id, edges in self.adj.items()
            if all(t == -1 for t in edges.values())
        }


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

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

            print(
                f"[BlueprintGenerator] Attempt {attempt} failed convergence check: "
                f"{violations}. Sending correction prompt."
            )
            self._append_correction(history, raw, violations)

        print("[BlueprintGenerator] Max retries reached; returning best available blueprint.")
        return blueprint

    # ------------------------------------------------------------------
    # LLM interaction helpers
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

    def _append_correction(
        self,
        history: ChatHistory,
        failed_blueprint: GraphBlueprint,
        violations: list[str],
    ) -> None:
        """Append the failed assistant response and a corrective user turn to history."""
        history.append({"role": "assistant", "content": failed_blueprint.model_dump_json()})
        history.append({
            "role": "user",
            "content": BLUEPRINT_CORRECTION.format(
                violations="\n".join(f"  - {v}" for v in violations)
            ),
        })

    # ------------------------------------------------------------------
    # Convergence validation — one method per check
    # ------------------------------------------------------------------

    @staticmethod
    def _convergence_violations(blueprint: GraphBlueprint, total_num_nodes: int) -> list[str]:
        """
        Orchestrates all structural checks and returns a combined list of
        human-readable violation strings.  An empty list means the blueprint
        is valid.
        """
        analysis = _BlueprintAnalysis(adj=blueprint.adjacency, total_num_nodes=total_num_nodes)
        return (
            BlueprintGenerator._check_convergence_ratio(analysis)
            + BlueprintGenerator._check_funnel(analysis)
            + BlueprintGenerator._check_reconvergence(analysis)
        )

    @staticmethod
    def _check_convergence_ratio(analysis: _BlueprintAnalysis) -> list[str]:
        """Fail if fewer than _MIN_CONVERGENCE_RATIO non-leaf nodes have 2+ incoming edges."""
        if not analysis.non_leaves:
            return []
        converging = [n for n in analysis.non_leaves if analysis.incoming[n] > 1]
        ratio = len(converging) / len(analysis.non_leaves)
        if ratio >= _MIN_CONVERGENCE_RATIO:
            return []
        return [
            f"Only {len(converging)}/{len(analysis.non_leaves)} non-leaf nodes have more than "
            f"one incoming edge ({ratio:.0%}); at least {_MIN_CONVERGENCE_RATIO:.0%} required. "
            f"Nodes with multiple incoming edges: {converging}."
        ]

    @staticmethod
    def _check_funnel(analysis: _BlueprintAnalysis) -> list[str]:
        """Fail if a single node absorbs more than _MAX_FUNNEL_RATIO of all non-leaf edges."""
        if not analysis.non_leaves:
            return []
        funnel_node = max(analysis.non_leaves, key=lambda n: analysis.incoming[n])
        funnel_count = analysis.incoming[funnel_node]
        if funnel_count <= len(analysis.non_leaves) * _MAX_FUNNEL_RATIO:
            return []
        return [
            f"Node {funnel_node} receives edges from {funnel_count} other nodes "
            f"({funnel_count / len(analysis.non_leaves):.0%} of non-leaf nodes) — "
            "this looks like the forbidden funnel anti-pattern."
        ]

    @staticmethod
    def _check_reconvergence(analysis: _BlueprintAnalysis) -> list[str]:
        """
        Fail for any fork node whose two non-leaf children share no common
        successor within 2 hops — i.e. tree branches that never reconverge.
        """
        bad_forks: list[int] = []
        for fork_node, edges in analysis.adj.items():
            targets = list(edges.values())
            if len(targets) < 2:
                continue
            child_a, child_b = targets[0], targets[1]
            if child_a == child_b or child_a == -1 or child_b == -1:
                continue
            if child_a in analysis.leaves or child_b in analysis.leaves:
                continue
            reach_a = BlueprintGenerator._successors_within_2(analysis.adj, child_a) | {child_a}
            reach_b = BlueprintGenerator._successors_within_2(analysis.adj, child_b) | {child_b}
            if not reach_a & reach_b:
                bad_forks.append(fork_node)

        if not bad_forks:
            return []
        return [
            f"Fork node(s) {bad_forks} branch into two paths that share NO common "
            "successor within 2 hops — the branches never reconverge. "
            "Each tree fork MUST have both children point to the same node within 2 hops."
        ]

    @staticmethod
    def _successors_within_2(adj: dict[int, dict[str, int]], node: int) -> set[int]:
        """Return all nodes reachable from *node* in 1 or 2 hops (excluding -1 sentinels)."""
        reachable: set[int] = set()
        for t1 in adj.get(node, {}).values():
            if t1 == -1:
                continue
            reachable.add(t1)
            for t2 in adj.get(t1, {}).values():
                if t2 != -1:
                    reachable.add(t2)
        return reachable

    # ------------------------------------------------------------------
    # Blueprint sanitisation — one method per concern
    # ------------------------------------------------------------------

    @staticmethod
    def _sanitise(blueprint_raw: GraphBlueprint, total_num_nodes: int) -> GraphBlueprint:
        """
        Post-process the raw blueprint to guarantee structural correctness.
        Delegates each concern to a focused helper.
        """
        adjacency = BlueprintGenerator._sanitise_adjacency(blueprint_raw.adjacency, total_num_nodes)
        win_nodes = BlueprintGenerator._sanitise_win_nodes(blueprint_raw.win_nodes, total_num_nodes)
        return GraphBlueprint(adjacency=adjacency, win_nodes=win_nodes)

    @staticmethod
    def _sanitise_adjacency(
        raw_adjacency: dict[int, dict[str, int]],
        total_num_nodes: int,
    ) -> dict[int, dict[str, int]]:
        """
        Ensure every node id 0…N-1 is present exactly once and that all
        edge targets are either -1 or a valid node id.
        """
        adjacency: dict[int, dict[str, int]] = {}
        for node_id in range(total_num_nodes):
            if node_id in raw_adjacency:
                adjacency[node_id] = {
                    gesture: (target if target == -1 or 0 <= target < total_num_nodes else -1)
                    for gesture, target in raw_adjacency[node_id].items()
                }
            else:
                adjacency[node_id] = {"0": -1, "1": -1}  # missing node → leaf
        return adjacency

    @staticmethod
    def _sanitise_win_nodes(raw_win_nodes: list[int], total_num_nodes: int) -> list[int]:
        """
        Filter win nodes to valid ids; fall back to the last node if none remain.
        """
        win_nodes = [n for n in raw_win_nodes if 0 <= n < total_num_nodes]
        return win_nodes if win_nodes else [total_num_nodes - 1]
