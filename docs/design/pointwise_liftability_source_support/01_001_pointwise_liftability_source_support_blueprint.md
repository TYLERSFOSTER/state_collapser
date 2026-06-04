# Pointwise Liftability And Source-Support Blueprint

Date: 2026-06-04

Status: implementation blueprint, not yet executed

## Source Material

This blueprint is grounded in:

```text
docs/design/pointwise_liftability_source_support/README.md
docs/engineer_continuity/2026/06/04/state_collapser_pointwise_liftability_diagnostic_report.md
docs/engineer_continuity/2026/06/04/state_collapser_pointwise_liftability_github_issue.md
src/state_collapser/tower/partition/action_layer.py
src/state_collapser/tower/partition/tower.py
src/state_collapser/training/fibers.py
src/state_collapser/training/stages.py
src/state_collapser/examples/plate_support_env/runtime.py
```

The downstream symptom was isolated in `big_boy_benchmarking` counterpoint
tower-control runs. Those runs found that quotient tiers can advertise
nonempty abstract action surfaces while selected abstract action cells fail at
execution with:

```text
no_lift_candidate_from_current_state
```

The Project Owner identified the mathematical reason: after state contraction,
an abstract quotient state-cell pools outgoing action data across all of its
representatives, but a concrete runtime sitting at one representative can only
execute action cells containing a concrete edge sourced at that representative,
unless an explicit within-fiber reanchoring/refinement procedure is available.

## Executive Summary

The current `state_collapser` runtime has two different notions entangled:

```text
quotient-level outgoing action availability
```

and:

```text
current-state executable liftability
```

These are not equivalent after contraction.

The current method:

```python
PartitionTower.outgoing_action_cells(tier, state_cell_id)
```

is a quotient-level readout. It correctly says which abstract action cells hang
over a state cell. It does not know the current concrete/base state and
therefore cannot answer whether any of those actions are executable from the
agent's current representative.

The current method:

```python
PartitionTower.lift_candidates(tier, action_cell_id, current_base_state)
```

prefers directly executable edges but falls back to representative edges from
other sources in the same quotient cell. That fallback is useful for quotient
readout and reasoning, but it is unsafe as an executable-control primitive.

The package needs a first-class pointwise liftability surface.

The correct runtime rule is:

```text
For pointwise execution from base state x, expose only action cells D_i whose
source-support chain contains x and return only concrete edges in D_i sourced
at x.
```

The correct Young-diagram data-structural rule is:

```text
Store adjacent-tier source-support pointers as the authoritative object.
Flattened base-source caches are optional hot-path materializations, not the
mathematical structure itself.
```

## Fixed Design Decisions

The following decisions are fixed for this blueprint.

1. Keep the existing `lift_candidates(...)` behavior for compatibility and
   quotient/readout semantics.

2. Add new strict pointwise APIs instead of silently changing old behavior.

3. Implement adjacent-tier source-support pointers as the authoritative
   Young-diagram/bin structure.

4. Add minimal flattened base-source edge caches in the same pass because
   runtime execution and masks need cheap current-state checks.

5. Add an `action_cell_by_edge_id` or equivalent index so lower-action support
   and pointwise queries do not require repeated scans.

6. Treat representative reanchoring/refinement as out of scope for the first
   fix. The first safe mode is pointwise execution only.

7. Update `PathFiber`, `FiberConditionedStage`, and example runtime
   executability predicates to use strict pointwise liftability.

## Attribution

### Project Owner

The Project Owner supplied the key mathematical distinction and prevented the
design from collapsing into a flat side-table patch.

The central PO insight is:

```text
When a quotient state-cell pools Out data, the executable lift must be sourced
at the current concrete representative, or else the runtime must explicitly
refine/reanchor inside the fiber before executing.
```

The PO also clarified that the efficient Young-diagram formulation is recursive
and adjacent-tier:

```text
tier-i support should point first to tier-(i-1) child bins,
not immediately flatten everything to base states.
```

For example:

```text
tier 0: [0], [1], [2], [3]
tier 1: [0,1], [2], [3]
tier 2: [0,1,2], [3]
```

At tier 2, the support pointers for an action out of `[0,1,2]` should point
first to child bins:

```text
[0,1]
[2]
```

and only recursively expand from there.

