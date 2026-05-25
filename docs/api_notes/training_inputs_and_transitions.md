# API Note: Training Inputs And Transitions

## ActionSelectionInput

`ActionSelectionInput` currently carries:

- `observation`
- `current_base_state`
- `runtime_snapshot`
- `tower_position_key`
- `action_mask`
- `history_window`
- `active_tier_state`
- `frozen_lower_context`
- `stage_context`
- `fiber_departure`
- `diagnostics`

The `current_base_state` and `frozen_lower_context` names remain compatibility
surfaces. New fiber-conditioned code should prefer the conceptual vocabulary
`total_state` and `frozen_quotient_behavior`.

## TrainingTransition

`TrainingTransition` currently carries:

- `source_input`
- `chosen_action`
- `reward`
- `target_input`
- `terminated`
- `truncated`
- `bootstrap_allowed`
- `diagnostics`
- `bootstrap_input`
- `bootstrap_reason`
- `runtime_snapshot_summary`
- `tower_position_key`
- `active_tier`
- `frozen_context_version`
- `stage_context`
- `projected_coarse_step`
- `fiber_departure`

The stage/fiber fields are additive and backward compatible. Existing flat
training loops can ignore them.

See [training surface quickstart](../usage/01_003_training_surface_quickstart.md)
for the loop-level role of these objects.
