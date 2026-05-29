# HGraphML Tensorization Follow-Up Bridge

Date: 2026-05-29

Status: upstream handoff note for HGraphML follow-up

## Purpose

This document explains what has to happen in `state_collapser` before HGraphML
can safely execute its downstream tensorization-compatibility follow-up.

The short version:

```text
HGraphML does not need full tensorization.
HGraphML needs a released state_collapser dependency that exposes
state_collapser.training.EncodingRegistry.
```

Until that is true, HGraphML can write a blueprint, but it cannot honestly claim
public compatibility with the new shared encoding surface.

## Current Reality

The HGraphML-side instruction document now lives in the HGraphML repo at:

```text
docs/design/tensorization/01_005_hgraphml_state_collapser_tensorization_followup_instructions.md
```

That document correctly says:

```text
HGraphML gets first-pass compatibility coverage,
not first-pass full tensorization.
```

The relevant upstream object is:

```python
from state_collapser.training import EncodingRegistry
```

The first-scope HGraphML-non-relevant objects are:

```python
ActionSelectionInput
TrainingTransition
TorchDecisionBatch
TorchTransitionBatch
ActionDecision
```

Those are RL and learner-boundary surfaces. HGraphML should not be forced
through them.

## The Actual Blocker

HGraphML currently depends on the public `state_collapser` `v0.6.0` tag.

The current HGraphML environment cannot import:

```python
from state_collapser.training import EncodingRegistry
```

from that installed dependency.

That means the public dependency pin HGraphML currently uses does not yet expose
the surface required by the compatibility pass.

The current `state_collapser` source tree does contain `EncodingRegistry`, but a
local source tree is not the same thing as a public installable dependency.

## Required Upstream Outcome

`state_collapser` must provide an installable commit, branch, or release tag
that exposes:

```python
from state_collapser.training import EncodingRegistry
from state_collapser.training import LinearizationConfig
from state_collapser.training import LinearizationState
from state_collapser.training import NumericBackend
from state_collapser.training import TensorDeviceKind
```

For HGraphML's immediate work, only `EncodingRegistry` is required.

The other names matter because they are part of the tensorization boundary
surface, but HGraphML should not use them in the first compatibility pass unless
a later blueprint explicitly says so.

## Required Sequence

### Step 1: Finish Or Confirm The Upstream Tensorization Boundary

Confirm that `state_collapser` has the tensorization boundary source and tests
in the intended branch or mainline:

```text
src/state_collapser/training/linearization.py
src/state_collapser/training/torch.py
tests/training/test_encoding_registry.py
tests/training/test_linearization_config.py
tests/training/test_linearized_records.py
tests/training/test_torch_batches.py
tests/examples/test_torch_tensor_boundary_smoke_model.py
```

The key HGraphML-relevant test is:

```text
tests/training/test_encoding_registry.py
```

It must prove that `EncodingRegistry.from_tower(...)` can be built from a
`PartitionTower` without constructing RL-specific training records.

### Step 2: Validate Upstream

Run the relevant upstream checks:

```bash
uv run pytest tests/training/test_encoding_registry.py
uv run pytest tests/tower/partition/test_hgraphml_downstream_compatibility.py
uv run pytest tests/training -k "linearization or torch"
uv run ruff check
uv run mypy
```

If Torch is not installed, Torch-specific tests may skip. That is acceptable
for the HGraphML bridge because HGraphML does not need Torch through
`state_collapser.training.torch`.

### Step 3: Make The Surface Installable For HGraphML

Choose one of these dependency routes:

```text
local editable checkout
    acceptable only for development

branch reference
    acceptable only for active testing

public release tag
    required before public HGraphML compatibility claims
```

Do not make HGraphML permanently depend on a short-lived Codex branch.

### Step 4: Verify From HGraphML

From the HGraphML repo, the following import must work against the selected
dependency:

```bash
uv run --extra dev python -c "from state_collapser.training import EncodingRegistry; print(EncodingRegistry.__name__)"
```

Expected output:

```text
EncodingRegistry
```

If this fails, HGraphML is not ready to implement the compatibility pass against
that dependency.

### Step 5: Write The HGraphML Blueprint

Once the dependency route is known, HGraphML can write a real blueprint.

That blueprint should be narrow:

```text
TensorGraph
    -> HGraphML state_collapser adapter
        -> PartitionTower
            -> EncodingRegistry.from_tower(...)
                -> graph-message-passing-compatible stable ids
```

It should explicitly forbid:

```text
TensorGraph
    -> fake RL ActionSelectionInput
        -> linearize_action_selection_input(...)
            -> TorchDecisionBatch
                -> graph message passing
```

That path is a category error.

## What HGraphML Should Implement First

The first HGraphML implementation should probably contain:

- a compatibility test importing `EncodingRegistry`;
- a test building `EncodingRegistry.from_tower(bundle.partition_tower)`;
- assertions that original HGraphML nodes and edges are encodable;
- assertions that node fibers and edge fibers remain compatible with the
  registry;
- API docs explaining that this is shared tower encoding, not RL tensorization.

Optionally, HGraphML may add:

```python
def build_encoding_registry(bundle: TowerBundle) -> EncodingRegistry:
    return EncodingRegistry.from_tower(bundle.partition_tower)
```

That helper is safer than adding an `encoding_registry` field to `TowerBundle`
in the first pass because it avoids changing the existing adapter object shape.

## What HGraphML Should Not Implement Yet

Do not implement:

- tensorized graph-message-passing kernels;
- replacement of `TensorGraph` ids with `state_collapser` ids throughout
  HGraphML;
- `LinearizedActionSelectionInput` usage in HGraphML;
- `LinearizedTrainingTransition` usage in HGraphML;
- `TorchDecisionBatch` usage in HGraphML;
- an RL learner path in HGraphML;
- benchmark speed-up claims from registry compatibility;
- changes to HGraphML lift semantics;
- changes to `collapse_messages(...)`.

The compatibility pass is about preserving the shared vocabulary boundary, not
about moving HGraphML into the RL tensorization path.

## Blueprint Readiness

HGraphML is close enough to write a blueprint now.

The blueprint should include a hard Phase 0 dependency gate:

```text
Do not implement public compatibility until the selected state_collapser
dependency exposes state_collapser.training.EncodingRegistry.
```

Current readiness:

```text
conceptual readiness: high
blueprint readiness: high
implementation-gameplan readiness: medium
public implementation readiness: blocked on installable dependency surface
```

## Acceptance Criteria For The Bridge

The cross-repo bridge is ready when:

- `state_collapser.training.EncodingRegistry` exists on an installable
  dependency target;
- `EncodingRegistry.from_tower(...)` works on a real `PartitionTower`;
- upstream HGraphML compatibility tests still pass;
- HGraphML can import the selected dependency and build a registry from its
  existing `TowerBundle`;
- HGraphML does not construct fake RL records;
- HGraphML docs state that registry compatibility is not full tensorized graph
  message passing.

## Summary

The thing that has to happen is not mysterious:

```text
release or otherwise expose EncodingRegistry from state_collapser,
then let HGraphML add narrow compatibility coverage around it.
```

Everything else is scope control.