### Downstream Benchmarking Engineer

The downstream benchmarking work isolated the concrete runtime symptom in BBB:
nonempty quotient action cells were being exposed to learners, but execution
failed because no selected action cell had a concrete lift from the current
state.

### Codex

Codex's role in this blueprint is to connect the PO/BBB diagnosis to the
current `state_collapser` source surfaces and produce an implementation-ready
design while preserving the recursive Young-diagram structure.

## Current Repo Reality

### `ActionPartitionLayer`

File:

```text
src/state_collapser/tower/partition/action_layer.py
```

The current action layer stores:

```python
outgoing_collection_by_state_cell
edge_ids_by_collection
action_cell_ids_by_collection
edge_ids_by_action_cell
source_cell_by_action_cell
target_cell_by_action_cell
label_key_by_action_cell
```

The action-cell rebuild path is:

```python
ActionPartitionLayer.rebuild_action_cells_for_collection(...)
```

It currently groups live edge ids by:

```text
(source_cell, target_cell, primitive action identity)
```

This grouping is quotient-correct, but it exposes exactly the ambiguity:
within a quotient state-cell, an action cell may have support from only some
representatives or child cells, not all of them.

The rebuild path is the right place to maintain source-support pointers because
it already has:

- the collection being rebuilt;
- each live edge id in that collection;
- the source state id of each edge;
- the current tier source cell;
- the target cell;
- and the action-cell grouping key.

### `PartitionTower`

File:

```text
src/state_collapser/tower/partition/tower.py
```

Current quotient/readout methods:

```python
outgoing_action_cells(tier, state_cell_id)
action_cell_members(tier, action_cell_id)
action_cell_for_edge(tier, edge)
representative_edges(tier, action_cell_id)
lift_candidates(tier, action_cell_id, current_base_state)
refinement_fiber(tier, cell_id)
```

Problem points:

- `outgoing_action_cells(...)` is quotient-level only.
- `action_cell_for_edge(...)` scans current action-cell maps.
- `lift_candidates(...)` falls back to representative edges, so it is not a
  strict executable query.
- There is no method that asks: "Which action cells are executable from this
  current base state?"
- There is no method that asks: "Does this tier have any executable action from
  this current base state?"

### `PathFiber`

File:

```text
src/state_collapser/training/fibers.py
```

Current behavior:

```python
action_vocabulary(total_state)
```

returns quotient-level outgoing action cells at the fine state cell.

```python
admissible_action_cells(total_state)
```

checks whether each fine action cell contains any edge matching the frozen
coarse step. It does not require that the matching edge be sourced at
`total_state`.

```python
lift_candidates(total_state, action_cell)
```

delegates to `tower.lift_candidates(...)`, which may return fallback
representatives not sourced at `total_state`.

### `FiberConditionedStage`

File:

```text
src/state_collapser/training/stages.py
```

Current behavior:

```python
lift_candidates = self.path_fiber.lift_candidates(...)
realized_edge = lift_candidates[0]
runtime_action = realized_edge.action
step_result = self.runtime.step(runtime_action)
```

The stage assumes the first lift candidate is executable from the current
runtime state. That assumption is not valid under the current fallback behavior.

### Example Runtime Predicate

File:

```text
src/state_collapser/examples/plate_support_env/runtime.py
```

Current behavior:

```python
return bool(tower.outgoing_action_cells(tier, state_cell))
```

This tests quotient-level nonemptiness. It does not test pointwise executable
liftability from the current base state.

## Mathematical Model

At tier `i`, let:

```text
pr_i : S_0 -> S_i
```

be the projection from concrete/base states to tier-`i` state cells.

Let:

```text
C_i in S_i
```

be a state cell and:

```text
D_i in Out_i(C_i)
```

be an action cell hanging over it.

The quotient-level predicate is:

```text
Out_i(C_i) != empty.
```

The pointwise executable predicate for current base state `x` is:

```text
there exists e in D_i with source(e) = x.
```

The native Young-diagram support structure should not primarily be:

```text
Supp_i(D_i) subset S_0.
```

That is a useful derived flattening, but it skips the recursive tower
structure.

The native adjacent support should be:

```text
Supp_{i -> i-1}(D_i)
    subset pr_{i,i-1}^{-1}(C_i),
```

where:

```text
pr_{i,i-1} : S_{i-1} -> S_i
```

is the adjacent projection between state partition tiers.

In words:

```text
the source support of a tier-i action cell is the set of tier-(i-1) child
state cells beneath its source cell from which the action cell has support.
```

Repeated recursively, this produces a support path:

```text
C_i
    -> C_{i-1}
    -> C_{i-2}
    -> ...
    -> C_0 = {x}
```

An action cell is pointwise executable from `x` if the current state's
lineage lies along such a source-support path and the bottom tier has at least
one concrete edge sourced at `x`.

## Data-Structure Design

### Authoritative Adjacent-Tier Support

The action layer should maintain source-support pointers from each action cell
to child state cells one tier below.

For `tier > 0`:

```python
source_child_cells_by_action_cell[
    action_cell_id
] -> tuple[StateCellId, ...]

edge_ids_by_action_cell_by_source_child[
    action_cell_id
][child_state_cell_id] -> tuple[EdgeId, ...]

lower_action_cells_by_action_cell_by_source_child[
    action_cell_id
][child_state_cell_id] -> tuple[ActionCellId, ...]

active_child_cells_by_collection[
    collection_id
] -> tuple[StateCellId, ...]
```

For `tier == 0`, the adjacent child is the concrete source state id. Since the
current `StateCellId` type is tiered, tier-0 singleton state cells can be used
as the child bins for uniformity:

```text
source edge id -> source StateId -> tier-0 StateCellId
```

The layer should also maintain:

```python
action_cell_by_edge_id[edge_id] -> ActionCellId
```

for each tier so that lower-action support and lookup can avoid scans.

### Derived Flattened Base-Source Cache

The first implementation should also materialize minimal base-source lookup
data for hot runtime checks:

```python
edge_ids_by_action_cell_by_base_source[
    action_cell_id
][source_state_id] -> tuple[EdgeId, ...]

base_source_ids_by_action_cell[
    action_cell_id
] -> tuple[StateId, ...]

base_active_source_ids_by_collection[
    collection_id
] -> tuple[StateId, ...]
```

This cache answers:

```text
Does current base state x support action cell D_i?
Which concrete edges in D_i are sourced at x?
Does state cell C_i have any action executable from x?
```

The cache is not the mathematical structure. It is a materialized readout of
the recursive pointer structure for direct runtime execution.

### Why Both Are Needed

Adjacent-tier pointers preserve the tower semantics:

```text
tier-i action
    -> supported tier-(i-1) state bins
    -> compatible lower action bins
    -> ...
```

Flattened base-source caches preserve runtime speed:

```text
current base state x
    -> O(1)-ish lookup for executable edges in D_i
```

The first implementation should build both while action cells are already being
rebuilt. This prevents later design churn where the package has strict
pointwise APIs but slow scans.

## Maintenance Strategy

### Rebuild Path

The primary maintenance point is:

```python
ActionPartitionLayer.rebuild_action_cells_for_collection(...)
```

During rebuild, for each edge id assigned to a new action cell:

1. Determine the current tier source cell.
2. Determine the current tier target cell.
3. Determine the action label key.
4. Determine the adjacent child source cell:

   ```text
   source_child = state_layers[tier - 1].cell_of(source_state_id)
   ```

   for `tier > 0`, or:

   ```text
   source_child = state_layers[0].cell_of(source_state_id)
   ```

   for `tier == 0`.

5. Record the edge id under:

   ```text
   action_cell -> source_child
   action_cell -> base source id
   ```

6. Record the source child as active for the collection.

7. Record:

   ```text
   action_cell_by_edge_id[edge_id] = action_cell_id
   ```

8. If `tier > 0`, determine the lower action cell containing this edge at
   `tier - 1`, and record it under:

   ```text
   action_cell -> source_child -> lower action cell
   ```

### API Shape Needed For Maintenance

The current `rebuild_action_cells_for_collection(...)` only receives one
`state_layer`. To build adjacent-tier support, the implementation needs access
to the previous/lower state layer and previous/lower action layer.

Possible approaches:

1. Extend the method signature to optionally accept:

   ```python
   lower_state_layer: StatePartitionLayer | None = None
   lower_action_layer: ActionPartitionLayer | None = None
   ```

