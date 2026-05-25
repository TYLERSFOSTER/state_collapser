# Final Initial Blueprint

## Status

This document is the first actual implementation blueprint for `state_collapser`.

It is derived from the accumulated design decisions recorded across:

- `module_design_desiderata.md`
- `package_best_practices_proposal.md`
- `reward_locality_for_quotient_training.md`
- `implementation_contracts.md`
- `mathematical_model.tex`

Those earlier documents preserve the history of design meetings and clarifications.

This document is different.

Its purpose is to state, in one place and at one level of detail, the concrete architecture that should be implemented first.

It should be treated as the current authoritative blueprint for the first implementation pass.

## Blueprint Term

In software development, the closest standard terms for "blueprint" are:

- **technical design specification**
- **architecture specification**
- **implementation specification**

For this repository, the best term is:

- **implementation blueprint**

because the document must bridge mathematical design, architecture, runtime behavior, and concrete code scaffolding.

## Core Scope

This blueprint is for the first implementation pass only.

It covers:

- the hidden graph contract
- the discovered graph and vista layers
- message passing for quotient-style skip knowledge
- contraction policies
- nested cumulative quotient-tier views
- full tower update after each newly discovered state
- reward computation and quotient-level reward aggregation
- runtime snapshots
- a first toy environment

It does not cover:

- full higher-categorical or simplicial path machinery
- final production optimization
- full ROS 2 integration
- final trainer zoo
- universal support for strongly nonlocal reward rules

## First-Principles System Picture

`state_collapser` is not primarily:

- a Gymnasium wrapper
- a graph-algorithms utility package
- a Torch-first learning library
- a robotics middleware package

It is primarily:

- a runtime graph-discovery and annotation engine
- over a hidden predicate-defined state-action graph
- with nested quotient-style views
- supporting tower construction during training

The package's core operational surface is:

- an agent moves by primitive actions in the base hidden graph
- the explored graph is updated
- the `1`-hop vista is updated
- contraction-policy consequences are applied
- the full current tower is updated immediately
- the agent's current position is known across all tiers
- reward is computed from the currently understood tower

## External Library Boundary

### Gymnasium

`gymnasium` is the environment-shell boundary.

It provides:

- `reset`
- `step`
- observation
- action
- reward
- termination and truncation

It does not provide:

- discovered graph `G^0_t`
- explored subgraph `H^0_t`
- `1`-hop vista graph
- contraction/equalization
- quotient views
- tier nesting
- full tower update
- cross-tier position tracking

Therefore the package should use Gymnasium where convenient, but the graph/tower runtime is package-native.

### Torch

`torch` is an optional learnable-backend surface.

The first implementation should not require it for:

- graph legality
- explored/vista updates
- contraction policies
- reward aggregation
- runtime tower maintenance

It may later support:

- learned embeddings
- learned contraction scoring
- learned policy heads
- accelerated reward/message computations

### ROS 2

`ROS 2` remains outside the first implementation scope.

The first implementation should not embed ROS runtime assumptions into core classes.

## Governing Mathematical Decisions

The following decisions are now fixed for the first implementation pass.

### Hidden Graph

The hidden graph is predicate-defined.

It is not the primary source of truth as a generic pre-materialized graph object.

Its truth conditions come from:

- state validity
- action validity
- edge validity
- action application

### State

The base state is:

- a minimal mathematical locus
- immutable
- hashable
- represented first as a frozen dataclass

The state should not itself store changing runtime notes or contraction annotations.

### Primitive Action

A primitive action is:

- immutable
- hashable
- explicit
- one-step or indecomposable

The contract must support multiple action-encoding styles.

### Runtime Notes And Annotations

Changing runtime data lives outside the base state.

It lives in node- and tier-indexed annotation stores attached to runtime graph layers.

### Quotienting

Contraction is an information-equalization operation.

What is equalized is not merely graph topology.

What is equalized is outgoing-edge possibility knowledge and related local annotations needed for quotient-style skip behavior.

### Tier Semantics

Quotient tiers are not isolated graph worlds.

They are nested cumulative quotient views over one shared discovered graph.

The crucial semantic rule is:

- outgoing-edge and coset information accumulates down the tower
- tier queries are cumulative in a "`<= k`" sense, not merely exact-tier-only

### Reward

Reward is local to primitive transitions in the implementation target region.

Compound reward is cumulative over local primitive-action reward contributions.

Quotient-edge reward aggregation must ignore internal collapsed edges and use only boundary-crossing preimage contributors.

## Concrete Runtime Ontology

The first implementation should operate with the following runtime objects.

### Layer 1: Hidden Graph Contract

Objects:

- `State`
- `PrimitiveAction`
- `BaseEdge`
- `GraphSpec`
- `HiddenGraph`

Purpose:

- answer legality and local-neighborhood questions
- define the hidden graph intensionally

### Layer 2: Discovered Runtime Graph

Objects:

- `ExploredGraph`
- `VistaGraph`
- `NodeAnnotationStore`
- `VistaPayload`
- `LocalStar`

Purpose:

- represent visited history
- represent the maintained `1`-hop fringe
- store state-local and tier-local runtime annotations
- support push/pull message passing

### Layer 3: Nested Quotient Views

Objects:

- `QuotientTierView`
- `ProjectionMap`
- `CosetStore`
- `TierAnnotationStore`

Purpose:

- represent tier-indexed quotient views over the shared discovered graph
- support cumulative outgoing-edge queries by tier
- track current tier positions

### Layer 4: Runtime Coordinator

Objects:

- `ContractionPolicy`
- `TowerRuntime`
- `RuntimeSnapshot`
- optional `TrustworthinessPolicy`

Purpose:

- apply contraction policy after each newly discovered step
- update the full tower immediately
- produce the runtime handoff object for downstream training/control logic

### Layer 5: Environment Adapter

Objects:

- `GymnasiumAdapter`
- toy environment implementation

Purpose:

- expose the package runtime through standard RL entry points
- keep adapter code thinner than the runtime itself

## Required Core Data Objects

### `State`

Required properties:

- immutable
- hashable
- serializable
- stable equality

Required fields:

- stable identity field or canonical payload
- environment-specific structured payload

Examples of payload content:

- discretized position
- arm-joint coordinates
- bounded symbolic fields
- region ids
- categorical markers

### `PrimitiveAction`

Required properties:

- immutable
- hashable
- serializable

Required fields:

- action identity or canonical payload
- encoded action content
- optional labels

### `BaseEdge`

Required fields:

- `source`
- `action`
- `target`
- optional labels

### `NodeAnnotationStore`

This is a central performance-sensitive runtime object.

It should store:

- local labels
- local notes/marks
- pushed vista payloads
- pulled vista payloads
- tier-local contraction marks
- tier-indexed cumulative outgoing-edge knowledge

It should support:

- rapid local update
- rapid cumulative tier query
- clean separation from state identity

It should not require labels to be numeric.

However, the implementation should leave room for later numeric encoding layers used for vectorized or GPU-backed optimization.

### `VistaPayload`

This must be interpreted operationally.

It is not generic context.

It carries newly available outgoing-edge possibility data.

Required contents:

- outgoing edge set from the sending state
- corresponding reachable target states
- relevant edge labels
- contraction or coset marks needed to interpret those outgoing possibilities

The payload may later be optimized into encoded numerical views, but the logical contents should remain as above.

## Hidden Graph Contract

The hidden graph should expose the following behavior:

- `is_valid_state`
- `is_valid_action`
- `apply_action`
- `is_valid_edge`
- `out_actions`
- `out_neighbors`
- `out_edges`

The implementation should treat this as the mathematical source of legality and local query, not as a cache of precomputed adjacency data.

Materialization of all nodes or edges is optional and environment-dependent.

## Runtime Layer Semantics

### Explored Graph

`ExploredGraph` stores:

- visited states
- traversed edges
- current base state
- current base path history

Its semantics are:

- the visited-history restriction of the hidden graph

### Vista Graph

`VistaGraph` stores:

- explored graph contents or references
- `1`-hop queried neighborhoods at visited states
- node annotations
- payload propagation results

Its semantics are:

- the explored graph plus the maintained local visible fringe

The package should treat the vista layer as the first genuinely operational graph layer.

### Quotient Tier View

This is a nested cumulative quotient view over the same discovered graph.

It should store:

- tier index
- source-layer reference
- projection maps
- coset membership
- current tier position
- tier-local cumulative outgoing-edge knowledge

The crucial rule is:

- the effective outgoing-edge query at tier `k` is cumulative, not exact-tier-isolated

So the implementation must support queries like:

- "what outgoing-edge possibilities are available through tier `k`?"

not merely:

- "what outgoing edges were introduced exactly at tier `k`?"

## Runtime Update Cycle

The first implementation should treat the runtime update cycle as the core algorithm.

One primitive environment step means:

1. execute primitive action in the base environment
2. decode and validate resulting base transition
3. add state and edge to explored graph
4. refresh `1`-hop vista at the newly occupied state
5. build the local star at tier `0`
6. apply the selected contraction policy at tier `0`
7. update tier-`0` annotations and quotient view
8. propagate the contraction consequences through every higher tier immediately
9. update the current position at every tier
10. recompute cumulative outgoing-edge knowledge where affected
11. compute current step reward
12. update cumulative base-path reward
13. update quotient-tier reward summaries using boundary-crossing preimage edges only
14. produce a runtime snapshot

