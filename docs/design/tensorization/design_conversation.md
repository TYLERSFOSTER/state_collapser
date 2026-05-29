# Tensorization Design Conversation

Date: 2026-05-29

Status: design conversation, not blueprint, not implementation gameplan

Primary trigger:

- `docs/design/model_train_surfaces/01_005_big_boy_benchmarking_tensorization_alignment_note.md`

Related repo context reviewed:

- `README.md`
- `CONTRIBUTING.md`
- `pyproject.toml`
- `docs/package_usage.md`
- `docs/public_api.md`
- `docs/usage/01_003_training_surface_quickstart.md`
- `docs/usage/01_004_fiber_conditioned_training.md`
- `docs/usage/01_005_using_your_own_training_loop.md`
- `docs/usage/01_009_downstream_applications.md`
- `docs/design/model_train_surfaces/`
- `docs/design/RL_framework_maturity/`
- `docs/code_review/synthetic_blow_review_kit/`
- `src/state_collapser/training/`
- `src/state_collapser/tower/`
- `src/state_collapser/adapters/gymnasium.py`
- `src/state_collapser/benchmarks/tower_runtime_bench.py`

## Purpose

This document starts the design conversation for tensorization in
`state_collapser`.

The immediate pressure comes from `big_boy_benchmarking`: serious downstream
counterpoint evaluation is intentionally paused until `state_collapser` can
represent tensor-capable disabled/enabled modes.

The deeper design question is:

> What is the minimum tensor-capable package architecture that lets
> `state_collapser` become serious about numeric ML workflows without becoming
> a bad clone of existing RL/ML frameworks?

The Project Owner's major concern is correct and should govern this track:

> We must be careful not to reproduce industrial tools that should instead be
> imported, wrapped, or adapted.

That concern is not secondary. It is the central constraint.

## Executive Summary

`state_collapser` currently owns a sparse graph/tower/control-flow
architecture. Its implemented training surfaces are Python-object surfaces:

```text
ActionSelectionInput
    -> ActionDecision
        -> TrainingTransition
            -> collector / learner / reference loop
```

The package does not yet own:

- tensor encoders
- device/dtype contracts
- batch contracts
- sequence contracts
- numeric action-mask contracts
- Torch model protocols
- replay/trajectory tensors
- checkpoint/resume payloads
- experiment manifests
- vectorized rollout surfaces

But tensorization should not mean:

```text
state_collapser becomes RLlib
state_collapser becomes Stable-Baselines3
state_collapser reimplements PyTorch
state_collapser owns PPO/SAC/DQN as product identity
state_collapser builds a giant .learn(...) framework
```

The right first target is narrower:

```text
structured package runtime object
    -> deterministic numeric encoding
        -> explicit backend/mode/device/dtype metadata
            -> optional tensor batch
                -> model/framework-owned learner
```

In mathematical language, this is an $\mathbb{R}$-linearization boundary.

In engineering language, this is:

```text
canonical encoders + tensor batch contracts + backend metadata
```

## Current Repo Reality

### Package Posture

`pyproject.toml` declares:

- core dependency: currently light, no mandatory NumPy/Torch
- `rl` extra: `gymnasium`, `numpy`
- `ml` extra: `torch`

So the repo already has the right dependency posture:

```text
core package should stay light
RL environment dependencies live behind rl extra
Torch/tensor dependencies live behind ml extra
```

This should be preserved.

### Training Surfaces Already Implemented

The core current training objects are:

- `ActionSelectionInput`
- `ActionDecision`
- `TrainingTransition`
- `StepCollector`
- `EpisodeCollector`
- `TabularQLearner`
- `FiberConditionedStage`
- `PathFiber`
- `FrozenQuotientBehavior`
- mask helpers
- continuation/bootstrap helpers
- runtime snapshot summaries

These are intentionally object-level surfaces. They carry Python objects,
runtime snapshots, tower-position keys, diagnostics, stage context, and fiber
departure payloads.

That is good. Tensorization should not erase this layer.

The current design rule from package docs remains:

```text
The engineer owns the loop.
The package owns the semantic handoff objects.
```

Tensorization should extend that rule:

```text
The engineer or external framework owns the learner.
The package owns deterministic conversion from semantic objects to numeric
records.
```

### Fiber-Conditioned Training Already Exists

The current chain is:

```text
PartitionTower
    -> FrozenQuotientBehavior
        -> PathFiber
            -> FiberConditionedStage
                -> ActionSelectionInput / TrainingTransition
```

