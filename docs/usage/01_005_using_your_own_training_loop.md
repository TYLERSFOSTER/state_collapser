# Using Your Own Training Loop

`state_collapser` does not hide the training loop.

For fiber-conditioned training, the direct loop remains:

```python
current_input = stage.reset(seed=0)

for _ in range(max_steps):
    decision = learner.act(current_input)
    transition = stage.step(decision)
    learner.observe(transition)
    learner.update()
    current_input = transition.target_input
```

The package-owned `stage` supplies:

- tower-position metadata
- fiber-derived action masks
- admissible action-cell realization
- departure diagnostics
- ordinary `TrainingTransition` records

The learner owns:

- action scoring
- exploration schedule
- gradient or tabular update
- replay/storage
- checkpointing
- model/device policy

This is deliberate. The package is meant to make serious training loops easier
to write by making the component surfaces good, not by turning training into a
closed framework.

## Fitting A Neural Learner Later

A neural learner can consume `ActionSelectionInput` exactly where the reference
`TabularQLearner` does. Future tensor/device utilities should convert:

- observation
- tower-position key
- action mask
- stage context
- diagnostics selected by the engineer

into model inputs. That tensor stack is not implemented yet.
