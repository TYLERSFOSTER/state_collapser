# Training Surface Quickstart

The current training package gives engineers component surfaces, not a hidden
`.learn(...)` framework.

The central loop shape is still ordinary:

```python
current_input = collector.reset_episode(seed=0)

for _ in range(max_steps):
    decision = learner.act(current_input)
    collected_step = collector.collect_step(current_input, decision)
    learner.observe(collected_step.transition)
    learner.update()
    current_input = collected_step.next_input
```

The important package-owned surfaces are:

- `ActionSelectionInput`
- `ActionDecision`
- `TrainingTransition`
- `StepCollector`
- `EpisodeCollector`
- `TabularQLearner`
- `run_reference_online_loop(...)`
- `run_reference_episode_loop(...)`

## ActionSelectionInput

`ActionSelectionInput` is what a learner sees when it must choose an action.

It carries:

- observation
- current compatibility state field
- runtime snapshot
- tower-position key
- optional action mask
- optional history window
- optional active-tier state
- optional compatibility frozen context
- optional `stage_context`
- optional `fiber_departure`
- diagnostics

The stage/fiber fields are additive. Existing flat tower-aware loops do not need
to pass them.

## TrainingTransition

`TrainingTransition` is the learner-facing result of a realized or diagnosed
step.

It carries:

- source input
- chosen action
- reward
- target input
- termination/truncation flags
- bootstrap semantics
- optional runtime summary
- optional stage context
- optional projected coarse step
- optional fiber departure

This is how `FiberConditionedStage` can remain compatible with ordinary learner
surfaces: the stage adds context to the same transition type rather than
inventing an unrelated training record.

## What The Engineer Owns

The engineer still owns:

- the model
- the optimizer
- the training loop
- experiment management
- checkpoint policy
- evaluation policy

The package supplies tower-aware structure and typed handoff objects.

## Tensorization Boundary

When a learner or benchmark harness needs numeric records or Torch tensors, use
the explicit tensorization boundary rather than changing the ordinary training
loop shape.

The current path is:

```text
ActionSelectionInput / TrainingTransition
    -> LinearizedActionSelectionInput / LinearizedTrainingTransition
        -> optional TorchDecisionBatch / TorchTransitionBatch
```

For exact imports and benchmark-mode labels, read
[tensorization boundary](./01_010_tensorization_boundary.md).