This is the package-specific semantic spine.

Tensorization must preserve:

- active tier
- fine tier
- coarse tier
- frozen behavior id/version
- fiber id
- action-cell vocabulary
- action mask
- lift candidates / realized lift
- fiber departure diagnostics
- bootstrap semantics
- runtime snapshot metadata

Ordinary RL frameworks do not know what these mean. Therefore these fields
cannot simply be hidden inside an opaque observation tensor with no package-side
manifest.

### Current Benchmarking

The package has a lightweight benchmark surface:

- `state_collapser.benchmarks.tower_runtime_bench`

It can record:

- steps
- elapsed time
- operations per second
- discovered state count
- discovered edge count
- tower depth
- readout requested
- morphism requested

This is useful smoke benchmarking. It is not yet a serious tensorization
benchmark and does not expose backend/mode/device metadata.

### Current Public API Policy

`docs/public_api.md` says that the only stable top-level public API is:

- `state_collapser.__version__`

Everything else is provisional unless explicitly promoted.

This matters because tensorization can begin as provisional under a documented
submodule, probably not exported at top-level yet.

## Big Boy Benchmarking Requirement

The downstream benchmark needs to distinguish:

```text
1. pre-linearization / current control-flow state_collapser
2. tensor-capable state_collapser with tensor path present but disabled
3. tensor-capable state_collapser with tensor path enabled
```

The alignment note proposes machine-readable states such as:

```text
numeric_backend = none_control_flow
numeric_backend = tensor_available_disabled
numeric_backend = tensor_enabled_cpu
numeric_backend = tensor_enabled_cuda
```

or:

```text
linearization_state = absent
linearization_state = present_disabled
linearization_state = present_enabled
```

The exact names are unsettled, but the semantic distinction is known and should
be preserved.

The important benchmark insight is subtle:

```text
pre-tensor state_collapser
```

is not the same benchmark condition as:

```text
tensor-capable state_collapser with tensorization disabled
```

Because adding a tensor-capable boundary can change:

- canonical encodings
- validation behavior
- state/action identity normalization
- mask representation
- batch boundaries
- timing overhead
- dependency metadata
- artifact metadata

The tensor-off arm of the serious benchmark must run through the tensor-capable
architecture boundary, even if no actual tensor learner is used.

#### PO Turn
My only concern here is that "pre-linearization / current control-flow state_collapser" creates code machinery that slows things down. The ideal would be that switching in/out the tensorization does not... ok this is waht I'm affraid of: that switch-out-able tensorization structure will be to heavy compared to a full retrofit. Does that make sense... like in physical mechanical terms, I like the idea of adding a dorr, but I'm really woried about the hinge that the door will need.

#### Codex Turn
Yes, that concern makes sense.  In the physical metaphor: adding a door is fine
only if the hinge does not become the heaviest part of the machine.

This means the tensorization design should avoid a switchable architecture that
puts every runtime path through a large abstraction layer just so tensors can be
enabled later.  The disabled path must not become:

```text
object input
    -> heavy linearization registry
        -> backend dispatcher
            -> disabled tensor adapter
                -> object learner
```

That would be a bad hinge.  It would slow down the current sparse/control-flow
architecture while providing no tensor benefit.

The better design is:

```text
semantic runtime path remains direct
optional linearization boundary is called only at explicit learner/benchmark
conversion points
```

So the first tensorization principle should be:

> Tensorization is an edge adapter, not a new spine through which all package
> runtime traffic must pass.

In practice, this means:

- `ActionSelectionInput`, `TrainingTransition`, `FiberConditionedStage`, and
  `PartitionTower` should remain normal Python semantic objects.
- The current object-level collector/learner path should remain able to run
  without constructing tensor batches.
- The tensorization layer should be invoked explicitly by a learner, adapter,
  benchmark harness, or conversion boundary.
- `tensor_available_disabled` should mean "the boundary exists and can report
  its configuration," not "all runtime objects are forced through tensor-ready
  wrappers."
- Backend mode checks should be cheap config checks, not polymorphic hot-path
  dispatch at every graph/tower operation.
- Stable ids and vocabularies should be reusable from existing tower registries
  where possible, not rebuilt through parallel tensor-specific registries unless
  needed.

The benchmark distinction still matters, but it should be implemented with
minimal hinge weight.  A good disabled tensor-capable mode might do only this:

```text
1. build or attach a LinearizationConfig
2. expose a LinearizationReport in artifacts
3. validate that required encoders/vocabularies are available
4. leave the actual object-level learner path untouched
```

Then enabled mode adds:

```text
5. call encode(...)
6. build tensor batch
7. send batch to Torch/model/device
```

This also changes how to think about "full retrofit" versus "switchable layer."
The right approach is not a giant switch woven through the runtime.  The right
approach is a retrofit at the data boundary:

```text
runtime/tower semantics stay sparse and object-native
model-facing boundary gets tensor-capable adapters
benchmark artifacts record which boundary was active
```

So yes: the door is good, but the hinge must be tiny, explicit, and located at
the learner/benchmark boundary rather than bolted through the whole tower
runtime.

## What We Know

### 1. Tensorization Is A Boundary, Not A Trainer

Tensorization is the package layer that converts:

```text
ActionSelectionInput / TrainingTransition / FiberConditionedStage context
```

into:

```text
numeric records / tensor batches / backend-visible metadata
```

It is not the layer that decides PPO versus DQN versus SAC.

### 2. The First Tensorization Layer Should Be Semantic-Preserving

The first tensorization layer should make the package's current semantic fields
numeric without losing their names.

Fields likely needing numeric treatment:

- observation
- current base state id
- tower position key
- active tier
- fine tier
- coarse tier
- action mask
- action vocabulary
- stage id
- fiber id
- frozen behavior id
- frozen behavior version
- bootstrap allowed
- terminated / truncated
- reward
- selected action
- fiber departure reason
- runtime/tower diagnostics selected for model use

Some of these should become tensors. Some should remain metadata sidecars.

### 3. Some Data Should Stay As Metadata

Not every object should be tensorized.

For example:

- arbitrary diagnostics
- raw `repr(...)` fields
- file paths
- schema names
- environment names
- git commit
- human-readable stage labels

These belong in manifests or sidecars, not model input tensors.

### 4. Action Masks Are First-Class

Action masks are already first-class in the training surfaces.

Tensorization must preserve:

- source action masks
- target/bootstrap action masks
- fiber-derived masks
- all-false mask cases
- absent mask cases

For a tensor learner, the mask needs a shape/dtype convention.

Open choices include:

- boolean tensor mask
- additive logits mask with `-inf`
- both, with boolean as canonical package representation

The first package-native convention should probably use boolean masks as the
semantic source of truth, then let model code derive logits masks.

### 5. Tower Position Requires A Vocabulary Or Encoding Registry

`tower_position_key` is currently a tuple of arbitrary objects or `None`.

Tensorization needs stable numeric IDs for:

- state cells
- action cells
- tower positions
- possibly base states and primitive actions

This implies an encoding registry or vocabulary object. It should be explicit,
versioned, and serializable enough for benchmark artifacts.

### 6. Opaque Observations Need Hooks

Gymnasium observations may be arrays, dictionaries, tuples, partial
observations, or domain objects.

The package should not guess all encodings automatically.

The existing Gymnasium wrapper already chooses explicit hooks:

- `state_key`
- `action_key`
- `edge_labeler`
- `action_mask`

Tensorization should follow the same philosophy:

```text
provide explicit encoder hooks before pretending inference is automatic
```

### 7. Torch Is The First ML Backend Target

The repo already has an `ml` extra with:

```text
torch>=2.4.0
```

Contributing docs name `torch` as the primary ML backend target.

Therefore first serious tensorization should be Torch-facing. But the core
semantic layer should not require Torch imports.

Likely split:

```text
state_collapser.training.linearization
    pure Python / optional NumPy-ish numeric records if needed

state_collapser.training.torch
    Torch tensor batches and device helpers behind ml extra
```

Names are provisional.

### 8. The Package Should Borrow Mature RL Engineering

The RL maturity docs already settle this:

`state_collapser` should borrow discipline from:

- RLlib
- Stable-Baselines3
- CleanRL
- Tianshou
- Acme
- TorchRL
- ordinary PyTorch practice

Borrow:

- shape/dtype/device discipline
- batch contracts
- vectorized rollout awareness
- replay/trajectory conventions
- checkpoint/resume discipline
- manifests
- train/eval split
- benchmark artifacts

Do not clone:

- distributed orchestration
- full algorithm catalog
- framework-owned `.learn(...)` as product identity
- advanced replay frameworks
- GPU/distributed data pipelines

