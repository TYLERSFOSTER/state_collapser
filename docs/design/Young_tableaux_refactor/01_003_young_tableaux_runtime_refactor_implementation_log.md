# Young Tableaux Runtime Refactor Implementation Log

## Status

This is the running implementation log for:

- `docs/design/Young_tableaux_refactor/01_002_young_tableaux_runtime_refactor_implementation_gameplan.md`

Implementation branch:

- `codex/young-tableaux-runtime-refactor`

## Phase 0: Execution Setup And Reality Binding

### Stage 0.1: Confirm Execution Authority

#### Action 0.1.1

Status: Completed.

Evidence:

- Project Owner instruction: "Alright I think we're ready to implement this gameplan: `docs/design/Young_tableaux_refactor/01_002_young_tableaux_runtime_refactor_implementation_gameplan.md` Make new branch to do this, per `prime_directive`. Proceed in correct Phase.Stage.Action step by step, again per `prime_directive`. Proceed."

#### Action 0.1.2

Status: Completed.

Evidence:

```text
git branch --show-current
codex/young-tableaux-runtime-refactor
```

```text
git status --short
<clean>
```

Notes:

- Branch was created from `main`.
- Working tree was clean before source implementation began.

### Stage 0.2: Bind Current Repository Reality

#### Action 0.2.1

Status: Completed.

Current reality summary:

- `TowerRuntime` still owns explored graph growth, vista refresh, reward
  accumulation, and runtime snapshots.
- `TowerRuntime._refresh_dynamic_tower(...)` still calls the legacy
  `build_dynamic_tower(...)` full-rebuild helper.
- `tower/construction.py` still builds fresh `QuotientTierView` objects by
  scanning visible states/edges, selecting the first 20 percent of eligible
  nontrivial edges, projecting all states/edges, and skipping internal loops.
- `QuotientTierView`, `ProjectionMap`, and `CosetStore` remain compatibility
  surfaces rather than partition-table runtime storage.
- `ContractionPolicy` remains a local-star selection protocol in
  `contract/policy.py`; it is not currently a persistent contraction-schema
  surface.
- `PrimitiveAction.labels` and `BaseEdge.labels` exist and remain the right raw
  label hooks for schema work.
- `core/rewards.py` still provides a mean-only `QuotientRewardSummary`.
- `ExploredGraph` and `VistaGraph` provide visited state/edge and one-hop vista
  surfaces, but no partition-tower registry.
- `training/inputs.py` still keys training by
  `snapshot.current_position_at_every_tier`.
- `tests/tower/test_runtime.py` still asserts legacy tier contraction records
  and first-step point-collapse behavior.
- `tests/integration/test_vertical_slice.py` still validates snapshot coherence,
  vista growth, local-star policy annotation messages, and cumulative rewards.

Gameplan mismatch assessment:

- No blocking mismatch found.
- Existing tests encode the legacy runtime behavior that later phases are
  expected to migrate.

#### Action 0.2.2

Status: Completed.

Command:

```text
uv run pytest tests/tower tests/quotient tests/integration
```

Result:

```text
61 passed
```

Notes:

- Baseline focused runtime/quotient/integration tests are green before source
  implementation.

## Phase 1: Package Skeleton And Type Authority

### Stage 1.1: Create Partition Package Skeleton

#### Action 1.1.1

Status: Completed.

Files created:

- `src/state_collapser/tower/partition/__init__.py`
- `src/state_collapser/tower/partition/ids.py`
- `src/state_collapser/tower/partition/base_registry.py`
- `src/state_collapser/tower/partition/schema.py`
- `src/state_collapser/tower/partition/state_layer.py`
- `src/state_collapser/tower/partition/action_layer.py`
- `src/state_collapser/tower/partition/loop_policy.py`
- `src/state_collapser/tower/partition/reward_aggregation.py`
- `src/state_collapser/tower/partition/update.py`
- `src/state_collapser/tower/partition/tower.py`
- `src/state_collapser/tower/partition/readout.py`
- `src/state_collapser/tower/partition/diagnostics.py`

#### Action 1.1.2

Status: Completed.

Files created:

