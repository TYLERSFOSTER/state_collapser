# Young Tableaux Runtime Refactor Implementation Gameplan

## Status

This document is the Phase.Stage.Action implementation gameplan for:

- `docs/design/Young_tableaux_refactor/01_001_young_tableaux_runtime_refactor_blueprint.md`

It is downstream of:

- `docs/code_review/01_001_loghrl_partition_tower_vs_src_review.md`
- `docs/design/logHRL.tex`
- `docs/prime_directive/prime_directive.md`
- `docs/prime_directive/git_practices.md`
- `docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md`
- `docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md`

This is an implementation gameplan.

It is not an implementation.

No source-code execution should begin until the Project Owner explicitly approves
execution of this gameplan.

Once approved, this gameplan is law. If implementation reality conflicts with
any action below, the implementer must stop, identify the exact
Phase.Stage.Action item that failed, and ask the Project Owner for guidance.
Silent simplification is forbidden.

## Readiness Assessment

The blueprint is complete enough to create an implementation gameplan.

The remaining open questions are not conceptual blockers. They are implementation
defaults and rollout choices. This gameplan fixes those defaults explicitly so
the future execution phase does not encode hidden design decisions.

## Fixed Defaults For This Gameplan

Unless the Project Owner changes these before execution, implementation should
use the following defaults.

1. Internal ids use frozen `slots=True` dataclasses wrapping integers and tier
   metadata where needed. This is slightly more verbose than raw integers, but it
   protects the refactor from mixing `StateId`, `EdgeId`, `StateCellId`, and
   `ActionCellId` during the first correctness-focused implementation. If later
   benchmarks show overhead, the ids can be optimized.

2. The new tower package lives under:

   ```text
   src/state_collapser/tower/partition/
   ```

   The schema protocol also lives there at first. The old
   `src/state_collapser/contract/policy.py` remains the local-star policy module.

3. Storage-level outgoing action data is called an `ActionCollection`.

4. Decision-level selectable abstract action classes are called `ActionCell`.

5. The first integration uses a `tower_backend` option internally, but the
   implementation must switch the default runtime backend to the partition tower
   before the gameplan is complete. The legacy builder may remain as a validator
   and fallback, but not as the normal final runtime path.

6. The canonical first schema example is a small synthetic tower test graph, not
   a large environment. `robot_constraint_toy` becomes the first example-family
   schema smoke test after the synthetic tests pass.

7. The first random-at-rate schema assigns each newly discovered edge to a
   persistent random block using a seeded PRNG and stored edge assignment. It
   must never resample old edges.

8. `QuotientTierView` readouts may be built eagerly for snapshots in the first
   green integration slice, but update diagnostics must count readout rebuilds
   separately from partition-core updates.

9. First-scope loop policy is `drop_internal` with recorded diagnostics. The
   `formal_stutter` policy should be represented in types/config where cheap,
   but full formal-stutter path semantics are not required before the first
   partition backend becomes default.

10. Reward aggregation is first implemented as standalone utilities and summary
    structures, then lightly wired into runtime summaries only where existing
    reward surfaces already expect quotient summaries.

11. The legacy `build_dynamic_tower(...)` remains until after partition backend
    runtime tests, integration tests, and example smoke tests pass. It should
    then be demoted to explicit legacy/validation naming, not silently deleted.

## Global Stop Conditions

Implementation must stop and ask the Project Owner if any of the following
occur.

- A Phase.Stage.Action item cannot be implemented as written.
- A proposed simplification would be needed.
- A file or symbol named in this gameplan no longer exists.
- A current test encodes behavior that directly contradicts the blueprint.
- A runtime error reveals a mismatch between this gameplan and repository
  reality.
- The partition update algorithm would require global scans in the normal step
  path contrary to the blueprint.
- The code cannot preserve existing primitive-action training loops without a
  broader design choice.
- A change would require modifying unrelated files outside the named scope of
  the current phase.

## Required Branch Discipline

Execution must not start on `main`.

Before touching implementation code, create or switch to:

```text
codex/young-tableaux-runtime-refactor
```

If the Project Owner requests a different branch name, use that name.

## Required Running Implementation Log

Execution must maintain:

```text
docs/design/Young_tableaux_refactor/01_003_young_tableaux_runtime_refactor_implementation_log.md
```

The log must record:

- each completed Phase.Stage.Action item
- exact tests run
- test outcomes
- surprises
- stop conditions
- Project Owner clarifications
- any authorized deviations

The log must not hide simplified work behind words like "first pass" unless the
Project Owner explicitly authorizes that simplification.

## Validation Command Set

The implementation should use increasingly broad validation.

Small focused validation:

```text
uv run pytest tests/tower tests/quotient
```

Runtime and integration validation:

```text
uv run pytest tests/tower tests/quotient tests/integration
```

Example smoke validation:

```text
uv run pytest tests/examples
```

Full validation:

```text
uv run pytest
```

If any validation command fails unexpectedly, stop and reconstruct reality before
editing further.

## Phase 0: Execution Setup And Reality Binding

### Stage 0.1: Confirm Execution Authority

#### Action 0.1.1

Confirm the Project Owner has explicitly approved execution of this gameplan.

Completion criteria:

- There is an explicit owner message approving implementation.
- The implementation log records that approval.

Stop condition:

- If approval is ambiguous, do not implement.

#### Action 0.1.2

Create or switch to the dedicated implementation branch.

Required branch:

```text
codex/young-tableaux-runtime-refactor
```

Completion criteria:

- The active branch is the implementation branch.
- `git status --short` is recorded in the implementation log.

Stop condition:

- If the working tree contains unrelated changes in files this gameplan needs to
  edit, stop and ask the Project Owner how to proceed.

### Stage 0.2: Bind Current Repository Reality

#### Action 0.2.1

Re-read these current files from disk:

```text
src/state_collapser/tower/runtime.py
src/state_collapser/tower/construction.py
src/state_collapser/tower/snapshot.py
src/state_collapser/quotient/tier_view.py
src/state_collapser/quotient/projection.py
src/state_collapser/quotient/cosets.py
src/state_collapser/contract/policy.py
src/state_collapser/core/rewards.py
src/state_collapser/core/action.py
src/state_collapser/core/edges.py
src/state_collapser/graph/explored_graph.py
src/state_collapser/graph/vista_graph.py
src/state_collapser/training/inputs.py
tests/tower/test_runtime.py
tests/quotient/test_tier_view.py
tests/integration/test_vertical_slice.py
```

Completion criteria:

- The implementation log contains a short "current reality" summary.
- Any mismatch with the blueprint is explicitly recorded.

Stop condition:

- If any file has changed in a way that invalidates the gameplan, stop and ask.

#### Action 0.2.2

Run focused baseline tests before implementation.

Required command:

```text
uv run pytest tests/tower tests/quotient tests/integration
```

Completion criteria:

- Baseline result is recorded in the implementation log.

Stop condition:

- If baseline tests fail unexpectedly, stop and diagnose before implementation.

## Phase 1: Package Skeleton And Type Authority

### Stage 1.1: Create Partition Package Skeleton

#### Action 1.1.1

Create the package directory:

```text
src/state_collapser/tower/partition/
```

Required files:

```text
src/state_collapser/tower/partition/__init__.py
src/state_collapser/tower/partition/ids.py
src/state_collapser/tower/partition/base_registry.py
src/state_collapser/tower/partition/schema.py
src/state_collapser/tower/partition/state_layer.py
src/state_collapser/tower/partition/action_layer.py
src/state_collapser/tower/partition/loop_policy.py
src/state_collapser/tower/partition/reward_aggregation.py
src/state_collapser/tower/partition/update.py
src/state_collapser/tower/partition/tower.py
src/state_collapser/tower/partition/readout.py
src/state_collapser/tower/partition/diagnostics.py
```

Completion criteria:

- Package imports without side effects.
- `__init__.py` exports only stable first-scope names.

Stop condition:

- If this file split collides with existing package structure, stop and ask.

#### Action 1.1.2

Create test package skeleton:

```text
tests/tower/partition/
```

Required files:

```text
tests/tower/partition/test_ids.py
tests/tower/partition/test_base_registry.py
tests/tower/partition/test_schema.py
tests/tower/partition/test_state_layer.py
tests/tower/partition/test_action_layer.py
tests/tower/partition/test_loop_policy.py
tests/tower/partition/test_reward_aggregation.py
tests/tower/partition/test_tower_initialization.py
tests/tower/partition/test_incremental_update.py
tests/tower/partition/test_readout.py
```

Completion criteria:

- Test files exist and are ready for phase-specific tests.

### Stage 1.2: Implement Id Types

#### Action 1.2.1

Implement frozen slot id dataclasses in:

```text
src/state_collapser/tower/partition/ids.py
```

Required ids:

```text
StateId
EdgeId
ActionId
TierIndex
SchemaBlockId
StateCellId
ActionCollectionId
ActionCellId
```

Required properties:

- hashable
- comparable by value
- deterministic repr
- no dependency on `State`, `BaseEdge`, or `PrimitiveAction`
- no ambient process state

Completion criteria:

- Tests in `tests/tower/partition/test_ids.py` cover equality, hashing, repr,
  and non-equality across id types.

#### Action 1.2.2

Implement id factory helpers if needed.

Required behavior:

- state ids and edge ids are allocated monotonically by registry-local counters
- cell ids include tier and ordinal
- action collection/action cell ids include tier and ordinal
- schema block ids can wrap labels, integers, or strings

Completion criteria:

- Tests prove ids are deterministic within a registry/tower run.

## Phase 2: Base Graph Registry

### Stage 2.1: Implement Registry Storage

#### Action 2.1.1

Implement `BaseGraphRegistry` in:

```text
src/state_collapser/tower/partition/base_registry.py
```

Required storage:

```text
state_id_by_state
state_by_id
edge_id_by_edge
edge_by_id
source_by_edge_id
target_by_edge_id
action_by_edge_id
labels_by_edge_id
outgoing_edge_ids_by_state_id
```

Completion criteria:

- Registering a state returns a stable `StateId`.
- Registering the same state twice returns the same `StateId`.
- Registering an edge registers its source and target states.
- Registering an edge returns a stable `EdgeId`.
- Outgoing index is updated only for the source state.

#### Action 2.1.2

Implement object lookup helpers.

Required helpers:

```text
state_for_id(state_id)
edge_for_id(edge_id)
source_state_id(edge_id)
target_state_id(edge_id)
action_for_edge_id(edge_id)
labels_for_edge_id(edge_id)
outgoing_edge_ids(state_id)
```

Completion criteria:

- Tests cover every helper.
- Missing ids raise clear errors or return documented `None` consistently.

### Stage 2.2: Implement Delta Registration

#### Action 2.2.1

Implement:

```text
register_states(states) -> tuple[StateId, ...]
register_edges(edges) -> tuple[EdgeId, ...]
register_delta(states, edges) -> RegistryDelta
```

Required `RegistryDelta` fields:

```text
new_state_ids
known_state_ids
new_edge_ids
known_edge_ids
```

Completion criteria:

- Tests distinguish new and known states/edges.
- Duplicate edges do not create duplicate ids.

