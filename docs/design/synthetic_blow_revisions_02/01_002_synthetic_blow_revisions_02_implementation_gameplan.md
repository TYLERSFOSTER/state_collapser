# Synthetic Blow Revisions 02 Implementation Gameplan

Date: 2026-06-04

Status: implementation gameplan, not yet executed

Source blueprint:

```text
docs/design/synthetic_blow_revisions_02/01_001_synthetic_blow_revisions_02_blueprint.md
```

Source review:

```text
docs/code_review/03_001_synthetic_blow_full_repo_review_current_state.md
```

Prime directive authority:

```text
docs/prime_directive/prime_directive.md
docs/prime_directive/git_practices.md
docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md
docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md
```

Downstream handoff:

```text
big_boy_benchmarking_synthetic_blow_revisions_02_handoff.md
```

## Purpose

This gameplan turns the second synthetic-Blow-review revision blueprint into an
ordered implementation procedure.

The implementation target is deliberately narrow:

1. make backend-independent linearization accept numeric NumPy observations;
2. add invariant checking for partition/action source-support tables;
3. make `FiberConditionedStage` concrete lift selection explicit;
4. remove or justify the unused mandatory `pillow` dependency;
5. clean stale front-door documentation points.

The implementation must not reopen the Project Owner's struck-through items.

## Prime Directive Execution Rule

This gameplan is not implementation approval by itself.

Execution requires explicit Project Owner approval after this document exists.

Once approved:

```text
this gameplan is law
```

Implementation must proceed in Phase.Stage.Action order unless the Project Owner
explicitly authorizes a change.

If repository reality conflicts with any action below, stop, identify the exact
failed action, and ask the Project Owner for guidance. Do not silently simplify,
skip, reorder, or reinterpret this plan.

## Branch Rule

Per:

```text
docs/prime_directive/git_practices.md
```

implementation must start on a dedicated branch.

Suggested branch:

```bash
git switch -c codex/synthetic-blow-revisions-02
```

Do not execute this gameplan directly on `main`.

## Running Log Rule

Create and maintain:

```text
docs/design/synthetic_blow_revisions_02/01_003_synthetic_blow_revisions_02_implementation_log.md
```

The log must record:

- branch name;
- Phase.Stage.Action completion;
- tests run and results;
- dependency/lockfile actions;
- surprises;
- Project Owner clarifications;
- downstream handoff implications;
- any full-stop decisions.

If an implementation shortcut becomes necessary, stop and ask before taking it.
Do not hide simplifications in the implementation log.

## Explicit Non-Goals

Do not implement:

- a Torch CI matrix or `ml` CI expansion;
- serious benchmark artifact writing;
- JSON/CSV benchmark result tables;
- replay buffers;
- vectorized rollout;
- checkpoint/resume;
- experiment manifests;
- a full tower-augmented Gymnasium wrapper;
- package-owned neural policy models;
- a broader tensorization rewrite;
- direct `big_boy_benchmarking` integration inside this repo.

These are valid future work items, but they were struck through or deferred for
this implementation pass.

## Fixed Design Decisions

1. NumPy support is added at the linearization boundary, not in the object-native
   runtime.
2. NumPy is imported lazily inside `linearization.py`, not at package import
   time.
3. Numeric `np.ndarray` observations become tuples of floats plus metadata.
4. Unsupported arrays fail in strict mode and sidecar in non-strict mode.
5. Partition invariants must check both adjacent-tier Young-diagram support and
   flattened base-source caches.
6. Invariant checking is explicit and test/debug oriented; it does not run on
   every runtime step by default.
7. `FiberConditionedStage` keeps deterministic first-candidate selection as its
   default.
8. Lift selection becomes an explicit hook, not a learner/model policy system.
9. `pillow` is removed from base dependencies if no current source/test usage is
   found.
10. Documentation cleanup must stay small and must not claim deferred benchmark
    artifact work exists.

## Phase 0: Branch, Baseline, And Log

Goal:

```text
Enter the implementation interval cleanly and establish baseline truth before
touching source code.
```

### Phase 0.Stage 1: Confirm Directive And Working Tree

#### Phase 0.Stage 1.Action 1

Read:

```text
docs/prime_directive/git_practices.md
docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md
docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md
```

