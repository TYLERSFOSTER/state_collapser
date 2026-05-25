# Young Tableaux Runtime Refactor Blueprint

## Status

This document is the first implementation blueprint for replacing the current
dynamic quotient-tower runtime with the nested state/action partition structure
described in `docs/design/logHRL.tex`.

It is downstream of:

- `docs/code_review/01_001_loghrl_partition_tower_vs_src_review.md`
- `docs/design/logHRL.tex`
- `docs/design/HRL_exploit-explore/01_020_package_owned_dynamic_tower_construction_blueprint.md`
- `docs/design/HRL_exploit-explore/01_021_package_owned_dynamic_tower_construction_implementation_gameplan.md`
- `docs/design/model_train_surfaces/01_001_model_and_training_surface_architecture.md`
- `docs/design/model_train_surfaces/01_002_model_and_training_surface_blueprint.md`
- `docs/engineer_continuity/2026/05/23/01_010_package_readiness_and_loghrl_research_document_consolidation.md`
- `docs/prime_directive/git_practices.md`

This is a blueprint, not an implementation gameplan.

It defines what should be built, why it should be built this way, which existing
surfaces it must preserve, and which older assumptions it supersedes.

Per `docs/prime_directive/git_practices.md`, the eventual implementation should
move to a dedicated implementation branch before execution.

## Central Goal

The central goal is to change the tower runtime model from repeated global
reconstruction to amortized local maintenance.

The current package can build useful quotient-tier views on small examples, but
it rebuilds the full tower from visible graph data on each refresh. The target
architecture should instead maintain the tower as a persistent system of nested
state/action partitions over the discovered base graph, updating only the
consequences of newly discovered states and edges.

The intended runtime shift is:

```text
current normal path:
  every step -> rescan visible graph -> rebuild tier 0 -> rebuild every tier

target normal path:
  every step -> add delta states/edges -> assign schema blocks -> update affected cells
```

This is not a micro-optimization. It is the difference between a research
scaffold that works on small examples and a runtime architecture that can scale
to serious evaluation.

## Controlling Interpretation

The TeX paper now describes the quotient tower as a RAM data structure, not only
as an abstract graph quotient.

The implementation target is:

- one discovered base graph `G_t^0`
- a nested state partition system over the base state set
- a nested action partition system over the base edge/action set
- outgoing-incidence pointers from state cells to action-side data
- an explicit or implicit ordered contraction schema over the relevant base-tier
  edge universe
- local coarsening updates when new edge information arrives
- optional but explicit loop/stutter and reward-aggregation conventions
- compatibility readouts that still look like quotient graph tiers to existing
  training and runtime code

The term "Young tableaux" is not meant to import the full algebraic/combinatorial
machinery of standard Young tableaux. In this repo it names the implementation
analogy: a set together with successively coarser labeled partition cells, where
cells at one tier sit inside cells at the next tier.

The actual data structure should therefore be ordinary Python data structures
representing nested partitions, cell membership, parent-cell maps, and incidence
pointers. It should not depend on a symbolic Young tableaux library.

## What This Supersedes

This blueprint supersedes the tower-construction mechanism implemented after
`docs/design/HRL_exploit-explore/01_020_package_owned_dynamic_tower_construction_blueprint.md`.

That older blueprint correctly moved ownership of tower construction into the
package runtime, and that was an important architectural correction. The current
code reflects that correction in `src/state_collapser/tower/runtime.py` and
`src/state_collapser/tower/construction.py`.

However, the older implementation remains an early scaffold. It does not
implement the current TeX model's RAM data structure.

The superseded assumptions are:

- quotient tiers are rebuilt from scratch as normal runtime behavior
- selected contractions can be chosen by a hard-coded "first 20 percent" rule
- quotient edges are the main action-side representation
- outgoing action information can remain implicit in quotient-edge tuple shapes
- loop deletion can be silent
- policy selection and tower contraction schema can remain loosely connected

The retained assumptions are:

- `TowerRuntime` remains the package-owned coordinator
- examples define environments and tasks, not tower construction internals
- `RuntimeSnapshot` remains the handoff object to training-facing code
- `QuotientTierView` remains useful as a compatibility/readout surface
- current training loops remain valid reference loops, not architectural errors

## Current Implementation Ground Truth

This section records the current state of `/src` so the refactor has an accurate
starting point.

## Runtime Ownership Today

`src/state_collapser/tower/runtime.py` owns:

- hidden graph access
- explored graph growth
- vista graph refresh
- current path rewards
- dynamic tower refresh
- runtime snapshot construction
- active-tier exploit/explore wrapper code

This ownership should remain.

The problem is not that tower construction lives in the wrong high-level owner.
The problem is that the owner currently calls a full rebuild helper on every
refresh.

Current hot path:

```text
TowerRuntime.reset(...)
  -> _refresh_dynamic_tower(...)
  -> build_dynamic_tower(...)

TowerRuntime.step(...)
  -> add BaseEdge to ExploredGraph
  -> refresh VistaGraph at current and next state
  -> maybe push/pull annotation payloads
  -> _refresh_dynamic_tower(...)
  -> build_dynamic_tower(...)
```

Target hot path:

```text
TowerRuntime.reset(...)
  -> PartitionTower.initialize_from_vista(...)
  -> compatibility snapshot

TowerRuntime.step(...)
  -> add BaseEdge to ExploredGraph
  -> refresh VistaGraph at touched states
  -> compute delta states/edges
  -> PartitionTower.update_with_delta(...)
  -> compatibility snapshot
```

## Tower Construction Today

`src/state_collapser/tower/construction.py` currently:

- gathers visible base edges from visited states and the vista cache
- gathers visible base states from explored states and visible edge endpoints
- builds tier `0` by assigning singleton quotient ids to states
- assigns a singleton-like quotient id to every visible base edge
- stores edge ids in `outgoing_knowledge_by_tier`
- repeatedly builds fresh `QuotientTierView` objects
- recomputes eligible nontrivial edges at each tier
- selects the first 20 percent of eligible edges
- builds connected components from selected endpoint pairs
- projects all base states into the next tier
- scans all base edges to build quotient edges
- silently skips projected loops