#### Action 2.2.2

Implement combined label extraction.

Required behavior:

- edge labels include `BaseEdge.labels`
- edge labels include `PrimitiveAction.labels`
- labels are stored as a stable tuple or frozenset

Completion criteria:

- Tests cover edge-only labels, action-only labels, both, and neither.

### Stage 2.3: Validate Registry

#### Action 2.3.1

Run:

```text
uv run pytest tests/tower/partition/test_ids.py tests/tower/partition/test_base_registry.py
```

Completion criteria:

- Tests pass.
- Implementation log records result.

## Phase 3: Contraction Schema Surface

### Stage 3.1: Implement Schema Protocol And Records

#### Action 3.1.1

Implement schema protocol and assignment records in:

```text
src/state_collapser/tower/partition/schema.py
```

Required names:

```text
ContractionSchema
SchemaAssignment
SchemaAssignmentStore
NoContractionSchema
LabelBlockSchema
DimensionwiseSchema
SeededRandomRateSchema
DiscoveryOrderChunkSchema
```

Required protocol behavior:

```text
assign_edge(edge_id, registry) -> SchemaBlockId | None
ordered_blocks() -> tuple[SchemaBlockId, ...]
```

Completion criteria:

- Schema assignment is separate from `ContractionPolicy.select(...)`.
- Existing `contract/policy.py` is not modified in this action.

#### Action 3.1.2

Implement `SchemaAssignmentStore`.

Required behavior:

- assigns each edge id at most once
- returns existing assignment for previously assigned edges
- stores edges by block id
- exposes ordered blocks
- exposes unscheduled edges if block assignment is `None`

Completion criteria:

- Tests prove assignment persistence.

### Stage 3.2: Implement Label And Dimensionwise Schemas

#### Action 3.2.1

Implement `LabelBlockSchema`.

Required behavior:

- accepts ordered label-to-block mapping
- checks labels from `BaseGraphRegistry.labels_for_edge_id(edge_id)`
- returns the first matching block in declared order
- returns `None` when no label matches

Completion criteria:

- Tests prove declared order controls block assignment.
- Tests prove no hard-coded sorting or 20 percent behavior remains in schema.

#### Action 3.2.2

Implement `DimensionwiseSchema`.

Required behavior:

- convenience constructor for ordered dimension labels
- maps labels such as `x`, `y`, `z` to corresponding schema blocks
- does not require environment-specific code

Completion criteria:

- Tests cover a three-dimension ordered block example.

### Stage 3.3: Implement Random And Discovery Schemas

#### Action 3.3.1

Implement `SeededRandomRateSchema`.

Required behavior:

- deterministic under seed
- assigns only newly seen edge ids when used through `SchemaAssignmentStore`
- never resamples old edge ids
- supports a configured number of blocks or rate/chunk interpretation
- records enough configuration in repr/diagnostics

Completion criteria:

- Tests prove adding new edges does not change old assignments.
- Tests prove same seed/discovery order gives same assignments.

#### Action 3.3.2

Implement `DiscoveryOrderChunkSchema`.

Required behavior:

- deterministic fallback for unlabeled environments
- assigns edges to blocks by discovery order and chunk size/rate
- useful in tests because it is predictable

Completion criteria:

- Tests cover chunk boundaries.

### Stage 3.4: Validate Schema Surface

#### Action 3.4.1

Run:

```text
uv run pytest tests/tower/partition/test_schema.py
```

Completion criteria:

- Tests pass.
- Implementation log records result.

## Phase 4: Loop Policy And Reward Aggregation

### Stage 4.1: Implement Loop Policy

#### Action 4.1.1

Implement loop-policy types in:

```text
src/state_collapser/tower/partition/loop_policy.py
```

Required names:

```text
LoopPolicyName
LoopPolicy
InternalEdgeRecord
```

Required first-scope policies:

```text
drop_internal
aggregate_internal
formal_stutter
```

Completion criteria:

- `drop_internal` is the default.
- All policies are representable even if `formal_stutter` has limited first-scope
  behavior.

#### Action 4.1.2

Implement internal-edge recording helpers.

Required behavior:

- record edge id
- record tier
- record containing state cell
- record selected loop policy
- optionally record reward contributor placeholder

Completion criteria:

- Tests prove internal edges are recorded under `drop_internal`.

### Stage 4.2: Implement Reward Aggregation

#### Action 4.2.1

Implement reward aggregation utilities in:

```text
src/state_collapser/tower/partition/reward_aggregation.py
```

Required names:

```text
RewardAggregator
RewardAggregationName
RewardAggregationResult
aggregate_rewards(...)
```

Required aggregators:

```text
sum
mean
max
softmax
p_mean
p_norm
custom callable
```

Completion criteria:

- Empty inputs have documented behavior.
- `max` and `mean` differ on a mixed reward list.
- `p = inf` behaves as max-type aggregation.

#### Action 4.2.2

Extend `src/state_collapser/core/rewards.py` without breaking existing callers.

Required behavior:

- existing `StepReward`, `PathRewardSummary`, and `summarize_path_rewards`
  remain compatible
- `QuotientRewardSummary` gains optional fields for aggregator name,
  aggregate reward, internal-loop policy, and internal contributors
- existing `mean_reward` behavior remains readable for old tests

Completion criteria:

- Existing reward tests still pass.
- New reward aggregation tests pass.

### Stage 4.3: Validate Loop And Reward Work

#### Action 4.3.1

Run:

```text
uv run pytest tests/tower/partition/test_loop_policy.py tests/tower/partition/test_reward_aggregation.py tests/quotient/test_reward_aggregation.py
```

