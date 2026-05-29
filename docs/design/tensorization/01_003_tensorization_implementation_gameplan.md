# Tensorization Implementation Gameplan

Date: 2026-05-29

Status: implementation gameplan, not implementation

This document is the Phase.Stage.Action implementation gameplan for:

- `docs/design/tensorization/01_001_tensorization_architecture_blueprint.md`
- `docs/design/tensorization/01_002_tensorization_engineer_usage_blueprint.md`

It is downstream of:

- `docs/design/tensorization/README.md`
- `docs/design/tensorization/design_conversation.md`
- `docs/design/model_train_surfaces/01_005_big_boy_benchmarking_tensorization_alignment_note.md`
- `docs/design/RL_framework_maturity/01_002_fiber_conditioned_training_spine_blueprint.md`
- `docs/design/RL_framework_maturity/01_003_fiber_conditioned_training_spine_engineer_documentation_blueprint.md`
- `docs/usage/01_003_training_surface_quickstart.md`
- `docs/usage/01_004_fiber_conditioned_training.md`
- `docs/usage/01_005_using_your_own_training_loop.md`
- `docs/usage/01_009_downstream_applications.md`
- `docs/public_api.md`
- `docs/prime_directive/prime_directive.md`
- `docs/prime_directive/git_practices.md`
- `docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md`
- `docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md`

No source-code execution should begin until the Project Owner explicitly
approves execution of this gameplan.

Once approved, this gameplan is law. If repository reality conflicts with any
Phase.Stage.Action item below, the implementer must stop, identify the exact
failed item, and ask the Project Owner for guidance. Silent simplification,
silent reordering, and silent reinterpretation are forbidden.

## Core Implementation Thesis

The implementation must create a tensor-capable boundary without turning
`state_collapser` into a tensor-first runtime.

The successful shape is:

```text
object-native tower/fiber/training semantics
    -> explicit linearization boundary
        -> optional numeric or Torch learner input
```

The forbidden shape is:

```text
object-native runtime
    -> hidden mandatory linearization layer
        -> backend dispatcher
            -> object-native learner anyway
```

The Project Owner's "tiny hinge" concern is the governing engineering constraint
for this work.

## Fixed Decisions From Blueprint Review

These decisions are fixed unless the Project Owner changes them before
execution.

1. Backend-independent numeric records live in:

   ```text
   src/state_collapser/training/linearization.py
   ```

2. Torch conversion lives in:

   ```text
   src/state_collapser/training/torch.py
   ```

3. No top-level package is created at:

   ```text
   src/state_collapser/ml/
   ```

4. Backend mode is represented by orthogonal fields, not one overloaded mode
   string:

   ```text
   LinearizationState = ABSENT | PRESENT_DISABLED | PRESENT_ENABLED
   NumericBackend = NONE | NUMPY | TORCH
   TensorDeviceKind = NONE | CPU | CUDA
   ```

5. Benchmark labels are derived labels, not source-of-truth configuration:

   ```text
   none_control_flow
   tensor_available_disabled
   tensor_enabled_cpu
   tensor_enabled_cuda
   ```

6. NumPy participates in first scope as a backend-independent numeric layer, but
   NumPy must not become an unconditional core import.

7. Torch remains behind the `ml` extra.

8. First scope fully supports fixed discrete action spaces and fixed or padded
   action masks.

9. Ragged fibers, lift candidates, variable action-cell vocabularies, and
   representative edge lists are metadata sidecars in first scope.

10. Linearized records are not persisted by default.

11. `LinearizationConfig`, `LinearizationReport`, registry summaries, and
    derived benchmark labels are persisted in artifacts or manifests where the
    relevant artifact surface exists.

12. HGraphML compatibility is first-pass important.

13. HGraphML does not get full tensorized graph-message-passing support in this
    implementation slice.

14. The shared encoding vocabulary must be useful for graph nodes, graph edges,
    state cells, action cells, tiers, and fibers.

15. HGraphML must not be forced to use RL-specific `ActionSelectionInput`,
    `TrainingTransition`, or Torch.

16. A tiny Torch smoke model is allowed only under tests/examples. It is not a
    package model family.

## Fixed Defaults For This Gameplan

Unless the Project Owner changes these before execution, implementation uses the
following defaults.

1. Dedicated implementation branch:

   ```text
   codex/tensorization-boundary
   ```

2. Running implementation log:

   ```text
   docs/design/tensorization/01_004_tensorization_implementation_log.md
   ```

3. Backend-independent implementation file:

   ```text
   src/state_collapser/training/linearization.py
   ```

4. Torch implementation file:

   ```text
   src/state_collapser/training/torch.py
   ```

5. Public training exports are added through:

   ```text
   src/state_collapser/training/__init__.py
   ```

6. First-scope usage documentation file:

   ```text
   docs/usage/01_010_tensorization_boundary.md
   ```

7. First-scope tests live primarily under:

   ```text
   tests/training/
   ```

8. HGraphML-facing compatibility protection extends or parallels:

   ```text
   tests/tower/partition/test_hgraphml_downstream_compatibility.py
   ```

9. NumPy import handling is optional and local. Do not edit core dependencies in
   `pyproject.toml` unless implementation reality proves that optional import
   checks are insufficient.

