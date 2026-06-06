# Synthetic Blow Review Revisions 02 Blueprint

Date: 2026-06-04

Status: blueprint

Source review:

- `docs/code_review/03_001_synthetic_blow_full_repo_review_current_state.md`

Related design authority:

- `docs/design/synthetic_blow_revisions_02/README.md`
- `docs/design/pointwise_liftability_source_support/README.md`
- `docs/design/pointwise_liftability_source_support/01_001_pointwise_liftability_source_support_blueprint.md`
- `docs/design/pointwise_liftability_source_support/01_002_pointwise_liftability_source_support_implementation_workplan.md`

## Executive Summary

This blueprint scopes the second synthetic-Blow-review revision pass after the
Project Owner struck through the review items that should not be implemented
now. The implementation target is intentionally narrow:

1. make backend-independent linearization accept the package's own NumPy
   observations;
2. add invariant checking for partition/action source-support indexes;
3. make `FiberConditionedStage`'s concrete lift selection explicit;
4. remove or relocate the unused mandatory `pillow` dependency;
5. refresh small stale front-door documentation points.

The unifying concern is engineering trust, not new capability breadth. The repo
already has a working partition tower, pointwise executable lift support,
fiber-conditioned training surfaces, and a tensorization boundary. The next pass
should make those surfaces harder to misuse and easier to validate without
reopening struck-through work about Torch CI, serious benchmarking, replay,
checkpointing, or a full tower-augmented Gymnasium wrapper.

## PO Triage

The Project Owner explicitly struck through the following items in
`docs/code_review/03_001_synthetic_blow_full_repo_review_current_state.md`:

- optional Torch boundary not exercised by default CI;
- serious benchmark artifact/harness work;
- replay/checkpoint/vectorized rollout/experiment-manifest framework work;
- full tower-augmented Gymnasium wrapper work.

Those items remain valid future concerns, but they are not part of this
implementation track.

The remaining in-scope items are:

- review item 2: NumPy observation linearization;
- review item 5: partition/action-layer invariant checking;
- review item 6: explicit concrete lift-selection policy;
- review item 8: unused mandatory `pillow` dependency;
- review item 9: small stale front-door documentation cleanup.

## Current Repo Ground Truth

### Linearization

The backend-independent linearization boundary lives in
`src/state_collapser/training/linearization.py`.

Current observations:

- `LinearizationConfig` already separates `LinearizationState`,
  `NumericBackend`, and `TensorDeviceKind`.
- `NumericBackend.NUMPY` exists and is described as the backend-independent
  numeric layer.
- `linearization.py` avoids importing Torch at module import time.
- `_linearize_observation(...)` currently accepts bool, int, float, list, and
  tuple observations.
- `_linearize_observation(...)` does not currently accept `np.ndarray`.
- Packaged Gymnasium examples return NumPy arrays from their observation
  encoders.

Primary code references:

- `src/state_collapser/training/linearization.py:52` through
  `src/state_collapser/training/linearization.py:63`
- `src/state_collapser/training/linearization.py:726` through
  `src/state_collapser/training/linearization.py:809`
- `src/state_collapser/training/linearization.py:973` through
  `src/state_collapser/training/linearization.py:996`
- `src/state_collapser/examples/plate_support_env/env.py:46` through
  `src/state_collapser/examples/plate_support_env/env.py:52`
- `src/state_collapser/examples/plate_support_env/env.py:396` through
  `src/state_collapser/examples/plate_support_env/env.py:441`

### Partition Source-Support

The pointwise-liftability work already added the central source-support data
needed for correct executable lift behavior.

Current observations:

- `ActionPartitionLayer` stores adjacent lower-tier source support through
  `source_child_cells_by_action_cell`,
  `edge_ids_by_action_cell_by_source_child`, and
  `lower_action_cells_by_action_cell_by_source_child`.
- It also stores flattened base-source caches through
  `edge_ids_by_action_cell_by_base_source`,
  `base_source_ids_by_action_cell`, and
  `base_active_source_ids_by_collection`.
- `PartitionTower.executable_lift_candidates(...)` uses the flattened
  base-source cache to answer current-base-state executable lift queries.