2. Keep the method signature but add a second support-enrichment pass in
   `PartitionTower` after action cells are rebuilt.

Decision: use option 1.

Reason:

- The action layer already loops over exactly the relevant edge ids.
- Support data should be built when the action cell id is created.
- A second pass risks re-scanning and increases the chance of stale indexes.

For tier 0, both lower arguments can be `None` and the support bottoms out at
tier-0 singleton cells/base sources.

### Dirty Collections

The current tower already rebuilds dirty action collections after incremental
updates and contractions. Source-support data should be cleared and rebuilt
only for the action cells in a dirty collection.

When obsolete action cells are removed, the implementation must remove their
entries from all new support maps:

```python
edge_ids_by_action_cell
source_cell_by_action_cell
target_cell_by_action_cell
label_key_by_action_cell
source_child_cells_by_action_cell
edge_ids_by_action_cell_by_source_child
lower_action_cells_by_action_cell_by_source_child
edge_ids_by_action_cell_by_base_source
base_source_ids_by_action_cell
action_cell_by_edge_id
```

Collection-level active caches should also be recomputed for the rebuilt
collection:

```python
active_child_cells_by_collection[collection_id]
base_active_source_ids_by_collection[collection_id]
```

## Query API

### Preserve Existing Quotient APIs

These methods should remain:

```python
outgoing_action_cells(tier, state_cell_id)
representative_edges(tier, action_cell_id)
lift_candidates(tier, action_cell_id, current_base_state)
```

But documentation should make clear:

```text
lift_candidates is not strict executable liftability.
It may return representative edges if no edge is sourced at current_base_state.
```

### New Strict Pointwise APIs

Add to `PartitionTower`:

```python
def executable_lift_candidates(
    self,
    tier: int,
    action_cell_id: ActionCellId,
    current_base_state: State,
) -> tuple[BaseEdge, ...]:
    """Return only member edges sourced at the current base state."""
```

Expected behavior:

```text
return ()
```

when no edge in `action_cell_id` has `edge.source == current_base_state`.

Add:

```python
def executable_action_cells(
    self,
    tier: int,
    state_cell_id: StateCellId,
    current_base_state: State,
) -> tuple[ActionCellId, ...]:
    """Return action cells with at least one executable lift from current state."""
```

Expected behavior:

```text
filter outgoing_action_cells(tier, state_cell_id)
by executable_lift_candidates(...)
```

Add:

```python
def tier_is_executable_from_state(
    self,
    tier: int,
    current_base_state: State,
) -> bool:
    """Return whether the current state has any executable action at a tier."""
```

Expected behavior:

```text
C = current_state_cell(tier, current_base_state)
return bool(executable_action_cells(tier, C, current_base_state))
```

### New Adjacent Support APIs

Add to `PartitionTower`:

```python
def supported_child_state_cells(
    self,
    tier: int,
    action_cell_id: ActionCellId,
) -> tuple[StateCellId, ...]:
    """Return tier-(i-1) child cells that support a tier-i action cell."""
```

For `tier == 0`, return `()`, or optionally return the tier-0 source singleton
cells. Decision: return `()` for `tier == 0` because there is no lower state
tier. Pointwise base-source queries cover tier-0 execution.

Add:

```python
def active_child_state_cells(
    self,
    tier: int,
    state_cell_id: StateCellId,
) -> tuple[StateCellId, ...]:
    """Return tier-(i-1) child cells supporting some outgoing action."""
```

For `tier == 0`, return `()`.

Add:

```python
def lower_action_cells_for_supported_child(
    self,
    tier: int,
    action_cell_id: ActionCellId,
    child_state_cell_id: StateCellId,
) -> tuple[ActionCellId, ...]:
    """Return lower action cells under a supported child source cell."""
```

For `tier == 0`, return `()`.

These APIs are not strictly needed for the first BBB pointwise fix, but they
are the mathematically honest surface for the Young-diagram source-support
structure and should be included.

## Training Surface Changes

### `PathFiber.action_vocabulary`

Current behavior:

```text
return all quotient outgoing action cells at the fine state cell.
```

Decision:

Keep this as a quotient vocabulary method for compatibility, but add:

```python
def executable_action_vocabulary(self, total_state: State) -> tuple[ActionCellId, ...]:
    ...
```

This method should call:

```python
tower.executable_action_cells(fine_tier, fine_state_cell, total_state)
```

### `PathFiber.admissible_action_cells`

Change the method so it only returns action cells that:

1. are executable from `total_state`; and
2. match/project to the frozen coarse step.

The matching predicate should be evaluated over strict executable candidates,
not over all action-cell members.

Pseudo-flow:

```python
for fine_action_cell in executable_action_vocabulary(total_state):
    executable_edges = tower.executable_lift_candidates(
        fine_tier,
        fine_action_cell,
        total_state,
    )
    if any(edge matches frozen step for edge in executable_edges):
        keep fine_action_cell
```

### `PathFiber.action_mask`

The mask should continue to be over a caller-provided vocabulary if supplied,
but admissibility must now be pointwise strict.

If no vocabulary is supplied, first-scope behavior can keep using
`action_vocabulary(...)` as the full quotient vocabulary, with the mask marking
only executable/admissible cells true. This preserves stable action dimensions
for learners while preventing invalid choices.

### `PathFiber.lift_candidates`

Change to strict behavior:

```python
return tower.executable_lift_candidates(...)
```

This is a change to `PathFiber`, not to `PartitionTower.lift_candidates`.

The reason is that `PathFiber` is an executable training surface. It should not
return quotient fallback representatives.

### `PathFiber.diagnose_departure`

Update diagnostics so `NO_LIFT_CANDIDATE` means:

```text
no current-state executable lift exists
```

not:

```text
no representative/readout candidate exists
```

The diagnostic payload should include counts:

```text
quotient_member_count
representative_candidate_count
executable_candidate_count
```

where feasible.

### `FiberConditionedStage.step`

No stage should step a runtime action unless the realized edge comes from
strict executable candidates.

After `PathFiber.lift_candidates` becomes strict, the current stage flow is
mostly safe:

```python
lift_candidates = self.path_fiber.lift_candidates(...)
if not lift_candidates:
    diagnostic transition
else:
    realized_edge = lift_candidates[0]
    runtime.step(realized_edge.action)
```

But tests should assert that the stage does not execute fallback
representatives from other sources.

## Runtime Predicate Changes

### `ExploitExploreTowerRuntime`

The runtime already accepts:

```python
tier_is_executable: Callable[[int], bool] | None
```

Do not change this protocol in the first pass.

Reason:

- It keeps the control runtime generic.
- Environment/example adapters can bind the predicate using their current
  runtime snapshot and base state.

### `PlateSupportExploitExploreRuntime`

Update:

```python
_tier_is_executable(...)
```

from quotient nonemptiness:

```python
bool(tower.outgoing_action_cells(tier, state_cell))
```

to pointwise strict executability:

```python
current_state = snapshot.current_base_state
return tower.tier_is_executable_from_state(tier, current_state)
```

with safe handling for missing snapshots/current states.

### Downstream BBB

BBB should receive a handoff after upstream implementation:

```text
use tower.tier_is_executable_from_state(...)
use tower.executable_action_cells(...)
use tower.executable_lift_candidates(...)
```

BBB should keep its execution-time diagnostic fallback, but after this fix,
`no_lift_candidate_from_current_state` should become a structural regression
signal rather than a normal control outcome.

## Test Blueprint

### Partition-Tower Minimal Reproduction

Add a test with:

```text
0 --contract--> 1
0 --to2-------> 2
1 --to2-------> 2
1 --one_only--> 2
```

After contracting `0 -> 1`, tier 1 has:

```text
[0,1], [2]
```

Assertions:

```text
outgoing_action_cells(1, [0,1]) includes one_only
lift_candidates(1, one_only_cell, 0) may still return representative edge 1 -> 2
executable_lift_candidates(1, one_only_cell, 0) == ()
executable_lift_candidates(1, one_only_cell, 1) == (1 --one_only--> 2)
executable_action_cells(1, [0,1], 0) excludes one_only
executable_action_cells(1, [0,1], 1) includes one_only
tier_is_executable_from_state(1, 0) is true because to2 exists from 0
```

This test should also cover:

```text
supported_child_state_cells(1, one_only_cell)
active_child_state_cells(1, [0,1])
```

### Recursive Support Test

Add a 3-simplex-style nested contraction test:

```text
tier 0: [0], [1], [2], [3]
tier 1: [0,1], [2], [3]
tier 2: [0,1,2], [3]
```

Assertions:

```text
supported_child_state_cells(2, D_2) returns tier-1 child bins, not base states
lower_action_cells_for_supported_child(2, D_2, [0,1]) returns tier-1 action cells
lower_action_cells_for_supported_child(2, D_2, [2]) returns tier-1 action cells
```

This test protects the PO's recursive Young-diagram point.

### Existing Compatibility Test

Keep the existing fallback behavior test:

```text
test_lift_candidates_fall_back_to_representatives
```

but update its docstring/name if necessary to clarify:

```text
lift_candidates is representative/readout behavior, not strict execution.
```

### PathFiber Tests

Add tests proving:

- `action_vocabulary` may contain quotient-available action cells;
- `action_mask` marks false for cells not executable from the current state;
- `admissible_action_cells` excludes matching coarse-step action cells when
  their matching edges are sourced at another representative;
- `PathFiber.lift_candidates` returns only strict executable candidates.

### FiberConditionedStage Tests

Add tests proving:

- the stage does not execute an action cell whose only representatives are
  sourced at another state;
- the stage emits a diagnostic transition with `NO_LIFT_CANDIDATE` or prevents
  the action via mask before stepping;
- the runtime's `step(...)` method is not called in that case.

### Plate-Support Runtime Tests

Update/add tests proving:

- `_tier_is_executable` calls pointwise strict tower logic;
- a tier with nonempty quotient outgoing cells but no executable current-state
  action is treated as non-executable;
- the runtime lifts to a finer executable tier when the coarse tier is not
  pointwise executable.

### Regression Tests

Run:

```bash
uv run pytest tests/tower/partition
uv run pytest tests/training
uv run pytest tests/tower/control
uv run pytest tests/examples/test_plate_support_env_exploit_explore_runtime.py
uv run pytest
uv run ruff check .
uv run mypy src
```

## Documentation Updates

Update:

```text
docs/usage/01_002_tower_runtime_mental_model.md
docs/usage/01_010_tensorization_boundary.md
docs/api_notes/tensorization_boundary.md
CONTRIBUTING.md
README.md
```

as needed.

Minimum documentation requirements:

1. Distinguish:

   ```text
   quotient-level outgoing action availability
   representative/readout lift candidates
   pointwise executable lift candidates
   adjacent-tier support pointers
   ```

2. Explain that `outgoing_action_cells(...)` is not an executability predicate.

3. Explain that `lift_candidates(...)` is representative/readout compatible
   and may return non-current-source edges.

4. Direct runtime/action-mask code to use:

   ```python
   executable_action_cells(...)
   executable_lift_candidates(...)
   tier_is_executable_from_state(...)
   ```

5. Add this design folder to documentation routing if appropriate.

## Backward Compatibility

The first implementation should be backward-compatible at the public API level:

- keep `outgoing_action_cells(...)`;
- keep `representative_edges(...)`;
- keep `lift_candidates(...)` behavior;
- add strict APIs with explicit names;
- update executable/training surfaces to use strict APIs.

Behavior may change for `PathFiber` and `FiberConditionedStage` because those
are executable training surfaces and currently expose unsafe candidates. That
behavioral change is intended and should be documented as a bug fix.

## Performance Expectations

Current worst-case behavior without source-support pointers:

```text
check action support from current state: scan edge members of action cell
check tier executability: scan outgoing action cells and their edge members
find lower support: scan refinement/action-cell data
```

Expected behavior with this blueprint:

```text
strict executable candidates from current base state: O(k)
action-cell executable membership check: O(1)-ish lookup plus output size
tier executable from current state: O(number of outgoing action cells) with
    cheap candidate checks, or O(1)-ish if collection-level base active cache
    is used
adjacent support enumeration: O(number of supported child bins)
recursive support walk: O(depth) without flattening
```

Here `k` is the number of concrete executable edges in the selected action
cell sourced at the current base state. That output cost is unavoidable.

The implementation should not perform a full graph scan for pointwise
executability.

## Risks

### Risk: Confusing Support Layers

The main conceptual risk is mixing:

```text
base-source support cache
```

with:

```text
adjacent-tier recursive support pointers
```

The cache is useful, but the recursive pointer structure is the authoritative
Young-diagram object.