Completion criteria:

- Tests pass.
- Implementation log records result.

## Phase 5: State Partition Layer

### Stage 5.1: Implement State Layer Data Structure

#### Action 5.1.1

Implement `StatePartitionLayer` in:

```text
src/state_collapser/tower/partition/state_layer.py
```

Required storage:

```text
tier_index
cell_of_state_id
members_by_cell_id
parent_cell_by_previous_cell_id
previous_cells_by_cell_id
```

Required constructors:

```text
singleton_layer(tier, state_ids)
carry_forward_from(previous_layer, tier)
```

Completion criteria:

- Singleton layer maps every state to its own cell.
- Carry-forward layer preserves cell membership and state pointers.

#### Action 5.1.2

Implement cell lookup and membership APIs.

Required methods:

```text
cell_of(state_id)
members(cell_id)
all_cell_ids()
contains_state(state_id)
```

Completion criteria:

- Tests cover all methods.

### Stage 5.2: Implement State Cell Merge

#### Action 5.2.1

Implement:

```text
merge_cells(left_cell_id, right_cell_id) -> StateCellMergeResult
```

Required behavior:

- no-op if cells are equal
- creates a new cell id when cells differ
- updates every member state to point to the new cell
- records previous cells
- records parent mapping from previous cells to new cell
- preserves unaffected cells

Completion criteria:

- Tests prove all member states point to new cell.
- Tests prove unaffected cells remain stable.

#### Action 5.2.2

Implement deterministic membership readout.

Required behavior:

- tests can compare member ids deterministically
- no reliance on hash iteration order in public/readout methods

Completion criteria:

- Tests compare exact member tuples.

### Stage 5.3: Validate State Layer

#### Action 5.3.1

Run:

```text
uv run pytest tests/tower/partition/test_state_layer.py
```

Completion criteria:

- Tests pass.
- Implementation log records result.

## Phase 6: Action Partition Layer

### Stage 6.1: Implement Action Collection Storage

#### Action 6.1.1

Implement `ActionPartitionLayer` in:

```text
src/state_collapser/tower/partition/action_layer.py
```

Required storage:

```text
tier_index
outgoing_collection_by_state_cell
edge_ids_by_collection
internal_edge_ids_by_state_cell
action_cell_ids_by_collection
edge_ids_by_action_cell
source_cell_by_action_cell
target_cell_by_action_cell
label_key_by_action_cell
```

Required constructors:

```text
from_state_layer_and_registry(tier, state_layer, registry)
carry_forward_from(previous_action_layer, new_state_layer, tier)
```

Completion criteria:

- Tier `0` outgoing collections initialize from registry outgoing edge ids.
- Each state cell has a first-class outgoing collection pointer.

#### Action 6.1.2

Implement outgoing collection lookup methods.

Required methods:

```text
outgoing_collection(state_cell_id)
edge_ids_for_collection(collection_id)
internal_edge_ids(state_cell_id)
```

Completion criteria:

- Tests prove outgoing lookup is direct and does not require scanning all action
  cells.

### Stage 6.2: Implement Action Collection Merge

#### Action 6.2.1

Implement:

```text
merge_collections(left_collection_id, right_collection_id, merged_state_cell_id, state_layer, registry, loop_policy)
```

Required behavior:

- creates a new action collection id
- unions edge ids from both collections
- removes or records internal edges whose source and target both lie in the
  merged state cell
- attaches the merged collection to the merged state cell
- records action merge diagnostics

Completion criteria:

- Tests prove outgoing data from both prior cells is available after merge.
- Tests prove internal edges are removed from navigation under `drop_internal`.
- Tests prove internal edge ids are recorded.

#### Action 6.2.2

Implement dirty collection tracking.

Required behavior:

- merging marks only affected collections dirty
- action-cell indexing can rebuild only dirty collections

Completion criteria:

- Tests prove unaffected collections are not marked dirty.

### Stage 6.3: Implement Decision-Level Action Cells

#### Action 6.3.1

Implement action-cell indexing for an outgoing collection.

Required grouping:

- group by source state cell
- group by target state cell
- optionally include a label/action key if needed
- exclude internal edges under `drop_internal`

Completion criteria:

- Tests prove action cells have source and target cells.
- Tests prove all member edge ids in an action cell share the same source/target
  cell pair at that tier.

#### Action 6.3.2

Implement representative-edge methods.

Required methods:

```text
action_cells_for_collection(collection_id)
edge_ids_for_action_cell(action_cell_id)
representative_edge_ids(action_cell_id)
```

Completion criteria:

- Tests prove representative edge lookup.

### Stage 6.4: Validate Action Layer

#### Action 6.4.1

Run:

```text
uv run pytest tests/tower/partition/test_action_layer.py
```

Completion criteria:

- Tests pass.
- Implementation log records result.

## Phase 7: Partition Tower Initialization And Full-Build Reference

### Stage 7.1: Implement Update Records And Diagnostics

#### Action 7.1.1

Implement records in:

```text
src/state_collapser/tower/partition/update.py
src/state_collapser/tower/partition/diagnostics.py
```

Required names:

```text
StateCellMergeRecord
ActionCollectionMergeRecord
TowerMorphism
TowerUpdateDiagnostics
TowerUpdateResult
```

Required fields:

- changed
- delta state ids
- delta edge ids
- schema assignments
- affected tiers
- state merges
- action merges
- internal edges
- current positions
- morphism
- diagnostic counters

Completion criteria:

- Records are immutable or mutation-safe.
- Tests can inspect every required field.

### Stage 7.2: Implement PartitionTower Initialization

#### Action 7.2.1

Implement `PartitionTower` in:

