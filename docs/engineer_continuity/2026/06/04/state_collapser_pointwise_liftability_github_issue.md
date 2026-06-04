# Draft GitHub Issue: Abstract Action Availability Is Being Confused With Pointwise Executable Liftability

## Summary

`state_collapser` currently exposes quotient/tower action availability in a way
that makes it easy for downstream runtime code to confuse:

```text
abstract action cells available from a quotient state cell
```

with:

```text
abstract action cells that have at least one concrete edge executable from the
current total/base state
```

Those are not equivalent after state contraction. A quotient state cell pools
outgoing action information across its representatives. A selected abstract
action may therefore have concrete representatives whose source is some other
state in the same quotient cell, but no representative whose source is the
runtime's current concrete state.

The bug class surfaced downstream in `big_boy_benchmarking` counterpoint
evaluations as repeated `no_lift_candidate_from_current_state` failures: the
controller selected a tier that had nonempty abstract outgoing action cells,
but the chosen action cells did not lift to executable concrete actions from
the current concrete state.

## Project Owner Observation

The Project Owner identified the core issue using a simplex-style example:

```text
Contract [0] -> [1].
The quotient cell [0,1] may have outgoing actions to [2].
But a lift from current representative [0] is executable only if the action has
a concrete edge sourced at [0].
```

The required lift rule is therefore not merely:

```text
choose an abstract state cell, choose one of its abstract action cells, then
choose a representative lift
```

It must be closer to:

```text
given current total state s inside quotient state cell C,
choose only action cells A such that A contains at least one concrete edge
whose source is s
```

Equivalently: lift from preimage states with nonempty `Out` for the selected
action, not merely from the preimage state set.

## Current Behavior

In `src/state_collapser/tower/partition/tower.py`, `PartitionTower.outgoing_action_cells`
returns the action cells attached to the current abstract state cell:

```python
collection_id = action_layer.outgoing_collection(state_cell_id)
return action_layer.action_cells_for_collection(collection_id)
```

That is quotient-level availability. It does not inspect the current concrete
state.

In the same file, `PartitionTower.lift_candidates` prefers representative edges
whose source is the current concrete state, but falls back to generic
representatives when none are directly executable:

```python
representatives = self.representative_edges(tier, action_cell_id)
directly_executable = tuple(
    edge for edge in representatives if edge.source == current_base_state
)
return directly_executable if directly_executable else representatives
```

That fallback is useful for quotient readout/reasoning, but it is dangerous
when downstream code treats `lift_candidates` as an executable-lift API.

## Minimal Reproduction

This tiny graph exposes the issue.

```python
from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.schema import DimensionwiseSchema
from state_collapser.tower.partition.tower import PartitionTower


def s(name):
    return State(payload=(name,), identity=name)


def a(label):
    return PrimitiveAction(payload=(label,), identity=(label,), labels=(label,))


def e(src, label, dst):
    return BaseEdge(source=src, action=a(label), target=dst, labels=(label,))


zero = s("0")
one = s("1")
two = s("2")

contract = e(zero, "contract", one)
zero_two = e(zero, "to2", two)
one_two = e(one, "to2", two)
one_only = e(one, "one_only", two)

tower = PartitionTower(schema=DimensionwiseSchema(("contract",)))
tower.initialize(
    initial_states=(zero, one, two),
    initial_edges=(contract, zero_two, one_two, one_only),
    current_state=zero,
)

cell = tower.current_state_cell(1, zero)
for action_cell in tower.outgoing_action_cells(1, cell):
    print(action_cell)
    print("members:", tower.action_cell_members(1, action_cell))
    print("lift from zero:", tower.lift_candidates(1, action_cell, zero))
```

Observed behavior includes an action cell whose only member is sourced at
`one`, but `lift_candidates(..., current_base_state=zero)` returns that edge as
a fallback representative.

Conceptually:

```text
quotient cell [0,1] has action one_only -> [2]
current concrete state is 0
there is no concrete one_only edge from 0
yet the current API can still surface the one_only representative as a lift
candidate
```

## Expected Behavior

The package should expose a first-class pointwise liftability API, and runtime
docs should distinguish it from quotient-level availability.

Possible API surface:

```python
PartitionTower.executable_action_cells(
    tier: int,
    state_cell_id: StateCellId,
    current_base_state: State,
) -> tuple[ActionCellId, ...]

PartitionTower.executable_lift_candidates(
    tier: int,
    action_cell_id: ActionCellId,
    current_base_state: State,
) -> tuple[BaseEdge, ...]

PartitionTower.tier_is_executable_from_state(
    tier: int,
    current_base_state: State,
) -> bool
```

The strict executable-lift query should return only concrete edges whose
`edge.source == current_base_state`. It should return an empty tuple when no
such edge exists.

The existing representative fallback can remain available, but it should be
named/documented as quotient representatives, not executable lift candidates.

## Downstream Impact

Downstream runtimes currently need to implement `tier_is_executable`. It is
natural, and currently easy, to implement it as:

```python
bool(tower.outgoing_action_cells(tier, current_state_cell))
```

That catches fully empty quotient-action surfaces, but it does not catch the
more subtle failure where a quotient state cell has outgoing abstract actions
and none of those actions is executable from the current concrete state.

This is the likely cause of repeated `no_lift_candidate_from_current_state`
failures observed in BBB counterpoint evaluations.

## Acceptance Criteria

- Add tests showing an asymmetric contracted cell where quotient outgoing
  actions exist but no action is executable from one representative.
- Add strict pointwise executable-lift query methods.
- Keep quotient/readout representative queries available, but rename or document
  them so they are not mistaken for executable lift.
- Update `PathFiber.admissible_action_cells`, `PathFiber.action_mask`, and
  `FiberConditionedStage.step` so learner-facing action masks only mark actions
  executable from the current total state.
- Update example runtime executable-tier predicates, especially
  `plate_support_env`, so they use pointwise executable-liftability rather than
  nonempty abstract outgoing action cells.
- Update docs to distinguish:
  - quotient-level outgoing action availability;
  - representative/readout lift candidates;
  - current-state executable lift candidates.

