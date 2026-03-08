"""
GraphTemplate: deterministically assigns every node in a game to a structural
role (hub, fork, branch, ring-source, mesh-cross, leaf) BEFORE the LLM is
called.

The template is pure Python — no LLM involvement.  It is passed to
build_blueprint_prompt() so that the LLM receives concrete, pre-computed node
ids rather than abstract design instructions it can ignore.

Topology roles (matching the six patterns from game-narrative science):
  BUS       — the linear spine that every player passes through
  HUB       — a bottleneck / STAR node targeted by many others
  FORK      — a node that splits into exactly two branch nodes
  BRANCH    — one arm of a fork; must point back to a hub within 1 hop
  RING_SRC  — a node that has one back-edge pointing to an earlier hub
  MESH      — a node that has one cross-edge to a non-adjacent already-used node
  LEAF      — terminal node (win or lose); both edges map to -1
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto


class NodeRole(Enum):
    BUS = auto()
    HUB = auto()
    FORK = auto()
    BRANCH = auto()
    RING_SRC = auto()
    MESH = auto()
    LEAF = auto()


@dataclass
class ForkGroup:
    """One tree-fork: a fork node and its two branch nodes, plus the hub they converge to."""
    fork_node: int
    branch_a: int
    branch_b: int
    converge_hub: int


@dataclass
class GraphTemplate:
    """
    Holds the pre-assigned structural roles and required edges for a graph of
    *total_num_nodes* nodes.

    Attributes
    ----------
    n               Total number of nodes.
    roles           Maps every node id to its :class:`NodeRole`.
    hubs            Ordered list of hub (STAR bottleneck) node ids.
    fork_groups     Each :class:`ForkGroup` describes one short tree-fork.
    ring_sources    Node ids that must carry a back-edge to an earlier hub.
    mesh_nodes      Node ids that must carry a cross-edge to any already-defined hub.
    win_leaves      Node ids that are winning leaf nodes.
    lose_leaves     Node ids that are losing leaf nodes.

    Required edges  (the LLM *must* include these)
    --------------
    required_edges  dict mapping node_id → list of target node ids that the
                    LLM must use as at least one of its two gesture targets.
    """
    n: int
    roles: dict[int, NodeRole] = field(default_factory=dict)
    hubs: list[int] = field(default_factory=list)
    fork_groups: list[ForkGroup] = field(default_factory=list)
    ring_sources: list[int] = field(default_factory=list)
    mesh_nodes: list[int] = field(default_factory=list)
    win_leaves: list[int] = field(default_factory=list)
    lose_leaves: list[int] = field(default_factory=list)
    required_edges: dict[int, list[int]] = field(default_factory=dict)

    @property
    def all_leaves(self) -> list[int]:
        return self.win_leaves + self.lose_leaves


def build_template(n: int) -> GraphTemplate:
    """
    Deterministically compute a :class:`GraphTemplate` for *n* nodes.

    Layout strategy
    ---------------
    The nodes are divided into three acts:
      - Early act  : first 25 %  — opening BUS spine + one TREE fork
      - Mid act    : middle 50 % — HUBs + MESH cross-links + optional second fork + RING
      - Late act   : last 25 %   — final HUB + RING source + LEAFs

    All percentages are rounded to whole node counts; the mid-act absorbs any
    rounding remainder so no node is ever left without a role.
    """
    t = GraphTemplate(n=n)

    early_end = max(1, math.floor(n * 0.25))
    late_start = max(early_end + 1, math.ceil(n * 0.75))

    early_ids = list(range(0, early_end))
    mid_ids   = list(range(early_end, late_start))
    late_ids  = list(range(late_start, n))

    _assign_leaves(t, late_ids)
    _assign_hubs(t, mid_ids, late_ids)
    _assign_early_act(t, early_ids)
    _assign_mid_act(t, mid_ids)
    _assign_late_act(t, late_ids)
    _assign_remaining_bus(t)
    _build_required_edges(t)

    return t


# ---------------------------------------------------------------------------
# Role-assignment helpers
# ---------------------------------------------------------------------------

def _assign_leaves(t: GraphTemplate, late_ids: list[int]) -> None:
    """Reserve the last 1-2 late nodes as leaves (win + optional lose)."""
    if not late_ids:
        t.win_leaves = [t.n - 1]
        t.roles[t.n - 1] = NodeRole.LEAF
        return

    t.win_leaves = [late_ids[-1]]
    t.roles[late_ids[-1]] = NodeRole.LEAF

    if len(late_ids) >= 2:
        t.lose_leaves = [late_ids[-2]]
        t.roles[late_ids[-2]] = NodeRole.LEAF


def _assign_hubs(t: GraphTemplate, mid_ids: list[int], late_ids: list[int]) -> None:
    """
    Choose 2 hubs:
      - mid_hub  : roughly the middle of the mid-act
      - late_hub : the first node of the late-act that is not a leaf
    """
    if mid_ids:
        mid_hub = mid_ids[len(mid_ids) // 2]
        t.hubs.append(mid_hub)
        t.roles[mid_hub] = NodeRole.HUB

    non_leaf_late = [x for x in late_ids if x not in t.all_leaves]
    if non_leaf_late:
        late_hub = non_leaf_late[0]
        t.hubs.append(late_hub)
        t.roles[late_hub] = NodeRole.HUB


def _assign_early_act(t: GraphTemplate, early_ids: list[int]) -> None:
    """
    Assign roles for the early act.
    With ≥3 early nodes: node 0 = BUS root, nodes 1 & 2 = FORK + first BRANCH pair.
    With fewer nodes everything is BUS.
    """
    for node_id in early_ids:
        if node_id not in t.roles:
            t.roles[node_id] = NodeRole.BUS

    if len(early_ids) >= 3 and t.hubs:
        fork_node   = early_ids[1]
        branch_a    = early_ids[2] if len(early_ids) > 2 else None
        # branch_b borrows the first available unassigned mid node
        branch_b    = _first_unassigned(t, start_after=early_ids[-1])

        if branch_a is not None and branch_b is not None:
            converge_hub = t.hubs[0]
            t.fork_groups.append(ForkGroup(fork_node, branch_a, branch_b, converge_hub))
            t.roles[fork_node] = NodeRole.FORK
            t.roles[branch_a]  = NodeRole.BRANCH
            t.roles[branch_b]  = NodeRole.BRANCH


def _assign_mid_act(t: GraphTemplate, mid_ids: list[int]) -> None:
    """
    In the mid-act, assign a second fork (if enough nodes remain), one RING_SRC,
    and one MESH node.  Everything else stays BUS.
    """
    unassigned = [x for x in mid_ids if x not in t.roles]

    # Second fork — needs fork + 2 branches + a hub target
    if len(t.hubs) >= 2 and len(unassigned) >= 3:
        fork2       = unassigned[0]
        branch_c    = unassigned[1]
        branch_d    = unassigned[2]
        converge_hub = t.hubs[-1]  # converge to the late hub
        t.fork_groups.append(ForkGroup(fork2, branch_c, branch_d, converge_hub))
        t.roles[fork2]    = NodeRole.FORK
        t.roles[branch_c] = NodeRole.BRANCH
        t.roles[branch_d] = NodeRole.BRANCH
        unassigned = unassigned[3:]

    # One ring source — points back to the first (mid) hub
    if unassigned and t.hubs:
        ring_node = unassigned.pop(0)
        t.ring_sources.append(ring_node)
        t.roles[ring_node] = NodeRole.RING_SRC

    # One mesh node — cross-links to any hub
    if unassigned and t.hubs:
        mesh_node = unassigned.pop(0)
        t.mesh_nodes.append(mesh_node)
        t.roles[mesh_node] = NodeRole.MESH

    # Remaining mid nodes → BUS
    for node_id in unassigned:
        if node_id not in t.roles:
            t.roles[node_id] = NodeRole.BUS


def _assign_late_act(t: GraphTemplate, late_ids: list[int]) -> None:
    """Late-act non-hub, non-leaf nodes become BUS."""
    for node_id in late_ids:
        if node_id not in t.roles:
            t.roles[node_id] = NodeRole.BUS


def _assign_remaining_bus(t: GraphTemplate) -> None:
    """Safety net: any node still without a role becomes BUS."""
    for node_id in range(t.n):
        if node_id not in t.roles:
            t.roles[node_id] = NodeRole.BUS


# ---------------------------------------------------------------------------
# Required-edges builder
# ---------------------------------------------------------------------------

def _build_required_edges(t: GraphTemplate) -> None:
    """
    Populate t.required_edges with the mandatory targets each non-leaf node
    must include as at least one of its two gesture targets.

    Rules encoded:
      BRANCH  → must point to its fork-group's converge_hub
      RING_SRC → must point back to hubs[0] (the mid-act hub)
      MESH    → must point to hubs[-1] (or hubs[0] if only one hub)
    """
    # Branch nodes must converge to their hub
    for fg in t.fork_groups:
        for branch in (fg.branch_a, fg.branch_b):
            t.required_edges.setdefault(branch, []).append(fg.converge_hub)

    # Ring sources must loop back to the earliest hub
    if t.hubs:
        for rs in t.ring_sources:
            t.required_edges.setdefault(rs, []).append(t.hubs[0])

    # Mesh nodes must cross-link to the latest hub
    if t.hubs:
        for mn in t.mesh_nodes:
            t.required_edges.setdefault(mn, []).append(t.hubs[-1])


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _first_unassigned(t: GraphTemplate, start_after: int) -> int | None:
    """Return the first node id > start_after that has no role yet."""
    for node_id in range(start_after + 1, t.n):
        if node_id not in t.roles:
            return node_id
    return None