```text
src/state_collapser/tower/partition/tower.py
```

Required constructor dependencies:

```text
schema
loop_policy
reward_aggregator
```

Required state:

```text
registry
schema_assignment_store
state_layers
action_layers
last_update_result
```

Completion criteria:

- Empty tower can be created.
- Constructor has explicit defaults and no ambient state.

#### Action 7.2.2

Implement:

```text
initialize(initial_states, initial_edges, current_state) -> TowerUpdateResult
```

Required behavior:

- registers states/edges
- creates tier-0 singleton state layer
- creates tier-0 action layer from outgoing buckets
- assigns schema blocks to registered edges
- processes all initial schema blocks to create initial partition layers
- sets current positions
- records diagnostics

Completion criteria:

- Tests cover empty initialization.
- Tests cover one-state/no-edge initialization.
- Tests cover two-state/one-edge point collapse under a schema that schedules
  the edge.

### Stage 7.3: Implement Full-Build Reference Path

#### Action 7.3.1

Implement a full-build partition reference helper.

Recommended location:

```text
src/state_collapser/tower/partition/tower.py
```

or:

```text
src/state_collapser/tower/partition/readout.py
```

Required behavior:

- builds a partition tower from a complete state/edge set
- uses the same schema assignment semantics
- uses the same loop policy
- produces the same partition-layer structure as incremental update on the same
  final graph

Completion criteria:

- Tests compare full initialization against stepwise initialization on a small
  graph.

### Stage 7.4: Validate Initialization

#### Action 7.4.1

Run:

```text
uv run pytest tests/tower/partition/test_tower_initialization.py
```

Completion criteria:

- Tests pass.
- Implementation log records result.

## Phase 8: Compatibility Readout To QuotientTierView

### Stage 8.1: Implement State Readout

#### Action 8.1.1

Implement readout helpers in:

```text
src/state_collapser/tower/partition/readout.py
```

Required method:

```text
to_quotient_tier_views(partition_tower) -> tuple[QuotientTierView, ...]
```

State-side readout requirements:

- set state projection from base `State` to tier state-cell id or stable
  readout key
- add node coset members for every state-cell member
- set current position for each tier

Completion criteria:

- Tests prove state projections match state partition layers.
- Tests prove `same_coset(...)` works through readout.

### Stage 8.2: Implement Action Readout

#### Action 8.2.1

Implement edge/action projection in `to_quotient_tier_views(...)`.

Required behavior:

- live inter-cell edges project to action-cell or quotient-edge readout ids
- internal edges project to `None` or are absent consistently with
  `projected_edge_is_trivial`
- edge coset membership is populated for live quotient action cells
- source/target information is encoded in readout ids only as adapter data, not
  core model

Completion criteria:

- Tests prove `projected_edge_is_trivial(...)` is true for internal edges.
- Tests prove live quotient edges/action cells have edge members.

### Stage 8.3: Validate Readout

#### Action 8.3.1

Run:

```text
uv run pytest tests/tower/partition/test_readout.py tests/quotient
```

Completion criteria:

- Tests pass.
- Existing quotient tests continue to pass.

## Phase 9: Incremental Update

### Stage 9.1: Implement Delta Update Entry Point

#### Action 9.1.1

Implement:

```text
PartitionTower.update_with_delta(delta_states, delta_edges, current_state) -> TowerUpdateResult
```

Required behavior:

- registers only delta states/edges
- updates tier-0 state/action structures for new graph information
- assigns schema blocks only to new edge ids
- updates current positions even when no structural change occurs
- returns identity morphism for no-op structural updates

Completion criteria:

- Tests cover empty delta.
- Tests cover new state with no edges.
- Tests cover new edge between known states.
- Tests cover new edge to new state.

### Stage 9.2: Implement Delta Edge Insertion Across Existing Layers

#### Action 9.2.1

For each new edge, insert outgoing edge data into relevant action layers.

Required behavior:

- the edge appears in the outgoing collection of the source state cell at each
  tier where it is not internal
- the edge is recorded as internal at tiers where source and target are already
  in the same state cell
- insertion marks only affected outgoing collections dirty

Completion criteria:

- Tests prove a new edge is visible as outgoing information before/independent
  of being a contraction edge.
- Tests cover the blueprint's "new edges are both data and possible
  contractions" nuance.

### Stage 9.3: Implement Schema-Driven Delta Contractions

#### Action 9.3.1

For each affected schema block, process delta edges assigned to that block.

Required behavior:

- look up source and target cells in the previous layer
- no-op if source and target cells are already equal
- merge state cells if distinct
- merge outgoing action collections
- remove/record internal loops
- update dirty action-cell indexes
- record merge diagnostics

Completion criteria:

- Tests prove one delta edge can create a new lower tier or update an existing
  tier.
- Tests prove repeated update of an already internal edge is no-op plus
  diagnostics.

#### Action 9.3.2

Ensure update uses schema block order.

Required behavior:

- dimensionwise schema contracts in declared order
- random schema respects stored block ids
- discovery-order schema respects chunk order

Completion criteria:

- Tests prove changing block order changes tier structure in an expected small
  example.

### Stage 9.4: Implement Tower Morphism Records

#### Action 9.4.1

Populate `TowerMorphism` in every update result.

Required behavior:

- old state cells map to new containing state cells
- old action collections map to new containing action collections where
  applicable
- unchanged tiers are recorded
- created tiers are recorded

Completion criteria:

- Tests prove no-op update returns identity morphism.
- Tests prove a merge maps two old cells to one new cell.

### Stage 9.5: Validate Incremental Update

#### Action 9.5.1

Run:

