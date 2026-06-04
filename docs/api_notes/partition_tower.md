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
- `executable_action_cells(tier, state_cell_id, current_state)`
- `action_cell_members(tier, action_cell_id)`
- `action_cell_for_edge(tier, edge)`
- `lift_candidates(tier, action_cell_id, current_state)`
- `executable_lift_candidates(tier, action_cell_id, current_state)`
- `tier_is_executable_from_state(tier, current_state)`

These methods do not require building `QuotientTierView` readouts.

## Quotient Queries Versus Pointwise Execution

`outgoing_action_cells(...)` is a quotient-level query. It returns abstract
action cells attached to a state cell after outgoing action data has been
pooled across representatives.

`lift_candidates(...)` is representative/readout-compatible. It prefers edges
sourced at the current state, but if none exist it may return deterministic
representatives from elsewhere in the quotient cell.

Executable control should use the strict pointwise methods:

- `executable_lift_candidates(...)`
- `executable_action_cells(...)`
- `tier_is_executable_from_state(...)`

Those methods return only action cells or edges with concrete current-state
support.

## Adjacent Source-Support Queries

The source-support structure is represented through adjacent Young-diagram
pointers:

- `supported_child_state_cells(tier, action_cell_id)`
- `active_child_state_cells(tier, state_cell_id)`
- `lower_action_cells_for_supported_child(tier, action_cell_id, child_state_cell_id)`

These queries expose tier-`i` support in terms of tier-`i-1` child bins. They
are the recursive structure behind the flattened executable-lift queries.

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
