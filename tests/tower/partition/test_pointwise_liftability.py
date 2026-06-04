"""Tests for pointwise liftability versus quotient availability."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.ids import ActionCellId
from state_collapser.tower.partition.schema import DimensionwiseSchema
from state_collapser.tower.partition.tower import PartitionTower


def state(name: str) -> State:
    """Build a named test state."""

    return State(payload=(name,), identity=name)


def action(label: str) -> PrimitiveAction:
    """Build a primitive action whose canonical identity is the label."""

    return PrimitiveAction(payload=(label,), identity=(label,), labels=(label,))


def edge(source: State, label: str, target: State) -> BaseEdge:
    """Build a labelled base edge."""

    return BaseEdge(source=source, action=action(label), target=target, labels=(label,))


def build_asymmetric_lift_tower() -> tuple[
    PartitionTower,
    State,
    State,
    State,
    BaseEdge,
    BaseEdge,
    BaseEdge,
    BaseEdge,
]:
    """Build the asymmetric quotient-available but not pointwise-liftable graph."""

    zero = state("0")
    one = state("1")
    two = state("2")
    contract = edge(zero, "contract", one)
    zero_to_two = edge(zero, "to2", two)
    one_to_two = edge(one, "to2", two)
    one_only = edge(one, "one_only", two)
    tower = PartitionTower(schema=DimensionwiseSchema(("contract",)))
    tower.initialize(
        initial_states=(zero, one, two),
        initial_edges=(contract, zero_to_two, one_to_two, one_only),
        current_state=zero,
    )
    return tower, zero, one, two, contract, zero_to_two, one_to_two, one_only


def build_recursive_support_tower() -> tuple[
    PartitionTower,
    State,
    State,
    State,
    State,
    BaseEdge,
    BaseEdge,
    BaseEdge,
    BaseEdge,
]:
    """Build a two-step nested contraction with outgoing support at tier 2."""

    zero = state("0")
    one = state("1")
    two = state("2")
    three = state("3")
    contract_zero_one = edge(zero, "contract01", one)
    contract_one_two = edge(one, "contract12", two)
    zero_to_three = edge(zero, "to3", three)
    two_to_three = edge(two, "to3", three)
    tower = PartitionTower(schema=DimensionwiseSchema(("contract01", "contract12")))
    tower.initialize(
        initial_states=(zero, one, two, three),
        initial_edges=(
            contract_zero_one,
            contract_one_two,
            zero_to_three,
            two_to_three,
        ),
        current_state=zero,
    )
    return (
        tower,
        zero,
        one,
        two,
        three,
        contract_zero_one,
        contract_one_two,
        zero_to_three,
        two_to_three,
    )


def action_cell_with_member(
    tower: PartitionTower,
    tier: int,
    candidates: tuple[ActionCellId, ...],
    member: BaseEdge,
) -> ActionCellId:
    """Return the action cell among candidates that contains a member edge."""

    for action_cell_id in candidates:
        if member in tower.action_cell_members(tier, action_cell_id):
            return action_cell_id
    raise AssertionError(f"could not find action cell containing {member!r}")


def test_quotient_action_availability_can_include_non_current_source_edges() -> None:
    """A quotient state cell can expose action data sourced at another member."""

    tower, zero, one, _two, _contract, _zero_to_two, _one_to_two, one_only = (
        build_asymmetric_lift_tower()
    )
    merged_cell = tower.current_state_cell(1, zero)

    assert merged_cell == tower.current_state_cell(1, one)
    assert merged_cell is not None
    assert set(tower.state_cell_members(1, merged_cell)) == {zero, one}

    action_cells = tower.outgoing_action_cells(1, merged_cell)
    one_only_cell = action_cell_with_member(tower, 1, action_cells, one_only)

    assert one_only in tower.action_cell_members(1, one_only_cell)


def test_lift_candidates_preserve_existing_representative_fallback_semantics() -> None:
    """The current lift API remains representative/readout-compatible."""

    tower, zero, _one, _two, _contract, _zero_to_two, _one_to_two, one_only = (
        build_asymmetric_lift_tower()
    )
    merged_cell = tower.current_state_cell(1, zero)
    assert merged_cell is not None
    one_only_cell = action_cell_with_member(
        tower,
        1,
        tower.outgoing_action_cells(1, merged_cell),
        one_only,
    )

    assert tower.lift_candidates(1, one_only_cell, zero) == (one_only,)


def test_executable_lift_candidates_are_strictly_pointwise() -> None:
    """Strict executable lifts never fall back to another source representative."""

    tower, zero, one, _two, _contract, _zero_to_two, _one_to_two, one_only = (
        build_asymmetric_lift_tower()
    )
    merged_cell = tower.current_state_cell(1, zero)
    assert merged_cell is not None
    one_only_cell = action_cell_with_member(
        tower,
        1,
        tower.outgoing_action_cells(1, merged_cell),
        one_only,
    )

    assert tower.executable_lift_candidates(1, one_only_cell, zero) == ()
    assert tower.executable_lift_candidates(1, one_only_cell, one) == (one_only,)


def test_executable_action_cells_filter_non_current_source_actions() -> None:
    """Executable action cells are quotient actions with current-source support."""

    tower, zero, one, _two, _contract, zero_to_two, _one_to_two, one_only = (
        build_asymmetric_lift_tower()
    )
    merged_cell = tower.current_state_cell(1, zero)
    assert merged_cell is not None
    action_cells = tower.outgoing_action_cells(1, merged_cell)
    one_only_cell = action_cell_with_member(tower, 1, action_cells, one_only)
    zero_to_two_cell = action_cell_with_member(tower, 1, action_cells, zero_to_two)

    assert one_only_cell not in tower.executable_action_cells(1, merged_cell, zero)
    assert zero_to_two_cell in tower.executable_action_cells(1, merged_cell, zero)
    assert one_only_cell in tower.executable_action_cells(1, merged_cell, one)


def test_tier_is_executable_from_state_uses_pointwise_action_support() -> None:
    """Tier executability is about the current state, not abstract Out alone."""

    tower, zero, _one, _two, _contract, _zero_to_two, _one_to_two, _one_only = (
        build_asymmetric_lift_tower()
    )
    unknown = state("unknown")

    assert tower.tier_is_executable_from_state(1, zero)
    assert not tower.tier_is_executable_from_state(-1, zero)
    assert not tower.tier_is_executable_from_state(999, zero)
    assert not tower.tier_is_executable_from_state(1, unknown)


def test_recursive_fixture_builds_nested_state_cells_for_future_support_queries() -> None:
    """The recursive fixture exposes tier-2 cells refined by tier-1 child bins."""

    tower, zero, one, two, _three, *_edges = build_recursive_support_tower()

    tier_one_zero_cell = tower.current_state_cell(1, zero)
    tier_one_one_cell = tower.current_state_cell(1, one)
    tier_one_two_cell = tower.current_state_cell(1, two)
    tier_two_zero_cell = tower.current_state_cell(2, zero)
    tier_two_two_cell = tower.current_state_cell(2, two)

    assert tier_one_zero_cell == tier_one_one_cell
    assert tier_one_zero_cell != tier_one_two_cell
    assert tier_two_zero_cell == tier_two_two_cell
    assert tier_two_zero_cell is not None

    state_fiber = tower.refinement_fiber(2, tier_two_zero_cell)

    assert set(state_fiber) == {tier_one_zero_cell, tier_one_two_cell}


def test_recursive_support_apis_return_adjacent_child_bins() -> None:
    """Tier-2 support points to tier-1 child bins before flattening to states."""

    (
        tower,
        zero,
        _one,
        two,
        _three,
        _contract_zero_one,
        _contract_one_two,
        zero_to_three,
        two_to_three,
    ) = build_recursive_support_tower()
    tier_two_cell = tower.current_state_cell(2, zero)
    tier_one_zero_cell = tower.current_state_cell(1, zero)
    tier_one_two_cell = tower.current_state_cell(1, two)
    assert tier_two_cell is not None
    assert tier_one_zero_cell is not None
    assert tier_one_two_cell is not None
    tier_two_action = action_cell_with_member(
        tower,
        2,
        tower.outgoing_action_cells(2, tier_two_cell),
        zero_to_three,
    )
    zero_to_three_tier_one = tower.action_cell_for_edge(1, zero_to_three)
    two_to_three_tier_one = tower.action_cell_for_edge(1, two_to_three)

    assert set(tower.supported_child_state_cells(2, tier_two_action)) == {
        tier_one_zero_cell,
        tier_one_two_cell,
    }
    assert tower.lower_action_cells_for_supported_child(
        2,
        tier_two_action,
        tier_one_zero_cell,
    ) == (zero_to_three_tier_one,)
    assert tower.lower_action_cells_for_supported_child(
        2,
        tier_two_action,
        tier_one_two_cell,
    ) == (two_to_three_tier_one,)
    assert set(tower.active_child_state_cells(2, tier_two_cell)) == {
        tier_one_zero_cell,
        tier_one_two_cell,
    }