```text
uv run pytest tests/tower/partition/test_incremental_update.py
```

Completion criteria:

- Tests pass.
- Implementation log records result.

## Phase 10: Full-Build Versus Incremental Equivalence

### Stage 10.1: Build Equivalence Fixtures

#### Action 10.1.1

Create deterministic synthetic graph fixtures in tests.

Required fixture families:

- two-state one-edge graph
- three-state path graph
- square graph with dimension labels
- graph with an edge that becomes internal after a merge
- graph with unlabeled edges for discovery-order schema

Completion criteria:

- Fixtures live in tests, not production code.
- Fixtures use existing `State`, `PrimitiveAction`, and `BaseEdge`.

### Stage 10.2: Assert Equivalence

#### Action 10.2.1

For each fixture, compare full-build and incremental partition towers.

Required comparisons:

- state partitions by tier
- action outgoing collections by tier
- internal edge records by tier
- schema assignments
- current positions
- compatibility `QuotientTierView` readouts

Completion criteria:

- Equivalence tests fail if action outgoing pointers are wrong.
- Equivalence tests fail if readout hides partition mismatch.

### Stage 10.3: Validate Equivalence

#### Action 10.3.1

Run:

```text
uv run pytest tests/tower/partition
```

Completion criteria:

- All partition tests pass.
- Implementation log records result.

## Phase 11: TowerRuntime Integration Behind Backend Boundary

### Stage 11.1: Add Runtime Backend Selection

#### Action 11.1.1

Modify:

```text
src/state_collapser/tower/runtime.py
```

Required behavior:

- `TowerRuntime` can own a `PartitionTower`
- constructor accepts explicit backend/config parameters without relying on
  ambient state
- legacy dynamic builder remains available temporarily
- backend selection is explicit and testable

Recommended constructor additions:

```text
tower_backend: str = "legacy"
contraction_schema: ContractionSchema | None = None
loop_policy: LoopPolicy | None = None
reward_aggregator: RewardAggregator | None = None
```

Completion criteria:

- Existing code paths still work with default legacy backend at this stage.
- New partition backend can be selected in a focused runtime test.

Stop condition:

- If constructor compatibility with examples requires a broader API decision,
  stop and ask.

### Stage 11.2: Wire Reset To Partition Backend

#### Action 11.2.1

Implement partition-backend behavior in `TowerRuntime.reset(...)`.

Required behavior:

- reset creates a fresh `PartitionTower`
- reset registers initial vista states/edges
- reset populates `self._quotient_tiers` from partition readout
- reset populates current positions from partition tower
- reset returns existing `RuntimeSnapshot` shape

Completion criteria:

- New runtime test passes for reset with partition backend.

### Stage 11.3: Wire Step To Partition Backend

#### Action 11.3.1

Implement partition-backend behavior in `TowerRuntime.step(...)`.

Required behavior:

- current primitive step semantics remain unchanged
- explored graph still records realized edge
- vista graph still refreshes current and next state
- delta states/edges are passed to `PartitionTower.update_with_delta(...)`
- no-new-exploration structural update returns identity morphism
- snapshot fields remain compatible

Completion criteria:

- Runtime tests pass with partition backend on tiny hidden graph.
- Diagnostics show delta update path.

### Stage 11.4: Preserve Runtime Query Methods

#### Action 11.4.1

Update `TowerRuntime` query methods to work with partition backend.

Required methods:

```text
quotient_tiers
selected_base_edges
tier_contraction_records
tower_stopping_reason
current_deepest_tier()
project_state_to_tier(...)
project_edge_to_tier(...)
states_share_coset(...)
projected_edge_is_trivial_at_tier(...)
tier_is_point(...)
tower_is_fully_propagated()
```

Completion criteria:

- Existing runtime tests pass in legacy mode.
- New partition backend tests pass for equivalent query methods.

### Stage 11.5: Validate Backend Integration

#### Action 11.5.1

Run:

```text
uv run pytest tests/tower/test_runtime.py tests/tower/partition
```

Completion criteria:

- Tests pass.
- Implementation log records result.

## Phase 12: Snapshot And Training Surface Compatibility

### Stage 12.1: Extend RuntimeSnapshot Additively

#### Action 12.1.1

Modify:

```text
src/state_collapser/tower/snapshot.py
```

Add optional fields:

```text
partition_tower_view
tower_update_result
```

Required behavior:

- existing `RuntimeSnapshot(...)` construction remains valid
- existing tests do not need to supply new fields
- fields are optional and default to `None`

Completion criteria:

- `tests/tower/test_snapshot.py` passes.

### Stage 12.2: Preserve ActionSelectionInput

#### Action 12.2.1

Modify only if needed:

```text
src/state_collapser/training/inputs.py
```

Required behavior:

- `tower_position_key(snapshot)` remains `tuple(snapshot.current_position_at_every_tier)`
- no mandatory dependency on partition tower internals
- optional partition diagnostics may be passed through existing diagnostics

Completion criteria:

- Existing training input tests pass.

### Stage 12.3: Validate Training Compatibility

#### Action 12.3.1

Run:

```text
uv run pytest tests/training tests/tower/test_snapshot.py
```

Completion criteria:

- Tests pass.
- Implementation log records result.

## Phase 13: Quotient Action And Lift Surfaces

### Stage 13.1: Expose Tower Query Methods

#### Action 13.1.1

Expose query methods on `PartitionTower`.

Required methods:

```text
current_state_cell(tier, state)
state_cell_members(tier, state_cell)
outgoing_action_cells(tier, state_cell)
action_cell_members(tier, action_cell)
representative_edges(tier, action_cell)
internal_edges(tier, state_cell)
```

