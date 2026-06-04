# Pointwise Liftability And Source-Support Implementation Gameplan

Date: 2026-06-04

Status: implementation gameplan, not yet executed

Authority:

```text
docs/design/pointwise_liftability_source_support/01_001_pointwise_liftability_source_support_blueprint.md
docs/prime_directive/prime_directive.md
docs/prime_directive/git_practices.md
docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md
docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md
```

## Purpose

This gameplan turns the pointwise liftability/source-support blueprint into an
ordered implementation procedure.

The implementation goal is to separate:

```text
quotient-level outgoing action availability
```

from:

```text
current-state executable liftability
```

without flattening away the recursive Young-diagram structure.

The implementation must add:

- adjacent-tier source-support pointers as the authoritative bin structure;
- minimal flattened base-source caches for hot pointwise execution queries;
- strict pointwise executable APIs on `PartitionTower`;
- training-surface updates so `PathFiber` and `FiberConditionedStage` do not
  step non-current-source representative edges;
- example runtime predicate updates;
- tests protecting the asymmetric simplex failure and recursive child-bin
  support semantics;
- documentation clarifying quotient availability versus executable liftability.

## Prime Directive Execution Rule

This gameplan is not implementation approval by itself.

Execution requires explicit PO approval after this document exists.

Once approved:

```text
this gameplan is law
```

Implementation must proceed in Phase.Stage.Action order unless the PO
explicitly authorizes a change.

If any action proves ambiguous, conflicts with repo reality, or would require a
simplified substitute, stop and ask the PO. Do not silently reduce scope.

## Branch Rule

Per:

```text
docs/prime_directive/git_practices.md
```

implementation must start on a dedicated branch.

Suggested branch:

```bash
git switch -c codex/pointwise-liftability-source-support
```

Do not implement this gameplan directly on `main`.

## Running Log Rule

Create and maintain:

```text
docs/design/pointwise_liftability_source_support/01_003_pointwise_liftability_source_support_implementation_log.md
```

The log must record:

- branch name;
- Phase.Stage.Action completion;
- tests run and results;
- surprises;
- PO clarifications;
- any full-stop decisions.

Do not hide simplifications inside the log. If a simplification is required,
stop and get PO approval first.

## Non-Goals

Do not implement:

- representative reanchoring;
- within-fiber internal motion policies;
- new stutter execution semantics;
- BBB-specific counterpoint logic inside `state_collapser`;
- a new learner architecture;
- tensorization changes except docs/testing if a direct interface implication
  appears;
- changes to the public behavior of `PartitionTower.lift_candidates(...)`.

## Phase 0: Branch, Baseline, And Log

### Phase 0.Stage 1: Enter Implementation Branch

#### Phase 0.Stage 1.Action 1

Read:

```text
docs/prime_directive/git_practices.md
docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md
```

Confirm the branch rule and exact-gameplan rule before touching source code.

#### Phase 0.Stage 1.Action 2

Check current repository state:

```bash
git status --short --branch
git log --oneline --decorate --max-count=8
```

If there are unrelated user changes, do not overwrite them.

#### Phase 0.Stage 1.Action 3

Create the implementation branch:

```bash
git switch -c codex/pointwise-liftability-source-support
```

If the branch already exists, inspect state before switching or reusing it.

### Phase 0.Stage 2: Create Implementation Log

#### Phase 0.Stage 2.Action 1

Create:

```text
docs/design/pointwise_liftability_source_support/01_003_pointwise_liftability_source_support_implementation_log.md
```

Include:

- date;
- branch name;
- blueprint path;
- gameplan path;
- implementation status table;
- validation section;
- surprise/blocker section.

#### Phase 0.Stage 2.Action 2

Record Phase 0 start in the implementation log before editing package source.

### Phase 0.Stage 3: Baseline Validation

#### Phase 0.Stage 3.Action 1

Run focused baseline tests that touch the relevant surfaces:

```bash
uv run pytest tests/tower/partition tests/training tests/tower/control tests/examples/test_plate_support_env_exploit_explore_runtime.py
```

#### Phase 0.Stage 3.Action 2

Record baseline results in the implementation log.

If baseline fails for reasons unrelated to this gameplan, stop and ask the PO.

## Phase 1: Test Fixtures For The Isolated Failure

