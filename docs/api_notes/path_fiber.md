# API Note: PathFiber

`PathFiber` describes the fine-tier action possibilities lying over a frozen
coarse quotient behavior.

Fields:

- `fiber_id`
- `tower`
- `fine_tier`
- `coarse_tier`
- `frozen_behavior`
- `metadata`

First-scope behavior validates adjacent tiers:

```text
coarse_tier == fine_tier + 1
```

## Core Methods

- `stage_context(stage_id)`
- `resolve_state_cells(total_state)`
- `current_fine_state_cell(total_state)`
- `current_coarse_state_cell(total_state)`
- `action_vocabulary(total_state)`
- `executable_action_vocabulary(total_state)`
- `admissible_action_cells(total_state)`
- `action_mask(total_state, action_vocabulary=None)`
- `lift_candidates(total_state, action_cell)`
- `diagnose_departure(total_state, action_cell)`

## Relationship To PartitionTower

`PathFiber` does not rebuild the tower. It composes existing tower queries:

- it starts from quotient-level outgoing fine action cells
- separately computes the action cells executable from the current total state
- projects current-state executable edges to the coarse tier
- keeps only executable action cells compatible with the frozen coarse step
- delegates executable candidates to
  `PartitionTower.executable_lift_candidates(...)`

Do not confuse this with `PartitionTower.refinement_fiber(...)`. The latter is a
local adjacent-cell query. `PathFiber` is the learner-facing structure over a
frozen coarse behavior.

`PathFiber.action_vocabulary(...)` remains the quotient-level vocabulary, which
is useful for stable learner action dimensions. `PathFiber.action_mask(...)`,
`PathFiber.admissible_action_cells(...)`, and `PathFiber.lift_candidates(...)`
are pointwise strict: they expose only actions with concrete current-state
support.