This is computationally adjacent to graph contraction on the state side. It is
not the nested partition table described in the TeX paper.

## Quotient Data Today

The current quotient package gives us useful compatibility primitives:

- `src/state_collapser/quotient/projection.py`
- `src/state_collapser/quotient/cosets.py`
- `src/state_collapser/quotient/tier_view.py`

`ProjectionMap` maps base states and base edges to quotient ids.

`CosetStore` stores reverse membership of quotient nodes and quotient edges.

`QuotientTierView` combines a projection map, coset store, global outgoing
knowledge by tier, and current position.

These are good readout surfaces. They are not enough as the core runtime model
because they do not store:

- first-class state partition layers
- first-class action partition layers
- parent/child maps between partition layers
- state-cell to outgoing-action pointers
- loop/stutter records
- schema block assignments
- incremental tower morphisms

The refactor should not throw these modules away. It should stop treating them
as the primary storage model.

## Contraction Policy Today

`src/state_collapser/contract/policy.py` currently defines:

- `ContractionPolicy`
- `LabelContractionPolicy`
- `SeededRandomContractionPolicy`

The protocol is local-star based:

```text
select(local_star) -> EdgeSelection
```

This is not the same as the paper's contraction schema:

```text
A_t^0 = Sigma_0^1 sqcup Sigma_0^2 sqcup ... sqcup Sigma_0^d
```

The label and random hooks are useful, but the current builder does not consume
them as the source of the tower contraction schedule. The refactor must introduce
a schema surface that assigns base edges to persistent ordered blocks.

## Labels Today

The raw label hooks already exist:

- `PrimitiveAction.labels`
- `BaseEdge.labels`

The missing piece is systematic use.

Most current examples do not label actions or edges by contraction dimension.
The robot constraint toy uses labels for target-region metadata such as `hinge`,
`safe`, and `elbow`, but that is not yet a general dimensionwise action schema.

The refactor should make labels useful without requiring every environment to
adopt labels immediately.

## Training Surfaces Today

The training-facing package already has the right design direction:

- `src/state_collapser/training/inputs.py`
- `src/state_collapser/training/decisions.py`
- `src/state_collapser/training/transitions.py`
- `src/state_collapser/training/collectors.py`
- `src/state_collapser/training/learners.py`
- `src/state_collapser/training/reference_loops.py`

The important current object is `ActionSelectionInput`.

It carries:

- observation
- current base state
- runtime snapshot
- tower position key
- optional action mask
- optional history window
- optional active-tier state
- optional frozen lower context
- diagnostics

This should remain. The refactor should enrich what `RuntimeSnapshot` can expose,
not replace the training philosophy.

The package should still expose components, not a master trainer.

## Runtime Snapshot Today

`src/state_collapser/tower/snapshot.py` currently exposes:

- `current_base_state`
- `explored_graph`
- `vista_graph`
- `ordered_quotient_tiers`
- `current_position_at_every_tier`
- current and cumulative reward summaries
- quotient-tier reward summaries
- optional active-control fields

Many tests and examples consume `ordered_quotient_tiers` and
`current_position_at_every_tier`.

The new partition tower should therefore provide compatibility readouts for these
fields during migration.

## Example Runtime Dependencies Today

Several examples expose `runtime.quotient_tiers` or rely on
`current_position_at_every_tier`.

Affected example families include:

- `rl_counterpoint_v3`
- `plate_support_env`
- `articulated_loop_env`
- `cable_parallel_env`
- `dual_arm_manipulation_env`
- `parallelogram_singularity_env`

The refactor should not require a simultaneous rewrite of every example
training loop. It should preserve position-key and quotient-tier readout
compatibility while adding the real partition surfaces.

## Core Architectural Decision

The new runtime core should be a persistent `PartitionTower`.

`PartitionTower` should own:

- base graph registry ids
- schema block assignments
- state partition layers
- action partition layers
- outgoing-incidence pointers
- loop/internal-edge records
- current positions by tier
- tower morphism/update metadata
- compatibility readout construction

`TowerRuntime` should own the environment/runtime orchestration and delegate
tower maintenance to `PartitionTower`.

`QuotientTierView` should become a readout/adapter type for legacy and
inspection surfaces.

The target ownership split is:

```text
TowerRuntime:
  owns environment step, explored graph, vista graph, rewards, snapshots

PartitionTower:
  owns persistent state/action partition tower and incremental updates

ContractionSchema:
  owns ordered edge-block assignment semantics

RewardAggregator:
  owns direct-image reward aggregation semantics

QuotientTierView adapter:
  presents compatibility graph-quotient views from partition tower data
```

## Proposed Package Shape

The exact file split can be settled in the implementation gameplan, but the
blueprint target should be close to:

```text
src/state_collapser/tower/partition/
    __init__.py
    ids.py
    base_registry.py
    schema.py
    state_layer.py
    action_layer.py
    loop_policy.py
    reward_aggregation.py
    tower.py
    update.py
    readout.py
    diagnostics.py
```

This can also be implemented as fewer files at first if that is safer. The
important thing is the conceptual split, not file proliferation.

The existing modules should evolve as follows:

```text
src/state_collapser/tower/runtime.py
  Keep as owner/orchestrator.
  Replace full rebuild hot path with PartitionTower updates.

src/state_collapser/tower/construction.py
  Keep as full-build validator/fallback during migration.
  Stop being the normal runtime update path.

src/state_collapser/quotient/*
  Keep as compatibility/readout types.
  Do not force them to carry the whole new runtime model.

src/state_collapser/contract/policy.py
  Keep local-star policies if useful for vista annotation.
  Add or split out contraction schema surfaces.

src/state_collapser/core/rewards.py
  Extend quotient reward summaries and aggregation rules.

src/state_collapser/training/*
  Keep component-surface philosophy.
  Add tower/action-cell decision inputs only where needed.
```