- `PartitionTower.supported_child_state_cells(...)`,
  `active_child_state_cells(...)`, and
  `lower_action_cells_for_supported_child(...)` preserve the adjacent-tier
  interpretation.

Primary code references:

- `src/state_collapser/tower/partition/action_layer.py:44` through
  `src/state_collapser/tower/partition/action_layer.py:109`
- `src/state_collapser/tower/partition/action_layer.py:305` through
  `src/state_collapser/tower/partition/action_layer.py:400`
- `src/state_collapser/tower/partition/action_layer.py:420` through
  `src/state_collapser/tower/partition/action_layer.py:480`
- `src/state_collapser/tower/partition/tower.py:304` through
  `src/state_collapser/tower/partition/tower.py:365`
- `src/state_collapser/tower/partition/tower.py:367` through
  `src/state_collapser/tower/partition/tower.py:428`

The pointwise-liftability README states the design constraint that matters here:
the flattened base-source caches are performance materializations, not the
mathematical object itself. The invariant design must protect the recursive
Young-diagram structure:

```text
tier-i action cell
    -> tier-(i-1) child state cells that actually source contributing edges
    -> recursively downward
    -> concrete executable edges at tier 0
```

### Fiber-Conditioned Stage Lift Selection

`FiberConditionedStage.step(...)` currently resolves an action decision to an
action cell, asks the path fiber for lift candidates, and silently chooses the
first candidate:

- `src/state_collapser/training/stages.py:153` through
  `src/state_collapser/training/stages.py:196`

That is deterministic, but it hides a policy choice. If two or more concrete
base edges realize the same abstract action cell from the current base state,
the package currently chooses by tuple order without naming that choice.

This should become an explicit hook with the current behavior preserved as the
default.

### Dependencies

`pyproject.toml` currently makes `pillow>=12.2.0` a base dependency:

- `pyproject.toml:36` through `pyproject.toml:38`

The synthetic review found no package or test usage of `PIL`, `pillow`, or
`Image` in current source. If that remains true during implementation,
`pillow` should be removed from base dependencies rather than carried for future
visualization intentions.

### Front-Door Docs

Small stale documentation points identified by the review:

- README install command points to `v0.7.0` while package metadata is `0.7.1`.
- `docs/artifact_contracts.md` still describes the repo as entering first
  implementation and points at early initial artifacts.
- README and CONTRIBUTING mention an instrumentation namespace that is currently
  empty.

Primary docs references:

- `README.md:66` through `README.md:70`
- `docs/artifact_contracts.md:5` through `docs/artifact_contracts.md:10`
- `README.md:304` through `README.md:326`
- `CONTRIBUTING.md:355` through `CONTRIBUTING.md:362`

## Design Principles

### Preserve The Object-Native Runtime

NumPy observation support must not force the runtime through tensor or array
adapters. The object-native runtime remains the source of truth. Linearization is
an explicit learner/benchmark boundary.

### Preserve Recursive Source-Support Semantics

Invariant checks must validate both:

- adjacent-tier support pointers, which are the conceptual Young-diagram
  structure;
- flattened base-source caches, which are hot-path materializations.

It would be a design error to implement only a flat map from base states to
actions and call that the invariant.

### Keep Hardening Out Of The Hot Path By Default

Invariant reports and assertions are for tests, debugging, and optionally future
benchmarks. They should not run automatically during every runtime step unless a
caller explicitly asks for debug validation.

### Preserve Backward Compatibility

The default behavior of `FiberConditionedStage` should remain deterministic
first-candidate selection. Existing callers should not have to supply a new
argument unless they want custom lift selection.

### Keep This Pass Small

This work should not create:

- a Torch CI matrix;
- serious benchmark artifacts;
- replay/checkpoint infrastructure;
- experiment manifests;
- a new Gymnasium tower wrapper;
- a new public model family;
- a broader tensorization rewrite.

## Work Package 1: NumPy Observation Linearization

### Goal

Make `linearize_action_selection_input(...)` accept numeric `np.ndarray`
observations in strict mode, including observations emitted by packaged example
environments.

