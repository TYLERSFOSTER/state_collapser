# Tensorization Engineer Usage Blueprint

Date: 2026-05-29

Status: blueprint, paired with
`01_001_tensorization_architecture_blueprint.md`

Source documents:

- `docs/design/tensorization/README.md`
- `docs/design/tensorization/design_conversation.md`
- `docs/design/tensorization/01_001_tensorization_architecture_blueprint.md`
- `docs/usage/01_003_training_surface_quickstart.md`
- `docs/usage/01_004_fiber_conditioned_training.md`
- `docs/usage/01_005_using_your_own_training_loop.md`
- `docs/usage/01_009_downstream_applications.md`

## Purpose

This blueprint describes how an engineer should use the first tensorization
surface once implemented.

It is paired with the architecture blueprint because usage pressure matters:
the design is only good if an engineer can opt into tensorization without
rewriting the package runtime, losing tower semantics, or paying hidden overhead
when tensorization is disabled.

## User-Facing Principle

The engineer should experience tensorization as:

```text
an optional conversion boundary near the learner
```

not as:

```text
a mandatory replacement for state_collapser runtime objects
```

The ordinary object-native loop remains valid:

```python
current_input = collector.reset_episode(seed=0)

for _ in range(max_steps):
    decision = learner.act(current_input)
    collected_step = collector.collect_step(current_input, decision)
    learner.observe(collected_step.transition)
    learner.update()
    current_input = collected_step.next_input
```

Tensorization adds an optional conversion step when the learner wants numeric
records or tensors.

## Expected Imports

Backend-independent linearization:

```python
from state_collapser.training.linearization import EncodingRegistry
from state_collapser.training.linearization import LinearizationConfig
from state_collapser.training.linearization import LinearizationState
from state_collapser.training.linearization import LinearizationReport
from state_collapser.training.linearization import NumericBackend
from state_collapser.training.linearization import TensorDeviceKind
```

Torch conversion, behind the `ml` extra:

```python
from state_collapser.training.torch import TorchDecisionBatch
from state_collapser.training.torch import TorchTransitionBatch
```

The exact function names are implementation details for the future gameplan,
but the usage shape should remain close to this.

## Install Expectations

Object-native control-flow use:

```bash
pip install -e .
```

RL/Gymnasium use with NumPy available:

```bash
pip install -e ".[rl]"
```

Torch tensor use:

```bash
pip install -e ".[ml]"
```

Development with all current extras:

```bash
pip install -e ".[dev,rl,ml]"
```

First-scope NumPy linearization should not require Torch. Torch conversion
should not be imported from core package paths.

## Mode 1: Existing Object-Native Runtime

This is the current direct path:

```text
LinearizationState.ABSENT
NumericBackend.NONE
TensorDeviceKind.NONE
```

Usage:

```python
current_input = collector.reset_episode(seed=0)
decision = learner.act(current_input)
step = collector.collect_step(current_input, decision)
```

Expected behavior:

- no linearization config required
- no tensor registry required
- no tensor batch created
- no Torch import
- no extra runtime dispatch

Benchmark label:

```text
none_control_flow
```

This mode is the pre-linearization baseline.

## Mode 2: Tensor-Capable But Disabled

This is the first important benchmark distinction:

```text
LinearizationState.PRESENT_DISABLED
NumericBackend.NUMPY
TensorDeviceKind.NONE
```

or:

```text
LinearizationState.PRESENT_DISABLED
NumericBackend.TORCH
TensorDeviceKind.CPU
```

depending on how the implementation chooses to validate backend availability.

Usage shape:

```python
config = LinearizationConfig(
    linearization_state=LinearizationState.PRESENT_DISABLED,
    numeric_backend=NumericBackend.NUMPY,
    device_kind=TensorDeviceKind.NONE,
    max_action_count=env.action_count,
    strict=True,
)

registry = EncodingRegistry.from_tower(runtime_snapshot.partition_tower_view)
report = config.build_report(registry=registry)

decision = learner.act(current_input)
```