There should be no ambiguity in code about whether the full tower update happens now or later.

It happens now.

## Contraction Policy System

The first implementation should ship with both:

- a label-based policy
- a seeded-random policy

Both should implement the same interface:

- select an edge family from a local star

The runtime, not the policy, performs quotient/tower mutation.

### Label-Based Policy

Intended use:

- where contraction labels are present and meaningful
- including region-specific parameter-reduction-like situations

### Random Policy

Intended use:

- general problem-agnostic contraction
- initial baseline behavior

The seeded-random implementation should be deterministic under fixed seed.

## Reward System Blueprint

### Primitive Reward

The first implementation must support primitive transition reward.

### Path Reward

The first implementation must support cumulative path reward via weighted aggregation over primitive rewards.

### Quotient Reward

The first implementation must support quotient-tier reward summaries defined from preimage contributors.

Important rule:

- internal collapsed member edges do not count as outgoing quotient-edge reward contributors
- only boundary-crossing preimage edges do

### Reward Objects

The runtime should at minimum expose:

- step reward
- cumulative path reward
- quotient-tier reward summaries

These should be present in the runtime snapshot, not reconstructed ad hoc later.

## Trustworthiness In Version 1

The review process clarified that trustworthiness is not central to version `1`.

Reason:

- the full tower is updated immediately after each newly discovered state
- episode progression already proceeds bottom-tier to top-tier via lifts

So the first implementation should:

- keep `TrustworthinessPolicy` as an extension point
- not make it a central runtime dependency

This is a simplification, not a loss.

## Runtime Snapshot

`TowerRuntime.step(...)` should return a full `RuntimeSnapshot`.

The snapshot should contain:

- current base state
- explored graph
- vista graph
- ordered quotient-tier views
- current position at every tier
- current step reward
- cumulative path reward
- quotient-tier reward summaries
- any needed metadata for downstream control/training

The package's own runtime should not reduce this to Gymnasium-style tuples internally.

Adapters may derive thinner views later.

## First Toy Environment Blueprint

The first toy environment should be:

- small
- inspectable
- structurally honest
- close in spirit to a real robotics constraint-navigation problem

Recommended direction:

- a discretized robot-arm-style constraint navigation environment

Required properties:

- hidden graph is not trivial to parametrize globally
- some regions admit local parameter-reduction-style labels
- some regions do not
- random contraction is meaningful
- label-based contraction is meaningful
- local reward on primitive transitions is meaningful

This environment should become:

- the first end-to-end example
- the first integration-test environment
- the first explanation artifact for future users

## Code Organization Blueprint

The initial code layout should implement the runtime ontology above.

Recommended layout:

```text
src/state_collapser/
    core/
        state.py
        action.py
        edges.py
        labels.py
        annotations.py
        rewards.py

    graph/
        spec.py
        hidden_graph.py
        explored_graph.py
        vista_graph.py
        local_star.py

    quotient/
        projection.py
        cosets.py
        tier_view.py

    contract/
        policy.py
        selection.py

    tower/
        runtime.py
        snapshot.py
        trustworthiness.py

    adapters/
        gymnasium.py

    examples/
        robot_constraint_toy.py
```

This layout should be treated as the first implementation target unless a later explicit decision revises it.

## Test Blueprint

The first implementation must be driven by unit tests from the beginning.

At minimum, tests must cover:

- state immutability and hashing
- primitive action immutability and hashing
- hidden graph legality predicates
- explored graph state/edge accumulation
- vista `1`-hop refresh behavior
- push/pull payload propagation
- node annotation store cumulative query semantics
- label-based contraction policy
- random contraction policy under fixed seed
- quotient projection correctness
- cumulative nested tier query semantics
- full tower update after new discovered state
- exclusion of internal collapsed edges from quotient reward aggregation
- runtime snapshot completeness
- toy-environment integration smoke behavior

## Documentation Consequences

The earlier design docs remain valid, but this blueprint sharpens them in the following ways:

- `gymnasium` should now be read strictly as an environment shell
- quotient tiers should now be read as nested cumulative views
- message passing should now be read as outgoing-edge possibility propagation
- trustworthiness should now be read as optional in version `1`

## Final Blueprint Statement

The first implementation of `state_collapser` should be built as a realtime nested graph-discovery, annotation, and quotient-view engine over a shared discovered graph, with immediate tower updates after each new discovered state, cumulative tier-indexed outgoing-edge queries, local primitive reward, quotient reward aggregation over boundary-crossing contributors, and a full runtime snapshot handoff after each step.