## Core Data Model

## Base Identifiers

The partition runtime should use compact stable ids internally.

Recommended ids:

```text
StateId
EdgeId
ActionId
StateCellId
ActionCellId
ActionCollectionId
SchemaBlockId
TierIndex
```

These can be lightweight wrappers or integer ids. The performance-oriented
default should be integer ids with typed aliases or frozen slot dataclasses only
where they buy clarity.

The package can still expose original `State`, `BaseEdge`, and `PrimitiveAction`
objects at public boundaries.

Internal partition operations should avoid repeatedly hashing heavy state and
edge objects when compact ids will do.

## BaseGraphRegistry

The new tower core needs a registry that gives the partition structure a stable
view of the discovered base graph.

Responsibilities:

- assign `StateId` to each discovered state
- assign `EdgeId` to each discovered base edge
- store `EdgeId -> source StateId`
- store `EdgeId -> target StateId`
- store `EdgeId -> PrimitiveAction` or `ActionId`
- store labels from `BaseEdge.labels` and `PrimitiveAction.labels`
- store outgoing edge ids by source state id
- detect newly discovered states
- detect newly discovered edges
- provide original object lookup for readouts and tests

Important: this registry should be the tower's internal graph memory, not a
replacement for `ExploredGraph` and `VistaGraph`. `ExploredGraph` and
`VistaGraph` remain runtime-facing objects. The registry is the partition
tower's normalized index over the relevant visible graph data.

Recommended shape:

```text
BaseGraphRegistry
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

Performance rule:

- edge/state id assignment happens only when an item is first discovered
- delta detection should be `O(delta)` relative to refreshed vista output
- no global visible-edge scan should be needed in the normal step path

## ContractionSchema

The new schema surface must be distinct from the current local-star
`ContractionPolicy`.

The schema answers:

```text
Given a base edge, which ordered contraction block does it belong to?
```

The runtime should persist that answer.

Required semantics:

- each scheduled edge receives a stable `SchemaBlockId`
- schema block order is inspectable
- schema assignment is deterministic for a fixed seed/config and discovery order
- newly discovered edges can be assigned without resampling old edges
- dimensionwise label schemas are supported
- random-at-rate schemas are supported
- unscheduled/no-op edges are representable if needed

Recommended protocol:

```text
class ContractionSchema:
    def assign_edge(edge_id, registry) -> SchemaBlockId | None: ...
    def ordered_blocks() -> tuple[SchemaBlockId, ...]: ...
    def block_sort_key(block_id) -> object: ...
```

Potential concrete schemas:

```text
LabelBlockSchema
  maps labels to ordered blocks such as x, y, z

DimensionwiseSchema
  convenience wrapper around LabelBlockSchema

SeededRandomRateSchema
  assigns newly discovered edges into persistent random blocks

DiscoveryOrderChunkSchema
  deterministic fallback based on discovery order and chunk size/rate

NoContractionSchema
  keeps tier 0 only
```

The current `LabelContractionPolicy` and `SeededRandomContractionPolicy` should
not be silently reinterpreted as schemas. That would be confusing because their
protocol is local-star selection. They can be adapted or deprecated, but the
new schema surface should be named honestly.

## StatePartitionLayer

A `StatePartitionLayer` represents the state-side Young diagram at one tier.

Responsibilities:

- map each discovered `StateId` to its active `StateCellId` at this tier
- store members of each state cell
- store parent/child or previous/next tier relationships
- support lookup of the current cell containing a state
- support creation of a merged cell from prior cells
- record which prior cells were coalesced into which new cell
- expose current state-cell ids for snapshot positions

Recommended shape:

```text
StatePartitionLayer
  tier_index
  cell_of_state_id: StateId -> StateCellId
  members_by_cell_id: StateCellId -> compact member set
  parent_cell_by_previous_cell_id: StateCellId -> StateCellId
  previous_cells_by_cell_id: StateCellId -> tuple[StateCellId, ...]
```

The implementation must be careful not to copy large member sets repeatedly.

Allowed strategies:

- union-by-size member storage
- persistent parent pointers plus lazy member expansion
- immutable `frozenset` only for small/test layers
- compact sorted tuples for deterministic tests
- debug-only materialized membership

The first implementation can be simpler than the final optimized structure, but
the normal update algorithm must not require a global state scan just to answer
"what cell contains this state?"

## ActionPartitionLayer

An `ActionPartitionLayer` represents the action-side Young diagram at one tier.

This is the most important missing structure in current `/src`.

It must represent outgoing action data as first-class data attached to state
cells. The exact naming should be chosen carefully because the TeX discussion
uses "action cell" and "outgoing-action cell collection" in close proximity.

The blueprint distinction is:

- storage-level outgoing bucket: the pooled base edges available from a state
  cell after coarsening
- decision-level quotient action: a selectable abstract action class derived
  from that outgoing bucket, usually grouped by target cell and optional action
  labels

The storage-level bucket is the core Young-diagram action partition.

The decision-level quotient action is the surface an RL engineer will usually
ask for when selecting actions downstairs.

The action layer should therefore support both:

```text
Out_i(C)
  all outgoing base edges available from state cell C at tier i

outgoing_action_cells(i, C)
  selectable quotient action classes derived from Out_i(C)
```

Minimum responsibilities:

- map a state cell to its outgoing action bucket or collection id
- map bucket/collection id to member edge ids
- map edge ids to active action-side status at this tier
- record internal/loop edges removed at this tier
- support merging two outgoing buckets during state-cell coalescence
- support fast query of outgoing action choices from a state cell
- support representative-edge lookup for lift/refinement

Recommended shape:

```text
ActionPartitionLayer
  tier_index
  outgoing_collection_by_state_cell: StateCellId -> ActionCollectionId
  edge_ids_by_collection: ActionCollectionId -> compact edge set
  internal_edge_ids_by_state_cell: StateCellId -> compact edge set
  action_cell_ids_by_collection: ActionCollectionId -> tuple[ActionCellId, ...]
  edge_ids_by_action_cell: ActionCellId -> compact edge set
  source_cell_by_action_cell: ActionCellId -> StateCellId
  target_cell_by_action_cell: ActionCellId -> StateCellId | None
  label_key_by_action_cell: ActionCellId -> object | None
