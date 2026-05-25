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
- `refinement_fiber(tier, cell_id)`

`PathFiber` composes these local tower queries into a training-stage view: given
a frozen coarse behavior, it identifies the fine actions that live over that
behavior.
