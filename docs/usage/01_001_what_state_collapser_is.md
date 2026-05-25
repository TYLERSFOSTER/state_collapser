# What `state_collapser` Is

`state_collapser` is a structural layer for reinforcement-learning problems.

It is easiest to place it next to familiar RL tools by contrast:

```text
RLlib says:
    Give me an env; I will run scalable RL algorithms on it.

Stable-Baselines3 says:
    Give me an env; I will run standard reliable RL algorithms on it.

state_collapser says:
    Give me an env or discovered transition system; I will construct a better
    hierarchical/quotient decision structure around it.
```

The package is therefore not trying to be a general training framework. It does
not currently own neural model families, optimizers, distributed rollout,
replay buffers, checkpoints, or experiment manifests. Those belong to the
engineer, the learner, or a later adapter.

The package owns a different layer:

```text
environment or transition system
    -> discovered graph
        -> partition tower
            -> quotient/fiber decision structure
                -> learner-facing inputs and transitions
```

That layer is not limited to RL. A downstream graph-ML package can also hand
`state_collapser` a known graph, treat it as already discovered, build a
partition tower, and lift coarse computations back along node and edge fibers.
The first concrete downstream application of this form is `HGraphML`.

In short:

```text
The package builds the stage.
You bring the learner.
The fiber is the lift.
```

## Current Maturity

This is still pre-alpha research-mode infrastructure. It has real runtime
surfaces and tests, but it should not be mistaken for a mature RL framework.

What exists now:

- graph, vista, and tower runtime machinery
- persistent state/action partition towers
- tower-aware training inputs, decisions, transitions, collectors, and reference
  loops
- `FrozenQuotientBehavior`, `PathFiber`, and `FiberConditionedStage`
- example environments and smoke training paths

What does not exist yet:

- serious PyTorch model families
- vectorized rollout
- full replay/checkpoint/manifest infrastructure
- RLlib or Stable-Baselines3 adapters
- production-scale benchmarking claims

For the implemented training-stage surface, start with
[fiber-conditioned training](./01_004_fiber_conditioned_training.md).

For the first non-RL downstream application, read
[downstream applications](./01_009_downstream_applications.md).
