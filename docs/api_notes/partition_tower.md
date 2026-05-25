# API Note: PartitionTower

`PartitionTower` is the runtime source of truth for nested state/action
partitions.

It owns:

- the total graph registry
- state partition layers
- action partition layers
- outgoing action collections
- decision-level action cells
- incremental update records

Compatibility quotient-tier readouts are available, but they are not the source
of truth for new fiber-conditioned training surfaces.

## Query Methods Used By PathFiber

`PathFiber` uses these tower methods directly:

- `current_state_cell(tier, state)`
- `outgoing_action_cells(tier, state_cell_id)`
- `action_cell_members(tier, action_cell_id)`
- `action_cell_for_edge(tier, edge)`
- `lift_candidates(tier, action_cell_id, current_state)`

These methods do not require building `QuotientTierView` readouts.

## Query Methods Used By HGraphML

`HGraphML` uses `PartitionTower` as a full-graph quotient constructor for graph
message passing. Its adapter currently relies on:

- `build_partition_tower_full(...)`
- `state_layers`
- `state_layer.all_cell_ids()`
- `state_layer.members(state_cell_id)`
- `state_layer.cell_of_state_id`
- `registry.state_for_id(state_id)`
- `registry.edge_ids`
- `registry.edge_for_id(edge_id)`
- `registry.source_state_id(edge_id)`
- `registry.target_state_id(edge_id)`

These queries let HGraphML recover node fibers, edge fibers, and coarse graph
readouts by tier without asking `state_collapser` to own the graph-ML message
passing loop.

## Compatibility Readouts

Use `to_quotient_tier_views()` or runtime compatibility methods only when an old
consumer needs quotient-tier view objects or when inspecting readout behavior.
Do not put those calls into hot-path stage stepping unless the design explicitly
requires it.