### Proposed Implementation Surface

Modify `_linearize_observation(...)` in
`src/state_collapser/training/linearization.py`.

Add a private helper, likely one of:

```python
def _linearize_numpy_observation(
    observation: object,
    *,
    strict: bool,
) -> tuple[tuple[float, ...], JsonDict] | None:
    ...
```

or:

```python
def _try_linearize_numpy_observation(
    observation: object,
    *,
    strict: bool,
) -> tuple[tuple[float, ...], JsonDict] | None:
    ...
```

The helper should return `None` when the observation is not a NumPy array, so
the existing bool/int/float/list/tuple branches remain straightforward.

### Optional Import Rule

Do not add a top-level `import numpy as np` to `linearization.py`.

Use a lazy import path:

```python
numpy_spec = importlib.util.find_spec("numpy")
if numpy_spec is None:
    return None
numpy_module = importlib.import_module("numpy")
```

This preserves the current package boundary:

- base package import does not require NumPy;
- the `rl` extra supplies NumPy for Gymnasium/example users;
- Torch remains optional and downstream.

### Supported NumPy Arrays

Strict mode should support arrays whose dtype kind is numeric or boolean:

- boolean arrays: `dtype.kind == "b"`
- signed integers: `dtype.kind == "i"`
- unsigned integers: `dtype.kind == "u"`
- floats: `dtype.kind == "f"`

Strict mode should reject:

- object arrays;
- string/unicode arrays;
- bytes arrays;
- complex arrays, unless a future design explicitly decides how complex values
  should be projected;
- structured arrays.

Non-strict mode should preserve sidecar metadata and return empty features for
unsupported arrays, matching the current unsupported-observation behavior.

### Feature Conversion

The first pass should flatten numeric arrays in row-major order and coerce values
to Python floats:

```python
features = tuple(float(value) for value in observation.reshape(-1).tolist())
```

The exact implementation may prefer `ravel()` or `reshape(-1)`. The important
point is that the result remains a backend-independent tuple of floats, not a
NumPy array and not a Torch tensor.

### Metadata

For NumPy observations, `observation_metadata` should include at least:

```python
{
    "kind": "numpy.ndarray",
    "shape": [...],
    "dtype": "...",
}
```

Shape should be JSON-safe, preferably a list of ints. Dtype should be
`str(observation.dtype)`.

The metadata should flow through the existing `_linearized_input_metadata(...)`
path, which already places observation metadata under
`metadata["observation"]`.

### Tests

Add focused tests in `tests/training/test_linearized_records.py` or a new
adjacent file.

Required cases:

1. strict numeric NumPy observation linearizes to the expected tuple of floats;
2. metadata records `kind`, `shape`, and `dtype`;
3. strict object array raises `ValueError`;
4. non-strict object array returns empty features and records unsupported
   observation metadata;
5. a real `PlateSupportEnv.reset(...)` observation linearizes successfully.

If a real example-environment test imports Gymnasium or NumPy, it can rely on
the `rl` extra because CI currently installs `dev` and `rl`.

### Non-Goals

Do not add full ragged tensor support.

Do not persist linearized records.

Do not add a NumPy batch object.

Do not make NumPy a base package dependency unless a later package-policy
decision explicitly moves it out of the `rl` extra.

## Work Package 2: Partition Source-Support Invariant Checking

### Goal

Add a structured invariant-checking surface that can verify the internal
consistency of state/action partition layers, especially the source-support
indexes added for pointwise liftability.

### Placement

The preferred implementation is a new module:

```text
src/state_collapser/tower/partition/invariants.py
```

This keeps invariant logic separate from update counters in
`diagnostics.py`, while still placing it near partition diagnostics.

Export the public-enough test/debug surface from:

```text
src/state_collapser/tower/partition/__init__.py
```

### Proposed Data Structures

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


@dataclass(frozen=True, slots=True)
class PartitionInvariantReport:
    issues: tuple[PartitionInvariantIssue, ...]

    @property
    def ok(self) -> bool: ...
    def assert_ok(self) -> None: ...
