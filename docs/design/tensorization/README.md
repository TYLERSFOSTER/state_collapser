# Tensorization Design Track

This folder organizes the design work for adding tensor-capable architecture to
`state_collapser`.

The immediate trigger is the downstream `big_boy_benchmarking` alignment note:

```text
docs/design/model_train_surfaces/01_005_big_boy_benchmarking_tensorization_alignment_note.md
```

That note identifies a benchmark blocker: serious downstream evaluation needs to
distinguish pre-linearization behavior from tensor-capable behavior with tensor
paths disabled or enabled.

## Working Scope

This track is about the package layer that turns structured runtime objects into
stable numeric objects:

- structured states
- primitive actions
- quotient/state cells
- action cells
- masks
- tower positions
- fiber/lift context
- runtime snapshots
- learner-facing decision inputs
- benchmark artifact metadata

Mathematically, this can be read as an `R`-linearization problem.

Engineering-wise, this is the beginning of:

- tensor/device contracts
- batch and sequence contracts
- action-mask numeric representation
- deterministic encoding rules
- disabled/enabled tensor backend modes
- timing hooks around conversion and learner boundaries
- benchmark-visible backend metadata

## Non-Goals For The First Pass

This folder should not assume that first-pass tensorization means building a full
production RL framework.

The first pass does not need to own:

- PPO/SAC/DQN implementations
- distributed rollout
- multi-GPU training
- RLlib or Stable-Baselines3 adapters
- production replay/checkpoint infrastructure
- final public API hardening

The narrower goal is to design the minimum tensor-capable architecture that lets
`state_collapser` and downstream benchmark repos distinguish:

```text
numeric_backend = none_control_flow
numeric_backend = tensor_available_disabled
numeric_backend = tensor_enabled_cpu
numeric_backend = tensor_enabled_cuda
```

Names can change, but the semantic distinction should remain explicit and
machine-readable.

## Current Documents

This folder now contains the design, implementation, and downstream bridge
records for the first tensorization boundary:

- `01_001_tensorization_architecture_blueprint.md`
- `01_002_tensorization_engineer_usage_blueprint.md`
- `01_003_tensorization_implementation_gameplan.md`
- `01_004_tensorization_implementation_log.md`
- `01_005_hgraphml_tensorization_followup_bridge.md`

## Current Status

The first tensorization boundary has been implemented in the package source and
released as part of `v0.7.0`.

The implemented source surfaces are:

- `src/state_collapser/training/linearization.py`
- `src/state_collapser/training/torch.py`

The boundary supports:

- backend-independent linearized records,
- `EncodingRegistry.from_tower(...)`,
- `LinearizationConfig`,
- `LinearizationReport`,
- explicit benchmark labels for disabled/enabled tensor paths,
- optional Torch batch conversion behind the `ml` extra.

This does not make `state_collapser` a full RL framework. Vectorized rollout,
large replay buffers, checkpoint/resume, experiment manifests, CUDA hardening,
and serious learner integration remain future work.