- `tests/tower/partition/test_ids.py`
- `tests/tower/partition/test_base_registry.py`
- `tests/tower/partition/test_schema.py`
- `tests/tower/partition/test_state_layer.py`
- `tests/tower/partition/test_action_layer.py`
- `tests/tower/partition/test_loop_policy.py`
- `tests/tower/partition/test_reward_aggregation.py`
- `tests/tower/partition/test_tower_initialization.py`
- `tests/tower/partition/test_incremental_update.py`
- `tests/tower/partition/test_readout.py`

### Stage 1.2: Implement Id Types

#### Action 1.2.1

Status: Completed.

Implemented:

- `StateId`
- `EdgeId`
- `ActionId`
- `TierIndex`
- `SchemaBlockId`
- `StateCellId`
- `ActionCollectionId`
- `ActionCellId`

#### Action 1.2.2

Status: Completed.

Implemented:

- `IdAllocator`

Validation:

```text
uv run pytest tests/tower/partition/test_ids.py
5 passed
```

## Phase 2: Base Graph Registry

### Stage 2.1: Implement Registry Storage

#### Action 2.1.1

Status: Completed.

Implemented:

- `BaseGraphRegistry`
- stable state, edge, and action id allocation
- endpoint lookup storage
- outgoing edge index by source state id
- combined label storage

#### Action 2.1.2

Status: Completed.

Implemented lookup helpers:

- `state_for_id(...)`
- `edge_for_id(...)`
- `source_state_id(...)`
- `target_state_id(...)`
- `action_for_edge_id(...)`
- `action_id_for_edge_id(...)`
- `labels_for_edge_id(...)`
- `outgoing_edge_ids(...)`

### Stage 2.2: Implement Delta Registration

#### Action 2.2.1

Status: Completed.

Implemented:

- `register_states(...)`
- `register_edges(...)`
- `register_delta(...)`
- `RegistryDelta`

#### Action 2.2.2

Status: Completed.

Implemented:

- stable edge/action label combination in registration order

### Stage 2.3: Validate Registry

#### Action 2.3.1

Status: Completed.

Command:

```text
uv run pytest tests/tower/partition/test_ids.py tests/tower/partition/test_base_registry.py
```

Result:

```text
12 passed
```

## Phase 3: Contraction Schema Surface

### Stage 3.1: Implement Schema Protocol And Records

#### Action 3.1.1

Status: Completed.

Implemented:

- `ContractionSchema`
- `SchemaAssignment`
- `SchemaAssignmentStore`
- `NoContractionSchema`
- `LabelBlockSchema`
- `DimensionwiseSchema`
- `SeededRandomRateSchema`
- `DiscoveryOrderChunkSchema`

#### Action 3.1.2

Status: Completed.

Implemented:

- persistent assignment by edge id
- edges by schema block
- unscheduled edge tracking
- scheduled edge readout

### Stage 3.2: Implement Label And Dimensionwise Schemas

#### Action 3.2.1

Status: Completed.

Implemented:

- label matching by declared order
- ordered mapping construction

#### Action 3.2.2

Status: Completed.

Implemented:

- ordered dimension labels via `DimensionwiseSchema`

### Stage 3.3: Implement Random And Discovery Schemas

#### Action 3.3.1

Status: Completed.

Implemented:

- deterministic seeded random block assignment
- persistent old assignments via `SchemaAssignmentStore`

#### Action 3.3.2

Status: Completed.

Implemented:

- deterministic discovery-order chunk schema

### Stage 3.4: Validate Schema Surface

#### Action 3.4.1

Status: Completed.

Reality note:

- Initial schema validation failed during collection because `Protocol` was
  imported from `collections.abc`; Python 3.11 requires `typing.Protocol`.
- The import was corrected in `schema.py`.

Command:

```text
uv run pytest tests/tower/partition/test_schema.py
```

Result:

```text
9 passed
```

## Phase 13: Quotient Action And Lift Surfaces

### Stage 13.1: Expose Tower Query Methods

#### Action 13.1.1

Status: Completed.

Implemented on `PartitionTower`:

- `state_cell_members(...)`
- `outgoing_action_cells(...)`
- `action_cell_members(...)`
- `representative_edges(...)`
- `internal_edges(...)`

### Stage 13.2: Implement Lift Candidate Query

#### Action 13.2.1

Status: Completed.

Implemented:

- `lift_candidates(tier, action_cell, current_base_state)`
- directly executable edge preference when an action-cell member starts at the
  current base state
- deterministic representative fallback when no direct primitive edge is
  available from the current base state

### Stage 13.3: Implement Refinement Fiber Query

#### Action 13.3.1

Status: Completed.

Implemented:

- adjacent lower-tier state-cell refinement fibers
- adjacent lower-tier action-collection fibers derived through state-cell fibers
- adjacent lower-tier action-cell fibers by live edge membership overlap

### Stage 13.4: Validate Action/Lift Surfaces

#### Action 13.4.1

Status: Completed.

Command:

```text
uv run pytest tests/tower/partition
```

Result:

```text
67 passed
```

## Phase 14: Switch Runtime Default To Partition Backend

### Stage 14.1: Make Partition Backend Default

#### Action 14.1.1

Status: Completed.

Implemented:

- `TowerRuntime` now defaults to `tower_backend="partition"`
- `tower_backend="legacy"` remains available by explicit opt-in
- constructor docstring documents the backend choice
- constructor validates backend names

### Stage 14.2: Update Runtime Tests

#### Action 14.2.1

Status: Completed.

Implemented:

- runtime tests now exercise the partition backend by default
- legacy contraction-record assertions opt into `tower_backend="legacy"`
- default runtime tests assert schema-driven partition assignment/update data
- partition backend tests assert current positions, trivial projected edges,
  shared cosets, no-op structural updates, and selected scheduled edges

### Stage 14.3: Validate Runtime Default

#### Action 14.3.1

Status: Completed.

Command:

```text
uv run pytest tests/tower tests/quotient
```

Result:

```text
124 passed
```

## Phase 15: Integration And Example Migration

### Stage 15.1: Update Vertical Slice Integration

#### Action 15.1.1

Status: Completed.

Validation:

```text
uv run pytest tests/integration/test_vertical_slice.py
7 passed
```

Notes:

- The existing vertical slice remained coherent under the partition default.
- Snapshot position length still matches quotient tier length.

### Stage 15.2: Adapt Robot Constraint Toy Schema Smoke

#### Action 15.2.1

Status: Completed.

Implemented:

- robot-constraint schema smoke test using `DimensionwiseSchema(("hinge",))`
- assertion that the labeled hinge vista edge induces the expected tier-1
  state-cell identification

### Stage 15.3: Preserve Existing Example Runtime Tests

#### Action 15.3.1

Status: Completed.

Reality note:

- First example-suite run produced three failures in
  `plate_support_env` exploit/explore tests because the controller expects a
  coarse tier and default partition construction had no schema for that example.
- `PlateSupportHiddenGraph` now labels its visible edges with
  `"plate-support-transition"`.
- `PlateSupportEnvRuntime` now supplies
  `DimensionwiseSchema(("plate-support-transition",))` by default, while still
  allowing an explicit schema override.
- `PlateSupportExploitExploreRuntime` snapshot control-field wrapping now
  preserves optional partition snapshot fields.
- One tower-training assertion was updated from legacy one-tier behavior to the
  new two-tier partition default.

### Stage 15.4: Validate Examples

#### Action 15.4.1

Status: Completed.

Command:

```text
uv run pytest tests/examples
```

Result:

```text
138 passed
```

## Phase 16: Legacy Builder Demotion

### Stage 16.1: Rename Or Mark Legacy Path

#### Action 16.1.1

Status: Completed.

Implemented:

- `tower/construction.py` module docstring now identifies the old builder as a
  legacy full-rebuild/validation path
- `build_dynamic_tower(...)` docstring now describes legacy
  full-reconstruction semantics
- `TowerRuntime` imports the function as `build_legacy_dynamic_tower` at the
  explicit legacy backend call site

### Stage 16.2: Preserve Validation Helper

#### Action 16.2.1

Status: Completed.