### Phase 1.Stage 1: Add Asymmetric Simplex Test Fixture

#### Phase 1.Stage 1.Action 1

Add a focused test helper, likely in a new file:

```text
tests/tower/partition/test_pointwise_liftability.py
```

Construct the graph:

```text
0 --contract--> 1
0 --to2-------> 2
1 --to2-------> 2
1 --one_only--> 2
```

Use the existing partition tower schema tools:

```python
DimensionwiseSchema(("contract",))
PartitionTower(...)
```

#### Phase 1.Stage 1.Action 2

Add an initial test documenting current quotient availability:

```text
tier 1 state cell for 0 and 1 is the same
outgoing_action_cells(1, [0,1]) includes one_only
```

At this point, strict executable APIs do not exist yet. The test should either
be marked as expected to evolve after Phase 3 or limited to current APIs.

#### Phase 1.Stage 1.Action 3

Add or preserve a test showing existing representative fallback behavior:

```text
lift_candidates(1, one_only_cell, 0) returns representative edge 1 --one_only--> 2
```

This protects backward compatibility and makes the semantic split explicit.

### Phase 1.Stage 2: Add Recursive Child-Bin Fixture

#### Phase 1.Stage 2.Action 1

Add a nested contraction fixture modeled on the PO's 3-simplex explanation:

```text
tier 0: [0], [1], [2], [3]
tier 1: [0,1], [2], [3]
tier 2: [0,1,2], [3]
```

The exact edge labels/schema may be chosen to make the current
`DimensionwiseSchema` produce two tiers:

```text
contract01
contract12
```

or equivalent stable canonical identities.

#### Phase 1.Stage 2.Action 2

Add placeholder assertions only where current APIs exist. The full recursive
support assertions belong after Phase 3 adds the APIs.

#### Phase 1.Stage 2.Action 3

Record Phase 1 test fixture status in the implementation log.

## Phase 2: Action Layer Source-Support Storage

### Phase 2.Stage 1: Extend Action Layer Fields

#### Phase 2.Stage 1.Action 1

Open:

```text
src/state_collapser/tower/partition/action_layer.py
src/state_collapser/tower/partition/ids.py
```

Verify whether `StateId` is already exported and importable.

#### Phase 2.Stage 1.Action 2

Add authoritative adjacent support fields to `ActionPartitionLayer`:

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
```

If tuple-valued fields are awkward during rebuild, use local mutable builders
and freeze into tuples before assigning to the dataclass fields.

#### Phase 2.Stage 1.Action 3

Add derived flattened hot-path fields:

```python
edge_ids_by_action_cell_by_base_source: dict[
    ActionCellId,
    dict[StateId, tuple[EdgeId, ...]],
]
base_source_ids_by_action_cell: dict[ActionCellId, tuple[StateId, ...]]
base_active_source_ids_by_collection: dict[ActionCollectionId, tuple[StateId, ...]]
action_cell_by_edge_id: dict[EdgeId, ActionCellId]
```

#### Phase 2.Stage 1.Action 4

Ensure all new fields use deterministic tuple order when stored.

Ordering should be stable across runs, matching existing tests' deterministic
style.

### Phase 2.Stage 2: Clear Obsolete Support State During Rebuild

#### Phase 2.Stage 2.Action 1

In `rebuild_action_cells_for_collection(...)`, extend obsolete action-cell
cleanup to remove entries from all new action-cell-level maps:

```python
source_child_cells_by_action_cell
edge_ids_by_action_cell_by_source_child
lower_action_cells_by_action_cell_by_source_child
edge_ids_by_action_cell_by_base_source
base_source_ids_by_action_cell
```

#### Phase 2.Stage 2.Action 2

Remove old `action_cell_by_edge_id` entries for every edge id formerly in the
obsolete action cell.

Do not clear unrelated edge entries in other action cells.

#### Phase 2.Stage 2.Action 3

Clear/rebuild collection-level entries:

```python
active_child_cells_by_collection[collection_id]
base_active_source_ids_by_collection[collection_id]
```

for the collection being rebuilt.

### Phase 2.Stage 3: Extend Rebuild Signature

#### Phase 2.Stage 3.Action 1

Change `ActionPartitionLayer.rebuild_action_cells_for_collection(...)` to
accept optional lower-layer context:

```python
lower_state_layer: StatePartitionLayer | None = None
lower_action_layer: ActionPartitionLayer | None = None
```

#### Phase 2.Stage 3.Action 2

Update every call site in:

```text
src/state_collapser/tower/partition/action_layer.py
src/state_collapser/tower/partition/tower.py
```

so each tier rebuild passes lower context where available.

Expected rule:

```text
tier 0: no lower state/action layer
tier i > 0: lower_state_layer = state_layers[i - 1]
              lower_action_layer = action_layers[i - 1]