```

The first implementation can simplify this by making `ActionCollectionId` the
primary object and deriving `ActionCellId` groups on demand. But the public
surface should be designed as if quotient action cells are real queryable
objects, because that is what training code will need.

Performance rule:

- the state-cell-to-action-collection pointer is first-class
- no caller should have to scan all quotient edges to find outgoing actions from
  the current coset

## LoopPolicy

Loop/internal-edge handling must become explicit.

The default training-friendly convention should be:

```text
drop_internal
```

Meaning:

- if an edge's source and target are in the same state cell at tier `i`, it is
  removed from the tier-`i` outgoing navigation surface
- it is not exposed as an ordinary selectable quotient action
- the quotient task intentionally ignores intra-coset movement at that tier

But the system must record enough metadata to say this happened.

Recommended policies:

```text
drop_internal
  remove internal loops from navigation, record counts/ids for diagnostics

aggregate_internal
  remove internal loops but aggregate their rewards/statistics as residual data

formal_stutter
  retain a non-navigation stutter symbol for theorem/accounting readouts
```

The key correction from the code review discussion is that stutters should be
optional, not forced as live actions. The package should not make quotient
training re-learn internal motion by default.

However, silent deletion is not acceptable. The chosen convention should be a
configuration object and should appear in diagnostics and reward summaries.

## RewardAggregator

The reward side must match the current TeX document.

Direct image reward is not assumed to be average only.

Supported aggregation family:

- `sum`
- `mean`
- `max`
- `softmax`
- `p_mean`
- `p_norm`
- custom callable

Important semantics:

- `mean` or conditional expectation is the exact linear descent case
- `max` is often better for RL when the quotient task should remember that a
  good lift exists
- `sum` may be useful for cumulative accounting
- `softmax` interpolates between average-like and max-like behavior
- `p = infinity` corresponds to max-type behavior
- internal loops can be ignored, aggregated separately, or represented as formal
  stutters depending on `LoopPolicy`

Recommended objects:

```text
RewardAggregator
  aggregate(values) -> float

QuotientRewardSummary
  aggregator_name
  contributing_rewards
  aggregate_reward
  internal_loop_policy
  internal_contributors
```

Current `core/rewards.py` only stores a mean reward in `QuotientRewardSummary`.
That should be extended rather than hard-coded to one interpretation.

## PartitionTower

`PartitionTower` is the main new runtime object.

Responsibilities:

- own `BaseGraphRegistry`
- own `ContractionSchema`
- own `LoopPolicy`
- own reward aggregation config
- own active state/action partition layers
- maintain current positions by tier
- update with delta states/edges
- expose tower morphism/update records
- produce compatibility `QuotientTierView` readouts
- expose quotient-action/lift surfaces

Recommended public methods:

```text
initialize(initial_states, initial_edges, current_state) -> TowerUpdateResult

update_with_delta(delta_states, delta_edges, current_state) -> TowerUpdateResult

current_state_cell(tier, state) -> StateCellId | None

current_position_at_every_tier(current_state) -> tuple[StateCellId | None, ...]

outgoing_action_cells(tier, state_cell) -> tuple[ActionCellId, ...]

action_cell_members(tier, action_cell) -> tuple[BaseEdge, ...]

representative_edges(tier, action_cell) -> tuple[BaseEdge, ...]

lift_candidates(tier, action_cell, current_base_state) -> tuple[BaseEdge, ...]

refinement_fiber(from_tier, to_tier, cell_or_action) -> object

to_quotient_tier_views() -> tuple[QuotientTierView, ...]
```

The exact method names can change. The required surfaces should not.

## TowerUpdateResult

Every update should return a compact result object.

Responsibilities:

- report whether the tower changed
- report delta state and edge ids
- report schema assignments for new edges
- report affected tiers
- report state-cell merges
- report action-bucket/action-cell merges
- report internal loop removals
- report current positions
- expose tower morphism data from previous active cells to current active cells
- carry diagnostics for testing and benchmarking

Recommended shape:

```text
TowerUpdateResult
  changed: bool
  delta_state_ids
  delta_edge_ids
  schema_assignments
  affected_tiers
  state_merges
  action_merges
  internal_edges
  current_position_by_tier
  morphism
  diagnostics
```

This object becomes essential for tests proving that updates are local rather
than accidental full rebuilds.

## TowerMorphism

The TeX paper discusses morphisms:

```text
G_t^bullet -> G_{t+1}^bullet
```

Implementation should represent this concretely enough for debugging and tests.

Minimum useful structure:

```text
TowerMorphism
  state_cell_image_by_tier
  action_collection_image_by_tier
  action_cell_image_by_tier
  unchanged_tiers
  created_tiers
