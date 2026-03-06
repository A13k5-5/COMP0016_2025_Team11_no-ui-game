"""
All system-prompt strings and per-node user-prompt builders used by the
local LLM pipeline.
"""
import json
from models import GraphBlueprint


SYS_QUANTITIES: str = (
    "You are a helpful assistant that generates structured output in JSON format. "
    "The structured output follows the NodeQuantities schema, which represents the number of nodes in the game. "
    'For example: if the user wants 20 nodes, the JSON must be {"nodes": 20}. '
    "Read the user's description carefully and decide a suitable number of nodes. "
    "Please use double quotes for JSON keys and values. "
)

SYS_BLUEPRINT: str = (
    "You are a graph-design assistant. "
    "Your task is to design the STRUCTURE of a text-based adventure game as a directed graph. "
    "You will be given the total number of nodes (N) and a story description. "
    "Output a GraphBlueprint JSON object with two fields: 'adjacency' and 'win_nodes'.\n\n"

    "WHAT A GRAPH IS (read carefully):\n"
    "  A graph is NOT a binary tree. In a binary tree every node has exactly one parent "
    "and no two paths ever meet again. That is WRONG for this task.\n"
    "  In a proper directed graph, multiple nodes can point TO THE SAME target node. "
    "This is called convergence, and it is REQUIRED.\n\n"

    "MANDATORY CONVERGENCE RULE:\n"
    "  At least HALF of the non-leaf nodes must be the target of 2 or more other nodes. "
    "This means you must deliberately reuse the same target id in many different adjacency entries. "
    "For example, if nodes 2, 4, and 7 all have '0' or '1' pointing to node 5, "
    "that is correct convergence.\n\n"

    "STRICTLY FORBIDDEN PATTERNS:\n"
    "  1. Binary tree: every node has exactly one incoming edge (from its unique parent). FORBIDDEN.\n"
    "  2. Funnel anti-pattern: all paths eventually converge onto a single 'hub' node "
    "just before the leaves (e.g. nodes 5,6,9,10 all point to node 11). FORBIDDEN.\n"
    "  3. Using a node id as a target that you have NOT also defined as a key in adjacency. FORBIDDEN.\n\n"

    "HOW TO DESIGN THE GRAPH (follow these steps):\n"
    "  Step 1 — Decide which 1-3 nodes will be LEAVES (win or lose). "
    "Leaf nodes map both gestures to -1.\n"
    "  Step 2 — Decide which nodes will be HUBS (targeted by many others). "
    "Choose 2 or more hub ids from the middle of the id range. "
    "Write them down before filling in the adjacency.\n"
    "  Step 3 — For each non-leaf node, at least one of its two gesture targets "
    "MUST point to a hub node or to another already-visited node, not always to a brand-new id.\n"
    "  Step 4 — Fill in adjacency for ALL ids 0 … N-1 (every id is a key exactly once).\n\n"

    "CONCRETE EXAMPLE for N=7 (study this pattern):\n"
    "  Leaves: 5 (lose), 6 (win). Hubs: 3, 4.\n"
    "  adjacency:\n"
    "    0 -> {0:1, 1:2}       (root branches to 1 and 2)\n"
    "    1 -> {0:3, 1:4}       (both targets are hubs)\n"
    "    2 -> {0:4, 1:3}       (both targets are hubs — same hubs as node 1!)\n"
    "    3 -> {0:5, 1:6}       (hub 3 leads to leaves)\n"
    "    4 -> {0:6, 1:5}       (hub 4 leads to leaves, different order)\n"
    "    5 -> {0:-1, 1:-1}     (lose leaf)\n"
    "    6 -> {0:-1, 1:-1}     (win leaf)\n"
    "  win_nodes: [6]\n"
    "  Notice: nodes 1 AND 2 both point to nodes 3 and 4 — that is convergence.\n\n"

    "ADJACENCY FORMAT:\n"
    "  adjacency is a dict mapping each node id (integer) to a dict with exactly "
    "two keys: '0' (right-hand gesture) and '1' (left-hand gesture), "
    "each mapping to an integer target node id, or -1 for a leaf.\n\n"

    "OUTPUT ONLY the GraphBlueprint JSON. No story text. "
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
    "The blueprint you just produced FAILS the convergence check. "
    "Here are the specific violations:\n{violations}\n\n"
    "Please redesign the graph from scratch and fix ALL of these issues. "
    "Remember the mandatory rules:\n"
    "  1. At least HALF of all non-leaf nodes must be pointed to by 2 or more other nodes.\n"
    "  2. No single node may receive edges from more than 60% of the non-leaf nodes "
    "(this is the funnel anti-pattern — it is FORBIDDEN).\n"
    "  3. You must NOT produce a binary tree (where every node has exactly one parent).\n"
    "Output only the corrected GraphBlueprint JSON."
)


def build_node_prompt(
    total_num_nodes: int,
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