```

If a call site cannot access lower layers directly, stop and decide whether a
small tower-level rebuild wrapper is needed.

### Phase 2.Stage 4: Build Adjacent And Base Support During Rebuild

#### Phase 2.Stage 4.Action 1

During grouping, build local structures:

```python
source_child_edge_ids_by_group
base_source_edge_ids_by_group
lower_action_cells_by_group_by_source_child
active_child_cells
base_active_source_ids
```

#### Phase 2.Stage 4.Action 2

For each edge id, compute:

```python
source_state_id = registry.source_state_id(edge_id)
base_source = source_state_id
```

#### Phase 2.Stage 4.Action 3

For tier `0`, compute the source child as the tier-0 source singleton cell:

```python
source_child = state_layer.cell_of(source_state_id)
```

#### Phase 2.Stage 4.Action 4

For tier `i > 0`, compute the source child from the lower state layer:

```python
source_child = lower_state_layer.cell_of(source_state_id)
```

This is the authoritative adjacent-bin pointer.

#### Phase 2.Stage 4.Action 5

If `lower_action_layer` exists, compute lower action support:

```python
lower_action_cell = lower_action_layer.action_cell_by_edge_id.get(edge_id)
```

Record it only if present.

If lower action cells are not yet guaranteed to be built before upper rebuild,
stop and inspect tower rebuild order. Do not fake this with scans unless the PO
approves.

#### Phase 2.Stage 4.Action 6

When creating each new action cell id, assign:

```python
edge_ids_by_action_cell[action_cell_id]
action_cell_by_edge_id[edge_id]
source_child_cells_by_action_cell[action_cell_id]
edge_ids_by_action_cell_by_source_child[action_cell_id]
lower_action_cells_by_action_cell_by_source_child[action_cell_id]
edge_ids_by_action_cell_by_base_source[action_cell_id]
base_source_ids_by_action_cell[action_cell_id]
```

#### Phase 2.Stage 4.Action 7

After all action cells are created for the collection, assign:

```python
active_child_cells_by_collection[collection_id]
base_active_source_ids_by_collection[collection_id]
```

### Phase 2.Stage 5: Add Action Layer Query Helpers

#### Phase 2.Stage 5.Action 1

Add helper methods to `ActionPartitionLayer`:

```python
source_child_cells(action_cell_id) -> tuple[StateCellId, ...]
edge_ids_for_source_child(action_cell_id, child_state_cell_id) -> tuple[EdgeId, ...]
lower_action_cells_for_source_child(action_cell_id, child_state_cell_id) -> tuple[ActionCellId, ...]
active_child_cells(collection_id) -> tuple[StateCellId, ...]
edge_ids_for_base_source(action_cell_id, source_state_id) -> tuple[EdgeId, ...]
base_source_ids(action_cell_id) -> tuple[StateId, ...]
base_active_source_ids(collection_id) -> tuple[StateId, ...]
action_cell_for_edge_id(edge_id) -> ActionCellId | None
```

#### Phase 2.Stage 5.Action 2

Add unit tests for these helpers at the action-layer level if an existing
`tests/tower/partition/test_action_layer.py` pattern supports it.

If direct action-layer setup is too cumbersome, cover the behavior through
`PartitionTower` in Phase 3 instead.

#### Phase 2.Stage 5.Action 3

Run focused action-layer tests:

```bash
uv run pytest tests/tower/partition/test_action_layer.py tests/tower/partition/test_pointwise_liftability.py
```

Record results in the implementation log.

## Phase 3: PartitionTower Strict And Recursive Support APIs

### Phase 3.Stage 1: Add Strict Executable Lift API

#### Phase 3.Stage 1.Action 1

In:

```text
src/state_collapser/tower/partition/tower.py
```

add:

```python
def executable_lift_candidates(
    self,
    tier: int,
    action_cell_id: ActionCellId,
    current_base_state: State,
) -> tuple[BaseEdge, ...]:
    ...