Validation helper status:

- `build_partition_tower_full(...)` remains available as the partition-semantics
  full-build helper.
- Full-build versus incremental equivalence tests continue to exercise this
  validation role.

### Stage 16.3: Validate Legacy Demotion

#### Action 16.3.1

Status: Completed.

Command:

```text
uv run pytest tests/tower tests/quotient tests/integration
```

Result:

```text
132 passed
```

## Phase 17: Performance Diagnostics And Locality Assertions

### Stage 17.1: Expose Diagnostics

#### Action 17.1.1

Status: Completed.

Confirmed diagnostic counters:

- `discovered_state_count`
- `discovered_edge_count`
- `delta_state_count`
- `delta_edge_count`
- `schema_assignment_count`
- `state_cell_merge_count`
- `action_collection_merge_count`
- `internal_edge_count`
- `dirty_collection_count`
- `compat_readout_rebuild_count`
- `full_rebuild_validation_count`

### Stage 17.2: Assert Locality Behavior

#### Action 17.2.1

Status: Completed.

Implemented tests asserting:

- no-op update has zero state/action merges
- no-op update has identity unchanged-tier morphism
- new single-edge update has bounded affected tiers in the small fixture
- normal updates report `full_rebuild_validation_count == 0`
- random assignments remain unchanged after new edge discovery

### Stage 17.3: Validate Diagnostics

#### Action 17.3.1

Status: Completed.

Command:

```text
uv run pytest tests/tower/partition tests/tower/test_runtime.py
```

Result:

```text
77 passed
```

## Phase 18: Documentation And Export Cleanup

### Stage 18.1: Update Package Exports

#### Action 18.1.1

Status: Completed.

Implemented:

- expanded `state_collapser.tower.partition` exports for stable first-scope
  partition runtime types
- exported schema, loop-policy, reward-aggregation, update-result, diagnostics,
  `PartitionTower`, and `build_partition_tower_full` surfaces

### Stage 18.2: Add Developer-Facing Notes

#### Action 18.2.1

Status: Completed.

Implemented concise module/package doc updates explaining:

- partition tower is the runtime model
- `QuotientTierView` is a compatibility readout
- `ContractionSchema` is distinct from local-star `ContractionPolicy`
- action collections are storage-level and action cells are decision-level
- loop/internal-edge policy is explicit

### Stage 18.3: Update README Or Design Docs Only If Needed

#### Action 18.3.1

Status: Completed.

Implemented:

- README core-feature wording now identifies persistent nested state/action
  partition towers with quotient-tier compatibility readouts.
- README implemented-surface wording now identifies the tower runtime as
  partition-backed.

Validation:

```text
uv run pytest tests/tower/partition tests/tower/test_runtime.py tests/tower/test_snapshot.py
77 passed
```

## Phase 19: Full Validation

### Stage 19.1: Run Focused Validation

#### Action 19.1.1

Status: Completed.

Command:

```text
uv run pytest tests/tower tests/quotient tests/integration
```

Result:

```text
131 passed
```

### Stage 19.2: Run Example Validation

#### Action 19.2.1

Status: Completed.

Command:

```text
uv run pytest tests/examples
```

Result:

```text
138 passed
```

### Stage 19.3: Run Full Validation

#### Action 19.3.1

Status: Completed.

Command:

```text
uv run pytest
```

Result:

```text
323 passed
```

Additional CI sanity check:

```text
uv run ruff check .
All checks passed!
```

## Phase 20: Final Review Against Blueprint

### Stage 20.1: Blueprint Acceptance Checklist

#### Action 20.1.1

Status: Completed.

Checklist:

- Satisfied: persistent nested state/action partition layers exist in
  `state_layer.py`, `action_layer.py`, and `tower.py`.
- Satisfied: tier `0` state cells are singleton cells via
  `StatePartitionLayer.singleton_layer(...)`.
- Satisfied: tier `0` action data initializes from outgoing edge buckets via
  `ActionPartitionLayer.from_state_layer_and_registry(...)`.
- Satisfied: state cells point to outgoing action data through
  `outgoing_collection_by_state_cell`.