10. Torch tests must use the existing pytest marker:

    ```text
    requires_torch
    ```

## Explicit Non-Goals

This gameplan does not implement:

- PPO
- DQN
- SAC
- A2C
- replay buffers
- vectorized rollout
- distributed rollout
- checkpoint/resume
- model-family APIs
- RLlib adapters
- Stable-Baselines3 adapters
- TorchRL adapters
- Tianshou adapters
- full ragged tensor support
- arbitrary Gymnasium observation inference
- HGraphML tensorized message passing
- `state_collapser.ml`

Any implementation drift toward these surfaces must stop.

## Global Stop Conditions

Implementation must stop and ask the Project Owner if any of the following
occur.

- A Phase.Stage.Action item cannot be implemented as written.
- Implementation would require putting NumPy into unconditional core imports.
- Implementation would require importing Torch from `state_collapser.training`.
- `state_collapser.training.linearization` imports Torch directly or
  transitively.
- `PRESENT_DISABLED` requires constructing linearized records or tensors on the
  hot path.
- Object-native reference loops must be rewritten to pass through the tensor
  boundary.
- HGraphML-facing partition-tower compatibility tests fail because the encoding
  layer became RL-specific.
- Fixed discrete action support requires committing to full ragged tensor
  design.
- A proposed "small helper" becomes an implicit learner framework.
- A test encodes behavior that contradicts the blueprint.
- Any file or symbol named in this gameplan no longer exists.

## Required Branch Discipline

Execution must not start on `main`.

Before touching implementation code, create or switch to:

```text
codex/tensorization-boundary
```

If the Project Owner requests a different branch name, use that branch.

Record the starting branch, starting commit, and starting `git status --short`
in:

```text
docs/design/tensorization/01_004_tensorization_implementation_log.md
```

## Required Running Implementation Log

Execution must maintain:

```text
docs/design/tensorization/01_004_tensorization_implementation_log.md
```

The log must record:

- branch name
- starting commit
- starting git status
- each completed Phase.Stage.Action item
- exact files edited
- exact tests run
- test outcomes
- surprises
- stop conditions
- Project Owner clarifications
- authorized deviations
- final validation status

The log must not rewrite the gameplan during execution. If the gameplan is
wrong, stop and ask the Project Owner.

## Validation Command Set

Use increasingly broad validation.

Focused linearization validation:

```text
uv run pytest tests/training -k "linearization or torch"
```

Tower and HGraphML-facing compatibility validation:

```text
uv run pytest tests/tower/partition/test_hgraphml_downstream_compatibility.py tests/tower/partition tests/training
```

Training-surface validation:

```text
uv run pytest tests/training tests/examples/test_plate_support_env_fiber_conditioned_stage.py tests/examples/test_training_semantics_shared.py
```

Full validation:

```text
uv run pytest
```

Static validation:

```text
uv run ruff check
uv run mypy
```

Torch-specific validation should be run only in an environment with the `ml`
extra installed:

```text
uv run pytest -m requires_torch tests/training
```

If a validation command fails unexpectedly, stop and reconstruct reality before
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
codex/tensorization-boundary
```

Completion criteria:

- The active branch is the implementation branch.
- `git status --short` is recorded in the implementation log.

Stop condition:

- If the working tree contains unrelated changes in files this gameplan must
  edit, stop and ask the Project Owner how to proceed.

### Stage 0.2: Bind Current Repository Reality

#### Action 0.2.1

Re-read these current files from disk:

```text
pyproject.toml
src/state_collapser/training/__init__.py
src/state_collapser/training/inputs.py
src/state_collapser/training/transitions.py
src/state_collapser/training/decisions.py
src/state_collapser/training/fibers.py
src/state_collapser/training/stages.py
src/state_collapser/tower/snapshot.py
src/state_collapser/tower/partition/ids.py
src/state_collapser/tower/partition/base_registry.py
src/state_collapser/tower/partition/tower.py
src/state_collapser/tower/partition/action_layer.py
tests/tower/partition/test_hgraphml_downstream_compatibility.py
```

Completion criteria:

- The implementation log summarizes the current relevant symbols and files.
- The implementer confirms that `ActionSelectionInput`, `TrainingTransition`,
  `ActionDecision`, `FiberStageContext`, `FiberDeparture`, `PathFiber`,
  `FiberConditionedStage`, `PartitionTower`, `BaseGraphRegistry`,
  `StateCellId`, `ActionCellId`, and `ActionCollectionId` exist.

Stop condition:

- If any named file or symbol does not exist, stop before implementing.

#### Action 0.2.2

Confirm optional dependency posture from `pyproject.toml`.

Required current facts:

- Core dependencies are light.
- `rl` extra includes NumPy.
- `ml` extra includes Torch.
- pytest marker `requires_torch` exists.

Completion criteria:

- The implementation log records whether these facts still hold.

Stop condition:

- If dependency posture has changed, stop and ask whether to revise this
  gameplan.

## Phase 1: Establish Backend-Independent Linearization Skeleton

### Stage 1.1: Create `training.linearization`

#### Action 1.1.1

Create:

```text
src/state_collapser/training/linearization.py
```

with a module docstring that states:

```text
Backend-independent semantic-to-numeric conversion boundary.
```

The docstring must also state that the module does not import Torch.

Completion criteria:

- The file exists.
- The file imports no Torch symbols.

Stop condition:

- If Torch appears necessary in this file, stop.

#### Action 1.1.2

Implement the three orthogonal enum surfaces as `StrEnum`:

```text
LinearizationState
NumericBackend
TensorDeviceKind
```

Required values:

```text
LinearizationState.ABSENT = "ABSENT"
LinearizationState.PRESENT_DISABLED = "PRESENT_DISABLED"
LinearizationState.PRESENT_ENABLED = "PRESENT_ENABLED"

