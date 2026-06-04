# Big Boy Benchmarking Pointwise Liftability Handoff

Date: 2026-06-04

Status: downstream integration note

## Purpose

This note records the upstream `state_collapser` pointwise liftability fix for
downstream `big_boy_benchmarking` tower-control adapters.

The prior downstream failure mode was:

```text
quotient state cell has nonempty abstract outgoing action cells
    -> learner selects an abstract action cell
    -> selected action has no concrete edge sourced at current base state
    -> executor reports no_lift_candidate_from_current_state
```

The upstream distinction is now explicit:

```text
outgoing_action_cells(...) is quotient/readout availability
executable_action_cells(...) is current-state executable availability
executable_lift_candidates(...) is strict current-state concrete liftability
```

## Required BBB Predicate Change

Replace weak tier executability checks of the form:

```python
bool(tower.outgoing_action_cells(tier, state_cell))
```

with:

```python
tower.tier_is_executable_from_state(tier, current_base_state)
```

This checks whether the current concrete state has at least one executable
action at that tier.

## Required BBB Vocabulary Change

For executable control, replace quotient vocabularies of the form:

```python
tower.outgoing_action_cells(tier, state_cell)
```

with:

```python
tower.executable_action_cells(tier, state_cell, current_base_state)
```

Use quotient vocabularies only for readout, diagnostics, or stable abstract
action accounting.

## Required BBB Lift Change

For direct execution, replace representative/readout candidates:

```python
tower.lift_candidates(tier, action_cell, current_base_state)
```

with:

```python
tower.executable_lift_candidates(tier, action_cell, current_base_state)
```

The strict method returns only concrete edges whose source is the current base
state. It returns `()` when no such edge exists.

## Diagnostic Semantics

After adopting the strict APIs, repeated:

```text
no_lift_candidate_from_current_state
```

should no longer be treated as a normal learner/runtime outcome for pointwise
execution. It should indicate one of:

- stale tower context;
- mis-synchronized current base state;
- downstream vocabulary built from quotient instead of executable action cells;
- downstream execution still using representative/readout lift candidates;
- or a genuine bug in upstream source-support maintenance.

## Optional Additional Counters

BBB reports may benefit from recording both counts:

```text
abstract_outgoing_action_cell_count
pointwise_executable_action_cell_count
```

The first is a quotient/readout count. The second is the executable-control
count.

