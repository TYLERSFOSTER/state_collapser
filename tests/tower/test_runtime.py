"""Tests for the tower runtime."""

from __future__ import annotations

from state_collapser.contract.policy import LabelContractionPolicy
from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.schema import DimensionwiseSchema
from state_collapser.tower.partition.tower import PartitionTower
from state_collapser.tower.runtime import TowerRuntime
from state_collapser.tower.snapshot import LiveRuntimeView, RuntimeSnapshot


class TinyHiddenGraph:
    """Tiny hidden graph for tower-runtime tests."""

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


def build_runtime() -> tuple[TowerRuntime, TinyHiddenGraph]:
    hidden = TinyHiddenGraph()
    runtime = TowerRuntime(
        hidden_graph=hidden,
        contraction_policy=LabelContractionPolicy(labels=frozenset({"boundary"})),
        contraction_schema=DimensionwiseSchema(("boundary",)),
        reward_function=lambda edge: 1.0,
    )
    return runtime, hidden


def build_legacy_runtime() -> tuple[TowerRuntime, TinyHiddenGraph]:
    hidden = TinyHiddenGraph()
    runtime = TowerRuntime(
        hidden_graph=hidden,
        tower_backend="legacy",
        contraction_policy=LabelContractionPolicy(labels=frozenset({"boundary"})),
        reward_function=lambda edge: 1.0,
    )
    return runtime, hidden


def test_reset_snapshot_shape() -> None:
    runtime, hidden = build_runtime()

    snapshot = runtime.reset(initial_state=hidden.s1)

    assert isinstance(snapshot, LiveRuntimeView)
    assert snapshot.current_base_state == hidden.s1
    assert snapshot.explored_graph.current_path() == (hidden.s1,)


def test_step_update_order() -> None:
    runtime, hidden = build_runtime()
    runtime.reset(initial_state=hidden.s1)

    snapshot = runtime.step(hidden.a)

    assert isinstance(snapshot, LiveRuntimeView)
    assert isinstance(snapshot.to_snapshot(), RuntimeSnapshot)
    assert snapshot.current_base_state == hidden.s2
    assert snapshot.explored_graph.current_path() == (hidden.s1, hidden.s2)
    assert snapshot.vista_graph.vista_neighbors(hidden.s1) == (hidden.s2,)


def test_immediate_full_tower_update() -> None:
    runtime, hidden = build_runtime()
    runtime.reset(initial_state=hidden.s1)

    snapshot = runtime.step(hidden.a)

    assert len(snapshot.current_position_at_every_tier) == 2
    assert runtime.tier_is_point(1)


def test_cross_tier_position_update() -> None:
    runtime, hidden = build_runtime()
    runtime.reset(initial_state=hidden.s1)

    snapshot = runtime.step(hidden.a)

    assert len(snapshot.current_position_at_every_tier) == 2
    assert snapshot.current_position_at_every_tier[0] is not None
    assert snapshot.current_position_at_every_tier[1] is not None


def test_runtime_supports_dynamic_queries() -> None:
    runtime, hidden = build_runtime()
    runtime.reset(initial_state=hidden.s1)
    runtime.step(hidden.a)

    assert runtime.current_deepest_tier() == 1
    assert runtime.project_state_to_tier(hidden.s2, 0) is not None
    assert runtime.project_state_to_tier(hidden.s2, 1) is not None
    assert runtime.projected_edge_is_trivial_at_tier(hidden.edge, 1) is True
    assert runtime.states_share_coset(hidden.s1, hidden.s2, 1) is True
    assert runtime.tower_is_fully_propagated() is True


def test_runtime_exposes_tierwise_contraction_records() -> None:
    runtime, hidden = build_legacy_runtime()
    runtime.reset(initial_state=hidden.s1)
    runtime.step(hidden.a)

    assert runtime.tier_contraction_records
    first_record = runtime.tier_contraction_records[0]
    assert first_record.tier_index == 0
    assert first_record.eligible_base_edges == (hidden.edge,)
    assert first_record.selected_base_edges == (hidden.edge,)
    assert first_record.retired_base_edges == (hidden.edge,)
    assert runtime.tower_stopping_reason == "no_nontrivial_remainder"


