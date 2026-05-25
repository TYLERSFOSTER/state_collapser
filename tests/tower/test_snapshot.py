"""Tests for runtime views and value snapshots."""

from __future__ import annotations

from state_collapser.core.rewards import PathRewardSummary, QuotientRewardSummary, StepReward
from state_collapser.graph.explored_graph import ExploredGraph
from state_collapser.graph.vista_graph import VistaGraph
from state_collapser.quotient.tier_view import QuotientTierView
from state_collapser.tower.snapshot import LiveRuntimeView, RuntimeSnapshot


def test_live_runtime_view_completeness() -> None:
    view = LiveRuntimeView(
        current_base_state=None,
        explored_graph=ExploredGraph(),
        vista_graph=VistaGraph(hidden_graph=None, explored_graph=ExploredGraph()),
        ordered_quotient_tiers=(QuotientTierView(tier=0),),
        current_position_at_every_tier=(None,),
        current_step_reward=StepReward(value=1.0),
        cumulative_path_reward=PathRewardSummary(step_rewards=(), total=0.0),
        quotient_tier_reward_summaries=(
            QuotientRewardSummary(contributing_rewards=(), mean_reward=0.0),
        ),
    )

    assert view.current_base_state is None
    assert len(view.ordered_quotient_tiers) == 1
    assert view.current_position_at_every_tier == (None,)
    assert view.partition_tower_view is None
    assert view.tower_update_result is None


def test_live_runtime_view_produces_value_snapshot() -> None:
    view = LiveRuntimeView(
        current_base_state="s0",
        explored_graph=ExploredGraph(),
        vista_graph=VistaGraph(hidden_graph=None, explored_graph=ExploredGraph()),
        ordered_quotient_tiers=(QuotientTierView(tier=0),),
        current_position_at_every_tier=("q0",),
        current_step_reward=StepReward(value=1.0),
        cumulative_path_reward=PathRewardSummary(
            step_rewards=(StepReward(value=1.0),),
            total=1.0,
        ),
        quotient_tier_reward_summaries=(),
    )

    snapshot = view.to_snapshot()

    assert isinstance(snapshot, RuntimeSnapshot)
    assert snapshot.current_base_state == "s0"
    assert snapshot.current_step_reward_value == 1.0
    assert snapshot.cumulative_reward_total == 1.0
    assert snapshot.quotient_tier_count == 1


def test_runtime_snapshot_is_value_shape_without_live_graph_fields() -> None:
    snapshot = RuntimeSnapshot(
        current_base_state="s0",
        current_position_at_every_tier=("q0",),
        current_step_reward_value=None,
        cumulative_reward_total=0.0,
        cumulative_reward_count=0,
        quotient_tier_count=1,
    )

    assert not hasattr(snapshot, "explored_graph")
    assert not hasattr(snapshot, "vista_graph")
    assert not hasattr(snapshot, "partition_tower_view")