```

Implementation should:

1. validate tier bounds;
2. resolve `current_base_state` to `StateId`;
3. use `edge_ids_for_base_source(action_cell_id, source_state_id)`;
4. return those edge ids as `BaseEdge` values.

No fallback representatives.

#### Phase 3.Stage 1.Action 2

Add tests:

```text
executable_lift_candidates(1, one_only_cell, zero) == ()
executable_lift_candidates(1, one_only_cell, one) == (one_only,)
```

#### Phase 3.Stage 1.Action 3

Keep and update compatibility tests proving:

```text
lift_candidates(...) still falls back to representatives
```

### Phase 3.Stage 2: Add Strict Executable Action-Cell API

#### Phase 3.Stage 2.Action 1

Add:

```python
def executable_action_cells(
    self,
    tier: int,
    state_cell_id: StateCellId,
    current_base_state: State,
) -> tuple[ActionCellId, ...]:
    ...
```

Implementation should filter:

```python
outgoing_action_cells(tier, state_cell_id)
```

through strict current-state executable candidates.

#### Phase 3.Stage 2.Action 2

Add tests:

```text
executable_action_cells(1, [0,1], 0) excludes one_only
executable_action_cells(1, [0,1], 1) includes one_only
```

#### Phase 3.Stage 2.Action 3

Preserve deterministic ordering from `outgoing_action_cells(...)`.

### Phase 3.Stage 3: Add Tier Executable From State API

#### Phase 3.Stage 3.Action 1

Add:

```python
def tier_is_executable_from_state(
    self,
    tier: int,
    current_base_state: State,
) -> bool:
    ...
```

Implementation:

```python
state_cell = self.current_state_cell(tier, current_base_state)
if state_cell is None:
    return False
return bool(self.executable_action_cells(tier, state_cell, current_base_state))
```

#### Phase 3.Stage 3.Action 2

Add tests:

```text
tier_is_executable_from_state(1, zero) is true because to2 exists
tier with only one_only from one is false for zero if no zero-supported actions exist
invalid tier returns false
unknown state returns false
```

### Phase 3.Stage 4: Add Adjacent Support APIs

#### Phase 3.Stage 4.Action 1

Add:

```python
def supported_child_state_cells(
    self,
    tier: int,
    action_cell_id: ActionCellId,
) -> tuple[StateCellId, ...]:
    ...
```

For invalid tier or tier `0`, return `()`.

#### Phase 3.Stage 4.Action 2

Add:

```python
def active_child_state_cells(
    self,
    tier: int,
    state_cell_id: StateCellId,
) -> tuple[StateCellId, ...]:
    ...
```

For invalid tier or tier `0`, return `()`.

#### Phase 3.Stage 4.Action 3

Add:

```python
def lower_action_cells_for_supported_child(
    self,
    tier: int,
    action_cell_id: ActionCellId,
    child_state_cell_id: StateCellId,
) -> tuple[ActionCellId, ...]:
    ...
```

For invalid tier or tier `0`, return `()`.

#### Phase 3.Stage 4.Action 4

Add recursive child-bin support tests:

```text
supported_child_state_cells(2, D_2) returns tier-1 child cells
lower_action_cells_for_supported_child(2, D_2, [0,1]) returns tier-1 action cells
lower_action_cells_for_supported_child(2, D_2, [2]) returns tier-1 action cells
```

### Phase 3.Stage 5: Make `action_cell_for_edge` Use Index

#### Phase 3.Stage 5.Action 1

Update:

```python
PartitionTower.action_cell_for_edge(...)
```

to use:

```python
action_layer.action_cell_for_edge_id(edge_id)
```

instead of scanning `edge_ids_by_action_cell`.

#### Phase 3.Stage 5.Action 2

Run:

```bash
uv run pytest tests/tower/partition/test_queries_and_lift.py tests/tower/partition/test_pointwise_liftability.py
```

Record results.

## Phase 4: PathFiber Pointwise Strict Semantics

### Phase 4.Stage 1: Add Executable Action Vocabulary

#### Phase 4.Stage 1.Action 1

In:

```text
src/state_collapser/training/fibers.py
```

add:

```python
def executable_action_vocabulary(self, total_state: State) -> tuple[ActionCellId, ...]:
    ...
