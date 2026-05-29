# Tensorization Architecture Blueprint

Date: 2026-05-29

Status: blueprint, not implementation gameplan

Source documents:

- `docs/design/tensorization/README.md`
- `docs/design/tensorization/design_conversation.md`
- `docs/design/model_train_surfaces/01_005_big_boy_benchmarking_tensorization_alignment_note.md`
- `docs/design/RL_framework_maturity/01_001_rl_framework_maturity_and_tower_training_spine_discussion.md`
- `docs/design/RL_framework_maturity/01_002_fiber_conditioned_training_spine_blueprint.md`
- `docs/usage/01_003_training_surface_quickstart.md`
- `docs/usage/01_004_fiber_conditioned_training.md`
- `docs/usage/01_005_using_your_own_training_loop.md`
- `docs/usage/01_009_downstream_applications.md`
- `docs/public_api.md`

## Purpose

This blueprint defines the first tensor-capable architecture target for
`state_collapser`.

The immediate need comes from `big_boy_benchmarking`: serious downstream
counterpoint evaluation needs to distinguish:

```text
pre-linearization control-flow behavior
tensor-capable architecture with tensor path disabled
tensor-capable architecture with tensor path enabled
```

The deeper architectural need is to make package-native tower/fiber/training
objects numerically legible without turning `state_collapser` into RLlib,
Stable-Baselines3, TorchRL, or a new neural RL framework.

## One-Sentence Target

Tensorization should be a tiny, explicit semantic-to-numeric boundary at the
learner/benchmark edge, not a mandatory new runtime spine.

## Central Constraint: The Tiny Hinge Rule

The Project Owner's central concern is that a switchable tensorization layer may
become a heavy hinge bolted through the whole machine.

That failure mode would look like:

```text
object input
    -> heavy linearization registry
        -> backend dispatcher
            -> disabled tensor adapter
                -> object learner
```

This blueprint forbids that shape.

The correct shape is:

```text
runtime/tower semantics stay sparse and object-native
model-facing boundary gets optional tensor-capable adapters
benchmark artifacts record which boundary was active
```

The object-native path must remain direct. Tensorization is called explicitly by
a learner, adapter, benchmark harness, or conversion boundary.

## Non-Goals

First-pass tensorization does not implement:

- PPO, DQN, SAC, A2C, or other algorithm families
- a package-owned `.learn(...)` framework
- distributed rollout
- multi-GPU training
- full replay-buffer infrastructure
- production checkpoint/resume
- external RLlib, SB3, TorchRL, or Tianshou adapters
- automatic observation inference for arbitrary Gymnasium spaces
- full ragged tensor support for every tower/fiber shape
- a top-level `state_collapser.ml` package

## Package Namespace

First-scope tensorization should live close to the existing training surfaces.

### Backend-Independent Namespace

Use:

```text
src/state_collapser/training/linearization.py
```

for:

- backend-independent configuration
- backend-independent reports
- encoding registries
- linearized numeric records
- NumPy-facing numeric arrays when NumPy is available
- manifest fragments
- optional debug export structures

This module must not import Torch at module import time.

### Torch Namespace

Use:

```text
src/state_collapser/training/torch.py
```

for:

- Torch tensor batches
- Torch device helpers
- Torch dtype helpers
- conversion from backend-independent records to Torch tensors
- tiny Torch smoke-test model helpers if needed

This module is behind the `ml` extra. If Torch is missing, importing or using
Torch-specific functions should fail clearly and locally.

### Namespaces Not Used In First Scope

Do not create:

```text
src/state_collapser/ml/
```

yet. A top-level `ml` package may become appropriate after there are multiple
model families, multiple backends, or stable public ML-facing APIs. First scope
does not need that.

## Backend Mode Vocabulary

Use orthogonal enum-like fields. Do not collapse all state into one overloaded
mode string.

### LinearizationState

```text
ABSENT
PRESENT_DISABLED
PRESENT_ENABLED
```

Meanings:

- `ABSENT`: no tensor-capable boundary is present; this is the current
  pre-linearization control-flow baseline.
- `PRESENT_DISABLED`: linearization config, validation, and report surfaces
  exist, but tensor conversion is intentionally not used for the learner path.
- `PRESENT_ENABLED`: linearization is active and numeric/tensor records are
  produced for the learner or benchmark path.

### NumericBackend

```text
NONE
NUMPY
TORCH
```

Meanings:

- `NONE`: no numeric backend is used.
- `NUMPY`: backend-independent numeric records may use NumPy arrays.
- `TORCH`: Torch tensor conversion is used.

### TensorDeviceKind

```text
NONE
CPU
CUDA
```

Meanings:

- `NONE`: no tensor device applies.
- `CPU`: tensor path uses CPU tensors.
- `CUDA`: tensor path uses CUDA tensors.

### Derived Benchmark Labels

