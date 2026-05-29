# API Note: Tensorization Boundary

The tensorization boundary is a provisional engineer-facing surface. It is
useful and tested, but it is not yet a stable top-level public API.

The runtime remains object-native by default. Tensorization is invoked
explicitly by a learner, adapter, or benchmark harness.

## Backend-Independent Imports

```python
from state_collapser.training import EncodingRegistry
from state_collapser.training import LinearizationConfig
from state_collapser.training import LinearizationReport
from state_collapser.training import LinearizationState
from state_collapser.training import LinearizedActionSelectionInput
from state_collapser.training import LinearizedTrainingTransition
from state_collapser.training import NumericBackend
from state_collapser.training import TensorDeviceKind
from state_collapser.training import build_linearization_report
from state_collapser.training import linearize_action_selection_input
from state_collapser.training import linearize_training_transition
```

## Torch-Specific Imports

Torch conversion lives behind the `ml` extra:

```python
from state_collapser.training.torch import TorchDecisionBatch
from state_collapser.training.torch import TorchTransitionBatch
from state_collapser.training.torch import action_decision_from_logits
```

## Benchmark Labels

Benchmark labels derive from the orthogonal mode fields on
`LinearizationConfig`.

The current labels are:

- `none_control_flow`
- `tensor_available_disabled`
- `tensor_enabled_cpu`
- `tensor_enabled_cuda`

Use `LinearizationReport.to_dict()` when recording benchmark artifacts.

## Stability Expectation

These surfaces may still change while the package remains pre-alpha. Changes
should be deliberate because they affect:

- model-facing learners,
- benchmark mode accounting,
- HGraphML-facing shared tower encoding,
- future artifact and checkpoint manifests.

For workflow-level guidance, read
[tensorization boundary](../usage/01_010_tensorization_boundary.md).