```

Implementation:

```python
fine_state_cell = self.current_fine_state_cell(total_state)
if fine_state_cell is None:
    return ()
return self.tower.executable_action_cells(
    self.fine_tier,
    fine_state_cell,
    total_state,
)
```

#### Phase 4.Stage 1.Action 2

Keep existing `action_vocabulary(...)` as quotient-level vocabulary.

Update docstrings to distinguish quotient vocabulary from executable
vocabulary.

### Phase 4.Stage 2: Make Admissibility Pointwise Strict

#### Phase 4.Stage 2.Action 1

Update:

```python
PathFiber.admissible_action_cells(...)
```

to iterate over:

```python
self.executable_action_vocabulary(total_state)
```

#### Phase 4.Stage 2.Action 2

Evaluate frozen-step matching only over:

```python
self.tower.executable_lift_candidates(...)
```

not all action-cell members.

#### Phase 4.Stage 2.Action 3

Add diagnostics-friendly local variables so test failures reveal:

```text
quotient vocabulary
executable vocabulary
executable candidate edges
projected coarse step
```

without changing public payloads yet.

### Phase 4.Stage 3: Make PathFiber Lift Candidates Strict

#### Phase 4.Stage 3.Action 1

Update:

```python
PathFiber.lift_candidates(...)
```

to return:

```python
self.tower.executable_lift_candidates(self.fine_tier, action_cell, total_state)
```

after admissibility check.

#### Phase 4.Stage 3.Action 2

Update the docstring from representative language to strict executable
language.

### Phase 4.Stage 4: Update PathFiber Diagnostics

#### Phase 4.Stage 4.Action 1

Update:

```python
PathFiber.diagnose_departure(...)
```

so `NO_LIFT_CANDIDATE` refers to no current-state executable lift.

#### Phase 4.Stage 4.Action 2

Include feasible diagnostic counts:

```text
quotient_member_count
representative_candidate_count
executable_candidate_count
```

If adding these counts requires broad diagnostic schema changes, stop and ask
the PO whether to add them now or defer.

### Phase 4.Stage 5: Add PathFiber Tests

#### Phase 4.Stage 5.Action 1

Add or update tests under:

```text
tests/training/
```

to prove:

```text
action_vocabulary may include quotient-available non-executable cells
executable_action_vocabulary excludes non-current-source cells
action_mask marks non-current-source cells false
admissible_action_cells excludes cells whose matching frozen-step edges are sourced elsewhere
PathFiber.lift_candidates returns strict executable edges only
```

#### Phase 4.Stage 5.Action 2

Run:

```bash
uv run pytest tests/training/test_path_fiber.py tests/training
```

Record results.

## Phase 5: FiberConditionedStage Safety

### Phase 5.Stage 1: Verify Stage Uses Strict Fiber Candidates

#### Phase 5.Stage 1.Action 1

Read:

```text
src/state_collapser/training/stages.py
```

Confirm that, after Phase 4, `FiberConditionedStage.step(...)` receives strict
candidates from `PathFiber.lift_candidates(...)`.

#### Phase 5.Stage 1.Action 2

If the stage still has a path that can step a representative edge sourced at
another state, update it to use:

```python
tower.executable_lift_candidates(...)
```

or the strict `PathFiber` method only.

### Phase 5.Stage 2: Add Stage Non-Execution Test

#### Phase 5.Stage 2.Action 1

Add a test proving the stage does not call:

```python
runtime.step(...)
```

when a selected action cell has only non-current-source representatives.

#### Phase 5.Stage 2.Action 2

Assert that the resulting transition carries:

```text
FiberDepartureReason.NO_LIFT_CANDIDATE
```

or that the action is prevented by mask before execution, depending on the
existing test harness.

#### Phase 5.Stage 2.Action 3

Run:

```bash
uv run pytest tests/training/test_fiber_conditioned_stage.py tests/training
```

Record results.

## Phase 6: Runtime Predicate And Example Integration

### Phase 6.Stage 1: Update Plate-Support Executability Predicate

#### Phase 6.Stage 1.Action 1

Open:

```text
src/state_collapser/examples/plate_support_env/runtime.py
```

Find:

```python
_tier_is_executable(...)
```

#### Phase 6.Stage 1.Action 2

Replace quotient nonemptiness:

```python
bool(tower.outgoing_action_cells(tier, state_cell))
```

with strict pointwise semantics:

```python
current_state = snapshot.current_base_state
if not isinstance(current_state, State):
    return False
