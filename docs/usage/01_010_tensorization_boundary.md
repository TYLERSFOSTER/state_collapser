# Tensorization Boundary

`state_collapser` keeps the runtime object-native by default.

Tensorization is an optional boundary near a learner, benchmark harness, or
model adapter. It converts package semantic objects into numeric records or
Torch tensors only when explicitly requested.

The intended shape is:

```text
ActionSelectionInput / TrainingTransition
    -> LinearizedActionSelectionInput / LinearizedTrainingTransition
        -> optional TorchDecisionBatch / TorchTransitionBatch
            -> external model or learner
```

The package does not provide PPO, DQN, SAC, replay buffers, vectorized rollout,
distributed rollout, or a package-owned `.learn(...)` framework here.

## Imports

Backend-independent surfaces:

```python
from state_collapser.training import EncodingRegistry
from state_collapser.training import LinearizationConfig
from state_collapser.training import LinearizationState
from state_collapser.training import NumericBackend
from state_collapser.training import TensorDeviceKind
from state_collapser.training import build_linearization_report
from state_collapser.training import linearize_action_selection_input
from state_collapser.training import linearize_training_transition
```

Torch-specific surfaces live behind the `ml` extra:

```python
from state_collapser.training.torch import TorchDecisionBatch
from state_collapser.training.torch import TorchTransitionBatch
from state_collapser.training.torch import action_decision_from_logits
```

## Object-Native Mode

The existing loop still works without tensorization:

```python
current_input = stage.reset(seed=0)

for _ in range(max_steps):
    decision = learner.act(current_input)
    transition = stage.step(decision)
    learner.observe(transition)
    learner.update()
    current_input = transition.target_input
```

This corresponds to:

```text
LinearizationState.ABSENT
NumericBackend.NONE
TensorDeviceKind.NONE
```

Benchmark label:

```text
none_control_flow
```

## Tensor-Capable But Disabled

Disabled mode records that a tensor-capable boundary exists, but the training
loop does not use it.

```python
config = LinearizationConfig(
    linearization_state=LinearizationState.PRESENT_DISABLED,
    numeric_backend=NumericBackend.NUMPY,
    device_kind=TensorDeviceKind.NONE,
    max_action_count=env_action_count,
)

registry = EncodingRegistry.from_tower(partition_tower)
report = build_linearization_report(config=config, registry=registry)
```

Benchmark label:

```text
tensor_available_disabled
```

This is useful for benchmarks that need to separate "old control-flow runtime"
from "tensor-capable architecture, not using tensors."

## Tensor Enabled On CPU

CPU Torch conversion is explicit:

```python
config = LinearizationConfig(
    linearization_state=LinearizationState.PRESENT_ENABLED,
    numeric_backend=NumericBackend.TORCH,
    device_kind=TensorDeviceKind.CPU,
    max_tower_depth=8,
    max_action_count=env_action_count,
)

registry = EncodingRegistry.from_tower(partition_tower)
linearized = linearize_action_selection_input(
    current_input,
    config=config,
    registry=registry,
)
batch = TorchDecisionBatch.from_linearized([linearized], config=config)
```

Benchmark label:

```text
tensor_enabled_cpu
```

## Tensor Enabled On CUDA

CUDA mode is explicit:

```python
config = LinearizationConfig(
    linearization_state=LinearizationState.PRESENT_ENABLED,
    numeric_backend=NumericBackend.TORCH,
    device_kind=TensorDeviceKind.CUDA,
    max_tower_depth=8,
    max_action_count=env_action_count,
)
```

Torch conversion raises if CUDA is requested but unavailable. Benchmark claims
about CUDA should be based on `LinearizationReport.cuda_available`.

Benchmark label:

```text
tensor_enabled_cuda
```

## Masks

Semantic source of truth:

```python
ActionSelectionInput.action_mask
```

First tensorized representation:

```text
boolean mask over fixed or padded action slots
```

Model code can derive additive masks:

```python
logits = logits.masked_fill(~batch.action_mask, float("-inf"))
```

The package keeps boolean masks as the boundary contract.

## Tower Position IDs

Use an `EncodingRegistry` to turn tower/cell identities into numeric ids:

```python
registry = EncodingRegistry.from_tower(partition_tower)
```

The registry covers:

- base states
- base edges
- primitive action ids
- state cells
- action cells
- action collections
- tower tiers
- stage ids
- fiber ids
- frozen behavior ids
- fiber departure reasons

This vocabulary is shared infrastructure. It is not RL-only.

## Fiber-Conditioned Training

`FiberConditionedStage` remains the semantic owner of:

- fiber-derived action masks
- action-cell vocabularies
- lift candidates
- departure diagnostics
- projected coarse steps
- frozen behavior context

The tensor boundary converts those semantics. It does not replace the stage.

Ragged details such as lift candidates and variable action-cell vocabularies are
preserved as metadata sidecars in the first implementation. Full ragged tensor
support is deferred.

## HGraphML Boundary

HGraphML compatibility is protected at the shared tower-encoding layer.

HGraphML should be able to reuse ids for graph nodes, graph edges, state cells,
action cells, tiers, and fibers without depending on:

- `ActionSelectionInput`
- `TrainingTransition`
- Torch
- RL-specific training loops

The Torch learner path may be RL/counterpoint-oriented. The encoding vocabulary
is intentionally broader.

## Artifact Reporting

Persist configs and reports, not every converted record:

```python
artifact["linearization_config"] = config.to_dict()
artifact["linearization_report"] = report.to_dict()
artifact["benchmark_mode"] = report.benchmark_label
```

Debug export of selected records is opt-in. Tensorization is not a replay or
checkpoint system.
