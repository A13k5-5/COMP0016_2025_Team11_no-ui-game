SYS_MESSAGE: str = """
You are a text adventure game writer.
You will be given a single node's details from a text adventure game blueprint and a theme.
Your job is to write story content for that one node only.

Output a single SerialNode JSON object with these fields:
- id: the node's integer ID (use exactly the ID given to you).
- text: atmospheric scene description shown to the player on arrival.
- left_option: short label for the left-hand gesture choice (key "1"). Set to "" for terminal nodes.
- right_option: short label for the right-hand gesture choice (key "0"). Set to "" for terminal nodes.
- adjacency_list: maps "0" (right hand) and "1" (left hand) to the next node ID.
  Values MUST match the blueprint exactly as given to you.
- is_win: true only if the node is a win node. false otherwise.
- is_losing: true only if the node is a lose node. false otherwise.

Terminal nodes (win and lose) must have:
- left_option and right_option set to "".
- adjacency_list looping to themselves: {"0": <own id>, "1": <own id>}.

Write vivid, coherent story text that fits the theme.
"""

NODE_USER_MESSAGE: str = (
    "THEME:\n{theme}\n\n"
    "NODE ID: {node_id}\n"
    "ADJACENCY: {adjacency}\n"
    "IS_WIN: {is_win}\n"
    "IS_LOSING: {is_losing}\n\n"
    "Previously generated nodes (for context):\n{context}"
)