## What We Do Not Know Yet

### 1. Where The First Tensorization API Should Live

Candidate namespaces:

```text
src/state_collapser/training/linearization.py
src/state_collapser/training/tensors.py
src/state_collapser/training/torch.py
src/state_collapser/ml/
src/state_collapser/adapters/torch.py
```

Open question:

> Should tensorization be considered part of `training`, part of `ml`, or an
> adapter layer?

Tentative answer:

- pure semantic encoding probably belongs under `training`
- backend-specific Torch conversion probably belongs under `training/torch.py`
  or `adapters/torch.py`
- avoid a top-level `ml` package until there is more than one backend or a
  real model-family surface

### 2. What The Canonical Backend Mode Names Should Be

The benchmark alignment note proposes:

```text
numeric_backend = none_control_flow
numeric_backend = tensor_available_disabled
numeric_backend = tensor_enabled_cpu
numeric_backend = tensor_enabled_cuda
```

This is clear, but possibly too backend-specific.

Alternative:

```text
linearization_state = absent | present_disabled | present_enabled
tensor_backend = none | torch
device = none | cpu | cuda
```

This separates:

- whether the linearization boundary exists
- whether tensors are enabled
- which backend/device is active

Open question:

> Should benchmark artifacts report one combined field or several orthogonal
> fields?

Likely answer:

> Use several orthogonal fields and allow downstream benchmark code to derive a
> combined label.

### 3. Whether NumPy Should Be Part Of The First Boundary

The `rl` extra already depends on NumPy, but core does not.

Possible choices:

1. core tensorization avoids NumPy and uses Python tuples/lists until Torch
   conversion;
2. numeric record layer uses NumPy arrays behind `rl` or new extra;
3. Torch layer converts directly from Python objects to tensors.

Risk:

- direct Python-to-Torch conversion can be slow if done in hot loops;
- introducing NumPy into core may unnecessarily harden a dependency;
- using both NumPy and Torch too early may create conversion churn.

Open question:

> Is first-scope tensorization about benchmark-visible correctness, or actual
> high-throughput training performance?

If the first scope is benchmark-visible correctness, Python records plus Torch
batch conversion may be enough.

### 4. What Counts As The Observation Tensor

`ActionSelectionInput.observation` is `object`.

In examples, observations can be small discrete states, dict-like values, or
domain-specific objects.

Open options:

- require user-provided `observation_encoder`
- provide default encoders only for simple scalars/tuples/dicts
- delegate observation tensorization entirely to external framework wrappers
- use Gymnasium spaces when present

Tentative answer:

> Require explicit encoders for serious use; provide tiny defaults only for
> tests and examples.

### 5. How To Encode Tower Position

Current `tower_position_key` may contain arbitrary state/cell objects.

Open options:

- hash to stable integer ids
- require registered tower cell IDs
- encode each tier as integer id with `-1` for missing
- encode variable tower depth with padding
- include separate `tower_depth` tensor

Important:

Tensorization should not rely on Python object hash stability across processes
or runs unless the vocabulary is explicitly persisted.

### 6. How To Represent Ragged Towers And Ragged Fibers

Different environments and even different moments in the same run may have:

- different tower depth
- different action vocabulary size
- different number of outgoing action cells
- different number of lift candidates
- different fiber sizes

Open options:

- pad to fixed max sizes per batch
- store ragged metadata sidecars
- use packed sequences
- use per-sample Python sidecars for first scope
- restrict first tensorized examples to fixed discrete action count

Tentative first scope:

> Use padded tensors for action masks and tower positions, plus metadata sidecars
> for ragged lift/fiber details.

### 7. Tensorize At Insertion Or At Sampling?

Replay design remains open.

Options:

- store Python `TrainingTransition` objects, tensorize when sampling;
- tensorize on insertion into a buffer;
- store both semantic object and numeric record;
- use external framework replay buffers and provide adapter conversion.

For first scope, the cleanest answer may be:

```text
semantic storage first, deterministic batch conversion second
```

This avoids prematurely owning a replay buffer.

But serious performance later may need tensorized storage.

### 8. What External Tool Should Be Wrapped First?

Candidates:

- PyTorch direct custom loop
- Stable-Baselines3-style Gymnasium stage adapter
- TorchRL/Tianshou-style batch/data collector
- RLlib adapter

Current likely order:

1. package-native Torch batch conversion and tiny reference loop
2. SB3-shaped stage adapter if needed
3. TorchRL/Tianshou-style integration if batch semantics fit well
4. RLlib later, because distributed/multi-policy integration is heavier

This order is not final.

### 9. How Much Replay/Checkpoint/Manifest Work Belongs In This Track

Tensorization touches artifacts because benchmark comparisons need metadata.

But full checkpoint/resume is larger than first tensorization.

Open question:

> Does the first tensorization blueprint include a minimal manifest only, or
> also first checkpoint payloads?

Tentative answer:

> Include benchmark-visible manifest fields immediately; defer full checkpoint
> resume unless the first Torch reference loop needs it.

### 10. HGraphML Impact

HGraphML is a downstream graph-ML consumer of partition towers.

Open question:

> Should tensorization be designed only for RL training surfaces, or also for
> graph-message-passing surfaces?

The answer is probably:

```text
first tensorize state_collapser's shared tower/fiber readout objects in a way
that can later serve both RL and graph ML
```

But the immediate benchmark blocker is RL/counterpoint.

## The Industrial-Tool Boundary

This is the most important design boundary.

### Things We Should Import Or Wrap

`state_collapser` should not reimplement:

- PyTorch tensors
- PyTorch modules
- optimizers
- autograd
- CUDA/device management beyond passing device choices through
- production replay buffers
- distributed rollout systems
- large vectorized env managers
- PPO/SAC/DQN algorithm suites
- experiment dashboards
- hyperparameter tuning systems
- multi-GPU orchestration

For these, the right relation is:

```text
use existing tool
wrap package semantics around it
record enough metadata so the package meaning survives
```

### Things We Probably Need To Own

`state_collapser` does need to own:

- what a tower position means
- what a state-cell/action-cell id means
- how a `PathFiber` becomes an action mask
- how frozen quotient behavior is represented
- how stage/fiber identity enters a learner input
- how lift/fiber diagnostics are preserved
- how package objects become stable numeric records
- how backend mode and linearization state are reported
- what benchmark metadata proves tensorization was disabled/enabled
- how an external learner's trained artifact is re-associated with tower/fiber
  semantics

These are not commodity RL framework concerns.

### Things We May Need As Small Reference Implementations

The package may need tiny, boring versions of:

- tensor batch dataclass
- Torch conversion helper
- simple Torch model protocol
- tiny reference model
- tiny reference loop
- minimal manifest writer
- small semantic-to-tensor tests

These should exist to:

- test package semantics
- show users the shape
- support `big_boy_benchmarking`
- define adapter contracts

They should not grow into:

- `state_collapser` PPO
- `state_collapser` distributed trainer
- `state_collapser` industrial replay service

## Possible First Architecture

This is not a blueprint yet, but the first architecture likely has these layers.

### Layer 0: Existing Semantic Objects