Key point:

```text
the object-native learner path remains direct
```

The disabled mode should validate/report the tensor-capable boundary, but it
should not force every runtime step through tensor construction.

Benchmark label:

```text
tensor_available_disabled
```

This is the tiny-hinge mode.

## Mode 3: Tensor Enabled On CPU

This is the first real tensor path:

```text
LinearizationState.PRESENT_ENABLED
NumericBackend.TORCH
TensorDeviceKind.CPU
```

Usage shape:

```python
config = LinearizationConfig(
    linearization_state=LinearizationState.PRESENT_ENABLED,
    numeric_backend=NumericBackend.TORCH,
    device_kind=TensorDeviceKind.CPU,
    max_action_count=env.action_count,
    strict=True,
)

registry = EncodingRegistry.from_tower(runtime_snapshot.partition_tower_view)
linearized_input = linearize_action_selection_input(
    current_input,
    config=config,
    registry=registry,
)
batch = TorchDecisionBatch.from_linearized([linearized_input], config=config)
model_output = model(batch)
decision = action_decision_from_model_output(model_output, batch)
```

The exact helper names may change. The usage rule should not:

```text
semantic input -> linearized record -> Torch batch -> model -> ActionDecision
```

Benchmark label:

```text
tensor_enabled_cpu
```

## Mode 4: Tensor Enabled On CUDA

CUDA mode is explicit:

```text
LinearizationState.PRESENT_ENABLED
NumericBackend.TORCH
TensorDeviceKind.CUDA
```

Usage shape:

```python
config = LinearizationConfig(
    linearization_state=LinearizationState.PRESENT_ENABLED,
    numeric_backend=NumericBackend.TORCH,
    device_kind=TensorDeviceKind.CUDA,
    max_action_count=env.action_count,
    strict=True,
)
```

Expected behavior:

- report records CUDA availability
- tensors are placed on CUDA only if available
- fallback behavior is explicit
- benchmark claims are not made unless report shows CUDA mode

Benchmark label:

```text
tensor_enabled_cuda
```

## Action Masks

For engineers, action masks should stay conceptually simple.

Semantic source of truth:

```python
ActionSelectionInput.action_mask
```

First tensorized representation:

```text
boolean mask over fixed/padded action slots
```

Model code can derive:

```text
additive logits mask
```

from the boolean mask.

Usage expectation:

```python
if batch.action_mask is not None:
    logits = logits.masked_fill(~batch.action_mask, float("-inf"))
```

The package should not hide mask semantics inside arbitrary diagnostics.

## Tower Position Encoding

Engineers should not pass raw Python object hashes to neural models.

Expected usage:

```python
registry = EncodingRegistry.from_tower(partition_tower)
linearized = linearize_action_selection_input(
    current_input,
    config=config,
    registry=registry,
)
```

The registry should convert:

- current base state
- tower position key
- state-cell ids
- action-cell ids
- stage/fiber ids

into stable numeric ids.

If an object cannot be encoded in `strict=True` mode, the conversion should fail
early with a clear error.

## Fiber-Conditioned Stage Usage

Fiber-conditioned training remains the primary package-native semantic story.

Object-native stage loop:

```python
current_input = stage.reset(seed=0)

for _ in range(max_steps):
    decision = learner.act(current_input)
    transition = stage.step(decision)
    learner.observe(transition)
    learner.update()
    current_input = transition.target_input
```

Tensor-enabled stage loop:

```python
current_input = stage.reset(seed=0)

for _ in range(max_steps):
    linearized = linearize_action_selection_input(
        current_input,
        config=config,
        registry=registry,
    )
    batch = TorchDecisionBatch.from_linearized([linearized], config=config)
    model_output = model(batch)
    decision = action_decision_from_model_output(model_output, batch)
    transition = stage.step(decision)
    current_input = transition.target_input
```