return tower.tier_is_executable_from_state(tier, current_state)
```

Preserve existing safe behavior for missing snapshot/tower view as appropriate.

#### Phase 6.Stage 1.Action 3

Ensure imports include `State` only if needed.

### Phase 6.Stage 2: Update Runtime Predicate Tests

#### Phase 6.Stage 2.Action 1

Update:

```text
tests/examples/test_plate_support_env_exploit_explore_runtime.py
```

so tests assert pointwise executability, not merely abstract outgoing
nonemptiness.

#### Phase 6.Stage 2.Action 2

Add a case where a coarse tier has nonempty quotient outgoing actions but no
current-state executable action, and confirm the runtime treats it as
non-executable.

#### Phase 6.Stage 2.Action 3

Run:

```bash
uv run pytest tests/examples/test_plate_support_env_exploit_explore_runtime.py tests/tower/control
```

Record results.

## Phase 7: Documentation Updates

### Phase 7.Stage 1: Update Tower Runtime Mental Model

#### Phase 7.Stage 1.Action 1

Update:

```text
docs/usage/01_002_tower_runtime_mental_model.md
```

to distinguish:

```text
outgoing_action_cells: quotient/readout availability
lift_candidates: representative/readout candidates with fallback
executable_lift_candidates: strict current-state executable edges
executable_action_cells: strict current-state action cells
tier_is_executable_from_state: runtime predicate for pointwise execution
```

#### Phase 7.Stage 1.Action 2

Add a short note that v0.7.1 empty-`Out` lifting is necessary but not
sufficient for pointwise liftability; nonempty quotient `Out` can still be
non-executable from the current representative.

### Phase 7.Stage 2: Update README/CONTRIBUTING Routing

#### Phase 7.Stage 2.Action 1

Inspect:

```text
README.md
CONTRIBUTING.md
```

for places that discuss tower runtime, liftability, HGraphML, BBB, or
evaluation semantics.

#### Phase 7.Stage 2.Action 2

Add minimal routing to:

```text
docs/design/pointwise_liftability_source_support/
```

without bloating the front door.

#### Phase 7.Stage 2.Action 3

In `CONTRIBUTING.md`, add focused test guidance for pointwise liftability if
there is an existing testing-guidance section.

### Phase 7.Stage 3: Update API Notes If Needed

#### Phase 7.Stage 3.Action 1

Inspect:

```text
docs/api_notes/
docs/package_usage.md
docs/public_api.md
```

if present/relevant.

#### Phase 7.Stage 3.Action 2

Add or update only routing/policy notes needed to prevent misuse of
`outgoing_action_cells(...)` as an executable predicate.

### Phase 7.Stage 4: Add Downstream Handoff Note

#### Phase 7.Stage 4.Action 1

Create:

```text
docs/design/pointwise_liftability_source_support/01_004_big_boy_benchmarking_pointwise_liftability_handoff.md
```

or reserve this for after implementation if the PO prefers. If creating now,
make clear it is upstream-to-downstream guidance after implementation.

#### Phase 7.Stage 4.Action 2

Include BBB replacement guidance:

```python
tower.tier_is_executable_from_state(tier, current_base_state)
tower.executable_action_cells(tier, state_cell, current_base_state)
tower.executable_lift_candidates(tier, action_cell, current_base_state)
```

#### Phase 7.Stage 4.Action 3

Explicitly say BBB should treat `no_lift_candidate_from_current_state` as a
structural regression after adopting these APIs.

## Phase 8: Validation And Cleanup

### Phase 8.Stage 1: Focused Validation

#### Phase 8.Stage 1.Action 1

Run:

```bash
uv run pytest tests/tower/partition/test_pointwise_liftability.py
```

#### Phase 8.Stage 1.Action 2

Run:

```bash
uv run pytest tests/tower/partition tests/training tests/tower/control tests/examples/test_plate_support_env_exploit_explore_runtime.py
```

#### Phase 8.Stage 1.Action 3

Record all results in the implementation log.

### Phase 8.Stage 2: Full Validation

#### Phase 8.Stage 2.Action 1

Run:

```bash
uv run pytest
```

#### Phase 8.Stage 2.Action 2

Run:

```bash
uv run ruff check .
```

#### Phase 8.Stage 2.Action 3

Run:

```bash
uv run mypy src
```

#### Phase 8.Stage 2.Action 4

Record results in the implementation log.

If any command fails, do not declare completion. Fix or stop for PO guidance
depending on failure type.

### Phase 8.Stage 3: Repo Status And Diff Review

#### Phase 8.Stage 3.Action 1

Run:

```bash
git status --short --branch
```

#### Phase 8.Stage 3.Action 2

Review the diff:

```bash
git diff -- src tests docs README.md CONTRIBUTING.md
```

Use narrower paths if the diff is large.

#### Phase 8.Stage 3.Action 3

Check that no unrelated files were modified.

#### Phase 8.Stage 3.Action 4

Update the implementation log with final status and validation summary.

## Phase 9: Completion Report

### Phase 9.Stage 1: Prepare Final Implementation Summary

#### Phase 9.Stage 1.Action 1

Summarize:

- APIs added;
- data structures added;
- training semantics changed;
- example/runtime predicate changed;
- tests added/updated;
- docs updated;
- validation results.

#### Phase 9.Stage 1.Action 2

Explicitly mention that `PartitionTower.lift_candidates(...)` remains
representative/readout compatible and that strict execution uses new APIs.

#### Phase 9.Stage 1.Action 3

Explicitly mention PO attribution:

```text
The recursive adjacent-tier source-support design is PO-directed and comes
from the Young-diagram/nested-coset interpretation.
```

### Phase 9.Stage 2: Await PO Merge/Commit Direction

#### Phase 9.Stage 2.Action 1

Do not merge to `main` unless the PO asks.

#### Phase 9.Stage 2.Action 2

If the PO asks for commit guidance, stage only relevant files.

#### Phase 9.Stage 2.Action 3

If the PO asks for merge commands, provide the standard branch-to-main merge
commands only after verifying branch status.

## Expected File Touch List

Likely implementation files:

```text
src/state_collapser/tower/partition/action_layer.py
src/state_collapser/tower/partition/tower.py
src/state_collapser/training/fibers.py
src/state_collapser/training/stages.py
src/state_collapser/examples/plate_support_env/runtime.py
```

Likely tests:

```text
tests/tower/partition/test_pointwise_liftability.py
tests/tower/partition/test_action_layer.py
tests/tower/partition/test_queries_and_lift.py
tests/training/test_path_fiber.py
tests/training/test_fiber_conditioned_stage.py
tests/examples/test_plate_support_env_exploit_explore_runtime.py
```

Likely docs:

```text
docs/design/pointwise_liftability_source_support/01_003_pointwise_liftability_source_support_implementation_log.md
docs/design/pointwise_liftability_source_support/01_004_big_boy_benchmarking_pointwise_liftability_handoff.md
docs/usage/01_002_tower_runtime_mental_model.md
README.md
CONTRIBUTING.md
```

Touch only additional files if implementation reality requires it, and record
why in the implementation log.

## Stop Conditions

Stop and ask the PO if:

- lower action-cell support cannot be built without scanning or major reorder;
- the action-layer rebuild signature change cascades more broadly than
  expected;
- preserving `lift_candidates(...)` compatibility conflicts with strict
  training behavior;
- tests imply representative reanchoring is needed for current package
  behavior;
- docs require changing mathematical claims rather than API wording;
- any action would need a simplified substitute.

## Acceptance Checklist

The work is complete only when all are true:

- `executable_lift_candidates(...)` exists and is strict.
- `executable_action_cells(...)` exists and is strict.
- `tier_is_executable_from_state(...)` exists and is strict.
- adjacent support APIs exist.
- action-layer support maps are maintained during rebuild.
- `action_cell_for_edge(...)` no longer scans action cells.
- `PathFiber` executable behavior is strict.
- `FiberConditionedStage` does not step non-current-source representatives.
- `plate_support_env` uses strict tier executability.
- asymmetric simplex tests pass.
- recursive child-bin tests pass.
- existing representative fallback tests still pass.
- focused tests pass.
- full `pytest` passes.
- `ruff check .` passes.
- `mypy src` passes.
- implementation log is complete.

