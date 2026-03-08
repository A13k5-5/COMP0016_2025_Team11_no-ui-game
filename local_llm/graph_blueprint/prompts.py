BLUEPRINT_MESSAGE: str = """
Design a text adventure game as a directed graph.
Each node is a scene with exactly two outgoing edges: "0" and "1" (player choices).
Player starts at node 0. Terminal nodes (win/lose) loop to themselves on both edges.
Output JSON with keys: "adjacency", "win_nodes", "lose_nodes".

Build the graph using this exact method:

STEP 1 — Choose two bottleneck node IDs, call them B1 and B2.
STEP 2 — Node 0 splits into branch A (starts at node 1) and branch B.
          Both branches must be 2+ nodes long and both must end by pointing TO B1.
STEP 3 — B1 splits into branch C and branch D.
          Both branches must be 2+ nodes long and both must end by pointing TO B2.
STEP 4 — B2 has one edge going to the WIN node and one edge going to a LOSE node.
STEP 5 — Inside any branch, one edge may go to a LOSE node instead of forward,
          but the other edge must continue the branch normally.

CRITICAL: Branches are LINEAR CHAINS — no sub-branching inside a branch.
Inside a branch, a non-last node sends BOTH edges to the SAME next node:
  CORRECT: "1": {"0": 2, "1": 2}   <- both edges go to node 2 (linear, no split)
  WRONG:   "1": {"0": 2, "1": 5}   <- edges go to different nodes (this creates a sub-branch)
The ONLY exception is when ONE edge goes to a LOSE node (step 5 above).

Here is a complete example where B1=7 and B2=14:

```json
{
  "adjacency": {
    "0":  {"0": 1,  "1": 4},
    "1":  {"0": 2,  "1": 2},
    "2":  {"0": 3,  "1": 15},
    "3":  {"0": 7,  "1": 7},
    "4":  {"0": 5,  "1": 5},
    "5":  {"0": 6,  "1": 16},
    "6":  {"0": 7,  "1": 7},
    "7":  {"0": 8,  "1": 11},
    "8":  {"0": 9,  "1": 9},
    "9":  {"0": 10, "1": 15},
    "10": {"0": 14, "1": 14},
    "11": {"0": 12, "1": 12},
    "12": {"0": 13, "1": 16},
    "13": {"0": 14, "1": 14},
    "14": {"0": 18, "1": 17},
    "15": {"0": 15, "1": 15},
    "16": {"0": 16, "1": 16},
    "17": {"0": 17, "1": 17},
    "18": {"0": 18, "1": 18}
  },
  "win_nodes": [18],
  "lose_nodes": [15, 16, 17]
}
```

In this example: B1=7, B2=14.
- Node 0 splits: branch A starts at 1, branch B starts at 4.
- Nodes 1, 4, 8, 11: both edges go to the same next node (linear, no sub-branch).
- Nodes 2, 5, 9, 12: good choice goes forward, bad choice goes to a lose node.
- Nodes 3, 6: branch ends — both edges go to B1 (node 7).
- Nodes 10, 13: branch ends — both edges go to B2 (node 14).
- Node 14 (B2): one edge -> win (18), one edge -> lose (17).

Verify before outputting:
- [ ] B1 appears as a target in at least 2 different nodes (nodes 3 and 6 in the example).
- [ ] B2 appears as a target in at least 2 different nodes (nodes 10 and 13 in the example).
- [ ] Every non-last branch node has BOTH edges pointing to the same target (linear chain).
- [ ] Exactly 1 win node. At most 4 lose nodes.
- [ ] At least one path from node 0 reaches the win node.

Generate the blueprint now.
"""
