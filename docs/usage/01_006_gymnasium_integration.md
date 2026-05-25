# Gymnasium Integration

The package already has Gymnasium-oriented adapter work, but
`FiberConditionedStage` is not Gymnasium-first.

Current Gymnasium-facing code is for observing and wrapping external
environment interaction. It helps bind:

- reset/step behavior
- observations
- action masks
- stable state keys
- stable action keys
- transition labels

Fiber-conditioned training is a package-native stage surface. It consumes a
runtime plus a `PartitionTower`, `FrozenQuotientBehavior`, and `PathFiber`.

The future direction is:

```text
FiberConditionedStage
    -> optional Gymnasium-like adapter
        -> optional SB3/RLlib integration
```

That adapter does not exist yet. The current docs should not be read as claiming
Stable-Baselines3 or RLlib compatibility.

For the adapter boundary that exists today, see
`state_collapser.adapters.gymnasium`.