```

The report should be easy to inspect in tests and debugging. `assert_ok()` should
raise `AssertionError` or `ValueError` with a concise summary. `AssertionError`
is probably best for test/debug invariant failure; `ValueError` is better for
public input validation. Since this is internal consistency checking,
`AssertionError` is acceptable.

### Proposed API

Add action-layer-level validation:

```python
def invariant_report(
    self,
    *,
    state_layer: StatePartitionLayer,
    registry: BaseGraphRegistry,
    lower_state_layer: StatePartitionLayer | None = None,
    lower_action_layer: ActionPartitionLayer | None = None,
    allow_dirty: bool = False,
) -> PartitionInvariantReport:
    ...

def assert_consistent(...) -> None:
    self.invariant_report(...).assert_ok()
```

Add tower-level validation:

```python
def invariant_report(
    self,
    *,
    allow_dirty: bool = False,
) -> PartitionInvariantReport:
    ...

def assert_consistent(self, *, allow_dirty: bool = False) -> None:
    self.invariant_report(allow_dirty=allow_dirty).assert_ok()
```

The tower-level method loops over each tier and delegates to the action layer,
passing lower-tier state/action layers when available.

### Required Invariants

At minimum, the action-layer report should validate:

1. every state cell in the state layer has an outgoing collection;
2. every outgoing collection referenced by a state cell exists in
   `edge_ids_by_collection`;
3. every collection listed in `edge_ids_by_collection` is either attached to a
   live state cell or intentionally obsolete only if the design explicitly
   permits obsolete collections;
4. no dirty collections remain when `allow_dirty=False`;
5. every action cell listed by a collection exists in
   `edge_ids_by_action_cell`;
6. every live edge in an action cell maps back through
   `action_cell_by_edge_id`;
7. every `action_cell_by_edge_id` entry points to an action cell containing that
   edge;
8. each action cell has source-cell, target-cell, and label-key entries;
9. every edge in an action cell has source and target cells matching the
   action-cell source and target entries under the current state layer;
10. no live action cell exposes an edge whose source and target are in the same
    current state cell;
11. source-child support matches the lower state layer when there is a lower
    tier, or the current state layer at tier 0;
12. `edge_ids_by_action_cell_by_source_child` contains exactly the edge ids whose
    source belongs to that child cell;
13. `lower_action_cells_by_action_cell_by_source_child` is consistent with the
    lower action layer when a lower action layer exists;
14. `edge_ids_by_action_cell_by_base_source` contains exactly the edge ids whose
    base source id is that source;
15. `base_source_ids_by_action_cell` equals the sorted keys of
    `edge_ids_by_action_cell_by_base_source`;
16. `active_child_cells_by_collection` equals the union of source-child cells
    across action cells in that collection;
17. `base_active_source_ids_by_collection` equals the union of base-source ids
    across action cells in that collection;
18. internal edges are not present in live action-cell edge sets;
19. internal edge records remain attached to the state cells that made them
    internal.

This invariant list deliberately checks both the recursive support structure and
the flattened base-source materialization.

### Relation To Pointwise Liftability

This is not a new liftability model. It is a hardening layer over the current
model.

The core correctness assertion is:

```text
If a tier-i action cell claims executable support from a base state, then that
support must be visible both in the recursive adjacent-tier pointers and in the
flattened base-source cache used by executable_lift_candidates(...).
```

The invariant checker should therefore make stale or mismatched caches
detectable immediately in tests.

### Tests

Add tests under `tests/tower/partition`.

Recommended file:

```text
tests/tower/partition/test_partition_invariants.py
```

Required cases:

1. a normal initialized tower reports `ok`;
2. a normal incrementally updated tower reports `ok`;
3. full/incremental equivalence fixtures can call `assert_consistent()`;
4. an intentionally corrupted `action_cell_by_edge_id` entry is detected;
5. an intentionally corrupted base-source cache is detected;
6. an intentionally corrupted source-child support entry is detected;
7. a dirty collection is detected when `allow_dirty=False`;
8. dirty collection detection can be suppressed when `allow_dirty=True`, if a
   test needs to inspect an intermediate layer state.

Implementation should avoid brittle tests that depend on private ordinal ids
unless the test builds and corrupts those ids directly from the tower it just
created.

### Non-Goals

Do not run invariant checks on every runtime step by default.

Do not replace the current source-support caches.

Do not remove representative/readout lift semantics.

Do not flatten the Young-diagram source-support model into only a base-state
side table.

## Work Package 3: Explicit Lift Selection In `FiberConditionedStage`

### Goal

Make concrete lift selection explicit while preserving current behavior.

### Current Behavior

The current stage chooses:

```python
realized_edge = lift_candidates[0]
```

This happens at `src/state_collapser/training/stages.py:190`.

### Proposed API

Add a top-level type alias:

```python
LiftSelector = Callable[
    [tuple[BaseEdge, ...], ActionSelectionInput, ActionCellId],
    BaseEdge,
]
```

Add a default function:

```python
def deterministic_first_lift_selector(
    lift_candidates: tuple[BaseEdge, ...],
    source_input: ActionSelectionInput,
    action_cell: ActionCellId,
) -> BaseEdge:
    return lift_candidates[0]
