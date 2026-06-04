# Pointwise Liftability And Source-Support Design

Date: 2026-06-04

Status: design workspace

## Purpose

This folder collects design work for the pointwise liftability/source-support
problem isolated by downstream `big_boy_benchmarking` evaluation of
`state_collapser`.

The core issue is:

```text
quotient-level outgoing action availability is not the same thing as
current-state executable liftability.
```

After state contraction, a quotient state-cell pools outgoing action data
across representatives. That is correct quotient semantics. But a concrete
runtime at current base state `s` can execute only action cells containing at
least one concrete edge sourced at `s`, unless the runtime has an explicit
within-fiber reanchoring/refinement rule.

## Source Reports

Initial diagnostic material lives in:

```text
docs/engineer_continuity/2026/06/04/state_collapser_pointwise_liftability_diagnostic_report.md
docs/engineer_continuity/2026/06/04/state_collapser_pointwise_liftability_github_issue.md
```

Those reports were produced from downstream benchmarking work with the Project
Owner and isolate the problem using BBB counterpoint tower-control failures.

## Design Direction

The design work here should preserve the Young-diagram / nested partition
picture. The likely correct structure is not merely a flat side table from
base states to executable actions.

The primary object should be adjacent-tier source-support pointers:

```text
tier-i action cell
    -> tier-(i-1) child state cells that actually source contributing edges
    -> recursively downward
    -> concrete executable edges at tier 0
```

Flattened base-source caches may be useful for hot runtime checks, but should
be treated as performance materializations of the recursive pointer structure,
not as the mathematical object itself.

## Attribution

The Project Owner identified the key mathematical distinction:

```text
choose only action cells whose supporting edge data is sourced at the current
concrete representative, or explicitly refine/reanchor inside the fiber first.
```

The downstream benchmarking engineer isolated the concrete runtime symptom:

```text
abstract action cells are nonempty, but selected abstract actions fail with
no_lift_candidate_from_current_state.
```

Codex's role in this folder should be to turn that diagnosis into a careful
repo-grounded blueprint and implementation gameplan without flattening away
the recursive Young-diagram structure.