```

If the implementation mutates active tables in place, then the morphism must be
recorded before old cell ids are overwritten or retired. A versioned cell-id
strategy is recommended:

```text
StateCellId(tier, generation, ordinal)
ActionCollectionId(tier, generation, ordinal)
ActionCellId(tier, generation, ordinal)
```

This avoids the conceptual bug of pretending a mutated object is both the old
cell and the new cell.

## Normal Runtime Algorithm

## Reset

On reset:

1. `TowerRuntime` resets `ExploredGraph` and `VistaGraph`.
2. If an initial state is provided, the runtime adds it to `ExploredGraph`.
3. `VistaGraph` refreshes the initial state's local vista.
4. `TowerRuntime` passes the initial visible states/edges to `PartitionTower`.
5. `PartitionTower` registers states and edges.
6. `PartitionTower` initializes tier-0 state cells as singletons.
7. `PartitionTower` initializes tier-0 outgoing buckets from outgoing edge ids.
8. `PartitionTower` assigns schema blocks to visible edges.
9. `PartitionTower` processes the schema blocks needed to construct the current
   initial tower.
10. `TowerRuntime` asks the tower for compatibility tier views and current
    positions.
11. `TowerRuntime` returns a `RuntimeSnapshot`.

The first reset may still behave like a full build because there is no prior
tower. That is fine.

The key is that subsequent steps should be incremental.

## Step With No New Exploration

If the realized move does not add new states or new visible base edges:

1. `ExploredGraph` may update current path/current state.
2. `VistaGraph` may refresh cached local vista.
3. `PartitionTower` receives an empty delta.
4. `PartitionTower` does not merge any cells.
5. `PartitionTower` updates current positions only.
6. The tower morphism is identity.
7. The snapshot still reflects the new current base state.

This case matters because many RL steps revisit known graph regions. The tower
should not rebuild when there is no new structural information.

## Step With New Vista

If the realized move discovers a new state or new visible base edges:

1. `TowerRuntime` identifies `delta_states` and `delta_edges`.
2. The base registry assigns ids only for the delta.
3. Tier `0` gets new singleton cells for new states.
4. Tier `0` outgoing buckets are updated for source states with new edges.
5. New edge ids receive persistent schema block assignments.
6. Each new edge is inserted into the outgoing data of the relevant existing
   state-cell chain unless it is internal at that tier.
7. For each schema block affected by the delta, the tower processes only the
   delta edges in that block and any cell merges they force.
8. Merging two state cells creates a new state cell at the relevant tier.
9. Merging two state cells coalesces their outgoing action data.
10. Internal edges created by the merge are removed or recorded according to the
    loop policy.
11. Dirty outgoing collections are re-indexed into quotient action cells only
    where needed.
12. Current positions and morphism records are updated.
13. Compatibility readouts are rebuilt only for affected tiers, or lazily on
    snapshot demand.

This is the heart of the refactor.

## Critical Nuance: New Edges Are Both Data And Possible Contractions

A newly discovered edge has two roles:

- it is outgoing information that must become visible from the state cells
  containing its source
- it may itself be a contraction-driving edge in one schema block

Even if a new edge's schema block is not currently causing a merge at some tier,
the edge may still need to be present in that tier's outgoing action data unless
it is internal there.

Therefore, the update algorithm must not only process new edges as contraction
events. It must also insert new edges into the outgoing action-side structure
along the existing state-cell chain.

This nuance is exactly where a naive "only contract delta edges" implementation
can become wrong.

## Coarsening Algorithm Sketch

The implementation gameplan should refine this, but the intended update shape is:

```text
update_with_delta(delta_states, delta_edges, current_state):
  register delta states and edges
  extend tier-0 state/action tables
  assign schema block ids to delta edges

  for each tier i in schema order:
    ensure tier i exists by carrying forward tier i-1 as needed

    insert delta outgoing edge data into tier i action structures

    for each delta edge e assigned to block i:
      source_cell = state_layer[i-1].cell_of(source(e))
      target_cell = state_layer[i-1].cell_of(target(e))

      if source_cell == target_cell:
        record e as internal/trivial at tier i
        continue

      merged_state_cell = merge_state_cells(source_cell, target_cell)
      merged_out = merge_outgoing_collections(Out(source_cell), Out(target_cell))
      internal = remove_or_record_edges_internal_to(merged_state_cell, merged_out)
      attach merged_out to merged_state_cell
      mark affected collections/action cells dirty

    rebuild only dirty quotient-action indexes for tier i
    update current position at tier i
    record morphism data
```

This sketch deliberately avoids saying "scan every base edge." Any step that
requires scanning every edge in normal operation is suspect and must be justified
as debug/validation only.

## Full-Build Validator

The existing `build_dynamic_tower(...)` should not remain the normal runtime
path, but some full-build path should remain available during migration.

Purpose:

- validate incremental results on small graphs
- provide a debugging fallback
- support deterministic tests
- help isolate schema bugs

However, the full-build validator must be updated to use the same schema
assignments and loop/reward conventions as the incremental tower. Otherwise it
will not be a valid comparison.

Recommended end state:

```text
build_partition_tower_full(...)
  slow but semantically equivalent reference builder

PartitionTower.update_with_delta(...)
  normal runtime path