def test_partition_backend_reset_builds_partition_tower_snapshot() -> None:
    runtime, hidden = build_runtime()

    snapshot = runtime.reset(initial_state=hidden.s1)

    assert runtime.partition_tower is not None
    assert snapshot.partition_tower_view is runtime.partition_tower
    assert snapshot.tower_update_result is runtime.last_tower_update_result
    assert len(snapshot.current_position_at_every_tier) == 2
    assert runtime.states_share_coset(hidden.s1, hidden.s2, 1)
    assert snapshot.current_position_at_every_tier[0] is not None
    assert snapshot.current_position_at_every_tier[1] is not None


def test_partition_backend_step_preserves_runtime_queries() -> None:
    runtime, hidden = build_runtime()
    runtime.reset(initial_state=hidden.s1)

    snapshot = runtime.step(hidden.a)

    assert snapshot.current_base_state == hidden.s2
    assert runtime.current_deepest_tier() == 1
    assert runtime.project_state_to_tier(hidden.s2, 1) is not None
    assert runtime.projected_edge_is_trivial_at_tier(hidden.edge, 1) is True
    assert runtime.states_share_coset(hidden.s1, hidden.s2, 1) is True
    assert runtime.last_tower_update_result is not None
    assert runtime.last_tower_update_result.changed is False
    assert runtime.tower_stopping_reason == "partition_noop"


def test_default_runtime_backend_is_partition_and_schema_driven() -> None:
    runtime, hidden = build_runtime()

    runtime.reset(initial_state=hidden.s1)

    assert runtime.partition_tower is not None
    assert runtime.tier_contraction_records == ()
    assert runtime.last_tower_update_result is not None
    assert runtime.last_tower_update_result.schema_assignments
    assert runtime.last_tower_update_result.diagnostics.discovered_state_count == 2
    assert runtime.last_tower_update_result.diagnostics.discovered_edge_count == 1
    assert runtime.last_tower_update_result.diagnostics.full_rebuild_validation_count == 0
    assert runtime.selected_base_edges == (hidden.edge,)
    assert runtime.projected_edge_is_trivial_at_tier(hidden.edge, 1)


def test_partition_backend_step_uses_local_delta_candidates(monkeypatch) -> None:
    runtime, hidden = build_runtime()
    runtime.reset(initial_state=hidden.s1)

    def fail_global_visible_graph_scan():
        raise AssertionError("normal partition step should not scan the full visible graph")

    monkeypatch.setattr(runtime, "_visible_base_graph", fail_global_visible_graph_scan)

    snapshot = runtime.step(hidden.a)

    assert snapshot.current_base_state == hidden.s2


def test_partition_backend_default_step_does_not_build_compatibility_readout(
    monkeypatch,
) -> None:
    runtime, hidden = build_runtime()
    runtime.reset(initial_state=hidden.s1)
    assert runtime.partition_tower is not None

    def fail_readout(self: PartitionTower) -> tuple[object, ...]:
        del self
        raise AssertionError("default step should not build quotient-tier readouts")

    monkeypatch.setattr(PartitionTower, "to_quotient_tier_views", fail_readout)

    snapshot = runtime.step(hidden.a)

    assert snapshot.current_base_state == hidden.s2
    assert snapshot.ordered_quotient_tiers == ()


def test_partition_backend_compatibility_readout_is_explicit_and_cached(
    monkeypatch,
) -> None:
    runtime, hidden = build_runtime()
    runtime.reset(initial_state=hidden.s1)
    assert runtime.partition_tower is not None

    readouts = runtime.compatibility_quotient_tiers()
    assert len(readouts) == 2

    def fail_readout(self: PartitionTower) -> tuple[object, ...]:
        del self
        raise AssertionError("cached readout should be reused")

    monkeypatch.setattr(PartitionTower, "to_quotient_tier_views", fail_readout)

    assert runtime.compatibility_quotient_tiers() == readouts


def test_partition_backend_step_invalidates_compatibility_readout_cache() -> None:
    runtime, hidden = build_runtime()
    runtime.reset(initial_state=hidden.s1)
    assert runtime.compatibility_quotient_tiers()

    runtime.step(hidden.a)

    assert runtime._compatibility_quotient_tiers is None
    assert runtime.compatibility_quotient_tiers()
