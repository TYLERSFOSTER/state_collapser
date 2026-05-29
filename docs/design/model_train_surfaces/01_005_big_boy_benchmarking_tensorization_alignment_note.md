# Big Boy Benchmarking Tensorization Alignment Note

Date: 2026-05-29

Source context: `/Users/foster/big_boy_benchmarking`

Benchmark context:

```text
docs/design/first_counterpoint_environment/first_counterpoint_serious_evaluation/
```

## Status

This note records a benchmark-driven blocker for `state_collapser` tensorization
work.

The first serious `big_boy_benchmarking` evaluation for the new counterpoint
environment is paused until `state_collapser` has a tensor-capable architecture
available as part of the package surface.

This is not a request to make `state_collapser` a full RL framework before any
benchmarking can happen. It is a narrower alignment requirement: the benchmark
needs to distinguish pre-tensor control-flow behavior from tensor-capable
behavior with tensor paths disabled or enabled.

## Core Conclusion

Current `state_collapser` is best understood as:

```text
sparse graph/tower/control-flow architecture
```

with research-grade tabular/training surfaces.

It is not yet:

```text
R-linearized / tensorized / vectorized / GPU-backed architecture
```

The missing layer can be described mathematically as `R-linearization`: turning
structured states, actions, quotient cells, action cells, masks, fibers,
runtime snapshots, and learner-facing inputs into stable numeric objects.

The engineering formulation is:

```text
tensor/device/batch/sequence/vectorized-rollout infrastructure
```

Those are two names for overlapping parts of the same gap.

## Benchmark Distinction That Matters

`big_boy_benchmarking` needs to avoid blurring these three categories:

```text
1. pre-linearization / current control-flow state_collapser
2. tensor-capable state_collapser with tensor path present but disabled
3. tensor-capable state_collapser with tensor path enabled
```

The current package state is category 1.

The clean benchmark ablation is category 2 versus category 3.

That distinction matters because tensorization can change behavior even when the
tensor path is disabled. It may force or alter:

- canonical numeric encodings;
- shape, dtype, and device contracts;
- action-mask representation;
- batch boundaries;
- deterministic conversion rules;
- validation and error behavior;
- state/action identity normalization;
- dependency/import surfaces;
- memory layout assumptions;
- timing overhead around conversion boundaries;
- runner APIs;
- artifact metadata.

Therefore:

```text
benchmarking state_collapser before tensorization exists
```

is not the same evidence as:

```text
benchmarking tensor-capable state_collapser with tensorization disabled
```

The former is only a pre-linearization baseline. The latter is the meaningful
tensor-off arm of a tensor-capable architecture benchmark.

## Why Big Boy Benchmarking Is Paused

`big_boy_benchmarking` now has a real counterpoint environment and smoke/
diagnostic harness. It can run:

- graph diagnostics;
- schema diagnostics;
- reward-fiber diagnostics;
- lift-fiber diagnostics;
- direct masked-random smoke;
- direct tabular-Q smoke;
- tower construction smoke.

Those are useful, but they do not yet support the intended serious evaluation.

The serious evaluation is blocked because it should compare behavior in an
architecture where tensorization is present as an explicit option, not absent as
future work.

## Minimum Tensorization Alignment Needs

For the counterpoint benchmark to resume as a serious evaluation, `state_collapser`
should expose enough tensorization structure to let downstream benchmark
artifacts distinguish at least:

```text
numeric_backend = none_control_flow
numeric_backend = tensor_available_disabled
numeric_backend = tensor_enabled_cpu
numeric_backend = tensor_enabled_cuda
```

or equivalently:

```text
linearization_state = absent
linearization_state = present_disabled
linearization_state = present_enabled
```

The exact names can change, but the distinction must be explicit and
machine-readable.

Minimum architecture needs likely include:

- canonical numeric encoding contracts for states;
- canonical numeric encoding contracts for primitive actions;
- canonical numeric encoding contracts for tower positions;
- action-mask tensor/array representation;
- deterministic conversion from structured runtime objects to numeric records;
- shape/dtype/device declarations;
- a disabled tensor path that still runs through the tensor-capable architecture
  boundary cleanly;
- an enabled tensor path, at least on CPU for first serious comparison;
- room for CUDA/GPU mode later if GPU claims are made;
- timing hooks around conversion, learner action, learner update, environment
  step, tower update, and artifact writing;
- dependency/backend state export for downstream artifact manifests.

## What Is Not Required For The First Resume Gate

The first serious counterpoint benchmark probably does not require all of this
at once:

- production RL framework maturity;
- PPO/SAC/DQN ownership;
- distributed rollout;
- multi-GPU training;
- large replay systems;
- external RLlib or Stable-Baselines3 adapters;
- polished public API finality.

The first resume gate is narrower:

```text
Can state_collapser represent and report tensor-capable disabled/enabled modes
in a way that big_boy_benchmarking can treat as benchmark conditions?
```

## Benchmark Claims To Avoid Until Then

Until this tensorization work exists, `big_boy_benchmarking` should not claim:

- tensor-off versus tensor-on evidence;
- GPU or CUDA performance;
- vectorized rollout performance;
- mature high-throughput RL substrate performance;
- serious final counterpoint benchmark evidence.

It may claim only:

```text
The counterpoint environment and smoke/diagnostic harness are runnable, and the
first serious evaluation is intentionally paused until state_collapser has a
tensor-capable architecture suitable for disabled/enabled benchmark modes.
```

## Resume Signal For Big Boy Benchmarking

When this repo has a tensor-capable path that can be disabled/enabled under an
explicit backend/mode contract, resume:

```text
/Users/foster/big_boy_benchmarking/docs/design/first_counterpoint_environment/first_counterpoint_serious_evaluation/design_discussion.md
```

The first question on resume should be:

```text
Has state_collapser reached the tensor-capable architecture state needed to make
the tensor-off versus tensor-on distinction meaningful?
```

Only then should `big_boy_benchmarking` proceed to blueprint and gameplan for the
first serious counterpoint evaluation.