```

The old current builder can be kept temporarily as `legacy_build_dynamic_tower`
until tests migrate.

## Compatibility Strategy

## Keep `RuntimeSnapshot`

`RuntimeSnapshot` should remain the main handoff object.

Additive fields may be introduced later:

```text
partition_tower_view
tower_update_result
loop_policy
reward_aggregator
```

But existing fields should remain stable:

```text
ordered_quotient_tiers
current_position_at_every_tier
```

The first implementation should preserve existing example tests where possible.

## Keep `QuotientTierView` As Readout

Existing callers expect:

- `tier.current_position`
- `tier.projection.project_state(...)`
- `tier.projection.project_edge(...)`
- `tier.cosets.quotient_node_members`
- `tier.cosets.quotient_edge_members`
- `tier.same_coset(...)`
- `tier.projected_edge_is_trivial(...)`
- `tier.is_point()`

The partition tower should be able to emit `QuotientTierView` objects from its
state/action tables.

Readout construction:

- state projection comes from `StatePartitionLayer.cell_of_state_id`
- node cosets come from state-cell membership
- edge projection comes from decision-level action cells or quotient-edge readout
- trivial projected edges come from internal-edge records or same-cell endpoint
  tests
- current position comes from current base state's state cell at each tier

Important: the adapter is allowed to be a little slower than the runtime core if
it is only built for snapshots/tests. The hot update path should not depend on
constructing full `QuotientTierView` objects every time.

## Preserve Tower Position Keys

Training code currently uses:

```text
tuple(snapshot.current_position_at_every_tier)
```

This should remain valid.

The ids in the tuple may change from tuple-shaped quotient-node ids to
`StateCellId`-like ids. That may break tests that compare exact reprs, but
should not break tests that treat ids opaquely.

If exact id stability is needed for saved artifacts, the implementation should
provide a serialization/stable-key method.

## Preserve Primitive-Action Reference Loops

The current training-surface philosophy is correct:

- package exposes components
- engineer owns training loop composition

Therefore, the refactor should not force every example to immediately train over
quotient action cells.

Supported loop styles after refactor:

- primitive-action loop keyed by tower position
- primitive-action loop with tower diagnostics
- quotient-action loop with immediate lift
- coarse policy downstairs plus refinement policy upstairs
- actor-critic over action cells with custom executor
- Q-learning over action-cell ids with lift candidates

The first implementation only needs to make these loops possible through clean
surfaces. It does not need to make one official trainer.

## New Public/Package Surfaces

The package should expose component surfaces for serious RL engineering use.

Minimum new tower query surfaces:

```text
current_state_cell(tier)
state_cell_members(tier, state_cell)
outgoing_action_cells(tier, state_cell)
action_cell_members(tier, action_cell)
representative_edges(tier, action_cell)
lift_candidates(tier, action_cell, current_base_state)
refinement_fiber(source_tier, target_tier, cell_or_action)
reward_aggregate(tier, action_cell, aggregator=None)
internal_edges(tier, state_cell)
```

Minimum diagnostics:

```text
last_update_delta_size
last_update_affected_tiers
last_update_state_merges
last_update_action_merges
last_update_internal_edges
last_update_schema_assignments
last_update_readout_rebuilds
```

Minimum schema surfaces:

```text
schema_assignment(edge)
edges_in_schema_block(block_id)
ordered_schema_blocks()
```

These surfaces are what make the tower usable without spelunking tuple-shaped
internal ids.

## Interaction With Existing Modules

## `TowerRuntime`

Required changes:

- add a `PartitionTower` member
- initialize it on reset
- update it on step
- keep `ExploredGraph` and `VistaGraph` ownership
- replace `_refresh_dynamic_tower` normal path
- still support seeded static `quotient_tiers` if needed, but mark as legacy or
  compatibility mode
- populate snapshots from partition tower readouts
- expose existing query methods through partition tower where possible

Current query methods should survive:

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

Some names may become compatibility names:

- `selected_base_edges` should probably become "selected/processed schema edges
  for last update" rather than first 20 percent of eligible edges
- `tier_contraction_records` should evolve into schema-block update records
- `tower_stopping_reason` should become less central when schema block depth is
  fixed/known

## `tower/construction.py`

Required changes:

- keep a full-build reference path
- remove hard-coded 20 percent selection from any authoritative path
- consume `ContractionSchema` assignments if used as validator
- construct partition layers before quotient readouts
- make loop policy explicit

Potential migration:

```text
construction.py
  legacy builder remains temporarily

partition/update.py
  new normal update path

partition/readout.py
  compatibility tier-view construction