Benchmark tooling may derive human-readable labels such as:

```text
none_control_flow
tensor_available_disabled
tensor_enabled_cpu
tensor_enabled_cuda
```

These labels are not the source of truth. They are derived from
`LinearizationState`, `NumericBackend`, and `TensorDeviceKind`.

## Dependency Posture

The package should preserve its current dependency layering.

Current `pyproject.toml` posture:

- core dependency set remains light
- `rl` extra includes `gymnasium` and `numpy`
- `ml` extra includes `torch`

First-scope decision:

- NumPy appears in first scope as the backend-independent numeric layer.
- NumPy should not become a core dependency unless a deliberate dependency
  decision is made.
- First implementation should use optional import checks or propose a small
  future `numeric` extra.
- Torch is required only for `state_collapser.training.torch`.

## Architecture Layers

## Layer 0: Existing Semantic Objects

The existing package objects remain the semantic source of truth:

```text
ActionSelectionInput
ActionDecision
TrainingTransition
RuntimeSnapshot
LiveRuntimeView
FiberStageContext
FiberDeparture
FrozenQuotientBehavior
PathFiber
FiberConditionedStage
PartitionTower
```

Tensorization does not replace these objects.

## Layer 1: LinearizationConfig

`LinearizationConfig` records how semantic objects should be converted into
numeric records or tensors.

Required fields:

- `linearization_state: LinearizationState`
- `numeric_backend: NumericBackend`
- `device_kind: TensorDeviceKind`
- `dtype: str | None`
- `mask_dtype: str`
- `max_tower_depth: int | None`
- `max_action_count: int | None`
- `sequence_length: int | None`
- `include_diagnostics: bool`
- `encoder_registry_id: str | None`
- `strict: bool`

Rules:

- `ABSENT` must not require encoders.
- `PRESENT_DISABLED` may validate encoder availability and emit reports, but
  should not force tensor batch construction.
- `PRESENT_ENABLED` requires enough encoders to produce the requested numeric
  or tensor records.
- `TORCH` backend with `CUDA` device kind must report CUDA availability.

## Layer 2: EncodingRegistry

`EncodingRegistry` maps package semantic identities to stable numeric ids.

It must support shared tower concepts, not just RL observations.

Required responsibilities:

- assign or resolve ids for base states
- assign or resolve ids for primitive actions or edges
- assign or resolve ids for state cells
- assign or resolve ids for action cells
- assign or resolve ids for tower tiers
- assign or resolve ids for stage ids
- assign or resolve ids for fiber ids
- assign or resolve ids for frozen behavior ids
- expose a serializable vocabulary summary
- carry a registry id or fingerprint

HGraphML constraint:

The registry must be compatible with graph-message-passing use cases that need
node/edge/cell/fiber ids without using RL-specific `ActionSelectionInput` or
`TrainingTransition` objects.

Relationship to existing tower registries:

- reuse ids from `PartitionTower.registry` when possible
- do not duplicate tower registrations unnecessarily
- allow additional user/domain vocabularies for observations or model features

## Layer 3: Linearized Records

Backend-independent records live in `state_collapser.training.linearization`.

Required first records:

- `LinearizedActionSelectionInput`
- `LinearizedTrainingTransition`

Likely fields for `LinearizedActionSelectionInput`:

- `observation`: NumPy array or Python numeric tuple
- `current_base_state_id: int | None`
- `tower_position_ids: tuple[int, ...]`
- `tower_depth: int`
- `active_tier: int | None`
- `fine_tier: int | None`
- `coarse_tier: int | None`
- `action_mask: tuple[bool, ...]`
- `action_count: int`
- `stage_id: int | None`
- `fiber_id: int | None`
- `frozen_behavior_id: int | None`
- `frozen_behavior_version: int | str | None`
- `fiber_departure_reason_id: int | None`
- `metadata: Mapping[str, object]`

Likely fields for `LinearizedTrainingTransition`:

- `source: LinearizedActionSelectionInput`
- `target: LinearizedActionSelectionInput`
- `chosen_action: int`
- `reward: float`
- `terminated: bool`
- `truncated: bool`
- `bootstrap_allowed: bool`
- `bootstrap_reason_id: int | None`
- `metadata: Mapping[str, object]`

Rules:

- fixed discrete actions are first-scope required
- action masks use fixed or padded shape in first scope
- ragged fibers and lift candidates remain sidecar metadata
- arbitrary diagnostics are not tensorized by default

## Layer 4: Torch Tensor Batches

Torch-specific batches live in `state_collapser.training.torch`.

Required first batches:

- `TorchDecisionBatch`
- `TorchTransitionBatch`

Likely `TorchDecisionBatch` fields:

- `observations`
- `tower_positions`
- `tower_depth`
- `active_tier`
- `action_mask`
- `stage_features`
- `metadata`

Likely `TorchTransitionBatch` fields:

- source decision batch fields
- target decision batch fields
- `actions`
- `rewards`
- `terminated`
- `truncated`
- `bootstrap_allowed`
- metadata sidecars

Rules:

- boolean masks are the semantic source of truth
- model code may derive additive logits masks
- no CUDA claim without explicit device metadata
- no Torch import from core or backend-independent module

## Layer 5: LinearizationReport

`LinearizationReport` is the benchmark-visible manifest fragment.

Required fields:

- `linearization_state`
- `numeric_backend`
- `device_kind`
- `backend_available`
- `enabled`
- `dtype`
- `mask_dtype`
- `numpy_available`
- `numpy_version`
- `torch_available`
- `torch_version`
- `cuda_available`
- `encoder_registry_id`
- `schema_fingerprint`
- `tower_fingerprint`
- `max_tower_depth`
- `max_action_count`
- `conversion_count`
- `conversion_elapsed_seconds`
- `debug_record_exported`

Rules:

- persist reports in benchmark artifacts
- persist configs in benchmark artifacts
- do not persist every linearized record by default
- optional debug export of selected records or batches is allowed

## Fixed Discrete First Scope And Ragged Sidecars

First implementation must fully support:

- integer action indices
- fixed action counts
- source masks
- target/bootstrap masks
- fixed or padded mask tensors
- fixed or padded tower-position tensors

First implementation must preserve, but need not fully tensorize:

- variable action-cell vocabularies
- ragged lift candidates
- ragged fiber contents
- variable outgoing action-cell collections
- representative edge lists

Preserve these as metadata sidecars with stable ids. Full ragged tensorization
is a second phase.

## HGraphML Compatibility

HGraphML compatibility is first-pass important.

First-pass tensorization is motivated by RL/counterpoint benchmarking, but the
shared encoding layer must remain compatible with HGraphML's use of
`state_collapser` partition towers for graph message passing.

Required compatibility rules:

- do not break HGraphML-facing partition tower APIs
- do not force HGraphML into RL-specific `ActionSelectionInput` /
  `TrainingTransition` objects
- do not require HGraphML to install Torch
- make shared ids useful for graph nodes, graph edges, state cells, action
  cells, tiers, and fibers
- add explicit compatibility coverage or audit checks for HGraphML-facing
  tower readout assumptions

The Torch learner path may be RL-specific. The linearization vocabulary should
not be.

## Tiny Torch Smoke Model

First scope should include a tiny Torch smoke model in tests/examples only.

Purpose:

- prove a `TorchDecisionBatch` can pass through `torch.nn.Module`
- prove output can be converted into an `ActionDecision`-compatible result
- exercise masks and device metadata

Non-purpose:

- provide a package model family
- declare an official `state_collapser` policy network
- implement PPO/DQN/SAC

The model should be intentionally boring.

## Benchmark Modes

### `none_control_flow`

Derived from:

```text
LinearizationState.ABSENT
NumericBackend.NONE
TensorDeviceKind.NONE
```

Meaning:

- current object-native behavior
- no tensor-capable boundary present
- historical/pre-linearization baseline

### `tensor_available_disabled`

Derived from:

```text
LinearizationState.PRESENT_DISABLED
NumericBackend.NUMPY or NumericBackend.TORCH
TensorDeviceKind.NONE or TensorDeviceKind.CPU
```

Meaning:

- config exists
- report exists
- encoders can be validated
- tensor learner path is disabled
- object-native learner path remains direct

This is the "tiny hinge" benchmark arm.

### `tensor_enabled_cpu`

Derived from:

```text
LinearizationState.PRESENT_ENABLED
NumericBackend.TORCH
TensorDeviceKind.CPU
```

Meaning:

- Torch tensors are built
- CPU device is used
- model or smoke model consumes tensors

### `tensor_enabled_cuda`

Derived from:

```text
LinearizationState.PRESENT_ENABLED
NumericBackend.TORCH
TensorDeviceKind.CUDA
```

Meaning:

- CUDA is explicitly selected and available
- tensors and model are on CUDA
- report records CUDA availability and device metadata

No CUDA benchmark claim is allowed unless the report proves this mode.

## Validation Requirements

First blueprint implementation should include tests for:

- enum/value construction
- config serialization
- report serialization
- no Torch import from `training.linearization`
- clear local failure if `training.torch` is used without Torch
- action-mask conversion
- tower-position id conversion
- fixed discrete transition conversion
- `PRESENT_DISABLED` does not construct Torch tensors
- `PRESENT_ENABLED` constructs Torch tensors when Torch is available
- tiny Torch smoke model path
- HGraphML-facing tower readout compatibility is preserved

## Blueprint Success Criteria

The architecture is ready for implementation when it can answer:

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

This blueprint answers those questions. It should be followed by the paired
engineer-usage blueprint before implementation gameplanning.
