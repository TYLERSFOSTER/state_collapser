# API Note: FrozenQuotientBehavior

`FrozenQuotientBehavior` represents coarse quotient behavior held fixed while a
finer stage is trained.

## FrozenQuotientStep

Fields:

- `coarse_tier`
- `source_cell`
- `action_cell`
- `target_cell`
- `metadata`

The action cell and target cell may be absent when the coarse behavior is
coarser than explicit action-cell readout, for example when the projected edge
has become internal.

## FrozenQuotientBehavior

Fields:

- `behavior_id`
- `coarse_tier`
- `supported_fine_tier`
- `tower_fingerprint`
- `schema_fingerprint`
- `decision_surface`
- `current_step`
- `path_prefix`
- `action_prefix`
- `version`
- `metadata`

First-scope behavior validates:

```text
coarse_tier == supported_fine_tier + 1
```

The class supports concrete-step behavior now and leaves room for future
policy-surface behavior through `decision_surface`.

Use `FrozenQuotientBehavior.from_step(...)` for the common concrete-step case.