- Satisfied: schema block assignment is explicit and persistent through
  `SchemaAssignmentStore`.
- Satisfied: dimensionwise and random-at-rate schemas exist as
  `DimensionwiseSchema` and `SeededRandomRateSchema`.
- Satisfied: incremental update processes delta graph information in the normal
  runtime path through `PartitionTower.update_with_delta(...)`.
- Satisfied: loop/internal-edge policy is explicit through `LoopPolicy` and
  `InternalEdgeRecord`.
- Satisfied: reward aggregation is not hard-coded to mean only; sum, mean, max,
  softmax, p-mean, p-norm, and custom aggregation are implemented.

### Stage 20.2: Compatibility Checklist

#### Action 20.2.1

Status: Completed.

Checklist:

- Satisfied: `RuntimeSnapshot.current_position_at_every_tier` remains available.
- Satisfied: `RuntimeSnapshot.ordered_quotient_tiers` remains available.
- Satisfied: primitive-action reference loops still run; full validation includes
  training/reference-loop tests.
- Satisfied: examples did not need a full simultaneous rewrite; only
  `PlateSupportEnvRuntime` needed a schema label/default and one expectation
  update.
- Satisfied: `TowerRuntime` query methods remain available and operate through
  partition compatibility readouts.

### Stage 20.3: Performance Criteria Checklist

#### Action 20.3.1

Status: Completed.

Checklist:

- Satisfied: update diagnostics show delta-based behavior through state/edge
  delta counts, merge counts, dirty collection counts, and full-rebuild
  validation counts.
- Satisfied: normal partition step path avoids the full visible-graph scan and
  uses local refreshed-state delta candidates.
- Satisfied: outgoing action query is local to the requested state cell through
  `PartitionTower.outgoing_action_cells(...)`.
- Satisfied: benchmark/performance hooks exist as `TowerUpdateDiagnostics`
  counters and runtime `tower_update_result` snapshot fields.

Validation note:

- Added `test_partition_backend_step_uses_local_delta_candidates(...)` to prevent
  accidental reintroduction of a full visible-graph scan in the normal partition
  step path.

## Phase 21: Final Git And Reporting Discipline

### Stage 21.1: Inspect Final Diff

#### Action 21.1.1

Status: Completed.

Branch:

```text
codex/young-tableaux-runtime-refactor
```

Commands:

```text
git status --short
git diff --check
git diff --stat
```

Results:

- `git diff --check` reported no whitespace errors.
- Changed files are related to the Young tableaux runtime refactor, runtime
  integration, example/schema migration, tests, README wording, and the required
  implementation log.
- Untracked additions are the new partition package, partition tests, test
  namespace markers, and implementation log.

### Stage 21.2: Final Implementation Report

#### Action 21.2.1

Status: Completed.

Implementation summary:

- Added persistent nested state/action partition tower runtime structures.
- Added schema-driven contraction assignment and incremental delta updates.
- Added action collections, action cells, loop policy, reward aggregation,
  diagnostics, compatibility readout, lift candidates, and refinement fibers.
- Integrated `PartitionTower` into `TowerRuntime` and made it the default
  backend.
- Preserved legacy full-rebuild builder as explicit legacy/validation path.
- Preserved existing snapshot/training surfaces additively.
- Migrated affected example expectations and added schema smoke coverage.

Final validation:

- `uv run pytest tests/tower tests/quotient tests/integration`: `132 passed`
- `uv run pytest tests/examples`: `138 passed`
- `uv run pytest`: `323 passed`
- `uv run ruff check .`: `All checks passed!`

Authorized deviations:

- None. One potential simplification in `TowerMorphism` was corrected before
  moving on.

Remaining risks:

- The implementation is correctness-first and not yet benchmarked for large
  graphs.
- Full tensor/vectorized training hardening remains explicitly out of scope.
- Full formal-stutter semantics remain represented but not mathematically
  completed in runtime behavior.

Ready to commit:

- Yes.

## Phase 4: Loop Policy And Reward Aggregation

### Stage 4.1: Implement Loop Policy

#### Action 4.1.1

Status: Completed.

Implemented:

- `LoopPolicyName`
- `LoopPolicy`
- `InternalEdgeRecord`
- `drop_internal`
- `aggregate_internal`
- `formal_stutter`

#### Action 4.1.2

Status: Completed.

Implemented:

- `record_internal_edge(...)`

### Stage 4.2: Implement Reward Aggregation

#### Action 4.2.1

Status: Completed.

Implemented:

- `RewardAggregationName`
- `RewardAggregationResult`
- `RewardAggregator`
- `aggregate_rewards(...)`
- `sum`, `mean`, `max`, `softmax`, `p_mean`, `p_norm`, and custom callable
  aggregation

#### Action 4.2.2

Status: Completed.

Implemented:

- Additive `QuotientRewardSummary` fields for aggregator name, aggregate reward,
  internal loop policy, and internal contributors.
- Existing mean reward behavior remains compatible.

### Stage 4.3: Validate Loop And Reward Work

#### Action 4.3.1

Status: Completed.

Reality note:

- Initial validation hit a pytest import mismatch between
  `tests/tower/partition/test_reward_aggregation.py` and
  `tests/quotient/test_reward_aggregation.py`.
- Added package namespace `__init__.py` files under `tests/`, `tests/tower/`,
  `tests/tower/partition/`, and `tests/quotient/` so pytest imports the files
  by distinct package-qualified names.

Command:

```text
uv run pytest tests/tower/partition/test_loop_policy.py tests/tower/partition/test_reward_aggregation.py tests/quotient/test_reward_aggregation.py
```

Result:

```text
13 passed
```

## Phase 5: State Partition Layer

### Stage 5.1: Implement State Layer Data Structure

#### Action 5.1.1

Status: Completed.

Implemented:

- `StatePartitionLayer`
- `singleton_layer(...)`
- `carry_forward_from(...)`
- state-to-cell storage
- cell membership storage
- parent/previous-cell maps

#### Action 5.1.2

Status: Completed.

Implemented:

- `cell_of(...)`
- `members(...)`
- `all_cell_ids(...)`
- `contains_state(...)`

### Stage 5.2: Implement State Cell Merge

#### Action 5.2.1

Status: Completed.

Implemented:

- `merge_cells(...)`
- `StateCellMergeResult`
- no-op same-cell merge behavior
- active cell replacement for merged cells

#### Action 5.2.2

Status: Completed.

Implemented:

- deterministic sorted membership readout

### Stage 5.3: Validate State Layer

#### Action 5.3.1

Status: Completed.

Command:

```text
uv run pytest tests/tower/partition/test_state_layer.py
```

Result:

```text
6 passed
```

## Phase 9: Incremental Update

### Stage 9.1: Implement Delta Update Entry Point

#### Action 9.1.1

Status: Completed.

Implemented:

- `PartitionTower.update_with_delta(...)`
- delta-only state and edge registration through `BaseGraphRegistry`
- schema assignment only for newly discovered edge ids
- tier-0 extension for newly discovered states and edges
- current-position refresh even when the structural update is a no-op
- identity morphism reporting for no-op structural updates

### Stage 9.2: Implement Delta Edge Insertion Across Existing Layers

#### Action 9.2.1

Status: Completed.

Implemented:

- insertion of new live edges into the outgoing collection of the source state
  cell at every existing non-internal tier
- internal-edge recording when a new edge is already internal at an existing
  tier
- dirty action-collection tracking only for touched outgoing collections

### Stage 9.3: Implement Schema-Driven Delta Contractions

#### Action 9.3.1

Status: Completed.

Implemented:

- schema-driven contraction of new edge ids at their assigned tier
- state-cell merge recording
- action-collection merge recording
- internal-loop removal/recording during merged collection rebuild
- dirty action-cell index rebuild after affected local updates

#### Action 9.3.2

Status: Completed.

Implemented:

- schema block lookup through the persistent assignment store
- dimensionwise block ordering through declared schema order
- random block stability through stored edge assignments

### Stage 9.4: Implement Tower Morphism Records

#### Action 9.4.1

Status: Completed.

Implemented:

- identity unchanged-tier reporting for no-op updates
- explicit old-state-cell to new-state-cell image maps after nontrivial updates
- explicit old-action-collection to new-action-collection image maps where the
  old collection is attached to an old active state cell
- explicit old-action-cell to new-action-cell image maps where the old action
  cell still has live representative edges after the update

### Stage 9.5: Validate Incremental Update

#### Action 9.5.1

Status: Completed.

Command:

```text
uv run pytest tests/tower/partition/test_incremental_update.py
```

Result:

```text
7 passed
```

## Phase 10: Full-Build Versus Incremental Equivalence

### Stage 10.1: Build Equivalence Fixtures

#### Action 10.1.1

Status: Completed.

Implemented deterministic fixture families in:

- `tests/tower/partition/test_full_incremental_equivalence.py`

Fixture coverage:

- two-state one-edge graph
- three-state path graph
- square graph with dimension labels
- graph with an edge that becomes internal after a merge
- graph with unlabeled edges for discovery-order schema

### Stage 10.2: Assert Equivalence

#### Action 10.2.1

Status: Completed.

Implemented normalized comparisons for:

- state partitions by tier
- outgoing action collections by tier
- internal edges by tier
- schema assignments
- current positions
- compatibility `QuotientTierView` readouts

Reality notes:

- The first equivalence run exposed that `readout.py` was iterating stale action
  collections that were no longer attached to active state cells. The readout
  was corrected to walk active state-cell-to-action-collection pointers only.
- The square graph fixture exposed stale action-cell grouping after a target-side
  state-cell merge. `BaseGraphRegistry` now maintains incoming-edge indexes, and
  `ActionPartitionLayer` dirties incoming source collections when their target
  partition data changes.
- Internal-edge bookkeeping was tightened so active cells carry internal edge
  ids forward across tiers and merges.

### Stage 10.3: Validate Equivalence

#### Action 10.3.1

Status: Completed.

Command:

```text
uv run pytest tests/tower/partition
```

Result:

```text
63 passed
```

## Phase 11: TowerRuntime Integration Behind Backend Boundary

### Stage 11.1: Add Runtime Backend Selection

#### Action 11.1.1

Status: Completed.

Implemented:

- explicit `tower_backend` constructor option on `TowerRuntime`
- optional `contraction_schema`, `loop_policy`, and `reward_aggregator`
  constructor dependencies
- `TowerRuntime` ownership of `PartitionTower` when
  `tower_backend="partition"`
- legacy backend preserved as the default during this phase

### Stage 11.2: Wire Reset To Partition Backend

#### Action 11.2.1

Status: Completed.

Implemented:

- partition-backend reset creates a fresh `PartitionTower`
- reset registers the currently visible vista states and edges
- reset populates quotient tiers from partition readout
- reset preserves the existing `RuntimeSnapshot` shape

### Stage 11.3: Wire Step To Partition Backend

#### Action 11.3.1

Status: Completed.

Implemented:

- primitive step semantics remain unchanged
- explored graph and vista graph updates remain unchanged
- partition backend computes visible graph deltas and calls
  `PartitionTower.update_with_delta(...)`
- no-new-exploration steps report `partition_noop` with an identity structural
  update

### Stage 11.4: Preserve Runtime Query Methods

#### Action 11.4.1

Status: Completed.

Implemented:

- existing runtime query methods continue to operate on compatibility
  `QuotientTierView` readouts
- focused tests cover partition-backend reset, step, current deepest tier,
  state projection, trivial projected edge detection, shared cosets, and no-op
  update diagnostics

### Stage 11.5: Validate Backend Integration

#### Action 11.5.1

Status: Completed.

Command:

```text
uv run pytest tests/tower/test_runtime.py tests/tower/partition
```

Result:

```text
71 passed
```

## Phase 12: Snapshot And Training Surface Compatibility

### Stage 12.1: Extend RuntimeSnapshot Additively

#### Action 12.1.1

Status: Completed.

Implemented:

- optional `partition_tower_view` field on `RuntimeSnapshot`
- optional `tower_update_result` field on `RuntimeSnapshot`
- default `None` values so existing snapshot construction remains valid
- partition-backend runtime snapshots populate both fields

