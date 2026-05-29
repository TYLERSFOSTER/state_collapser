# Downstream Applications

`state_collapser` is primarily developed as a quotient/tower runtime for
reinforcement-learning state/action structure. It is also useful as a structural
backend for other graph-dataflow systems.

The first concrete downstream application is `HGraphML`.

## HGraphML

`HGraphML` is a lightweight graph-ML research package that uses
`state_collapser` quotient towers as scaffolding for trainable graph message
passing.

Its core move is:

```text
known graph
    -> state_collapser partition tower
        -> coarse graph/message pass
            -> lift over node and edge fibers
                -> fine graph readout
```

This is different from the ordinary RL use case. In reinforcement learning, the
graph is usually discovered over time as the agent explores. In `HGraphML`, the
computational graph is typically already known. The downstream package therefore
uses the partition-tower machinery as a full-graph quotient constructor rather
than as an exploration loop.

## Why This Matters

`HGraphML` is an important application because it tests whether the
`state_collapser` tower model is a general graph-structure layer rather than
only an RL-specific controller helper.

In the graph-ML setting:

- states become graph nodes,
- primitive actions become directed graph edges,
- contraction schemas become graph coarsening rules,
- state cells become coarse nodes,
- action/edge cells become coarse message-passing channels,
- fibers become the preimage data needed to lift coarse messages back to the
  fine graph.

This makes `HGraphML` a downstream compatibility target for the partition-tower
runtime.

## Current Downstream Dependency Surface

`HGraphML` currently relies on:

- `state_collapser.core.State`
- `state_collapser.core.PrimitiveAction`
- `state_collapser.core.BaseEdge`
- `state_collapser.tower.partition.ContractionSchema`
- `state_collapser.tower.partition.LabelBlockSchema`
- `state_collapser.tower.partition.PartitionTower`
- `state_collapser.tower.partition.build_partition_tower_full`

It also relies on stable-enough read access to partition-tower layers so it can
recover:

- node fibers from state-cell members,
- edge fibers from edge preimages grouped by coarse source and target cells,
- coarse graph readouts by tier.

Starting with the `v0.7.0` tensorization boundary, HGraphML can also target the
shared tower-encoding layer:

```python
from state_collapser.training import EncodingRegistry
```

That registry is useful for graph-message-passing ids because it can be built
from a `PartitionTower` without constructing RL-specific `ActionSelectionInput`
or `TrainingTransition` objects and without importing Torch.

These surfaces are still pre-alpha, but they are now more than internal
implementation details: they have at least one real downstream package depending
on them.

## Compatibility Expectations

Changes to the partition-tower runtime should consider HGraphML before they
land. In particular, avoid silently breaking:

- full-graph tower construction from already-known states and edges,
- label/schema-based contraction,
- stable state and edge registration,
- state-cell member queries,
- edge source/target queries by registered edge id,
- action/edge-cell semantics needed to recover fine-edge fibers,
- lazy readout behavior that keeps the hot path separate from compatibility
  quotient views.

If the existing surface is not the right long-term public API for HGraphML, the
preferred fix is to add a clearer `state_collapser`-owned readout or adapter
surface. The wrong fix is for HGraphML to reimplement tower construction
locally.

## Release Implication

Because HGraphML depends on `state_collapser`, public release planning for
`state_collapser` now has a downstream constraint:

```text
Do not make a public release that breaks HGraphML's first import unless the
break is intentional, documented, and paired with a migration path.
```

This does not mean the current HGraphML-facing surfaces are stable forever. It
does mean they should be treated as real compatibility surfaces during release,
security, and public API audits.