```

Add a dataclass field:

```python
lift_selector: LiftSelector = deterministic_first_lift_selector
```

The field should sit near `action_resolver`, because both control how abstract
action-cell decisions become runtime-executable primitive actions.

### Selector Validation

After calling the selector, `FiberConditionedStage` should verify that the
returned edge is one of the candidate edges. If it is not, raise a clear
`ValueError`, for example:

```text
Lift selector returned an edge outside the available lift candidates.
```

Do not silently accept invalid selector output. That would reintroduce the same
kind of hidden execution mismatch this pass is trying to eliminate.

### Diagnostics

Add diagnostics to successful transitions:

```python
transition_diagnostics["lift_candidate_count"] = len(lift_candidates)
transition_diagnostics["selected_lift_index"] = ...
transition_diagnostics["lift_selector"] = ...
```

The selected index should be the index of the returned edge in
`lift_candidates`.

The selector name can be derived conservatively:

```python
getattr(self.lift_selector, "__name__", type(self.lift_selector).__name__)
```

Keep the existing diagnostics:

- `fiber_action_cell`
- `realized_edge`

### Tests

Add or extend tests in:

```text
tests/training/test_fiber_conditioned_stage.py
```

Required cases:

1. default behavior still chooses the first lift candidate;
2. custom selector can choose a non-first candidate;
3. transition diagnostics record candidate count, selected index, and selector
   name;
4. invalid selector output raises `ValueError`;
5. existing no-lift-candidate diagnostic behavior is unchanged.

The fixture should deliberately create an action cell with at least two
candidate concrete edges from the current base state. If an existing fixture can
be adapted cleanly, use it. Otherwise build a tiny test tower directly.

### Non-Goals

Do not add a policy-learning interface here.

Do not make the selector stochastic by default.

Do not add replay, evaluation, or model-mode semantics.

Do not change `ActionDecision` shape.

## Work Package 4: Mandatory `pillow` Dependency Cleanup

### Goal

Remove unused mandatory dependency surface unless implementation discovers a
current source dependency that the review missed.

### Proposed Action

During implementation, rerun:

```bash
rg -n "PIL|pillow|Image" src tests pyproject.toml README.md docs
```

If no source/test usage exists, remove:

```toml
dependencies = [
    "pillow>=12.2.0",
]
```

from `pyproject.toml`.

If `dependencies` becomes empty, use the valid package form preferred by
Hatchling/PEP 621. Either remove the `dependencies` field entirely or leave it
as an empty list only if that is accepted by the project tooling. Removing the
field is probably cleaner.

Then update `uv.lock`.

### Optional Extra Decision

Do not add a new visualization extra in this pass unless current source actually
needs it. The review issue is unused dependency cleanup, not new visualization
design.

If future instrumentation needs Pillow, add a future optional group such as:

```toml
visualization = [
  "pillow>=12.2.0",
]
```

But that is out of scope for this pass unless a real caller appears.

### Tests And Validation

The main validation is packaging/tooling:

- `uv sync --extra dev --extra rl`
- `uv run python -m build` if the implementation workplan includes build
  validation;
- full pytest.

If a simple metadata test exists or is appropriate, it can assert that importing
`state_collapser` does not require Pillow. Do not add a brittle test that merely
locks dependency text unless maintainers want pyproject dependency policy tested
directly.

## Work Package 5: Small Front-Door Documentation Cleanup

### Goal

Clean stale front-door docs identified by the review without reopening deferred
benchmark/framework work.

### README Install Tag

Update the public GitHub tag install command from `v0.7.0` to `v0.7.1`:

- source: `README.md:66` through `README.md:70`

This is a simple version alignment fix.

### Artifact Contracts

Rewrite `docs/artifact_contracts.md` so it no longer says the project is
entering first implementation.

The updated file should distinguish:

- active value/runtime artifacts, such as `RuntimeSnapshot` and
  `LiveRuntimeView`;
- active tensorization metadata artifacts, such as `LinearizationConfig` and
  `LinearizationReport`;
- active design/continuity artifacts;
- deferred serious benchmark artifacts.

Because serious benchmark artifact work is struck through for this pass, the
artifact contract update must not claim benchmark artifact implementation exists.
It can say that serious benchmark artifacts are a future category named in
`EVALUATION.md` and `CONTRIBUTING.md`.

### Instrumentation Wording

README and CONTRIBUTING currently identify an instrumentation namespace that is
empty. The cleanup should make the wording precise:

- the namespace is planned/reserved;
- implemented instrumentation tooling is not yet present;
- contributors should use that namespace only when adding real metrics or
  visualization work.

Do not create instrumentation tooling in this pass.

### Documentation Non-Goals

Do not rewrite README broadly.

Do not rewrite CONTRIBUTING broadly.

Do not add benchmark-harness claims.

Do not change public API policy except if required by the dependency or
linearization changes.

## Cross-Package And Downstream Compatibility

### HGraphML

HGraphML compatibility matters here because the invariant checker must not
define source support in a purely RL-specific way.

The invariant surfaces should validate the shared tower encoding/readout
structure HGraphML depends on:

- state cells;
- action cells;
- source child cells;
- edge fibers;
- base edge registration;
- coarse endpoint recovery.

The implementation should rerun:

```bash
uv run pytest tests/tower/partition/test_hgraphml_downstream_compatibility.py
```

No HGraphML code changes are expected in this pass.

### big_boy_benchmarking

This pass should make `state_collapser` safer for downstream benchmark users by:

- linearizing actual NumPy observations;
- making lift selection explicit;
- giving partition source-support a hard invariant surface.

It should not add benchmark artifacts or integrate with `big_boy_benchmarking`
directly. That work was struck through for now.

## File-Level Change Map

Expected source files:

- `src/state_collapser/training/linearization.py`
- `src/state_collapser/training/stages.py`
- `src/state_collapser/tower/partition/action_layer.py`
- `src/state_collapser/tower/partition/tower.py`
- `src/state_collapser/tower/partition/invariants.py`
- `src/state_collapser/tower/partition/__init__.py`
- `pyproject.toml`
- `uv.lock`

Expected test files:

- `tests/training/test_linearized_records.py`
- `tests/training/test_fiber_conditioned_stage.py`
- `tests/tower/partition/test_partition_invariants.py`
- possibly `tests/tower/partition/test_full_incremental_equivalence.py`
- possibly `tests/tower/partition/test_hgraphml_downstream_compatibility.py`

Expected docs files:

- `README.md`
- `CONTRIBUTING.md`
- `docs/artifact_contracts.md`
- possibly `docs/package_usage.md` only if dependency wording requires it

Expected design/log files after workplan execution:

- `docs/design/synthetic_blow_revisions_02/01_002_synthetic_blow_revisions_02_implementation_workplan.md`
- `docs/design/synthetic_blow_revisions_02/01_003_synthetic_blow_revisions_02_implementation_log.md`

## Test Strategy

### Focused Tests First

NumPy linearization:

```bash
uv run pytest tests/training/test_linearized_records.py
```

Partition invariants:

```bash
uv run pytest tests/tower/partition/test_partition_invariants.py
uv run pytest tests/tower/partition/test_full_incremental_equivalence.py
uv run pytest tests/tower/partition/test_pointwise_liftability.py
uv run pytest tests/tower/partition/test_queries_and_lift.py
uv run pytest tests/tower/partition/test_hgraphml_downstream_compatibility.py
```

Lift selector:

```bash
uv run pytest tests/training/test_fiber_conditioned_stage.py
uv run pytest tests/examples/test_plate_support_env_fiber_conditioned_stage.py
```

Dependency/docs smoke:

```bash
uv run python -c "import state_collapser; print(state_collapser.__version__)"
```

### Full Validation

The implementation pass should finish with:

```bash
uv run ruff check .
uv run mypy src
uv run pytest
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only
```

If `pillow` is removed from dependencies, also validate the lock/build surface:

```bash
uv lock
uv sync --extra dev --extra rl
uv run python -m build
```

The implementation workplan should decide whether build validation is required
in the execution pass. Given that dependency metadata changes are in scope, build
validation is recommended.

## Risk Analysis

### Risk: Lazy NumPy Handling Breaks Strict Typing

`linearization.py` is under strict mypy. Lazy optional import code can easily
produce `Any` leakage or type errors.

Mitigation:

- isolate NumPy use in a small helper;
- keep imported module typed as `object` or `Any` locally;
- avoid exposing NumPy types in public annotations.

### Risk: Invariant Checker Becomes Too Expensive

The invariant checker will walk internal dictionaries and edge sets. That is
fine for tests/debugging, but not for runtime hot paths.

Mitigation:

- do not call it automatically during `step`;
- expose it as explicit `invariant_report()` / `assert_consistent()`;
- keep future benchmark usage opt-in.

### Risk: Invariant Checker Encodes The Wrong Mathematics

A flat base-source checker alone would miss the recursive adjacent-tier support
structure.

Mitigation:

- validate both adjacent child support and flattened base-source caches;
- keep pointwise-liftability README as design authority;
- run HGraphML compatibility tests.

### Risk: Lift Selector Becomes A Policy Framework

The selector can accidentally grow into a learner/model surface.

Mitigation:

- selector only chooses among already-computed concrete lift candidates;
- selector returns a `BaseEdge`;
- no replay, stochastic policy, or model state added here;
- default remains deterministic first candidate.

### Risk: Dependency Cleanup Breaks Source Install

Removing a dependency can expose hidden imports if the search missed something.

Mitigation:

- rerun source search;
- run full pytest;
- run package build after lock update.

### Risk: Documentation Cleanup Reopens Deferred Work

Artifact-contract cleanup could drift into serious benchmark manifest design,
which was struck through.

Mitigation:

- document future benchmark artifacts as deferred;
- do not add artifact writer APIs in this pass;
- keep README/CONTRIBUTING changes minimal.

## Acceptance Criteria

This blueprint is satisfied when:

1. Numeric NumPy observations from packaged examples linearize successfully.
2. Unsupported NumPy arrays fail in strict mode and sidecar in non-strict mode.
3. Partition/action-layer invariant reports exist and are used in tests.
4. Invariant checks validate both recursive adjacent-tier support and flattened
   base-source caches.
5. `FiberConditionedStage` has an explicit lift selector with deterministic
   first-candidate default behavior.
6. Lift selection diagnostics record candidate count, selected index, and
   selector identity.
7. Invalid lift selector output fails clearly.
8. Unused mandatory `pillow` dependency is removed or justified by discovered
   source usage.
9. README install tag is aligned with current package version.
10. `docs/artifact_contracts.md` no longer describes the repo as entering first
    implementation.
11. Instrumentation wording is precise about planned versus implemented
    surfaces.
12. Full local validation passes.

## Blueprint-To-Workplan Readiness

This blueprint is detailed enough to write a Phase.Stage.Action implementation
workplan.

The workplan should preserve the same scope boundaries:

- implement the five in-scope work packages;
- do not implement struck-through review items;
- create a dedicated implementation branch only after the workplan is written
  and approved for execution, per `docs/prime_directive/git_practices.md`.