### Risk: Breaking Existing Tests That Assume `lift_candidates`

Existing tests intentionally check fallback representative behavior. Do not
silently break them. Add strict APIs and update tests to distinguish old and
new semantics.

### Risk: Overbuilding Reanchoring

Representative reanchoring is mathematically natural but not free. The first
fix should not invent internal motion policies, stutter execution semantics,
or within-fiber navigation. It should make pointwise execution safe.

### Risk: Performance Regression From Scans

If the implementation adds strict methods but implements them by repeatedly
scanning action-cell members, BBB may still suffer. The support/cache indexes
are part of the fix, not a luxury.

### Risk: Incremental Update Staleness

Because the tower updates incrementally, all support maps must be cleared and
rebuilt with dirty collections. Stale `action_cell_by_edge_id` or
source-support maps would produce hard-to-debug lift failures.

## Implementation Sketch

### Phase 1 Shape

At the action-layer level, add fields:

```python
source_child_cells_by_action_cell: dict[ActionCellId, tuple[StateCellId, ...]]
edge_ids_by_action_cell_by_source_child: dict[
    ActionCellId,
    dict[StateCellId, tuple[EdgeId, ...]],
]
lower_action_cells_by_action_cell_by_source_child: dict[
    ActionCellId,
    dict[StateCellId, tuple[ActionCellId, ...]],
]
active_child_cells_by_collection: dict[ActionCollectionId, tuple[StateCellId, ...]]
edge_ids_by_action_cell_by_base_source: dict[
    ActionCellId,
    dict[StateId, tuple[EdgeId, ...]],
]
base_source_ids_by_action_cell: dict[ActionCellId, tuple[StateId, ...]]
base_active_source_ids_by_collection: dict[ActionCollectionId, tuple[StateId, ...]]
action_cell_by_edge_id: dict[EdgeId, ActionCellId]
```

`StateId` should be imported from `ids.py`.

### Phase 1 Rebuild

Extend:

```python
rebuild_action_cells_for_collection(...)
```

with optional lower-layer context:

```python
lower_state_layer: StatePartitionLayer | None = None
lower_action_layer: ActionPartitionLayer | None = None
```

During rebuild:

- clear old support entries for obsolete action cells;
- group edges as before;
- create action cells as before;
- assign `action_cell_by_edge_id`;
- build source-child maps;
- build base-source maps;
- build active collection maps;
- build lower-action maps where lower layer exists.

### Phase 1 Tower Queries

Add strict and support query wrappers to `PartitionTower`.

These wrappers should validate tier bounds and return empty tuples on invalid
tiers, matching existing style.

### Phase 1 Training Updates

Update `PathFiber` first, then `FiberConditionedStage` tests should become
straightforward.

### Phase 1 Example Updates

Update `plate_support_env` predicate.

### Phase 1 Documentation

Update docs only after tests confirm the behavior.

## Acceptance Criteria

The implementation is complete when:

1. `PartitionTower` exposes strict pointwise executable APIs.

2. `PartitionTower` exposes adjacent-tier support APIs.

3. Existing `lift_candidates(...)` representative fallback remains available.

4. The asymmetric simplex repro is covered by tests.

5. Recursive child-bin support is covered by tests.

6. `PathFiber` masks/admissibility/lift candidates are pointwise strict.

7. `FiberConditionedStage` never steps a representative edge sourced at another
   base state.

8. `plate_support_env` uses pointwise tier executability.

9. Docs distinguish quotient availability, representative candidates, and
   executable candidates.

10. Full tests, Ruff, and mypy pass.

## Expected Downstream Effect

After this work, BBB should be able to replace weak predicates:

```python
bool(tower.outgoing_action_cells(tier, state_cell))
```

with:

```python
tower.tier_is_executable_from_state(tier, current_base_state)
```

and replace quotient vocabularies for executable control:

```python
tower.outgoing_action_cells(tier, state_cell)
```

with:

```python
tower.executable_action_cells(tier, state_cell, current_base_state)
```

Expected downstream failure reduction:

```text
no_lift_candidate_from_current_state
```

should stop appearing as a normal learner/runtime outcome for pointwise
execution. If it appears, it should indicate a stale tower context,
mis-synchronized current state, or a downstream bug.