### Stage 12.2: Preserve ActionSelectionInput

#### Action 12.2.1

Status: Completed.

Assessment:

- `training/inputs.py` did not require modification.
- `tower_position_key(snapshot)` remains
  `tuple(snapshot.current_position_at_every_tier)`.
- Training-facing input construction does not depend on partition internals.

### Stage 12.3: Validate Training Compatibility

#### Action 12.3.1

Status: Completed.

Command:

```text
uv run pytest tests/training tests/tower/test_snapshot.py
```

Result:

```text
9 passed
```

## Phase 7: Partition Tower Initialization And Full-Build Reference

### Stage 7.1: Implement Update Records And Diagnostics

#### Action 7.1.1

Status: Completed.

Implemented:

- `StateCellMergeRecord`
- `ActionCollectionMergeRecord`
- `TowerMorphism`
- `TowerUpdateDiagnostics`
- `TowerUpdateResult`

### Stage 7.2: Implement PartitionTower Initialization

#### Action 7.2.1

Status: Completed.

Implemented:

- `PartitionTower`
- explicit schema, loop policy, and reward aggregator dependencies
- registry ownership
- schema assignment store ownership
- state/action layer storage
- `last_update_result`

#### Action 7.2.2

Status: Completed.

Implemented:

- `PartitionTower.initialize(...)`
- tier-0 singleton state layer creation
- tier-0 outgoing action layer creation
- schema block processing
- state/action merge records
- current positions
- diagnostics

### Stage 7.3: Implement Full-Build Reference Path

#### Action 7.3.1

Status: Completed.

Implemented:

- `build_partition_tower_full(...)`

### Stage 7.4: Validate Initialization

#### Action 7.4.1

Status: Completed.

Command:

```text
uv run pytest tests/tower/partition/test_tower_initialization.py
```

Result:

```text
4 passed
```

## Phase 8: Compatibility Readout To QuotientTierView

### Stage 8.1: Implement State Readout

#### Action 8.1.1

Status: Completed.

Implemented:

- `to_quotient_tier_views(...)`
- state projection from base state to state-cell id
- node coset membership from state partition membership
- tier current positions

### Stage 8.2: Implement Action Readout

#### Action 8.2.1

Status: Completed.

Implemented:

- live edge projection through decision-level partition action cells
- internal edge omission from edge projection
- quotient-edge membership for live action cells
- outgoing knowledge breadcrumbs for compatibility

### Stage 8.3: Validate Readout

#### Action 8.3.1

Status: Completed.

Command:

```text
uv run pytest tests/tower/partition/test_readout.py tests/quotient
```

Result:

```text
11 passed
```

## Phase 6: Action Partition Layer

### Stage 6.1: Implement Action Collection Storage

#### Action 6.1.1

Status: Completed.

Implemented:

- `ActionPartitionLayer`
- `ActionCollectionMergeResult`
- `from_state_layer_and_registry(...)`
- `carry_forward_from(...)`
- first-class state-cell-to-action-collection pointers

#### Action 6.1.2

Status: Completed.

Implemented:

- `outgoing_collection(...)`
- `edge_ids_for_collection(...)`
- `internal_edge_ids(...)`

### Stage 6.2: Implement Action Collection Merge

#### Action 6.2.1

Status: Completed.

Implemented:

- action collection merge
- outgoing edge union
- internal edge detection and recording under `LoopPolicy`
- merged collection attachment to merged state cell

#### Action 6.2.2

Status: Completed.

Implemented:

- dirty collection tracking for affected collections

### Stage 6.3: Implement Decision-Level Action Cells

#### Action 6.3.1

Status: Completed.

Implemented:

- action-cell grouping by source cell, target cell, and action identity

#### Action 6.3.2

Status: Completed.

Implemented:

- `action_cells_for_collection(...)`
- `edge_ids_for_action_cell(...)`
- `representative_edge_ids(...)`

### Stage 6.4: Validate Action Layer

#### Action 6.4.1

Status: Completed.

Command:

```text
uv run pytest tests/tower/partition/test_action_layer.py
```

Result:

```text
6 passed
```
