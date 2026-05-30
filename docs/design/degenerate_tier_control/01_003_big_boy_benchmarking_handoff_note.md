# Big Boy Benchmarking Degenerate Tier Control Handoff

Date: 2026-05-30

Status: downstream integration note

## Purpose

The upstream `state_collapser` degenerate-tier control work gives downstream
active-tier runtimes a generic way to avoid choosing actions at tiers whose
current state-cell has empty outgoing action cells.

`big_boy_benchmarking` should wire this support through its counterpoint
tower-control adapter instead of keeping the empty-action guard inside the
learner.

## Required Downstream Predicate

The counterpoint adapter should pass a predicate equivalent to:

```python
def tier_is_executable(tier: int) -> bool:
    positions = latest_runtime_snapshot.current_position_at_every_tier
    tower = latest_runtime_snapshot.partition_tower_view
    if tower is None:
        return True
    if tier < 0 or tier >= len(positions):
        return False
    state_cell = positions[tier]
    if state_cell is None:
        return False
    return bool(tower.outgoing_action_cells(tier, state_cell))
```

The predicate should be passed into:

```python
ExploitExploreTowerRuntime(..., tier_is_executable=tier_is_executable)
```

## Immediate Expected Effect

The previous artifact failure path was:

```text
active coarse tier has zero outgoing action cells
    -> learner returns -1
    -> executor reports invalid_action_index
    -> zero concrete steps
```

After wiring the predicate, BBB should instead see:

```text
active coarse tier has zero outgoing action cells
    -> state_collapser active-tier runtime lifts to a finer executable tier
    -> learner chooses only once a nonempty action surface exists
```

Only if tier `0` is also non-executable should BBB receive a clean no-action
control result.

## Optional Stricter Counterpoint Predicate

For the first fix, checking `outgoing_action_cells(...)` is sufficient because
the recorded failures happened before an action cell or lift candidate existed.

Later, BBB may choose a stricter predicate:

```text
tier is executable if:
    outgoing_action_cells(tier, current_cell) is nonempty
    and at least one outgoing action cell has a legal concrete lift candidate
```

That stricter rule belongs downstream because legality masks and concrete
counterpoint action realization are BBB/environment-specific.