Confirm that execution has explicit Project Owner approval. If approval has not
been given, stop.

#### Phase 0.Stage 1.Action 2

Check repository state:

```bash
git status --short --branch
git log --oneline --decorate --max-count=8
```

If unrelated modified or untracked user files are present, record them in the
implementation log and do not overwrite them.

#### Phase 0.Stage 1.Action 3

Create the implementation branch:

```bash
git switch -c codex/synthetic-blow-revisions-02
```

If the branch already exists, stop and inspect before reusing it.

### Phase 0.Stage 2: Create Implementation Log

#### Phase 0.Stage 2.Action 1

Create:

```text
docs/design/synthetic_blow_revisions_02/01_003_synthetic_blow_revisions_02_implementation_log.md
```

Include:

- date;
- branch name;
- blueprint path;
- gameplan path;
- status table for each phase;
- validation section;
- dependency/lockfile section;
- downstream handoff section;
- surprise/blocker section.

#### Phase 0.Stage 2.Action 2

Record Phase 0 start in the implementation log before editing package source.

### Phase 0.Stage 3: Baseline Validation

#### Phase 0.Stage 3.Action 1

Run static validation:

```bash
uv run ruff check .
uv run mypy src
```

Record results.

#### Phase 0.Stage 3.Action 2

Run focused baseline tests:

```bash
uv run pytest tests/training/test_linearized_records.py
uv run pytest tests/training/test_fiber_conditioned_stage.py
uv run pytest tests/tower/partition/test_pointwise_liftability.py
uv run pytest tests/tower/partition/test_hgraphml_downstream_compatibility.py
```

Record results.

#### Phase 0.Stage 3.Action 3

Run current package-wide pytest if baseline focused tests pass:

```bash
uv run pytest
```

Record skipped tests as well as passes.

#### Phase 0.Stage 3.Action 4

Run the benchmark smoke command only as a smoke check, not as benchmark evidence:

```bash
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only
```

Record result.

## Phase 1: NumPy Observation Linearization

Goal:

```text
Numeric NumPy observations from packaged examples can be linearized without
forcing NumPy into the object-native runtime or base package import path.
```

### Phase 1.Stage 1: Add Failing Tests First

#### Phase 1.Stage 1.Action 1

Open:

```text
tests/training/test_linearized_records.py
```

Identify the existing fixture helpers for building an `ActionSelectionInput`,
`PartitionTower`, `EncodingRegistry`, and `LinearizationConfig`.

#### Phase 1.Stage 1.Action 2

Add a test for a numeric NumPy observation.

Required assertion shape:

```text
observation_features == tuple(float values in row-major order)
metadata["observation"]["kind"] == "numpy.ndarray"
metadata["observation"]["shape"] == [...]
metadata["observation"]["dtype"] == "..."
```

#### Phase 1.Stage 1.Action 3

Add a strict-mode object-array rejection test.

Expected:

```text
ValueError
```

The error message should identify that unsupported NumPy observation dtype or
unsupported observation data was found.

#### Phase 1.Stage 1.Action 4

Add a non-strict object-array sidecar test.

Expected:

```text
linearized.observation_features == ()
metadata["observation"] contains unsupported observation metadata
```

#### Phase 1.Stage 1.Action 5

Add a real packaged-example observation test using:

```text
state_collapser.examples.plate_support_env.PlateSupportEnv
```

Build an observation from `env.reset(seed=...)`, pass it through
`linearize_action_selection_input(...)`, and assert it linearizes to the expected
feature width.

If importing the example reveals a missing optional dependency in the current
environment, stop and inspect. CI currently installs `rl`, so this test is
expected to be valid under normal CI.

#### Phase 1.Stage 1.Action 6

Run the new/modified tests and confirm they fail for the expected reason before
implementation:

```bash
uv run pytest tests/training/test_linearized_records.py
```

If they fail for unrelated reasons, stop and diagnose.

### Phase 1.Stage 2: Implement Lazy NumPy Observation Handling

#### Phase 1.Stage 2.Action 1

Open:

```text
src/state_collapser/training/linearization.py
```

Confirm `_linearize_observation(...)` still matches the blueprint description:
bool/int/float/list/tuple only.

