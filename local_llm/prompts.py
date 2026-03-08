"""
All system-prompt strings and per-node user-prompt builders used by the
local LLM pipeline.
"""
import json
from models import GraphBlueprint
from graph_template import GraphTemplate, NodeRole, build_template


SYS_QUANTITIES: str = (
    "You are a helpful assistant that generates structured output in JSON format. "
    "The structured output follows the NodeQuantities schema, which represents the number of nodes in the game. "
    'For example: if the user wants 20 nodes, the JSON must be {"nodes": 20}. '
    "It might be the case that the user gives a vague or open-ended description of their game, without explicitly stating a number. "
    "In such case, read the user's description carefully and decide a suitable number of nodes to make the game fun and interesting"
    "while respecting the user's constraints. "
    "Please use double quotes for JSON keys and values. "
)

SYS_BLUEPRINT: str = (
    "You are a graph-structure assistant for a text-based adventure game. "
    "You will be given a story description and a complete list of HARD CONSTRAINTS "
    "specifying exactly which node ids must be connected to which. "
    "Your only job is to output a valid GraphBlueprint JSON that satisfies every constraint.\n\n"

    "OUTPUT FORMAT:\n"
    "  A JSON object with exactly two keys:\n"
    "  • 'adjacency': maps every node id (0 … N-1) to a dict with keys '0' and '1', "
    "each holding an integer target node id or -1 (for a terminal leaf node).\n"
    "  • 'win_nodes': a JSON array of the winning leaf node ids.\n\n"

    "RULES:\n"
    "  1. Every node id from 0 to N-1 must appear exactly once as a key in adjacency.\n"
    "  2. Every HARD CONSTRAINT edge listed in the prompt MUST appear in your adjacency "
    "as at least one of the two gesture targets ('0' or '1') for that node.\n"
    "  3. For the second gesture target of each node you have creative freedom — "
    "pick any valid node id that fits the story, including another hub or an already-used target.\n"
    "  4. Leaf nodes must map BOTH gestures to -1.\n"
    "  5. Use only node ids in the range [0, N-1] or -1. No other values.\n\n"

    "Output ONLY the GraphBlueprint JSON. No story text, no explanation. "
    "Use double quotes for all JSON keys and string values."
)

SYS_NODE_WRITER: str = (
    "You are a creative writer for a text-based adventure game. "
    "In each turn you will be told which node to write and given its exact adjacency constraints. "
    "You MUST respect those constraints exactly — do not invent new node ids. "
    "Keep the story consistent across turns: every node should feel like part of the same story. "
    "Respond with only a valid SerialNode JSON object and nothing else."
)

NODE_WRITER_PRIMER: str = (
    "Understood. I will write all nodes consistently within the given graph structure."
)

BLUEPRINT_CORRECTION: str = (
    "The blueprint you produced FAILS the structural checks. "
    "Here are the specific violations:\n{violations}\n\n"
    "You MUST produce a new GraphBlueprint JSON that satisfies ALL of the original "
    "HARD CONSTRAINTS listed above. Each HARD CONSTRAINT specifies a required edge "
    "that must appear as at least one gesture target ('0' or '1') for that node. "
    "Do not ignore any constraint.\n\n"
    "Reminder of what the constraints enforce:\n"
    "  • BRANCH nodes must point to their convergence hub (prevents un-reconverged trees).\n"
    "  • RING_SRC nodes must point back to an earlier hub (creates a loop).\n"
    "  • MESH nodes must cross-link to a hub (creates dense connections).\n\n"
    "Output only the corrected GraphBlueprint JSON."
)


