"""Integration tests for the end-to-end vertical slice."""

from __future__ import annotations

from state_collapser.contract.policy import LabelContractionPolicy, SeededRandomContractionPolicy
from state_collapser.core.action import PrimitiveAction
from state_collapser.examples.robot_constraint_toy import run_robot_constraint_vertical_slice


def test_discovered_graph_grows_over_time() -> None:
    actions = (
        PrimitiveAction(payload=("move", "right"), identity="action:right"),
        PrimitiveAction(payload=("move", "right"), identity="action:right"),
    )

    snapshots = run_robot_constraint_vertical_slice(actions)

    assert len(snapshots[0].explored_graph.current_path()) < len(
        snapshots[-1].explored_graph.current_path()
    )


def test_vista_graph_grows_over_time() -> None:
    actions = (PrimitiveAction(payload=("move", "up"), identity="action:up"),)
    snapshots = run_robot_constraint_vertical_slice(actions)
    start_state = snapshots[0].current_base_state

    assert snapshots[0].vista_graph.vista_edges(start_state)
    assert snapshots[-1].vista_graph.vista_edges(start_state)


def test_push_pull_changes_annotation_state() -> None:
    actions = (
        PrimitiveAction(payload=("move", "up"), identity="action:up"),
        PrimitiveAction(payload=("move", "up"), identity="action:up"),
    )
    snapshots = run_robot_constraint_vertical_slice(
        actions,
        contraction_policy=LabelContractionPolicy(labels=frozenset({"hinge", "safe", "elbow"})),
        include_compatibility_readouts=True,
    )
    final_snapshot = snapshots[-1]
    source_state = snapshots[-2].current_base_state
    next_state = final_snapshot.current_base_state

    assert final_snapshot.vista_graph.node_payload(next_state).pushed_payloads
    assert final_snapshot.vista_graph.node_payload(source_state).pulled_payloads


def test_both_contraction_policies_work_in_same_runtime_pipeline() -> None:
    actions = (
        PrimitiveAction(payload=("move", "right"), identity="action:right"),
        PrimitiveAction(payload=("move", "right"), identity="action:right"),
        PrimitiveAction(payload=("move", "up"), identity="action:up"),
        PrimitiveAction(payload=("move", "up"), identity="action:up"),
    )

    label_snapshots = run_robot_constraint_vertical_slice(
        actions,
        contraction_policy=LabelContractionPolicy(labels=frozenset({"hinge", "safe", "elbow"})),
    )
    random_snapshots = run_robot_constraint_vertical_slice(
        actions,
        contraction_policy=SeededRandomContractionPolicy(seed=7, sample_size=1),
    )

    assert label_snapshots[-1].current_base_state is not None
    assert random_snapshots[-1].current_base_state is not None


def test_quotient_tier_views_update_cumulatively() -> None:
    actions = (PrimitiveAction(payload=("move", "up"), identity="action:up"),)
    snapshots = run_robot_constraint_vertical_slice(
        actions,
        contraction_policy=LabelContractionPolicy(labels=frozenset({"hinge", "safe", "elbow"})),
        include_compatibility_readouts=True,
    )
    tier = snapshots[-1].ordered_quotient_tiers[0]

    assert tier.current_position is not None
    assert tier.outgoing_edge_knowledge_upto(0)


def test_reward_aggregation_works() -> None:
    actions = (
        PrimitiveAction(payload=("move", "right"), identity="action:right"),
        PrimitiveAction(payload=("move", "right"), identity="action:right"),
        PrimitiveAction(payload=("move", "up"), identity="action:up"),
        PrimitiveAction(payload=("move", "up"), identity="action:up"),
    )
    snapshots = run_robot_constraint_vertical_slice(actions)

    assert snapshots[-1].cumulative_path_reward.total == 4.0


def test_runtime_snapshots_remain_coherent() -> None:
    actions = (PrimitiveAction(payload=("move", "right"), identity="action:right"),)
    snapshots = run_robot_constraint_vertical_slice(actions)
    final_snapshot = snapshots[-1]

    assert final_snapshot.current_base_state == final_snapshot.explored_graph.current_state()
    assert final_snapshot.current_position_at_every_tier
    assert final_snapshot.ordered_quotient_tiers == ()