The stage still owns:

- fiber-derived masks
- lift candidate resolution
- departure diagnostics
- projected coarse step
- frozen behavior context

The tensor layer converts those semantics. It does not replace them.

## Fixed Discrete First Scope

First engineer-facing tensorization should support fixed discrete action spaces
well.

Supported first:

- integer action indices
- fixed action count
- fixed/padded action mask
- source/target transition tensors
- tower position tensors padded by `max_tower_depth`

Preserved as sidecars first:

- variable action-cell vocabularies
- ragged lift candidate lists
- representative edges
- variable fiber contents

Engineers should not expect full ragged tensor support in the first release of
this track.

## Linearized Record Persistence

Default behavior:

```text
do not persist every linearized record
```

Persist:

- `LinearizationConfig`
- `LinearizationReport`
- registry summary or fingerprint
- benchmark label derived from mode fields

Optional debug behavior:

- export selected linearized records
- export selected tensor batches
- include debug files in benchmark artifacts when explicitly requested

Reason:

Persisting every record would turn tensorization into replay/logging design too
early.

## HGraphML Usage Boundary

HGraphML compatibility matters in first scope.

However, HGraphML should not be forced into RL training objects.

Correct relation:

```text
shared EncodingRegistry / tower-cell ids
    can serve both RL and HGraphML later

RL-specific ActionSelectionInput tensorization
    serves counterpoint/training first
```

Usage implications:

- HGraphML should not need `ActionSelectionInput`.
- HGraphML should not need `TrainingTransition`.
- HGraphML should not need Torch because `state_collapser` added Torch support.
- HGraphML-facing partition tower readout assumptions must keep working.

If HGraphML later wants tensorized graph message passing, it should be able to
reuse the shared tower/cell/action/fiber encoding concepts without depending on
RL-specific learner inputs.

## Tiny Torch Smoke Model

The first Torch model should be a test/example object only.

It should prove:

```text
TorchDecisionBatch -> torch.nn.Module -> ActionDecision-compatible output
```

It should not be documented as:

```text
the official state_collapser policy model
```

User-facing language should say:

> This model exists only to test and demonstrate the tensor boundary.

## What Engineers Should Import From Existing Tools

Engineers should use existing tools for:

- neural network modules
- optimizers
- autograd
- standard RL algorithms
- serious replay buffers
- distributed rollout
- experiment dashboards
- hyperparameter tuning

`state_collapser` provides the package-semantic conversion boundary. It does not
try to replace those tools.

## Minimal Engineer Story For Big Boy Benchmarking

`big_boy_benchmarking` should eventually be able to record:

```python
report = LinearizationReport(...)
artifact["linearization"] = report.to_dict()
artifact["benchmark_mode"] = report.derived_benchmark_label
```

Then benchmark conditions can distinguish:

```text
none_control_flow
tensor_available_disabled
tensor_enabled_cpu
tensor_enabled_cuda
```

without guessing from code paths.

## Documentation Requirements

When implemented, engineer docs should explain:

- why object-native mode still exists
- how to install `rl` and `ml` extras
- what `PRESENT_DISABLED` means
- how to create or attach an `EncodingRegistry`
- how masks are represented
- how tower position ids are produced
- how to run the tiny Torch smoke model
- how to inspect `LinearizationReport`
- what is not persisted by default
- why HGraphML compatibility is protected

## Usage Blueprint Success Criteria

The usage story is acceptable when an engineer can answer:

- How do I keep using the object-native loop?
- How do I enable report-only tensor-capable mode?
- How do I produce a CPU Torch batch?
- How do I know CUDA was actually used?
- What objects remain semantic source of truth?
- What data becomes tensorized?
- What remains metadata sidecar?
- What does this not implement?
- How does this avoid reproducing RLlib or SB3?

This blueprint answers those questions at design level. The implementation
gameplan should later turn them into examples, API notes, and tests.