NumericBackend.NONE = "NONE"
NumericBackend.NUMPY = "NUMPY"
NumericBackend.TORCH = "TORCH"

TensorDeviceKind.NONE = "NONE"
TensorDeviceKind.CPU = "CPU"
TensorDeviceKind.CUDA = "CUDA"
```

Completion criteria:

- Values are stable strings suitable for manifests.
- No combined mode enum is introduced.

### Stage 1.2: Add Configuration And Report Data

#### Action 1.2.1

Implement `LinearizationConfig` as a frozen `slots=True` dataclass.

Required fields:

```text
linearization_state: LinearizationState
numeric_backend: NumericBackend
device_kind: TensorDeviceKind
dtype: str | None = None
mask_dtype: str = "bool"
max_tower_depth: int | None = None
max_action_count: int | None = None
sequence_length: int | None = None
include_diagnostics: bool = False
encoder_registry_id: str | None = None
strict: bool = True
debug_export_records: bool = False
```

Completion criteria:

- The config can serialize to a JSON-safe dict.
- The config can be reconstructed from that dict.
- Construction validates obviously inconsistent values.

Required validation:

- `ABSENT` requires `NumericBackend.NONE`.
- `ABSENT` requires `TensorDeviceKind.NONE`.
- `NumericBackend.NONE` requires `TensorDeviceKind.NONE`.
- `TensorDeviceKind.CUDA` requires `NumericBackend.TORCH`.
- `PRESENT_ENABLED` cannot use `NumericBackend.NONE`.

Stop condition:

- If validation would make `PRESENT_DISABLED` construct tensors, stop.

#### Action 1.2.2

Implement a derived benchmark-label method on `LinearizationConfig`.

Required output:

```text
none_control_flow
tensor_available_disabled
tensor_enabled_cpu
tensor_enabled_cuda
```

Rules:

- `ABSENT/NONE/NONE` derives `none_control_flow`.
- `PRESENT_DISABLED/*/*` derives `tensor_available_disabled` when the backend
  selection is internally valid.
- `PRESENT_ENABLED/TORCH/CPU` derives `tensor_enabled_cpu`.
- `PRESENT_ENABLED/TORCH/CUDA` derives `tensor_enabled_cuda`.

Completion criteria:

- Labels are derived from enum fields.
- Labels are not stored as independent source-of-truth state.

#### Action 1.2.3

Implement `LinearizationReport` as a frozen `slots=True` dataclass.

Required fields:

```text
linearization_state: LinearizationState
numeric_backend: NumericBackend
device_kind: TensorDeviceKind
benchmark_label: str
backend_available: bool
enabled: bool
dtype: str | None
mask_dtype: str
numpy_available: bool
numpy_version: str | None
torch_available: bool
torch_version: str | None
cuda_available: bool
encoder_registry_id: str | None
schema_fingerprint: str | None
tower_fingerprint: str | None
max_tower_depth: int | None
max_action_count: int | None
conversion_count: int = 0
conversion_elapsed_seconds: float = 0.0
debug_record_exported: bool = False
metadata: Mapping[str, object] = field(default_factory=dict)
```

Completion criteria:

- The report can serialize to a JSON-safe dict.
- The report records enough information for `big_boy_benchmarking` to
  distinguish absent, disabled, CPU-enabled, and CUDA-enabled modes.
- The report does not require persisting every record.

#### Action 1.2.4

Implement local availability helpers inside `linearization.py`.

Required helpers:

```text
numpy_availability()
torch_availability()
```

Rules:

- Use local optional imports or `importlib` checks.
- Do not import Torch at module import time.
- Do not fail module import if NumPy is missing.
- Do not fail module import if Torch is missing.

Completion criteria:

- `import state_collapser.training.linearization` works without NumPy.
- `import state_collapser.training.linearization` works without Torch.

## Phase 2: Implement Shared Encoding Registry

### Stage 2.1: Define Registry Summary And Stable Vocabulary

#### Action 2.1.1

Implement `EncodingRegistry` in:

```text
src/state_collapser/training/linearization.py
```

Required responsibilities:

- encode base states
- encode primitive actions or edge ids
- encode state cells
- encode action cells
- encode action collections where useful
- encode tower tiers
- encode stage ids
- encode fiber ids
- encode frozen behavior ids
- encode fiber departure reasons
- expose a serializable vocabulary summary
- expose a stable `registry_id`

Completion criteria:

- The registry is useful without RL-specific input objects.
- The registry can be constructed from tower/readout concepts alone.
- The registry is HGraphML-compatible.

Stop condition:

- If the registry requires `ActionSelectionInput` or `TrainingTransition` to
  exist, stop.

#### Action 2.1.2

Implement `EncodingRegistry.from_tower(...)`.

Accepted first-scope input:

```text
PartitionTower
```

Required behavior:

- reuse ids from `PartitionTower.registry` where possible
- encode `StateId.value`
- encode `EdgeId.value`
- encode `ActionId.value`
- encode `StateCellId(tier, ordinal)`
- encode `ActionCellId(tier, ordinal)`
- encode `ActionCollectionId(tier, ordinal)` where available
- encode tower tier indices

Completion criteria:

- The registry does not duplicate base graph ids when typed ids already exist.
- The registry summary can be serialized without raw object payloads.
- The registry supports HGraphML-style node/edge/cell readout without RL
  training objects.

#### Action 2.1.3

Implement deterministic registry fingerprinting.

Required behavior:

- Fingerprint depends on stable id summaries, not Python object identity.
- Fingerprint is safe for manifests.
- Fingerprint is repeatable for the same tower registration order.

Completion criteria:

- `EncodingRegistry.registry_id` is stable enough for benchmark manifests.
- Tests can assert repeatability.

### Stage 2.2: Encode Stage And Fiber Metadata

#### Action 2.2.1

Add registry methods for `FiberStageContext`.

Required encoded values:

- `stage_id`
- `fiber_id`
- `fine_tier`
- `coarse_tier`
- `frozen_behavior_id`
- `frozen_behavior_version`

Completion criteria:

- Stage/fiber ids are stable numeric ids.
- The original string ids remain available in metadata sidecars or registry
  summaries.

#### Action 2.2.2

Add registry methods for `FiberDeparture`.

Required encoded values:

- `FiberDepartureReason`
- optional stage context

Completion criteria:

- Known departure reasons get stable ids.
- Unknown or absent departure maps to `None` or a documented sentinel.

## Phase 3: Implement Backend-Independent Linearized Records

### Stage 3.1: Define Linearized Action Input

#### Action 3.1.1

Implement `LinearizedActionSelectionInput` as a frozen `slots=True` dataclass.

Required fields:

```text
observation_features: tuple[float, ...]
current_base_state_id: int | None
tower_position_ids: tuple[int | None, ...]
tower_depth: int
active_tier: int | None
fine_tier: int | None
coarse_tier: int | None
action_mask: tuple[bool, ...]
action_count: int
stage_id: int | None
fiber_id: int | None
frozen_behavior_id: int | None
frozen_behavior_version: int | str | None
fiber_departure_reason_id: int | None
metadata: Mapping[str, object]
```

Completion criteria:

- The record is backend-independent.
- The record is JSON-safe except for clearly marked sidecar metadata.
- The record does not contain Torch tensors.

#### Action 3.1.2

Implement a small observation linearization helper.

First-scope supported observation forms:

- `int`
- `float`
- `bool`
- flat tuple/list of `int`, `float`, or `bool`

Rules:

- In `strict=True`, unsupported observations fail clearly.
- In `strict=False`, unsupported observations become an empty feature tuple and
  the raw observation is preserved only as sidecar metadata or repr-safe
  diagnostics.

Completion criteria:

- The helper is deliberately small.
- It does not attempt arbitrary Gymnasium-space inference.

Stop condition:

- If observation support starts becoming a full Gymnasium observation encoder,
  stop.

### Stage 3.2: Convert Action Selection Inputs

#### Action 3.2.1

Implement:

```text
linearize_action_selection_input(...)
```

Required inputs:

```text
action_input: ActionSelectionInput
config: LinearizationConfig
registry: EncodingRegistry
```

Required behavior:

- `ABSENT` should fail or no-op explicitly when conversion is requested.
- `PRESENT_DISABLED` may validate but should not be required by object-native
  loops.
- `PRESENT_ENABLED` returns `LinearizedActionSelectionInput`.
- Use `action_input.current_base_state`.
- Use `action_input.runtime_snapshot.current_position_at_every_tier`.
- Use `action_input.runtime_snapshot.active_control_tier`.
- Use `action_input.stage_context`.
- Use `action_input.fiber_departure`.
- Use `action_input.diagnostics["fiber_action_vocabulary"]` as the first-scope
  action-vocabulary sidecar when present.

Completion criteria:

- Fixed discrete masks are padded or validated against `max_action_count`.
- Missing masks are represented as all-true masks when an action count can be
  inferred.
- Ragged action vocabulary stays in metadata sidecars.
- Lift candidates are not tensorized.

Stop condition:

- If conversion needs to reach into private `FiberConditionedStage` fields,
  stop. The stage already publishes `fiber_action_vocabulary` through
  diagnostics.

#### Action 3.2.2

Implement mask normalization.

Required behavior:

- Input `tuple[bool, ...] | None`.
- If `max_action_count` is set, output exactly that length.
- If input mask is shorter than `max_action_count`, pad with `False`.
- If input mask is longer than `max_action_count`, fail in strict mode.
- If no mask is present and action count can be inferred, output all `True`.
- If no mask is present and action count cannot be inferred, output empty tuple
  in non-strict mode and fail in strict mode.

Completion criteria:

- Boolean masks remain the semantic source of truth.
- Additive logits masks are not introduced in `linearization.py`.

### Stage 3.3: Define And Convert Linearized Transitions

#### Action 3.3.1

Implement `LinearizedTrainingTransition` as a frozen `slots=True` dataclass.

Required fields:

```text
source: LinearizedActionSelectionInput
target: LinearizedActionSelectionInput
chosen_action: int
reward: float
terminated: bool
truncated: bool
bootstrap_allowed: bool
bootstrap_reason_id: int | None
metadata: Mapping[str, object]
```

Completion criteria:

- The record is backend-independent.
- `chosen_action` is an integer index in first scope.
- Non-integer chosen actions fail in strict mode unless they can be resolved
  through the action vocabulary sidecar.

#### Action 3.3.2

Implement:

```text
linearize_training_transition(...)
```

Required inputs:

```text
transition: TrainingTransition
config: LinearizationConfig
registry: EncodingRegistry
```

Required behavior:

- Convert source and target inputs through `linearize_action_selection_input`.
- Preserve `bootstrap_allowed`.
- Encode or sidecar `bootstrap_reason`.
- Preserve diagnostics only when `include_diagnostics=True`.
- Do not persist records by default.

Completion criteria:

- Transitions from `FiberConditionedStage.step(...)` can be linearized.
- Basic tabular/reference-loop transitions can be linearized when action choices
  are integer discrete actions.

## Phase 4: Implement Report Construction And Timing Hooks

### Stage 4.1: Build Reports From Config And Registry

#### Action 4.1.1

Implement:

```text
build_linearization_report(...)
```

Required inputs:

```text
config: LinearizationConfig
registry: EncodingRegistry | None = None
tower: PartitionTower | None = None
conversion_count: int = 0
conversion_elapsed_seconds: float = 0.0
debug_record_exported: bool = False
```

Required behavior:

- Populate backend availability.
- Populate derived benchmark label.
- Populate registry id when available.
- Populate tower fingerprint when available.
- Populate schema fingerprint when available or leave `None` explicitly.

Completion criteria:

- `big_boy_benchmarking` can consume the report as an artifact fragment.
- The report distinguishes absent, disabled, enabled CPU, and enabled CUDA.

#### Action 4.1.2

Implement a small conversion timing helper or counter surface.

Rules:

- Timing occurs only around explicit conversion calls.
- No object-native runtime hot path is instrumented by default.
- Disabled mode may build a report without incrementing conversion count.

Completion criteria:

- A benchmark can record `conversion_count`.
- A benchmark can record `conversion_elapsed_seconds`.
- Object-native loops do not pay hidden timing overhead.

### Stage 4.2: Add Debug Export Surface Without Default Persistence

#### Action 4.2.1

Implement JSON-safe debug export helpers for selected records.

Rules:

- Export is opt-in through config or explicit helper calls.
- Exported data must be JSON-safe.
- Export helpers do not write files directly unless the caller supplies the
  target path or artifact writer.

Completion criteria:

- The package can debug sampled records.
- The package does not become a replay/logging system.

Stop condition:

- If export design starts requiring replay-buffer or checkpoint design, stop.

## Phase 5: Wire Public Exports Without Creating Hidden Runtime Coupling

### Stage 5.1: Update Training Exports

#### Action 5.1.1

Export backend-independent symbols from:

```text
src/state_collapser/training/__init__.py
```

Required exports:

```text
EncodingRegistry
LinearizationConfig
LinearizationReport
LinearizationState
LinearizedActionSelectionInput
LinearizedTrainingTransition
NumericBackend
TensorDeviceKind
build_linearization_report
linearize_action_selection_input
linearize_training_transition
```

Completion criteria:

- Public imports match the usage blueprint.
- Importing `state_collapser.training` still does not import Torch.

Stop condition:

- If exporting these symbols imports Torch, stop.

### Stage 5.2: Preserve Existing Object-Native API

#### Action 5.2.1

Run existing training tests before touching Torch code.

Required command:

```text
uv run pytest tests/training
```

Completion criteria:

- Existing training tests still pass.
- No existing object-native loop needs linearization config.

Stop condition:

- If object-native tests require tensorization setup, stop.

## Phase 6: Implement Torch Boundary Behind `ml`

### Stage 6.1: Create `training.torch`

#### Action 6.1.1

Create:

```text
src/state_collapser/training/torch.py
```

Required behavior:

- Torch-specific imports are local to this module.
- Missing Torch fails clearly and locally.
- The module does not import from external RL frameworks.

Completion criteria:

- `state_collapser.training.linearization` remains Torch-free.
- `state_collapser.training.torch` is the only first-scope Torch surface.

#### Action 6.1.2

Implement Torch availability and device helpers.

Required behavior:

- CPU device construction works when Torch is installed.
- CUDA selection verifies `torch.cuda.is_available()`.
- CUDA unavailable in CUDA mode produces a clear error or report state.

Completion criteria:

- No CUDA benchmark claim can be made without explicit report evidence.

### Stage 6.2: Define Torch Batch Data

#### Action 6.2.1

Implement `TorchDecisionBatch`.

Required fields:

```text
observations
tower_positions
tower_depth
active_tier
action_mask
stage_features
metadata
```

Required constructor:

```text
TorchDecisionBatch.from_linearized(...)
```

Completion criteria:

- The constructor accepts one or more `LinearizedActionSelectionInput` records.
- Boolean masks remain boolean tensors.
- Device placement follows `LinearizationConfig`.
- Metadata sidecars are preserved without tensorizing ragged data.

#### Action 6.2.2

Implement `TorchTransitionBatch`.

Required constructor:

```text
TorchTransitionBatch.from_linearized(...)
```

Required fields:

- source decision batch
- target decision batch
- actions
- rewards
- terminated
- truncated
- bootstrap_allowed
- metadata

Completion criteria:

- A batch of `LinearizedTrainingTransition` records can be converted.
- Actions are integer tensors.
- Rewards are floating tensors.
- Termination/bootstrap flags are boolean tensors.

### Stage 6.3: Add ActionDecision Conversion Helper

#### Action 6.3.1

Implement a minimal helper that converts model output into an
`ActionDecision`-compatible object.

Acceptable first helper:

```text
action_decision_from_logits(...)
```

Required behavior:

- Accepts logits for a single batch row or a clearly documented batch form.
- Applies boolean action masks correctly.
- Chooses an integer action index.
- Returns `ActionDecision(chosen_action=<int>, action_logits=..., diagnostics=...)`.

Completion criteria:

- The helper proves the boundary from Torch output back into package semantics.
- The helper is not described as an RL algorithm.

Stop condition:

- If this grows into sampling policy classes, exploration schedules, or PPO/DQN
  logic, stop.

## Phase 7: Add Tests For Backend-Independent Linearization

### Stage 7.1: Config, Report, And Import Tests

#### Action 7.1.1

Create or update:

```text
tests/training/test_linearization_config.py
```

Required test coverage:

- enum values are stable
- valid configs construct
- invalid configs fail
- configs serialize and deserialize
- derived benchmark labels are correct

Completion criteria:

- All orthogonal mode combinations used by the blueprints are tested.

#### Action 7.1.2

Create or update:

```text
tests/training/test_linearization_report.py
```

Required test coverage:

- reports serialize to JSON-safe dicts
- reports contain backend availability fields
- disabled mode reports enabled false
- enabled mode reports enabled true
- conversion counters are present

Completion criteria:

- `big_boy_benchmarking` artifact needs are test-visible.

#### Action 7.1.3

Create or update:

```text
tests/training/test_linearization_imports.py
```

Required test coverage:

- importing `state_collapser.training.linearization` does not import Torch
- importing `state_collapser.training` does not import Torch
- missing Torch produces only a local Torch-surface failure

Completion criteria:

- The dependency boundary is protected by tests.

### Stage 7.2: Encoding Registry Tests

#### Action 7.2.1

Create or update:

```text
tests/training/test_encoding_registry.py
```

Required test coverage:

- registry can be built from `PartitionTower`
- base state ids reuse tower registry ids
- edge/action ids reuse tower registry ids
- state cell ids encode tier and ordinal
- action cell ids encode tier and ordinal
- tier ids are stable
- registry summary serializes
- registry fingerprint is deterministic

Completion criteria:

- Shared tower encoding is covered before RL-specific conversion tests.

#### Action 7.2.2

Add HGraphML-facing encoding compatibility coverage.

Preferred location:

```text
tests/tower/partition/test_hgraphml_downstream_compatibility.py
```

or:

```text
tests/training/test_hgraphml_encoding_compatibility.py
```

Required test coverage:

- an encoding registry can be built from the same tower used by the existing
  HGraphML-shaped readout test
- node/cell/edge ids can be summarized without `ActionSelectionInput`
- the test imports no Torch
- the test constructs no `TrainingTransition`

Completion criteria:

- HGraphML compatibility is protected from day one.

Stop condition:

- If this test requires RL training objects, the encoding design is wrong.

### Stage 7.3: Linearized Record Tests

#### Action 7.3.1

Create or update:

```text
tests/training/test_linearized_action_selection_input.py
```

Required test coverage:

- scalar observations convert
- flat numeric observations convert
- unsupported observations fail in strict mode
- unsupported observations sidecar in non-strict mode
- current base state ids encode
- tower position ids encode
- active tier encodes
- stage/fiber context encodes
- fiber departure reason encodes
- masks normalize and pad
- oversized masks fail in strict mode

Completion criteria:

- Fixed discrete action support is real.

#### Action 7.3.2

Create or update:

```text
tests/training/test_linearized_training_transition.py
```

Required test coverage:

- source and target inputs convert
- integer chosen actions convert
- non-integer chosen actions fail in strict mode unless explicitly resolvable
- reward/termination/truncation/bootstrap fields preserve semantics
- diagnostics are included only when requested

Completion criteria:

- `TrainingTransition` tensorization boundary is covered.

## Phase 8: Add Torch Boundary Tests

### Stage 8.1: Torch Batch Tests

#### Action 8.1.1

Create or update:

```text
tests/training/test_torch_batches.py
```

Mark Torch-required tests with:

```text
@pytest.mark.requires_torch
```

Required test coverage:

- `TorchDecisionBatch.from_linearized(...)` builds CPU tensors
- action masks are boolean tensors
- tower positions are integer tensors with documented padding
- metadata sidecars are preserved
- `TorchTransitionBatch.from_linearized(...)` builds action/reward/done tensors

Completion criteria:

- Torch conversion is real but locally isolated.

#### Action 8.1.2

Add CUDA-mode tests that skip when CUDA is unavailable.

Required test coverage:

- CUDA config reports unavailable when CUDA is unavailable
- CUDA tensor creation only runs when CUDA is available
- no CUDA benchmark label is asserted without CUDA availability

Completion criteria:

- Device semantics are honest.

### Stage 8.2: Tiny Torch Smoke Model

#### Action 8.2.1

Create a tiny Torch smoke-model test under:

```text
tests/examples/
```

Acceptable file:

```text
tests/examples/test_torch_tensor_boundary_smoke_model.py
```

Required behavior:

- build a `LinearizedActionSelectionInput`
- build a `TorchDecisionBatch`
- pass batch through a tiny `torch.nn.Module`
- convert logits to `ActionDecision`
- confirm chosen action respects mask

Completion criteria:

- The test proves:

  ```text
  TorchDecisionBatch -> torch.nn.Module -> ActionDecision
  ```

- The model is local to the test.
- The model is not exported as package API.

Stop condition:

- If this becomes a package policy model, stop.

## Phase 9: Integrate With Existing Training And Fiber Surfaces

### Stage 9.1: Fiber-Conditioned Stage Compatibility

#### Action 9.1.1

Add a test that linearizes an input produced by `FiberConditionedStage.reset(...)`
or `FiberConditionedStage.current_input()`.

Preferred existing validation surface:

```text
tests/examples/test_plate_support_env_fiber_conditioned_stage.py
```

or a new test under:

```text
tests/training/
```

Required test coverage:

- `stage_context` survives linearization
- `fiber_action_vocabulary` is preserved as sidecar metadata
- `action_mask` is fixed/padded correctly
- `fine_tier` and `coarse_tier` encode

Completion criteria:

- The tower/fiber training spine can feed the tensor boundary.

#### Action 9.1.2

Add a test that linearizes a transition produced by
`FiberConditionedStage.step(...)`.

Required test coverage:

- `TrainingTransition.source_input` linearizes
- `TrainingTransition.target_input` linearizes
- `bootstrap_allowed` preserves semantics
- `fiber_departure` encodes if present
- non-ragged tensor fields are available
- ragged lift candidates remain sidecars

Completion criteria:

- Fiber-conditioned train/lift/freeze semantics survive conversion.

### Stage 9.2: Object-Native Loop Non-Regression

#### Action 9.2.1

Run existing reference-loop and learner tests.

Required command:

```text
uv run pytest tests/training/test_learners_and_reference_loops.py tests/training/test_collectors.py tests/training/test_fiber_conditioned_stage.py
```

Completion criteria:

- Existing loops still work without tensorization config.

Stop condition:

- If object-native loops need tensorization objects, the implementation violates
  the tiny hinge rule.

## Phase 10: Integrate Benchmark-Visible Reporting

### Stage 10.1: Make Report Fragments Easy To Consume

#### Action 10.1.1

Ensure `LinearizationConfig.to_dict()` and `LinearizationReport.to_dict()`
produce artifact-safe dictionaries.

Required behavior:

- strings for enum values
- no raw Python object reprs except intentionally named metadata fields
- no tensor objects
- no NumPy arrays
- no Torch tensors

Completion criteria:

- A benchmark harness can insert these dicts into JSON artifacts.

#### Action 10.1.2

Add tests that simulate `big_boy_benchmarking` mode labels.

Required cases:

- `ABSENT/NONE/NONE`
- `PRESENT_DISABLED/NUMPY/NONE`
- `PRESENT_DISABLED/TORCH/CPU`
- `PRESENT_ENABLED/TORCH/CPU`
- `PRESENT_ENABLED/TORCH/CUDA`

Completion criteria:

- The downstream benchmark labels are stable.
- Labels come from config/report, not call-site guessing.

### Stage 10.2: Preserve Disabled-Mode Directness

#### Action 10.2.1

Add a disabled-mode test proving report construction does not construct Torch
batches.

Required behavior:

- Build `LinearizationConfig(PRESENT_DISABLED, ...)`.
- Build `LinearizationReport`.
- Run an object-native learner action without calling conversion.
- Assert no `TorchDecisionBatch` is created.

Completion criteria:

- `tensor_available_disabled` measures boundary availability without hidden
  tensor overhead.

Stop condition:

- If disabled mode can only be tested by running conversion every step, stop.

## Phase 11: Documentation Implementation

### Stage 11.1: Add Engineer Usage Documentation

#### Action 11.1.1

Create:

```text
docs/usage/01_010_tensorization_boundary.md
```

Required sections:

- what tensorization is
- what tensorization is not
- object-native mode
- tensor-capable disabled mode
- tensor-enabled CPU mode
- tensor-enabled CUDA mode
- action masks
- tower position ids
- fiber-conditioned stage usage
- HGraphML compatibility boundary
- tiny Torch smoke model
- artifact/report fields

Completion criteria:

- The doc lets an engineer use the implemented boundary without reading design
  documents.
- The doc states that `state_collapser` is not RLlib, SB3, or TorchRL.

#### Action 11.1.2

Update routing docs to mention the new usage document.

Candidate files:

```text
README.md
docs/public_api.md
docs/package_usage.md
```

Required behavior:

- Keep root docs concise.
- Route engineers to the tensorization usage doc.
- Do not overclaim mature RL framework status.

Completion criteria:

- Root documentation accurately routes tensor-curious engineers.

### Stage 11.2: Update Design And Continuity Hooks

#### Action 11.2.1

Update the running implementation log with final implementation notes.

Required content:

- exact files created
- exact tests added
- exact tests run
- whether NumPy remained optional
- whether Torch remained behind `ml`
- HGraphML compatibility result
- any deviations from this gameplan

Completion criteria:

- Future engineers can reconstruct what happened.

## Phase 12: Full Validation And Completion Review

### Stage 12.1: Focused Validation

#### Action 12.1.1

Run focused tests:

```text
uv run pytest tests/training -k "linearization or torch"
```

Completion criteria:

- Focused linearization tests pass.

Stop condition:

- Any unexpected failure requires full-stop diagnosis.

#### Action 12.1.2

Run HGraphML-facing compatibility tests:

```text
uv run pytest tests/tower/partition/test_hgraphml_downstream_compatibility.py
```

Completion criteria:

- Existing downstream-readout assumptions still pass.
- New encoding compatibility assertions pass.

Stop condition:

- Any HGraphML-facing break requires Project Owner review.

### Stage 12.2: Training And Example Validation

#### Action 12.2.1

Run training and selected example tests:

```text
uv run pytest tests/training tests/examples/test_plate_support_env_fiber_conditioned_stage.py tests/examples/test_training_semantics_shared.py
```

Completion criteria:

- Object-native training surfaces still pass.
- Fiber-conditioned stage surfaces still pass.

#### Action 12.2.2

Run Torch tests if Torch is installed:

```text
uv run pytest -m requires_torch tests/training tests/examples/test_torch_tensor_boundary_smoke_model.py
```

Completion criteria:

- Torch boundary tests pass in an `ml` environment.
- If Torch is not installed, the implementation log records that these tests
  were not run and why.

### Stage 12.3: Static And Full Validation

#### Action 12.3.1

Run static checks:

```text
uv run ruff check
uv run mypy
```

Completion criteria:

- Ruff passes.
- Mypy passes.

#### Action 12.3.2

Run full tests:

```text
uv run pytest
```

Completion criteria:

- Full test suite passes.

Stop condition:

- Any unexpected failure requires diagnosis before completion can be claimed.

### Stage 12.4: Final Semantic Completion Check

#### Action 12.4.1

Verify the implementation against the two blueprint success criteria.

Required answers:

- Where do backend-independent records live?
- Where does Torch conversion live?
- How does a benchmark distinguish absent, disabled, CPU-enabled, and CUDA
  enabled modes?
- How does the disabled path avoid hot-path overhead?
- How are masks represented?
- How are tower positions encoded?
- How does HGraphML remain compatible?
- What is persisted?
- What is explicitly deferred?
- How does an engineer keep using the object-native loop?
- How does an engineer enable report-only tensor-capable mode?
- How does an engineer produce a CPU Torch batch?
- How does an engineer know CUDA was actually used?
- What objects remain semantic source of truth?
- What data becomes tensorized?
- What remains metadata sidecar?
- How does this avoid reproducing RLlib or SB3?

Completion criteria:

- All answers are either implemented, documented, or explicitly deferred exactly
  as described by the blueprints.

#### Action 12.4.2

Record completion in the implementation log.

Required content:

- final git status
- final validation commands and outcomes
- known residual risks
- deferred work
- merge-readiness statement

Completion criteria:

- The implementation log is complete enough for a future continuity report.

## Final Merge-Readiness Criteria

The implementation is ready to merge only when all of the following are true.

- `state_collapser.training.linearization` exists and imports no Torch.
- `state_collapser.training.torch` exists and is the only Torch-specific first
  surface.
- `LinearizationConfig` and `LinearizationReport` serialize cleanly.
- Derived benchmark labels exist and are tested.
- Fixed discrete masks and action indices are tested.
- Tower position ids are tested.
- Fiber-conditioned stage inputs and transitions can be linearized.
- HGraphML-facing encoding compatibility is tested without RL-specific objects.
- Object-native loops remain direct.
- `PRESENT_DISABLED` does not construct Torch batches.
- Tiny Torch smoke model exists only in tests/examples.
- Usage documentation exists and routes engineers correctly.
- The implementation log records all test outcomes.
- No source claims mature RL-framework status.

## Known Deferred Work

The following work remains outside this implementation slice.

- full ragged tensor support
- replay buffer design
- checkpoint/resume
- vectorized rollout
- distributed rollout
- RL algorithm implementations
- package model families
- HGraphML tensorized graph-message-passing kernels
- external framework adapters
- full experiment/artifact contract beyond config/report fragments
- performance benchmarking in `big_boy_benchmarking`