def build_blueprint_prompt(n: int, user_prompt: str) -> tuple[str, GraphTemplate]:
    """
    Build the user-turn prompt for the blueprint LLM call.

    This function pre-computes a :class:`GraphTemplate` that deterministically
    assigns every node a structural role and a set of required edges.  Those
    required edges are rendered as explicit, numbered HARD CONSTRAINTS in the
    prompt so the LLM cannot ignore them.

    :returns: (prompt_string, template) — the template is also returned so the
              caller can pass it to the validator without recomputing it.
    """
    template = build_template(n)
    lines: list[str] = []

    lines.append(f"Design a GraphBlueprint for a {n}-node text adventure.")
    lines.append(f"Story description: {user_prompt}\n")
    lines.append(f"Total nodes: {n}  (ids 0 to {n - 1})")
    lines.append(f"Win leaf node(s): {template.win_leaves}")
    lines.append(f"Lose leaf node(s): {template.lose_leaves}")
    lines.append(f"Hub (bottleneck) nodes: {template.hubs}  "
                 f"← these must receive edges from many other nodes\n")

    lines.append("NODE ROLES (every node listed, role is informational):")
    for node_id in range(n):
        role = template.roles.get(node_id, NodeRole.BUS)
        lines.append(f"  node {node_id:>3} — {role.name}")
    lines.append("")

    lines.append("HARD CONSTRAINTS (you MUST obey every line below):")
    lines.append("  Each constraint says: node X must have at least one gesture pointing to Y.")
    lines.append("  Use the other gesture freely — point it to any valid node that fits the story.\n")

    constraint_num = 1

    # Leaf constraints
    for leaf in template.all_leaves:
        lines.append(f"  [{constraint_num}] node {leaf} is a LEAF → adjacency MUST be "
                     f'{{\"0\": -1, \"1\": -1}}')
        constraint_num += 1

    # Branch convergence constraints
    for fg in template.fork_groups:
        lines.append(
            f"  [{constraint_num}] node {fg.branch_a} (BRANCH) → at least one gesture "
            f"MUST point to hub {fg.converge_hub}  "
            f"[tree fork {fg.fork_node}→({fg.branch_a},{fg.branch_b})→{fg.converge_hub}]"
        )
        constraint_num += 1
        lines.append(
            f"  [{constraint_num}] node {fg.branch_b} (BRANCH) → at least one gesture "
            f"MUST point to hub {fg.converge_hub}  "
            f"[same fork, other branch]"
        )
        constraint_num += 1

    # Ring back-edge constraints
    if template.hubs:
        for rs in template.ring_sources:
            lines.append(
                f"  [{constraint_num}] node {rs} (RING_SRC) → at least one gesture "
                f"MUST point back to hub {template.hubs[0]}  [loop / cycle back-edge]"
            )
            constraint_num += 1

    # Mesh cross-link constraints
    if template.hubs:
        for mn in template.mesh_nodes:
            lines.append(
                f"  [{constraint_num}] node {mn} (MESH) → at least one gesture "
                f"MUST point to hub {template.hubs[-1]}  [cross-link]"
            )
            constraint_num += 1

    lines.append("")
    lines.append(
        "Fill in ALL remaining edges however you like, as long as every target is a valid "
        f"node id in [0, {n - 1}] or -1 for a leaf. "
        "For non-leaf nodes avoid pointing both gestures to brand-new, never-before-used ids — "
        "prefer reusing hub ids or other already-constrained targets."
    )

    return "\n".join(lines), template



def build_node_prompt(total_num_nodes: int,
    cur_node_num: int,
    blueprint: GraphBlueprint,
) -> str:
    """
    Build the user-turn prompt that instructs the model to write a single
    SerialNode.  All structural constraints are derived from the blueprint so
    the model has no freedom to invent invalid node ids.
    """
    remaining = total_num_nodes - cur_node_num
    adjacency_for_node: dict = blueprint.adjacency.get(cur_node_num, {})
    win_nodes: list[int] = blueprint.win_nodes
    is_win: bool = cur_node_num in win_nodes

    # Incoming edges — which nodes point to this one?
    incoming = [
        src
        for src, edges in blueprint.adjacency.items()
        if cur_node_num in edges.values()
    ]
    incoming_label = incoming if incoming else ["it is the root"]

    return (
        f"You are writing story content for a text-based adventure game that has exactly "
        f"{total_num_nodes} nodes in total (ids 0 to {total_num_nodes - 1}). "
        f"You are now writing node {cur_node_num} "
        f"(there are {remaining} node(s) left to write including this one). "
        "Generate a single SerialNode JSON object. "
        "\n\nSERIALNODE FIELD DEFINITIONS:\n"
        "- id: the integer id of this node (must match the id you are asked to generate).\n"
        "- text: the story text shown to the player at this node.\n"
        "- left_option: the short label for the left-hand gesture choice "
        "(empty string for leaf nodes).\n"
        "- right_option: the short label for the right-hand gesture choice "
        "(empty string for leaf nodes).\n"
        "- adjacency_list: maps gesture keys to the id of the next node. "
        f"  For this node the adjacency MUST be exactly: {json.dumps(adjacency_for_node)}. "
        "  Use -1 to signal a leaf (win/lose) node with no outgoing edges.\n"
        f"- is_win: set to {'true' if is_win else 'false'} for this node.\n"
        "\nCONSTRAINTS:\n"
        f"  * Only use node ids in the range [0, {total_num_nodes - 1}] for any adjacency targets.\n"
        f"  * The winning node id(s) for this game are: {win_nodes}.\n"
        f"  * This node is reachable from nodes: {incoming_label}.\n"
        "  * The story must be self-contained within the given number of nodes — "
        "do NOT reference nodes that do not exist.\n"
        "  * Leaf nodes (is_win=true or dead-end) must have empty left_option, "
        "empty right_option, and adjacency_list mapping both gestures to -1.\n"
        "Please use double quotes for JSON keys and values. "
    )

