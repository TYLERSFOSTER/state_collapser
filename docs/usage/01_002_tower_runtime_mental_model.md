# Tower Runtime Mental Model

The runtime source of truth is the discovered total transition graph together
with nested state/action partition tables.

The notation `G_t^0` should be read as the total discovered graph at time `t`.
It is not globally "the base graph" in new user-facing vocabulary, because
"base" is relative to a projection. The package keeps compatibility names where
older APIs already use them, but new training surfaces should prefer:

- total graph
- total state
- fine tier
- coarse tier
- upstairs
- downstairs

## Tier Direction

Tier `0` is the finest implemented tier: the total discovered graph.

Increasing tier index means moving to a coarser quotient:

```text
tier 0      finest / total discovered graph
tier 1      coarser quotient
tier 2      still coarser quotient
...
```

So an adjacent first-scope fiber-conditioned training stage uses:

```text
fine_tier = i
coarse_tier = i + 1
```

## Partition Tower

The runtime partition tower is implemented by
`state_collapser.tower.partition.PartitionTower`.

Conceptually it stores:

- a registry for total states and concrete edges
- state partition layers by tier
- action partition layers by tier
- outgoing action collections attached to state cells
- decision-level action cells inside those outgoing collections

The compatibility `QuotientTierView` readouts are not the hot-path source of
truth. They are materialized readouts for older code and inspection. New runtime
queries should use `PartitionTower` directly.

## Local Query Vocabulary

Important runtime queries include:

- `current_state_cell(tier, state)`
- `state_cell_members(tier, state_cell_id)`
- `outgoing_action_cells(tier, state_cell_id)`
- `action_cell_members(tier, action_cell_id)`
- `action_cell_for_edge(tier, edge)`
- `representative_edges(tier, action_cell_id)`
- `lift_candidates(tier, action_cell_id, current_state)`
- `executable_lift_candidates(tier, action_cell_id, current_state)`
- `executable_action_cells(tier, state_cell_id, current_state)`
- `tier_is_executable_from_state(tier, current_state)`
- `supported_child_state_cells(tier, action_cell_id)`
- `active_child_state_cells(tier, state_cell_id)`
- `lower_action_cells_for_supported_child(tier, action_cell_id, child_state_cell_id)`
- `refinement_fiber(tier, cell_id)`

`PathFiber` composes these local tower queries into a training-stage view: given
a frozen coarse behavior, it identifies the fine actions that live over that
behavior.

## Quotient Availability Versus Executable Liftability

Do not use `outgoing_action_cells(...)` as a direct runtime executability
predicate.

After contraction, a state cell may pool outgoing action data from several
concrete representatives. Therefore:

```text
outgoing_action_cells(tier, state_cell_id)
```

answers the quotient/readout question:

```text
Which abstract action cells hang over this state cell?
```

It does not answer:

```text
Which abstract action cells have a concrete edge sourced at the current base
state?
```

For pointwise execution, use:

```text
executable_action_cells(tier, state_cell_id, current_state)
executable_lift_candidates(tier, action_cell_id, current_state)
tier_is_executable_from_state(tier, current_state)
```

The older `lift_candidates(...)` method remains representative/readout
compatible: it prefers current-source edges but may fall back to deterministic
representatives from elsewhere in the quotient cell. That is useful for
quotient reasoning and inspection, but executable control and learner masks
should use the strict executable APIs.

The adjacent support APIs expose the Young-diagram structure directly:

```text
supported_child_state_cells(...)
active_child_state_cells(...)
lower_action_cells_for_supported_child(...)
```

These queries point from a tier-`i` action/state cell to tier-`i-1` child bins
that actually support outgoing action data. Flattened current-state execution
checks are a hot-path materialization of that recursive support structure.

## Executable Tiers And Empty Outgoing Cells

Not every coarse tier is necessarily an executable action surface at every
runtime state. A coarse state cell can validly swallow all currently outgoing
edges into internal loops, leaving:

```text
outgoing_action_cells(tier, current_state_cell) == ()
```

That is not a partition-tower bug. It means the tier is an address,
diagnostic, or pass-through level for the current decision rather than a place
where a learner should choose an action.

The exploit/explore active-tier runtime handles this by lifting through
empty-`Out` tiers until it reaches the nearest finer tier with executable
outgoing action cells. Only if tier `0` also has empty outgoing actions does
the runtime return a no-action control result.

This empty-`Out` guard is necessary but not sufficient for pointwise
liftability. A tier can have nonempty quotient `Out` while no selected abstract
action is executable from the current concrete representative. Runtime
predicates should therefore check pointwise executable liftability, not merely
nonempty quotient outgoing data.