Already implemented:

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
PartitionTower
```

No change in meaning.

### Layer 1: Linearization Configuration

Possible object:

```python
LinearizationConfig
```

Fields might include:

- `linearization_state`
- `backend`
- `device`
- `dtype`
- `mask_dtype`
- `max_tower_depth`
- `max_action_count`
- `sequence_length`
- `include_diagnostics`
- `encoder_registry_id`
- `strict`

This object should be serializable into benchmark artifacts.

### Layer 2: Encoding Registry

Possible object:

```python
EncodingRegistry
```

Responsibilities:

- assign stable integer ids to state identities
- assign stable integer ids to primitive actions
- assign stable integer ids to state cells
- assign stable integer ids to action cells
- assign stable integer ids to fiber/stage/frozen behavior identities when
  needed
- export/import vocabulary metadata

Open issue:

Should this registry live outside the runtime, or be derived from
`PartitionTower.registry`?

Likely:

- derive known tower IDs from `PartitionTower.registry`;
- use a separate tensorization registry for extra user/domain encodings.

### Layer 3: Numeric Record

Possible object:

```python
LinearizedActionSelectionInput
```

This is backend-independent and might contain Python tuples/lists/ints/floats:

- observation vector
- tower position ids
- active tier id
- action mask tuple
- stage/fiber ids
- bootstrap flags
- sidecar metadata

This layer lets `tensor_available_disabled` still run through the same
conversion boundary without producing Torch tensors.

### Layer 4: Tensor Batch

Possible object:

```python
TensorDecisionBatch
```

Torch-backed fields:

- `observations`
- `tower_positions`
- `action_mask`
- `active_tier`
- `stage_features`
- `bootstrap_allowed`
- maybe `rewards`, `actions`, `terminated`, `truncated` for transition batches

Sidecars:

- original semantic ids
- stage/fiber metadata
- diagnostics chosen for logging
- registry references

### Layer 5: Backend Report / Manifest Fragment

Possible object:

```python
LinearizationReport
```

Fields:

- `linearization_state`
- `backend`
- `backend_available`
- `enabled`
- `device`
- `dtype`
- `torch_version` if applicable
- `cuda_available` if applicable
- `encoder_registry_id`
- `schema_fingerprint`
- `tower_fingerprint`
- timing counters

This is the minimum object `big_boy_benchmarking` needs to distinguish benchmark
conditions.

## Benchmark Modes To Support

The first design should support four benchmark-visible modes.

### Mode 1: `none_control_flow`

Current behavior.

No tensor-capable boundary is present.

Used only as historical/pre-linearization baseline.

### Mode 2: `tensor_available_disabled`

The encoding registry and linearization boundary exist.

The code still feeds object-level inputs to the current learner or tabular
reference path.

But benchmark artifacts can prove:

- tensorization config existed
- deterministic encoders existed
- validation passed
- tensor path was intentionally disabled
- conversion/timing hooks were available

This is the important tensor-off arm.

### Mode 3: `tensor_enabled_cpu`

Torch conversion runs on CPU.

This is the first enabled tensor mode.

No CUDA claims.

### Mode 4: `tensor_enabled_cuda`

Torch conversion and model execution use CUDA when available.

This should only be claimed after tests and benchmarks explicitly verify:

- device selection
- tensor movement
- timing hooks
- fallback behavior
- artifact metadata

CUDA should not be silently implied by installing Torch.

## What The First Blueprint Should Decide

The next design document should decide:

1. Namespace and package layout.
2. Exact backend/mode vocabulary.
3. The first semantic objects to linearize.
4. Whether to create a backend-independent numeric record.
5. Whether first Torch support is direct dependency under `ml` extra only.
6. How action masks are represented.
7. How tower positions are encoded.
8. How stage/fiber/frozen behavior metadata is encoded or sidecarred.
9. What manifest fragment is required for benchmarks.
10. What tiny reference tests/examples prove the mode distinction.

## What The First Blueprint Should Not Try To Decide

The next design document should not try to decide:

1. Full PPO/SAC/DQN integration.
2. Full replay-buffer architecture.
3. Full checkpoint/resume design.
4. Distributed training.
5. Multi-GPU.
6. Hyperparameter tuning.
7. Final public API stability.
8. All future external framework adapters.
9. Automatic observation encoding for arbitrary Gymnasium spaces.
10. ROS 2 tensor/dataflow integration.

Those matter, but they are not the resume gate for `big_boy_benchmarking`.

## Sharp Open Questions For PO

### 1. Is `tensor_available_disabled` a hard first-scope requirement?

The alignment note says yes. Confirm whether this must be implemented before
any serious counterpoint benchmark resumes.

Resolved: yes. The first implementation must distinguish pre-linearization
control-flow behavior from tensor-capable disabled behavior. However, the
disabled path must be a tiny hinge at the learner/benchmark boundary, not a
mandatory wrapper through the runtime hot path.

### 2. Is Torch definitely the first enabled backend?

The repo already has `torch` in the `ml` extra. Confirm whether first-scope
enabled tensor mode should be Torch-only.

Resolved: yes. Torch is the first enabled tensor backend. The backend-specific
Torch conversion should live behind the `ml` extra. Core package imports should
not require Torch.

### 3. Should first tensorization support only fixed discrete action spaces?

Supporting variable action-cell vocabularies and ragged fibers is harder. A
fixed-discrete first pass may be enough for counterpoint and current examples,
provided the design does not block ragged action-cell support later.

Resolved: first pass should fully support fixed discrete action spaces and
fixed/padded masks. Ragged tower/fiber details should be preserved as metadata
sidecars, not fully tensorized in first scope. Full ragged tensor support is a
second phase.

### 4. Should linearized records be persisted?

Options:

- no, only manifest/config is persisted;
- yes, records can be written for debug artifacts;
- only sampled batches are persisted in benchmark artifacts.

Resolved: not by default. First scope should persist `LinearizationConfig` and
`LinearizationReport` in artifacts/manifests, but should not persist every
linearized record. Optional debug export for sampled records or batches is
allowed.

### 5. Should HGraphML be included in first tensorization tests?

HGraphML may eventually benefit from tower/fiber tensorization, but the
immediate blocker is `big_boy_benchmarking`.

Resolved: HGraphML compatibility is first-pass important, but HGraphML does not
need full tensorization in first scope. First tensorization work must not break
HGraphML's current `state_collapser` dependency surface. If linearization
touches shared tower/cell/action encoding, that encoding should be reusable by
HGraphML later. Add explicit compatibility tests or audit checks for the
HGraphML-facing tower readout assumptions. Do not force HGraphML into
RL-specific `ActionSelectionInput` / `TrainingTransition` objects, and do not
require HGraphML to depend on Torch.

### 6. Should the first blueprint include a minimal Torch model?

A tiny model may be useful to prove the tensor path works, but it risks pulling
the design toward model-family work. The safer version is a tiny test model,
not a serious learner.

Resolved: yes, include a tiny Torch smoke model in tests/examples only. It
should prove that a tensor batch can pass through `torch.nn.Module` and produce
an `ActionDecision`-compatible output. It must not become a package model
family or "the state_collapser policy model."

### 7. Should this track own manifest work or only emit manifest fragments?

Benchmarking needs backend metadata. Full experiment manifests are larger.

Possible compromise:

```text
tensorization emits a LinearizationReport;
benchmark/artifact code embeds it into larger manifests later.
```

Resolved: first scope should own a manifest fragment, not a full experiment
artifact system. The tensorization layer emits `LinearizationReport`; benchmark
or experiment code embeds it into larger artifacts.

## Locked First Blueprint Decisions

The following decisions are now locked for the first blueprint pass.

### Module Namespace

Use:

```text
state_collapser.training.linearization
```

for backend-independent numeric records, configuration, reports, encoding
registries, and NumPy-facing linearization.

Use:

```text
state_collapser.training.torch
```

for Torch conversion and Torch tensor batches behind the `ml` extra.

Do not create a top-level `state_collapser.ml` package yet.

### Backend Mode Vocabulary

Use orthogonal enum-like fields instead of one overloaded mode string:

```text
LinearizationState = ABSENT | PRESENT_DISABLED | PRESENT_ENABLED
NumericBackend = NONE | NUMPY | TORCH
TensorDeviceKind = NONE | CPU | CUDA
```

Benchmark-facing labels such as:

```text
none_control_flow
tensor_available_disabled
tensor_enabled_cpu
tensor_enabled_cuda
```

should be derived from those fields.

### NumPy First Scope

NumPy appears in first scope as the backend-independent numeric layer, but not
as an unconditional core dependency unless that dependency shift is explicitly
accepted. Since NumPy already exists in the `rl` extra, the first blueprint
should either use optional import checks or propose a small future `numeric`
extra.

Torch is not required for basic linearization.

### Ragged Support

First implementation fully supports fixed discrete action spaces. It preserves
ragged fibers, variable action-cell vocabularies, and lift candidates as
metadata sidecars. Full ragged tensorization comes later.

### Persistence

Persist `LinearizationConfig` and `LinearizationReport`. Do not persist every
linearized record by default. Optional debug export of selected records/batches
is allowed.

### HGraphML Compatibility

First-pass tensorization is RL/counterpoint-driven, but shared tower encoding
must be HGraphML-compatible from day one.

The linearization vocabulary must not be designed as only RL
observation/action encoding. It must be able to represent shared tower concepts:

- state ids
- action/edge ids
- state-cell ids
- action-cell ids
- tower-tier ids
- fiber/readout ids

The Torch learner path may be RL-specific. The shared encoding layer should not
be.

### Tiny Torch Model

Include a toy Torch smoke model in tests/examples. It proves the tensor path,
not a package-owned neural model family.

## Working Conclusion

The tensorization track should be framed as:

```text
R-linearization and backend-mode reporting for package-native tower/fiber
training surfaces.
```

It should not be framed as:

```text
build a new RL framework
```

The first serious design goal is to make this distinction implementable:

```text
pre-linearization control-flow baseline
    !=
tensor-capable architecture with tensor path disabled
    !=
tensor-capable architecture with tensor path enabled
```

If we get that boundary right, `big_boy_benchmarking` can resume with honest
benchmark conditions, and `state_collapser` can move toward serious neural
training without losing its actual identity.