Completion criteria:

- Tests prove a caller can query outgoing action cells from the current cell
  without inspecting `QuotientTierView`.

### Stage 13.2: Implement Lift Candidate Query

#### Action 13.2.1

Implement:

```text
lift_candidates(tier, action_cell, current_base_state)
```

First-scope behavior:

- return member base edges whose source is the current base state when available
- otherwise return representative member edges in deterministic order
- do not attempt full path planning inside a coset in first scope
- document that full coset navigation/refinement is a later executor concern

Completion criteria:

- Tests cover direct executable candidate and representative fallback.

Stop condition:

- If this method requires a broader lift semantics decision than the blueprint
  authorizes, stop and ask.

### Stage 13.3: Implement Refinement Fiber Query

#### Action 13.3.1

Implement a first-scope `refinement_fiber(...)`.

Required behavior:

- state-cell fiber from tier `i` to tier `i-1`
- action-cell/action-collection fiber from tier `i` to tier `i-1` where available
- deterministic readout

Completion criteria:

- Tests prove adjacent-tier state and action fibers are queryable.

### Stage 13.4: Validate Action/Lift Surfaces

#### Action 13.4.1

Run:

```text
uv run pytest tests/tower/partition
```

Completion criteria:

- Tests pass.
- Implementation log records result.

## Phase 14: Switch Runtime Default To Partition Backend

### Stage 14.1: Make Partition Backend Default

#### Action 14.1.1

Modify `TowerRuntime` so the partition backend is the default normal runtime
path.

Required behavior:

- no explicit backend means partition backend
- legacy backend remains available by explicit opt-in
- constructor docs explain backend choice
- no existing example should need to pass backend just to run

Completion criteria:

- Runtime tests now exercise partition backend by default.
- Tests that need legacy behavior opt into it explicitly.

### Stage 14.2: Update Runtime Tests

#### Action 14.2.1

Update:

```text
tests/tower/test_runtime.py
```

Required test changes:

- remove dependence on first-20-percent selection
- assert schema-driven selection/update records
- assert partition backend current positions
- assert `projected_edge_is_trivial_at_tier(...)`
- assert `states_share_coset(...)`
- assert no-op structural update where possible

Completion criteria:

- Tests encode new partition semantics.

### Stage 14.3: Validate Runtime Default

#### Action 14.3.1

Run:

```text
uv run pytest tests/tower tests/quotient
```

Completion criteria:

- Tests pass.
- Implementation log records result.

## Phase 15: Integration And Example Migration

### Stage 15.1: Update Vertical Slice Integration

#### Action 15.1.1

Update:

```text
tests/integration/test_vertical_slice.py
```

Required behavior:

- snapshots remain coherent
- current positions length matches quotient tiers length
- partition backend exposes outgoing action diagnostics where appropriate
- reward aggregation still works

Completion criteria:

- Integration tests pass under partition default.

### Stage 15.2: Adapt Robot Constraint Toy Schema Smoke

#### Action 15.2.1

Inspect and update as needed:

```text
src/state_collapser/examples/robot_constraint_toy.py
tests/examples/test_robot_constraint_toy.py
```

Required behavior:

- add or use labels suitable for a simple schema test
- assert schema-controlled contraction behavior where feasible
- preserve existing vertical slice behavior

Completion criteria:

- Robot constraint toy tests pass.

### Stage 15.3: Preserve Existing Example Runtime Tests

#### Action 15.3.1

Run and update example runtime tests only where needed:

```text
tests/examples/test_*runtime_integration.py
tests/examples/test_*tower_training.py
```

Required behavior:

- examples continue to expose current tower positions
- primitive-action training loops continue to run
- no example is forced to train over quotient action cells

Completion criteria:

- Example runtime and tower training tests pass.

Stop condition:

- If many examples require semantic rewrites rather than compatibility fixes,
  stop and ask for rollout guidance.

### Stage 15.4: Validate Examples

#### Action 15.4.1

Run:

```text
uv run pytest tests/examples
```

Completion criteria:

- Tests pass.
- Implementation log records result.

## Phase 16: Legacy Builder Demotion

### Stage 16.1: Rename Or Mark Legacy Path

#### Action 16.1.1

Modify:

```text
src/state_collapser/tower/construction.py
```

Required behavior:

- old `build_dynamic_tower(...)` path is no longer normal runtime authority
- legacy behavior is clearly named or documented as legacy/validation
- hard-coded 20 percent behavior is not exposed as the default package
  contraction semantics

Completion criteria:

- No production runtime default calls the old builder.
- Any remaining call is explicitly legacy or validation.

### Stage 16.2: Preserve Validation Helper

#### Action 16.2.1

Keep or add a full-build validation helper that uses partition semantics.

Required behavior:

- helper can compare incremental and full-build partition towers
- helper uses schema assignments and loop policy consistently

Completion criteria:

- Equivalence tests still pass.

### Stage 16.3: Validate Legacy Demotion

#### Action 16.3.1

Run:

```text
uv run pytest tests/tower tests/quotient tests/integration
```

Completion criteria:

- Tests pass.
- Implementation log records result.

## Phase 17: Performance Diagnostics And Locality Assertions

### Stage 17.1: Expose Diagnostics

#### Action 17.1.1

Ensure `TowerUpdateDiagnostics` exposes counters:

```text
discovered_state_count
discovered_edge_count
delta_state_count
delta_edge_count
schema_assignment_count
state_cell_merge_count
action_collection_merge_count
internal_edge_count
dirty_collection_count
compat_readout_rebuild_count
full_rebuild_validation_count
```

Completion criteria:

- Tests inspect these counters after reset, no-op update, and new-vista update.