#### Phase 1.Stage 2.Action 2

Add any needed typing imports locally and minimally.

If `Any` or `cast` is needed for strict mypy, import it from `typing`.

Do not expose NumPy types in function annotations.

#### Phase 1.Stage 2.Action 3

Add a private helper:

```python
def _try_linearize_numpy_observation(
    observation: object,
    *,
    strict: bool,
) -> tuple[tuple[float, ...], JsonDict] | None:
    ...
```

The helper must return `None` when NumPy is unavailable or when `observation` is
not an `np.ndarray`.

#### Phase 1.Stage 2.Action 4

Inside the helper, use lazy optional import:

```python
if importlib.util.find_spec("numpy") is None:
    return None
numpy_module = importlib.import_module("numpy")
```

Do not add `import numpy as np` at module top level.

#### Phase 1.Stage 2.Action 5

Support dtype kinds:

```text
b, i, u, f
```

Reject unsupported dtype kinds in strict mode.

In non-strict mode, return:

```python
(), {"unsupported_observation_repr": repr(observation), ...}
```

Include NumPy shape/dtype/kind metadata if available.

#### Phase 1.Stage 2.Action 6

Flatten supported arrays in row-major order and convert to Python floats.

The resulting record must remain:

```python
tuple[float, ...]
```

not a NumPy array and not a Torch tensor.

#### Phase 1.Stage 2.Action 7

Update `_linearize_observation(...)` so it checks the NumPy helper before the
generic unsupported-object fallback.

Keep existing bool/int/float/list/tuple semantics unchanged.

### Phase 1.Stage 3: Validate NumPy Linearization

#### Phase 1.Stage 3.Action 1

Run:

```bash
uv run pytest tests/training/test_linearized_records.py
```

#### Phase 1.Stage 3.Action 2

Run:

```bash
uv run mypy src
```

Strict typing issues are likely here. Fix them locally inside
`linearization.py`; do not loosen project-wide typing.

#### Phase 1.Stage 3.Action 3

Update the implementation log with:

- helper name;
- supported dtype kinds;
- tests added;
- mypy result;
- any strict/non-strict behavior details.

## Phase 2: Partition Source-Support Invariant Checking

Goal:

```text
Make stale or inconsistent partition/action source-support indexes mechanically
detectable in tests and debug use.
```

### Phase 2.Stage 1: Add Invariant Module And Report Types

#### Phase 2.Stage 1.Action 1

Create:

```text
src/state_collapser/tower/partition/invariants.py
```

#### Phase 2.Stage 1.Action 2

Add:

```python
@dataclass(frozen=True, slots=True)
class PartitionInvariantIssue:
    tier: int
    code: str
    message: str
    state_cell_id: StateCellId | None = None
    action_collection_id: ActionCollectionId | None = None
    action_cell_id: ActionCellId | None = None
    edge_id: EdgeId | None = None
```

Use only project id types already defined under
`src/state_collapser/tower/partition/ids.py`.

#### Phase 2.Stage 1.Action 3

Add:

```python
@dataclass(frozen=True, slots=True)
class PartitionInvariantReport:
    issues: tuple[PartitionInvariantIssue, ...]

    @property
    def ok(self) -> bool: ...
    def assert_ok(self) -> None: ...
```

`assert_ok()` should raise `AssertionError` with a concise summary containing at
least the first issue code and message.

#### Phase 2.Stage 1.Action 4

Add `__all__` exports for the report types and invariant functions.

### Phase 2.Stage 2: Implement Action-Layer Invariant Function

#### Phase 2.Stage 2.Action 1

In `invariants.py`, add:

```python
def action_layer_invariant_report(
    action_layer: ActionPartitionLayer,
    *,
    state_layer: StatePartitionLayer,
    registry: BaseGraphRegistry,
    lower_state_layer: StatePartitionLayer | None = None,
    lower_action_layer: ActionPartitionLayer | None = None,
    allow_dirty: bool = False,
) -> PartitionInvariantReport:
    ...
```

If imports create a circular dependency, use `TYPE_CHECKING` for annotations and
runtime-safe imports where necessary.

#### Phase 2.Stage 2.Action 2

Validate state-cell to outgoing-collection structure:

- each state cell has one outgoing collection;
- each referenced collection exists in `edge_ids_by_collection`;
- every live collection is attached to a state cell;
- dirty collections are reported when `allow_dirty=False`.

#### Phase 2.Stage 2.Action 3

Validate collection to action-cell structure:

- every action cell listed by a collection exists in `edge_ids_by_action_cell`;
- every action cell has source-cell, target-cell, and label-key entries;
- every action-cell edge maps back through `action_cell_by_edge_id`;
- every `action_cell_by_edge_id` reverse entry points to an action cell that
  contains the edge.

#### Phase 2.Stage 2.Action 4

Validate edge geometry:

- each action-cell edge source belongs to the recorded source cell under the
  current state layer;
- each action-cell edge target belongs to the recorded target cell under the
  current state layer;
- live action cells do not expose internal source-cell equals target-cell edges.

#### Phase 2.Stage 2.Action 5

Validate adjacent-tier Young-diagram source support:

- source child cells match `lower_state_layer.cell_of(source_state_id)` when
  lower state layer exists;
- tier 0 uses current state cells as source child cells;
- `edge_ids_by_action_cell_by_source_child` equals the edge partition by source
  child;
- when `lower_action_layer` exists,
  `lower_action_cells_by_action_cell_by_source_child` is consistent with the
  lower layer's `action_cell_for_edge_id(...)`.

#### Phase 2.Stage 2.Action 6

Validate flattened base-source materialization:

- `edge_ids_by_action_cell_by_base_source` equals the edge partition by base
  source state id;
- `base_source_ids_by_action_cell` equals sorted base-source keys;
- `base_active_source_ids_by_collection` equals the union of base sources across
  action cells in that collection.

#### Phase 2.Stage 2.Action 7

Validate collection-level active child sources:

- `active_child_cells_by_collection` equals the union of child source cells
  across action cells in that collection.

#### Phase 2.Stage 2.Action 8

Validate internal-edge separation:

- edge ids recorded as internal for a state cell are not present in live action
  cells;
- internal edge records point to the state cell and tier where they are stored.

Do not overfit to a single schema fixture. The check should validate structure
generically.

### Phase 2.Stage 3: Add Layer And Tower APIs

#### Phase 2.Stage 3.Action 1

In:

```text
src/state_collapser/tower/partition/action_layer.py
```

add:

```python
def invariant_report(...): ...
def assert_consistent(...): ...
```

Prefer local imports inside these methods to avoid import cycles.

#### Phase 2.Stage 3.Action 2

In:

```text
src/state_collapser/tower/partition/tower.py
```

add:

```python
def invariant_report(self, *, allow_dirty: bool = False) -> PartitionInvariantReport:
    ...

def assert_consistent(self, *, allow_dirty: bool = False) -> None:
    ...
```

The tower-level method must iterate over every tier, pass lower-tier layers when
available, merge reports, and return one combined report.

#### Phase 2.Stage 3.Action 3

Export invariant report types from:

```text
src/state_collapser/tower/partition/__init__.py
```

Do not promote these to top-level `state_collapser.__init__`.

### Phase 2.Stage 4: Add Invariant Tests

#### Phase 2.Stage 4.Action 1

Create:

```text
tests/tower/partition/test_partition_invariants.py
```

#### Phase 2.Stage 4.Action 2

Add a passing initialized-tower invariant test.

Use a small nontrivial tower with at least one contraction and at least one live
outgoing action cell.

#### Phase 2.Stage 4.Action 3

Add a passing incremental-update invariant test.

Either reuse existing full/incremental fixture patterns or build a small
incremental tower directly.

#### Phase 2.Stage 4.Action 4

Add corruption tests:

- corrupt `action_cell_by_edge_id`;
- corrupt `edge_ids_by_action_cell_by_base_source`;
- corrupt `edge_ids_by_action_cell_by_source_child`;
- add a fake dirty collection and verify `allow_dirty=False` catches it;
- verify `allow_dirty=True` suppresses the dirty-only issue if no other issue is
  present.

Do not use broad monkeypatching. Mutate the specific test tower's dictionaries
directly so the expected invariant failure is precise.

#### Phase 2.Stage 4.Action 5

If practical, add `tower.assert_consistent()` calls to one or more existing
partition tests:

```text
tests/tower/partition/test_full_incremental_equivalence.py
tests/tower/partition/test_pointwise_liftability.py
tests/tower/partition/test_hgraphml_downstream_compatibility.py
```

Keep these additions small. Do not rewrite the tests.

### Phase 2.Stage 5: Validate Partition Invariants

#### Phase 2.Stage 5.Action 1

Run:

```bash
uv run pytest tests/tower/partition/test_partition_invariants.py
```

#### Phase 2.Stage 5.Action 2

Run:

```bash
uv run pytest tests/tower/partition/test_full_incremental_equivalence.py
uv run pytest tests/tower/partition/test_pointwise_liftability.py
uv run pytest tests/tower/partition/test_queries_and_lift.py
uv run pytest tests/tower/partition/test_hgraphml_downstream_compatibility.py
```

#### Phase 2.Stage 5.Action 3

Run:

```bash
uv run mypy src
```

Fix strict typing issues locally.

#### Phase 2.Stage 5.Action 4

Update the implementation log with:

- invariant API names;
- issue codes used;
- test results;
- any intentional non-hot-path design notes.

## Phase 3: Explicit Lift Selection In `FiberConditionedStage`

Goal:

```text
Replace hidden first-candidate concrete lift selection with an explicit,
default-preserving selector hook.
```

### Phase 3.Stage 1: Add Tests First

#### Phase 3.Stage 1.Action 1

Open:

```text
tests/training/test_fiber_conditioned_stage.py
```

Inspect existing fixtures for `FiberConditionedStage`, `PathFiber`, and runtime
step recording.

#### Phase 3.Stage 1.Action 2

Add or adapt a fixture where one abstract action cell has at least two concrete
lift candidates from the current base state.

If existing fixtures cannot produce this cleanly, build a tiny direct tower
fixture.

The fixture should create two distinct `BaseEdge` instances that land in the
same action cell at the relevant tier. A likely pattern is:

- same source state;
- same action canonical identity;
- targets that collapse into the same target cell at the stage tier.

#### Phase 3.Stage 1.Action 3

Add a test proving the default selector chooses the first lift candidate.

Assert:

- runtime action corresponds to the first candidate;
- transition diagnostics contain candidate count;
- selected index is `0`.

#### Phase 3.Stage 1.Action 4

Add a test proving a custom selector can choose a non-first candidate.

Assert:

- runtime action corresponds to the selected non-first candidate;
- transition diagnostics record the correct selected index;
- selector name is recorded.

#### Phase 3.Stage 1.Action 5

Add a test where a selector returns an edge outside `lift_candidates`.

Expected:

```text
ValueError
```

#### Phase 3.Stage 1.Action 6

Run:

```bash
uv run pytest tests/training/test_fiber_conditioned_stage.py
```

Confirm the new tests fail for expected missing-selector reasons.

### Phase 3.Stage 2: Implement Selector Hook

#### Phase 3.Stage 2.Action 1

Open:

```text
src/state_collapser/training/stages.py
```

#### Phase 3.Stage 2.Action 2

Add type alias:

```python
LiftSelector = Callable[
    [tuple[BaseEdge, ...], ActionSelectionInput, ActionCellId],
    BaseEdge,
]
```

Place it near the stage protocol/type definitions.

#### Phase 3.Stage 2.Action 3

Add default function:

```python
def deterministic_first_lift_selector(
    lift_candidates: tuple[BaseEdge, ...],
    source_input: ActionSelectionInput,
    action_cell: ActionCellId,
) -> BaseEdge:
    return lift_candidates[0]
```

The unused parameters are acceptable because they make the selector signature
future-proof without becoming a policy framework. If Ruff flags unused arguments,
use leading underscores or reference them minimally.

#### Phase 3.Stage 2.Action 4

Add dataclass field to `FiberConditionedStage`:

```python
lift_selector: LiftSelector = deterministic_first_lift_selector
```

Place it near `action_resolver`.

#### Phase 3.Stage 2.Action 5

Replace:

```python
realized_edge = lift_candidates[0]
```

with a helper or inline logic that:

1. calls `self.lift_selector(lift_candidates, source_input, action_cell)`;
2. verifies the returned edge is in `lift_candidates`;
3. computes selected index;
4. raises `ValueError` for invalid selector output.

#### Phase 3.Stage 2.Action 6

Add successful-transition diagnostics:

```python
transition_diagnostics["lift_candidate_count"] = len(lift_candidates)
transition_diagnostics["selected_lift_index"] = selected_lift_index
transition_diagnostics["lift_selector"] = selector_name
```

Keep existing diagnostics:

```python
fiber_action_cell
realized_edge
```

#### Phase 3.Stage 2.Action 7

Export `LiftSelector` and `deterministic_first_lift_selector` from
`src/state_collapser/training/__init__.py` if current training package export
style suggests stage helpers are exported there.

If exporting would broaden public surface awkwardly, stop and decide with the
Project Owner or document why the helper remains module-local.

### Phase 3.Stage 3: Validate Lift Selector

#### Phase 3.Stage 3.Action 1

Run:

```bash
uv run pytest tests/training/test_fiber_conditioned_stage.py
uv run pytest tests/examples/test_plate_support_env_fiber_conditioned_stage.py
```

#### Phase 3.Stage 3.Action 2

Run:

```bash
uv run mypy src
uv run ruff check src/state_collapser/training/stages.py tests/training/test_fiber_conditioned_stage.py
```

#### Phase 3.Stage 3.Action 3

Update the implementation log with:

- selector API signature;
- default behavior;
- diagnostics keys;
- tests run.

## Phase 4: Mandatory `pillow` Dependency Cleanup

Goal:

```text
Remove unused mandatory dependency weight from the base package, or document a
real current source need if one is discovered.
```

### Phase 4.Stage 1: Reconfirm Usage

#### Phase 4.Stage 1.Action 1

Run:

```bash
rg -n "PIL|pillow|Image" src tests pyproject.toml README.md docs
```

#### Phase 4.Stage 1.Action 2

Inspect all source/test hits.

If source or tests currently import/use Pillow, stop and update the
implementation log with the discovered reason before changing dependencies.

If only docs/design/pyproject references appear, proceed.

### Phase 4.Stage 2: Remove Or Relocate Dependency

#### Phase 4.Stage 2.Action 1

Open:

```text
pyproject.toml
```

#### Phase 4.Stage 2.Action 2

If no source/test usage exists, remove `pillow>=12.2.0` from base dependencies.

If the dependency list becomes empty, remove the `dependencies = [...]` field
entirely unless tooling requires an empty list.

Do not add a visualization extra unless a real current caller requires it.

#### Phase 4.Stage 2.Action 3

Update lockfile:

```bash
uv lock
```

If `uv lock` needs network access or fails for environment reasons, follow the
sandbox/escalation protocol and record the failure in the implementation log.

### Phase 4.Stage 3: Validate Dependency Cleanup

#### Phase 4.Stage 3.Action 1

Run:

```bash
uv sync --extra dev --extra rl
```

#### Phase 4.Stage 3.Action 2

Run import smoke:

```bash
uv run python -c "import state_collapser; print(state_collapser.__version__)"
```

#### Phase 4.Stage 3.Action 3

Run package build:

```bash
uv run python -m build
```

If build artifacts are created under `dist/`, inspect `.gitignore` and avoid
staging generated distributions unless explicitly requested.

#### Phase 4.Stage 3.Action 4

Update implementation log with dependency decision, lockfile result, sync
result, and build result.

## Phase 5: Small Front-Door Documentation Cleanup

Goal:

```text
Align front-door docs with current package reality without reopening deferred
benchmark/framework work.
```

### Phase 5.Stage 1: README Version Alignment

#### Phase 5.Stage 1.Action 1

Open:

```text
README.md
```

#### Phase 5.Stage 1.Action 2

Update the GitHub tag install command from:

```text
@v0.7.0
```

to:

```text
@v0.7.1
```

Do not rewrite the installation section broadly.

### Phase 5.Stage 2: Artifact Contract Refresh

#### Phase 5.Stage 2.Action 1

Open:

```text
docs/artifact_contracts.md
```

#### Phase 5.Stage 2.Action 2

Rewrite the stale "first implementation phase" language.

The refreshed document must represent current artifact reality:

- runtime value artifacts such as `RuntimeSnapshot`;
- live runtime view surfaces such as `LiveRuntimeView`;
- tensorization metadata such as `LinearizationConfig` and
  `LinearizationReport`;
- design/gameplan/log/continuity artifacts;
- deferred benchmark artifacts as future work, not implemented outputs.

#### Phase 5.Stage 2.Action 3

Do not add benchmark artifact writer claims.

Do not imply serious benchmark manifests exist.

### Phase 5.Stage 3: Instrumentation Wording

#### Phase 5.Stage 3.Action 1

Open:

```text
README.md
CONTRIBUTING.md
```

#### Phase 5.Stage 3.Action 2

Where instrumentation is mentioned, clarify that instrumentation namespaces are
planned/reserved and implemented tooling is not yet present.

Do not create instrumentation source files in this pass.

#### Phase 5.Stage 3.Action 3

Check whether `docs/package_usage.md` or `docs/public_api.md` need a small
dependency wording change after `pillow` cleanup.

If not needed, leave them unchanged.

### Phase 5.Stage 4: Validate Documentation Cleanup

#### Phase 5.Stage 4.Action 1

Run:

```bash
rg -n "v0\\.7\\.0|entering the first implementation phase|pillow|Pillow|instrumentation" README.md CONTRIBUTING.md docs/artifact_contracts.md docs/package_usage.md docs/public_api.md pyproject.toml
```

Inspect hits manually. Expected historical or future-work hits may remain, but
front-door stale claims should be gone.

#### Phase 5.Stage 4.Action 2

Update implementation log with documentation files changed and remaining
intentional hits.

## Phase 6: Downstream Handoff Alignment

Goal:

```text
Keep big_boy_benchmarking engineers aligned with upstream API and behavior
changes without implementing BBB work in this repo.
```

### Phase 6.Stage 1: Review Root Handoff

#### Phase 6.Stage 1.Action 1

Open:

```text
big_boy_benchmarking_synthetic_blow_revisions_02_handoff.md
```

#### Phase 6.Stage 1.Action 2

Compare the handoff against the implemented API names and diagnostics keys.

If implementation changed names from the blueprint, update the handoff to match
actual code.

### Phase 6.Stage 2: Add Implementation-Specific Details

#### Phase 6.Stage 2.Action 1

Add exact invariant API names after implementation:

```text
PartitionTower.invariant_report(...)
PartitionTower.assert_consistent(...)
ActionPartitionLayer.invariant_report(...)
ActionPartitionLayer.assert_consistent(...)
```

Only include APIs that actually exist.

#### Phase 6.Stage 2.Action 2

Add exact lift-selector diagnostics keys after implementation.

Only include keys that actually exist.

#### Phase 6.Stage 2.Action 3

Add exact NumPy observation metadata keys after implementation.

Only include keys that actually exist.

### Phase 6.Stage 3: Validate Handoff Accuracy

#### Phase 6.Stage 3.Action 1

Search for outdated placeholder language:

```bash
rg -n "expected|planned|TODO|exact API" big_boy_benchmarking_synthetic_blow_revisions_02_handoff.md
```

Any remaining planned/future language must be intentional and accurate.

#### Phase 6.Stage 3.Action 2

Update implementation log with downstream handoff status.

## Phase 7: Full Validation

Goal:

```text
Prove the implementation is locally coherent before closeout.
```

### Phase 7.Stage 1: Focused Validation

#### Phase 7.Stage 1.Action 1

Run NumPy linearization tests:

```bash
uv run pytest tests/training/test_linearized_records.py
```

#### Phase 7.Stage 1.Action 2

Run partition invariant and source-support tests:

```bash
uv run pytest tests/tower/partition/test_partition_invariants.py
uv run pytest tests/tower/partition/test_full_incremental_equivalence.py
uv run pytest tests/tower/partition/test_pointwise_liftability.py
uv run pytest tests/tower/partition/test_queries_and_lift.py
uv run pytest tests/tower/partition/test_hgraphml_downstream_compatibility.py
```

#### Phase 7.Stage 1.Action 3

Run lift-selection tests:

```bash
uv run pytest tests/training/test_fiber_conditioned_stage.py
uv run pytest tests/examples/test_plate_support_env_fiber_conditioned_stage.py
```