```

## `contract/policy.py`

Required changes:

- introduce schema objects or move them into `tower/partition/schema.py`
- clarify that local-star policies are not contraction schemas
- possibly keep `ContractionPolicy` for vista annotation/message selection
- add compatibility adapters where natural

Recommended naming:

```text
LocalEdgeSelectionPolicy
ContractionSchema
EdgeBlockSchema
```

Avoid naming the new schema `ContractionPolicy` unless the old protocol is
changed deliberately.

## `core/action.py` And `core/edges.py`

Likely changes:

- preserve existing `labels` fields
- document labels as schema-friendly structural metadata
- maybe add helper accessors for combined edge/action labels
- avoid requiring labels for all environments

No broad rewrite is required here.

## `graph/explored_graph.py` And `graph/vista_graph.py`

Likely changes:

- add or expose delta-friendly methods if needed
- avoid forcing the tower to rescan all visited states each step
- preserve annotation stores for any remaining local message/diagnostic use

The new partition tower should not depend on `VistaGraph.push_message` and
`pull_message` for core construction. The paper has moved to partition coarsening
as the explicit data structure.

## `quotient/*`

Likely changes:

- keep current classes
- possibly add adapter helpers
- do not overload `QuotientTierView` with every new partition invariant

`QuotientTierView` is a view. The partition tower is the model.

## `core/rewards.py`

Required changes:

- extend quotient reward summaries beyond mean-only
- represent aggregator name/config
- represent internal-loop policy where relevant
- support max and order-`p` aggregation

This can be a lightweight first pass. The tower refactor should not become a
full reward-system rewrite.

## `training/*`

Required changes:

- preserve existing component surfaces
- add optional action-cell/fiber diagnostics to `ActionSelectionInput` only when
  needed
- do not create a master trainer
- ensure reference loops can still use primitive actions

Potential additive surfaces:

```text
TowerActionSurface
QuotientActionSelectionInput
LiftCandidateBatch
```

These should be optional, not required for every environment.

## Example Environments

Required changes:

- current example tests should remain as stable as possible
- add schema labels to at least one or two examples for meaningful tests
- do not force all examples to adopt dimensionwise labels immediately

Likely first examples to adapt:

- `robot_constraint_toy` for label/dimension schema smoke tests
- `plate_support_env` for exploit/explore integration
- one small synthetic graph in `tests/tower` for deterministic partition tests

Later examples can add labels when evaluation work requires it.

## Testing Blueprint

The refactor needs serious tests because it changes the core representation.

## Unit Tests For Ids And Registry

Required tests:

- states receive stable ids
- edges receive stable ids
- duplicate edge registration is idempotent
- outgoing edge index updates only for source state
- labels combine edge and action labels correctly
- delta detection distinguishes known and new edges

## Unit Tests For Schema

Required tests:

- label schema assigns expected blocks
- dimensionwise schema preserves declared block order
- random schema is deterministic under seed
- random schema assigns only new edges during delta update
- old random assignments do not jitter after new edges arrive
- unscheduled edges are handled explicitly

These tests directly cover the code-review finding that the current
`ContractionPolicy` does not control tower construction.

## Unit Tests For State Layers

Required tests:

- tier `0` state cells are singletons
- merging two cells creates a new cell id
- all member states point to the new cell
- unaffected states keep inherited pointers
- parent/child maps are correct
- repeated merge of already equal cells is a no-op
- membership readout is deterministic

## Unit Tests For Action Layers

Required tests:

- tier `0` outgoing buckets initialize from source state's outgoing edges
- state-cell-to-outgoing-action pointer exists
- merging state cells merges outgoing buckets
- merged outgoing data is available from every representative state's cell
- internal loops are removed or recorded according to loop policy
- outgoing action-cell queries do not scan all global edges
- representative edges are returned for action cells
- target-cell grouping works for decision-level quotient actions

These tests are the most important new paper-conformance tests.

## Unit Tests For Loop And Reward Policies

Required tests:

- `drop_internal` removes internal actions from navigation
- `drop_internal` records internal edge ids/counts
- `formal_stutter` produces stutter readout without exposing it as ordinary
  navigation unless requested
- `aggregate_internal` records residual reward contributors
- reward aggregators support mean, sum, max, softmax, and p-style aggregation
- `max` and `mean` produce different expected summaries on the same action cell

## Unit Tests For Incremental Equivalence

Required tests:

- build a small deterministic graph by full build
- build the same graph through stepwise delta updates
- assert same state partitions by tier
- assert same action outgoing buckets by tier
- assert same internal edge records by tier
- assert same compatibility `QuotientTierView` readouts
- assert same current positions

This is the key proof that the new runtime is not merely faster but semantically
correct relative to the full specification.

## Unit Tests For Locality

Required tests:

- no-op move returns identity tower morphism
- adding one new edge touches only expected tiers/cells
- update diagnostics report delta sizes
- adapter readout can be lazy or affected-tier only
- old random schema assignments remain untouched

These tests should not rely on wall-clock timing. They should assert structural
operation counts exposed in diagnostics.

## Runtime Tests

Existing `tests/tower/test_runtime.py` will need updates.

Likely changes:

- `test_immediate_full_tower_update` can still assert point collapse on tiny
  graph
- `test_runtime_supports_dynamic_queries` should still pass through adapters
- `test_runtime_exposes_tierwise_contraction_records` should be rewritten around
  schema block/update records
- add tests proving `LabelBlockSchema` controls the selected contraction block
- add tests proving old `LabelContractionPolicy` no longer falsely appears to
  control tower construction unless adapted

## Integration Tests

Existing integration tests should mostly continue to assert:

- snapshots remain coherent
- current positions exist
- tower depth behaves sensibly
- primitive-action training loops still run
- reward totals still accumulate

New integration tests should assert:

- partition tower readouts are present
- outgoing action-cell surface is queryable from a runtime snapshot or runtime
- lift candidates exist for a simple quotient action cell
- no-new-exploration step does not rebuild the tower
- new-vista step reports a non-empty update result

## Example Training Tests

Current training tests that key by `current_position_at_every_tier` should remain
valid.

New tests should cover:

- action selection input can carry partition diagnostics
- a primitive-action learner can ignore new tower action surfaces
- an engineer-authored quotient-action loop can query action cells and lift
  candidates

This protects the design principle from the model/training surface documents:
the package provides the parts, not one rigid training choreography.

## Expected Test Breakages

The following tests or assumptions are expected to need modification:

- tests asserting exact `TierContractionRecord.selected_base_edges`
- tests assuming `outgoing_edge_knowledge_by_tier` is the main outgoing surface
- tests relying on the first 20 percent hard-coded selection behavior
- tests treating `LabelContractionPolicy` as if it defines the tower schema
- tests comparing exact quotient id shapes instead of opaque ids

These breakages are healthy if the replacements assert the new invariants.

## Performance Blueprint

## Current Cost Shape

The current runtime tends toward:

```text
each refresh:
  collect visible base edges
  collect visible base states
  build tier 0
  for each tier:
    scan/sort eligible visible edges
    select first 20 percent
    build connected components
    scan all base states
    scan all base edges
    create quotient edge ids
```

Across a long online run where the discovered graph grows over time, this can
push cumulative cost toward:

```text
sum_t O(d_t * (n_t + m_t))
```

or worse when sorting and repeated object allocation are considered.

## Target Cost Shape

The target normal update cost is:

```text
O(delta states + delta edges)
+ O(schema assignment on delta edges)
+ O(affected state-cell merges)
+ O(affected outgoing collection updates)
+ O(dirty action-cell reindexing)
+ O(snapshot/readout work requested)
```

In sparse RL exploration, `delta` is usually small. Often it is one realized edge
plus a small local vista.

The implementation should aim for cumulative cost closer to:

```text
near-linear or quasilinear in discovered graph information
```

rather than repeatedly proportional to the full discovered graph at every step.

## Performance Requirements

Required runtime discipline:

- no global edge scan in normal `step` tower update
- no global state scan in normal `step` tower update except compatibility
  snapshot fallback
- schema assignment happens once per new edge
- random schema assignments are persisted
- outgoing queries are state-cell pointer lookups
- merging uses compact ids
- member-set copying is bounded or structurally shared
- compatibility readouts can be lazy or affected-tier only

Acceptable first-scope compromises:

- simple Python sets for member storage in small tests
- full readout construction in snapshots while the partition core is validated
- debug-only full rebuild comparison
- no tensor/vectorized implementation yet

Unacceptable first-scope compromises:

- new schema callback called over all edges every tier
- action-cell queries implemented by scanning all quotient edge ids
- random schema resampled on every rebuild
- silent loop deletion with no configured convention
- breaking existing primitive-action training loops without a compatibility path

## Diagnostics For Benchmarking

The new tower should expose counters for serious evaluation:

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

These counters will let us measure whether the new architecture actually avoids
global reconstruction.

## Design Risks

## Risk: Naive Partition Tables Copy Too Much

If every merge copies full member sets and full outgoing edge sets at every tier,
the new structure can become slower and more memory-heavy than the old builder.

Mitigation:

- use compact ids
- use union-by-size
- use structural sharing where practical
- materialize large member sets lazily
- keep debug/readout materialization separate from hot-path updates

## Risk: Action Vocabulary Becomes Confused

The paper and code need a careful distinction between:

- outgoing action buckets used by the coarsening data structure
- selectable quotient action cells used by agents
- original primitive actions used by environments

Mitigation:

- choose names deliberately in the implementation gameplan
- document the distinction in module docstrings
- test each surface independently

## Risk: Compatibility Adapter Hides Bad Core Semantics

It is possible to produce plausible `QuotientTierView` readouts while the
partition tower internals are wrong.

Mitigation:

- test partition tables directly
- test action outgoing pointers directly
- test incremental/full equivalence
- treat `QuotientTierView` as readout, not proof of correctness

## Risk: Random Schema Jitter

If random block assignment is recomputed instead of persisted, the tower can
change for reasons unrelated to exploration.

Mitigation:

- assign random block once per edge id
- store assignment in `PartitionTower`
- include random assignment stability tests

## Risk: Too Much Public API Too Early

The project is still research-mode. Over-hardening the API can freeze wrong
names and wrong abstractions.

Mitigation:

- mark new partition surfaces as package-facing or experimental
- preserve old snapshot fields
- keep training loop composition engineer-owned
- document unstable internals honestly

## Risk: Refactor Sprawls Across Examples

The examples are numerous. A refactor that requires every example to be fully
schema-labeled at once will bog down.

Mitigation:

- preserve primitive-action reference loops
- add labels to a minimal subset first
- let unlabeled environments use deterministic fallback/no-op schemas
- migrate examples incrementally

## Risk: Loop/Reward Semantics Overclaim

If the docs imply exact reward preservation while the code drops internal loops,
the package will overclaim.

Mitigation:

- expose `LoopPolicy`
- expose `RewardAggregator`
- describe quotient reward as aggregation/forgetting
- keep conditional expectation as one special exact case
- allow max and other ML-practical aggregators

## Rollout Shape

This is not the implementation gameplan, but the implementation should likely
roll out in this order:

1. Add ids, registry, schema objects, and unit tests.
2. Add state/action partition layers with direct tests.
3. Add full-build partition reference builder.
4. Add incremental `PartitionTower.update_with_delta`.
5. Add `QuotientTierView` compatibility readout.
6. Wire `TowerRuntime` behind a feature flag or experimental backend.
7. Migrate runtime tests to partition semantics.
8. Add outgoing action/lift query surfaces.
9. Extend reward aggregation and loop policy summaries.
10. Migrate selected example tests.
11. Make partition backend the default once tests prove compatibility.
12. Keep legacy builder temporarily for validation, then demote or remove.

The eventual gameplan should turn this into Phase.Stage.Action form.

## Acceptance Criteria

The refactor is successful when all of the following are true.

Core tower criteria:

- the tower is stored as persistent nested state/action partition layers
- tier `0` state cells are singleton cells
- tier `0` action data is initialized from outgoing edge buckets
- state cells point to outgoing action data as first-class structure
- schema block assignment is explicit and persistent
- dimensionwise and random-at-rate schemas exist
- incremental update processes only delta graph information in the normal path
- loop/internal-edge policy is explicit
- reward aggregation is not hard-coded to mean only

Compatibility criteria:

- `RuntimeSnapshot.current_position_at_every_tier` remains available
- `RuntimeSnapshot.ordered_quotient_tiers` remains available through readout
- existing primitive-action reference loops still run
- examples do not need full simultaneous rewrite
- `TowerRuntime` query methods remain available or have clear replacements

Testing criteria:

- partition layers have direct unit tests
- action outgoing pointers have direct unit tests
- schema assignment has direct unit tests
- incremental update matches full-build reference on small deterministic graphs
- no-op updates produce identity morphisms
- random schema assignments are stable
- loop policies and reward aggregators are tested
- integration tests still pass after migration

Performance criteria:

- update diagnostics show delta-based behavior
- normal step path avoids global edge scans
- outgoing action query is local to current state cell
- benchmark hooks exist for serious evaluation

## Open Design Questions Before Gameplan

These are not blockers for the blueprint, but they should be answered or fixed
by the implementation gameplan.

1. Should the first implementation use integer ids with type aliases, or frozen
   slot dataclasses for ids?

2. Should `PartitionTower` live entirely under `tower/partition/`, or should some
   schema surfaces live under `contract/`?

3. What should the final names be for storage-level outgoing buckets versus
   decision-level quotient action cells?

4. Should the partition backend be introduced behind a feature flag first, or
   become default immediately after the first green test slice?

5. Which example should become the canonical dimensionwise-label schema example?

6. What should be the first random-at-rate schema semantics: per-edge iid block
   assignment, per-source outgoing fraction, or discovery-order chunks?

7. Should `QuotientTierView` readouts be built eagerly on every snapshot in the
   first slice, or lazily on demand?

8. Should `formal_stutter` be implemented in the first slice, or should first
   scope support `drop_internal` plus recorded diagnostics only?

9. How much reward aggregation should be wired into runtime snapshots in the
   first slice versus implemented as standalone utilities?

10. When should the legacy `build_dynamic_tower(...)` be deprecated?

## Final Blueprint Judgment

This refactor is the right next architectural move.

The current implementation is good enough as proof that package-owned quotient
tower construction can live in the runtime. It is not good enough as the runtime
model implied by the current research document.

The Young-tableaux/partition refactor should improve correctness and runtime
performance at the same time because both issues have the same root cause:
outgoing action data is currently implicit and repeatedly reconstructed, when it
should be first-class and locally maintained.

The design target is therefore:

```text
same discovered base graph
+ persistent nested state partitions
+ persistent nested action partitions
+ first-class outgoing pointers
+ persistent contraction schema
+ explicit loop/reward aggregation conventions
+ compatibility readouts for existing training surfaces
```

That target matches the current TeX paper, respects the package-owned runtime
architecture, preserves the professional training-surface philosophy, and gives
the repo a credible path from small-example research scaffold to serious
evaluation runtime.