### Stage 17.2: Assert Locality Behavior

#### Action 17.2.1

Add tests proving normal update does not behave like a full rebuild.

Required assertions:

- no-op update has zero state/action merges
- no-op update has identity morphism
- new single-edge update has bounded affected-tier/dirty-collection counts in a
  small fixture
- old random assignments remain unchanged after new edge discovery

Completion criteria:

- Tests fail if implementation rebuilds everything and reports it as local.

### Stage 17.3: Validate Diagnostics

#### Action 17.3.1

Run:

```text
uv run pytest tests/tower/partition tests/tower/test_runtime.py
```

Completion criteria:

- Tests pass.
- Implementation log records result.

## Phase 18: Documentation And Export Cleanup

### Stage 18.1: Update Package Exports

#### Action 18.1.1

Update:

```text
src/state_collapser/tower/partition/__init__.py
```

Required behavior:

- export stable first-scope types
- do not export internal helper-only functions unless needed by tests or users
- keep experimental surfaces named honestly

Completion criteria:

- Import tests pass.

### Stage 18.2: Add Developer-Facing Notes

#### Action 18.2.1

Add concise module docstrings explaining:

- partition tower is the runtime model
- `QuotientTierView` is a compatibility readout
- `ContractionSchema` is distinct from local-star `ContractionPolicy`
- action collections are storage-level
- action cells are decision-level
- loop policy is explicit

Completion criteria:

- Key modules have enough docstring context for future maintainers.

### Stage 18.3: Update README Or Design Docs Only If Needed

#### Action 18.3.1

Inspect README and nearby design docs for direct claims contradicted by the new
runtime.

Completion criteria:

- If claims need updating, update them.
- If no updates are needed, record that in the implementation log.

Stop condition:

- If README changes would broaden release claims, stop and ask before editing.

## Phase 19: Full Validation

### Stage 19.1: Run Focused Validation

#### Action 19.1.1

Run:

```text
uv run pytest tests/tower tests/quotient tests/integration
```

Completion criteria:

- Tests pass.
- Implementation log records result.

### Stage 19.2: Run Example Validation

#### Action 19.2.1

Run:

```text
uv run pytest tests/examples
```

Completion criteria:

- Tests pass.
- Implementation log records result.

### Stage 19.3: Run Full Validation

#### Action 19.3.1

Run:

```text
uv run pytest
```

Completion criteria:

- Full test suite passes.
- Implementation log records result.

Stop condition:

- If full validation fails because of unrelated pre-existing failures, bind that
  reality with exact failing tests and ask the Project Owner how to proceed.

## Phase 20: Final Review Against Blueprint

### Stage 20.1: Blueprint Acceptance Checklist

#### Action 20.1.1

Check implementation against every core tower criterion in the blueprint.

Required checklist:

- persistent nested state/action partition layers exist
- tier `0` state cells are singleton cells
- tier `0` action data initializes from outgoing edge buckets
- state cells point to outgoing action data as first-class structure
- schema block assignment is explicit and persistent
- dimensionwise and random-at-rate schemas exist
- incremental update processes delta graph information in the normal path
- loop/internal-edge policy is explicit
- reward aggregation is not hard-coded to mean only

Completion criteria:

- Implementation log records each item as satisfied or blocked.
- Any blocked item has Project Owner guidance.

### Stage 20.2: Compatibility Checklist

#### Action 20.2.1

Check compatibility criteria.

Required checklist:

- `RuntimeSnapshot.current_position_at_every_tier` remains available
- `RuntimeSnapshot.ordered_quotient_tiers` remains available
- primitive-action reference loops still run
- examples did not need a full simultaneous rewrite
- `TowerRuntime` query methods remain available or have clear replacements

Completion criteria:

- Implementation log records each item.

### Stage 20.3: Performance Criteria Checklist

#### Action 20.3.1

Check performance criteria.

Required checklist:

- update diagnostics show delta-based behavior
- normal step path avoids global edge scans except explicit readout/validation
- outgoing action query is local to current state cell
- benchmark hooks/counters exist

Completion criteria:

- Implementation log records each item.

## Phase 21: Final Git And Reporting Discipline

### Stage 21.1: Inspect Final Diff

#### Action 21.1.1

Inspect final diff and status.

Required checks:

```text
git status --short
git diff --check
```

Completion criteria:

- No whitespace errors.
- Changed files are all related to this gameplan or explicitly authorized.

### Stage 21.2: Final Implementation Report

#### Action 21.2.1

Prepare final report to Project Owner.

Required content:

- implementation summary
- tests run and results
- files changed
- any deviations authorized by PO
- any remaining risks
- whether work is ready to commit

Completion criteria:

- Report is concise enough to review but complete enough for handoff.

## Explicit Non-Goals

This gameplan does not require:

- vectorized tensor training surfaces
- GPU/CUDA partition kernels
- full path planning inside cosets
- a master trainer
- full formal-stutter theorem machinery
- public API freeze
- immediate relabeling of every example environment
- benchmark publication

These may become later work.

## Final Execution Rule

When the Project Owner says to execute this gameplan, the implementer must:

1. create or switch to the implementation branch
2. create the implementation log
3. execute Phase.Stage.Action items in order
4. verify each phase before moving forward
5. stop on ambiguity or mismatch
6. never silently simplify the plan

This gameplan is intentionally detailed because the refactor touches the core
runtime model. The point is not bureaucracy. The point is to make the runtime
architecture precise enough that implementation can finally match the paper:
persistent nested state/action partitions, first-class outgoing pointers,
schema-driven coarsening, explicit loop/reward conventions, and compatibility
with the existing training surfaces.
