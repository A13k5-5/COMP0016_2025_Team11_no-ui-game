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
    "It might be the case that the user gives a vague or open-ended description of their game, without explicitly stating a number. "
    "In such case, read the user's description carefully and decide a suitable number of nodes to make the game fun and interesting"
    "while respecting the user's constraints. "
    "Please use double quotes for JSON keys and values. "
)

SYS_BLUEPRINT: str = (
    "You are a graph-design assistant. "
    "Your task is to design the STRUCTURE of a text-based adventure game as a directed graph. "
    "You will be given the total number of nodes (N) and a story description. "
    "Output a GraphBlueprint JSON object with two fields: 'adjacency' and 'win_nodes'.\n\n"

    "═══════════════════════════════════════════════════════════\n"
    "CORE DESIGN PHILOSOPHY\n"
    "═══════════════════════════════════════════════════════════\n"
    "Think of the graph like a RIVER WITH TRIBUTARIES. "
    "The story has a clear overall flow from start to end, but at key dramatic moments "
    "the path forks briefly and then FLOWS BACK TOGETHER into shared waypoints. "
    "This gives the player meaningful choices without making every player's experience "
    "completely different — they will all pass through the same major story beats.\n\n"
    "You MUST use a MIX of the following topology patterns within a single graph. "
    "No single pattern should dominate the whole graph.\n\n"

    "  PATTERN — BUS (linear spine)\n"
    "    A straight chain: A→B→C. Use this for unavoidable story beats that "
    "every player must experience (e.g. the opening scene, the final confrontation).\n\n"

    "  PATTERN — TREE BRANCH (short-lived fork, STRICTLY LIMITED)\n"
    "    One node splits into two paths. RULE: the two branches MUST reconverge "
    "onto the SAME node within AT MOST 2 hops. This means:\n"
    "      fork→branchA→merge   AND   fork→branchB→merge\n"
    "    (both branchA and branchB point to 'merge' — the same node id).\n"
    "    A fork whose branches never meet again is FORBIDDEN.\n\n"

    "  PATTERN — STAR (hub with many incoming edges)\n"
    "    Several nodes all point to the same hub node. Use this for major "
    "story waypoints that the player always reaches regardless of earlier choices.\n\n"

    "  PATTERN — RING (loop / cycle)\n"
    "    A node eventually points back to an earlier node. Use sparingly for "
    "exploration loops (e.g. 'search the room again').\n\n"

    "  PATTERN — MESH (dense cross-connections)\n"
    "    Nodes freely cross-link to previously visited or upcoming shared nodes. "
    "Use in the mid-game to create a rich web of consequences.\n\n"

    "═══════════════════════════════════════════════════════════\n"
    "STEP 1 — PLAN THE MACRO STRUCTURE (do this before any node ids)\n"
    "═══════════════════════════════════════════════════════════\n"
    "  a) Divide the N nodes into three ACTS: early (~25%), mid (~50%), late (~25%).\n"
    "  b) Choose 2-4 BOTTLENECK (hub) nodes — one in mid-act, one in late-act — "
    "that ALL paths must pass through. These are your STAR hubs.\n"
    "  c) Plan 1-2 short TREE forks in the early/mid act. Each fork has exactly 2 "
    "branch nodes that BOTH point back to the same bottleneck hub within 2 hops.\n"
    "  d) Add 1-2 RING back-edges in the mid act for exploration flavour.\n"
    "  e) Choose 1-3 LEAF nodes for win/lose endings. Leaves map both gestures to -1.\n"
    "  Write down: [bottleneck ids] [fork ids] [branch ids] [leaf ids] before step 2.\n\n"

    "═══════════════════════════════════════════════════════════\n"
    "STEP 2 — FILL IN ADJACENCY\n"
    "═══════════════════════════════════════════════════════════\n"
    "  * Every id from 0 to N-1 must appear exactly ONCE as a key.\n"
    "  * For EVERY non-leaf node, AT LEAST ONE of its two gesture targets must be "
    "a bottleneck hub or a node already targeted by another node. "
    "NEVER let both targets be fresh, never-before-used ids.\n"
    "  * Each tree fork must have both its branch nodes reconverge to the same hub "
    "within 2 hops — verify this before writing the JSON.\n"
    "  * At least 35% of all non-leaf nodes must have 2 or more incoming edges.\n\n"

    "═══════════════════════════════════════════════════════════\n"
    "WORKED EXAMPLE  N=12, win=10, lose=11\n"
    "═══════════════════════════════════════════════════════════\n"
    "  Bottlenecks: 4 (mid-act hub), 8 (late-act hub).\n"
    "  Early fork: node 1 branches to 2 and 3; both 2 and 3 point to hub 4.  ← TREE (depth 1)\n"
    "  Mid fork:   node 5 branches to 6 and 7; both 6 and 7 point to hub 8.  ← TREE (depth 1)\n"
    "  Ring:       node 9 has one gesture pointing back to hub 4.             ← RING\n"
    "  Mesh cross: node 8 has one gesture pointing to node 5 (already visited path). ← MESH\n\n"
    "  adjacency:\n"
    "    0->{0:1,  1:2 }   (opening — bus step, but shortcut straight to 2)\n"
    "    1->{0:2,  1:3 }   (early fork)\n"
    "    2->{0:4,  1:3 }   (branch A — converges at hub 4 within 1 hop)\n"
    "    3->{0:4,  1:2 }   (branch B — converges at hub 4 within 1 hop; cross-link to 2)\n"
    "    4->{0:5,  1:6 }   (mid-act hub — star: receives edges from 2 and 3)\n"
    "    5->{0:6,  1:7 }   (mid fork)\n"
    "    6->{0:8,  1:7 }   (branch C — converges at hub 8 within 1 hop)\n"
    "    7->{0:8,  1:6 }   (branch D — converges at hub 8 within 1 hop; cross-link to 6)\n"
    "    8->{0:9,  1:5 }   (late-act hub — mesh: one gesture loops back to 5)\n"
    "    9->{0:10, 1:4 }   (ring: one gesture loops back to mid-act hub 4)\n"
    "   10->{0:-1, 1:-1}   (WIN leaf)\n"
    "   11->{0:-1, 1:-1}   (LOSE leaf — reachable if sanitiser adds it)\n"
    "  win_nodes: [10]\n\n"
    "  Convergence check: nodes 4 receives edges from {2,3,9} = 3 sources. "
    "Node 8 receives from {6,7} = 2 sources. "
    "Node 6 receives from {5,7} = 2 sources. "
    "Node 7 receives from {5,6} = 2 sources. ✓\n\n"

    "═══════════════════════════════════════════════════════════\n"
    "STRICTLY FORBIDDEN\n"
    "═══════════════════════════════════════════════════════════\n"
    "  1. Tree branches that never reconverge (depth > 2 before merging). FORBIDDEN.\n"
    "  2. A graph that is ENTIRELY one pattern (all tree, all bus, all mesh…). FORBIDDEN.\n"
    "  3. Single-funnel: ALL paths collapsing onto ONE node just before the leaves. FORBIDDEN.\n"
    "  4. Referencing a node id that is not a key in adjacency. FORBIDDEN.\n\n"

    "ADJACENCY FORMAT:\n"
    "  adjacency maps each node id (integer) to a dict with exactly two keys: "
    "'0' (right-hand gesture) and '1' (left-hand gesture), "
    "each mapping to an integer target node id or -1 for a leaf.\n\n"

    "OUTPUT ONLY the GraphBlueprint JSON. No story text, no explanation. "
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
    "Please redesign the graph from SCRATCH and fix ALL of these issues.\n\n"
    "REMINDER — the graph must use a MIX of topology patterns, like a river with tributaries:\n"
    "  • BUS: unavoidable linear beats every player passes through.\n"
    "  • TREE BRANCH (strictly limited): a fork into 2 paths that MUST reconverge "
    "onto the same node within AT MOST 2 hops. "
    "A fork whose branches never meet again is FORBIDDEN.\n"
    "  • STAR: 2-4 bottleneck hub nodes that many paths funnel into.\n"
    "  • RING: one or two back-edges that let the player revisit an earlier hub.\n"
    "  • MESH: mid-game cross-links between non-adjacent nodes.\n\n"
    "No single pattern should dominate. Do NOT use only tree structure.\n\n"
    "Mandatory rules:\n"
    "  1. Every tree fork must have its two branches reconverge within 2 hops.\n"
    "  2. At least 35% of all non-leaf nodes must have 2 or more incoming edges.\n"
    "  3. No single node may receive edges from more than 60% of the non-leaf nodes "
    "(single-funnel anti-pattern — FORBIDDEN).\n"
    "  4. You must NOT produce a pure binary tree (every node has exactly one parent).\n\n"
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