#### Phase 7.Stage 1.Action 4

Run benchmark smoke:

```bash
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only
```

### Phase 7.Stage 2: Static And Full Validation

#### Phase 7.Stage 2.Action 1

Run:

```bash
uv run ruff check .
```

#### Phase 7.Stage 2.Action 2

Run:

```bash
uv run mypy src
```

#### Phase 7.Stage 2.Action 3

Run:

```bash
uv run pytest
```

#### Phase 7.Stage 2.Action 4

If dependency metadata changed, run:

```bash
uv run python -m build
```

Confirm generated artifacts are ignored or unstaged unless the Project Owner
explicitly requests otherwise.

### Phase 7.Stage 3: Diff Review

#### Phase 7.Stage 3.Action 1

Run:

```bash
git diff --check
```

#### Phase 7.Stage 3.Action 2

Run:

```bash
git diff --stat
```

Inspect whether changed files match this gameplan.

#### Phase 7.Stage 3.Action 3

Run:

```bash
git status --short --branch
```

Confirm unrelated user files were not modified.

#### Phase 7.Stage 3.Action 4

Update implementation log with final validation results and changed-file
summary.

## Phase 8: Closeout

Goal:

```text
Leave the implementation interval legible for review, commit, and merge.
```

### Phase 8.Stage 1: Final Implementation Log

#### Phase 8.Stage 1.Action 1

Complete:

```text
docs/design/synthetic_blow_revisions_02/01_003_synthetic_blow_revisions_02_implementation_log.md
```

The log must state:

- completed phases;
- tests run;
- tests not run, if any;
- dependency/lockfile changes;
- downstream handoff status;
- remaining risks;
- struck-through items intentionally not implemented.

#### Phase 8.Stage 1.Action 2

Record any deviations from the gameplan.

If there were no deviations, say so explicitly.

### Phase 8.Stage 2: Final Report To Project Owner

#### Phase 8.Stage 2.Action 1

Report:

- implementation summary;
- files changed;
- validation results;
- whether `pillow` was removed or retained;
- downstream handoff doc path;
- any risks.

Do not claim a commit or merge unless those actions were explicitly requested
and completed.

### Phase 8.Stage 3: Optional Commit Preparation

#### Phase 8.Stage 3.Action 1

Only if the Project Owner asks for a commit, propose a concise commit message.

Suggested message:

```text
Harden synthetic review revision surfaces
```

Do not commit automatically unless explicitly requested.

## Acceptance Checklist

Implementation is complete only when all applicable items are true:

- [ ] Implementation occurred on a dedicated branch.
- [ ] Implementation log exists and is current.
- [ ] Numeric NumPy observations linearize in strict mode.
- [ ] Unsupported NumPy arrays fail in strict mode.
- [ ] Unsupported NumPy arrays sidecar in non-strict mode.
- [ ] Real `PlateSupportEnv` observation linearizes.
- [ ] Partition invariant report types exist.
- [ ] `ActionPartitionLayer` exposes invariant reporting/assertion.
- [ ] `PartitionTower` exposes invariant reporting/assertion.
- [ ] Invariants validate adjacent-tier source support.
- [ ] Invariants validate flattened base-source caches.
- [ ] Corruption tests catch stale action/source indexes.
- [ ] `FiberConditionedStage` exposes a lift selector hook.
- [ ] Default lift selector preserves first-candidate behavior.
- [ ] Custom lift selector can choose a non-first candidate.
- [ ] Invalid lift selector output raises clearly.
- [ ] Lift-selection diagnostics are recorded.
- [ ] `pillow` is removed from base dependencies or justified by current source usage.
- [ ] `uv.lock` is updated if dependency metadata changes.
- [ ] README install tag is aligned with current version.
- [ ] `docs/artifact_contracts.md` no longer describes first implementation state.
- [ ] Instrumentation wording is accurate.
- [ ] BBB handoff is accurate after implementation.
- [ ] Focused tests pass.
- [ ] Ruff passes.
- [ ] mypy passes.
- [ ] Full pytest passes.
- [ ] Benchmark smoke passes.
- [ ] Build passes if dependency metadata changed.
- [ ] `git diff --check` passes.

