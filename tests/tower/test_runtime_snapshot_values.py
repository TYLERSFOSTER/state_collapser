"""Tests for serializable runtime value snapshots."""

from __future__ import annotations

import json

from state_collapser.contract.policy import LabelContractionPolicy
from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.runtime import TowerRuntime
from state_collapser.tower.snapshot import RuntimeSnapshot


class _TinyHiddenGraph:
    def __init__(self) -> None:
        self.s1 = State(payload=("start",), identity="s1")
        self.s2 = State(payload=("goal",), identity="s2")
        self.a = PrimitiveAction(payload=("step",), identity="a1", labels=("forward",))
        self.edge = BaseEdge(source=self.s1, action=self.a, target=self.s2, labels=("boundary",))

    def apply_action(self, state: State, action: PrimitiveAction) -> State | None:
        if state == self.s1 and action == self.a:
            return self.s2
        return None

    def out_edges(self, state: State) -> list[BaseEdge]:
        if state == self.s1:
            return [self.edge]
        return []


def test_runtime_snapshot_to_dict_is_json_serializable() -> None:
    snapshot = RuntimeSnapshot(
        current_base_state="s0",
        current_position_at_every_tier=("q0",),
        current_step_reward_value=1.0,
        cumulative_reward_total=2.0,
        cumulative_reward_count=2,
        quotient_tier_count=1,
        diagnostics={"ok": True},
    )

    json.dumps(snapshot.to_dict())


def test_runtime_snapshot_to_dict_excludes_live_graph_and_tower_fields() -> None:
    graph = _TinyHiddenGraph()
    runtime = TowerRuntime(
        hidden_graph=graph,
        contraction_policy=LabelContractionPolicy(labels=frozenset({"boundary"})),
    )
    value_snapshot = runtime.reset(initial_state=graph.s1).to_snapshot()
    data = value_snapshot.to_dict()

    assert "explored_graph" not in data
    assert "vista_graph" not in data
    assert "partition_tower_view" not in data
    assert "ordered_quotient_tiers" not in data
    json.dumps(data)


def test_runtime_snapshot_value_is_stable_after_runtime_advances() -> None:
    graph = _TinyHiddenGraph()
    runtime = TowerRuntime(
        hidden_graph=graph,
        contraction_policy=LabelContractionPolicy(labels=frozenset({"boundary"})),
        reward_function=lambda edge: 1.0,
    )
    reset_snapshot = runtime.reset(initial_state=graph.s1).to_snapshot()
    before = reset_snapshot.to_dict()

    runtime.step(graph.a)

    assert reset_snapshot.to_dict() == before
