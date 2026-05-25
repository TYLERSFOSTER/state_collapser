# Package Best Practices Proposal

## Implementation Status Note

This proposal has now been partially realized in code.

Implemented first-pass package layers now include:

- `state_collapser.core`
- `state_collapser.graph`
- `state_collapser.contract`
- `state_collapser.quotient`
- `state_collapser.tower`
- `state_collapser.examples`
- `state_collapser.adapters`

The current code still treats most of these as provisional internal surfaces rather than stable public API.

For current implementation authority, defer to:

- `docs/design/final_initial/final_initial_blueprint.md`
- `docs/design/final_initial/final_initial_implementation_gameplan.md`

## Purpose

This document is a first proposal for how `state_collapser` should be structured as a professional Python library.

It is downstream of [`module_design_desiderata.md`](./module_design_desiderata.md), but it has a different job.

The desiderata document records the conceptual picture of the system.

This document proposes a concrete package setup that would let that picture become a real, shareable, maintainable library.

The intended audience is:

- the project owner
- future engineering collaborators
- future users trying to understand what kind of package `state_collapser` is supposed to be

## Correct System Picture

The most important setup fact is that `state_collapser` is not primarily a package about ultimate physical reality.

It is primarily a package about:

- modeled reality
- implicit graph structure over modeled states
- contraction and quotienting over that modeled graph
- offline and online tower construction
- hierarchical control and training over the resulting tower

So the library should not be designed as:

- just a Gymnasium wrapper
- just a graph algorithms package
- just a Torch training package
- just a robotics package

It should be designed as a library whose own core abstractions are:

- modeled states
- labels
- notes / annotations / persistent marks
- transitions
- contraction operations
- information equalization
- tower levels
- hierarchical control and refinement

Everything else should sit around that core.

## The Role Of Gymnasium

`gymnasium` is still a good primary environment boundary, but only if it is understood correctly.

Gymnasium is not the source of the tower model.

It is the source of a standard interaction shell:

- reset
- step
- observation
- action
- reward
- termination / truncation

That is enough for `state_collapser`, because the package is supposed to contribute the extra structure.

Crucially, Gymnasium does not fight the current system picture.

A Gymnasium environment can absolutely host a world in which the agent can:

- read persistent marks
- write persistent marks
- revisit regions where earlier marks matter
- have transitions or observations influenced by those marks

So the right architectural statement is:

- Gymnasium hosts the experience loop
- `state_collapser` builds modeled states, notes, graph structure, contractions, and towers on top of that loop

This is a strong fit, not a bad one.

## The Role Of Torch

`torch` is also a good fit, but only as a learnable-backend surface.

Torch should not define the ontology of the package.

It should support optional learned subroutines such as:

- state embedding
- similarity scoring
- contraction proposal scoring
- message-passing components
- tier-local policies
- refinement policies

The package should remain structurally useful even when Torch is absent.

That means:

- structural analysis should not require Torch
- offline contraction should not require Torch
- small explicit examples should not require Torch

Torch should be a strong optional layer, not the minimum identity of the library.

## The Role Of ROS 2

`ROS 2` should remain the outer robotics integration boundary.

That means:

- no core mathematical modules should depend directly on ROS runtime machinery
- robotics-facing adapters should live at the edge of the package
- the core should remain about modeled reality and tower structure

This matters because the repo is not primarily trying to solve:

- hardware deployment correctness
- robot middleware orchestration
- actuator/driver integration

Those belong to the larger robotics stack.

`state_collapser` should instead produce structures and behaviors that can later be integrated into such a stack.

## Core Design Principle

The package should be designed around one central thought:

**the agent moves in fine space, but can think and plan in coarse space**

That means the library needs to model both:

- fine execution
- coarse internal control structure

And it needs to preserve the distinction between them.

A quotient edge should not automatically mean:

- a literal physical transition

It should usually mean something more like:

- a coarse exit relation
- an option
- a macro-action
- a reusable local route promise

This is why the package needs explicit refinement structure between tiers.

## Current Mathematical Scope Boundary

The present package stage should be kept narrower than the full mathematical horizon suggested by the project.

There is a real possibility that the deepest correct picture eventually involves:

- path-space-aware quotients
- path fibers over quotient paths
- localization-style constructions
- simplicial or higher-categorical tower structure
- a more Malik-Foster-style simplicial HNSW implementation

That broader direction should be acknowledged explicitly.

But it should not be forced into the first concrete package implementation.

The current scope boundary should be:

- quotient and tower structure implemented at the graph or `1`-categorical level
- reward treated as decorating `Cat^1(G_t)`
- compositional reasoning handled through edge structure and induced edge composition

In other words, the package should presently be built around graph-level quotienting with rich coset data, not around a full simplicial or `(\infty)`-categorical implementation.

Best-practices recommendation:

- document the higher-categorical direction as a real future path
- keep the current library implementation at the graph/compositional edge level
- treat any fuller simplicial or higher-categorical realization as a later development stage or a child library

## Proposed High-Level Package Shape

The most natural professional setup is a layered package with five major bands:

1. **Core modeled-state band**
   - state records
   - labels
   - annotations / notes
   - transitions

2. **Structural band**
   - graph views over modeled states
   - statistics
   - contraction and equalization
   - tower construction

3. **Control/training band**
   - online note writing
   - message passing
   - hierarchical control
   - tier refinement
   - training workflows

4. **Adapter band**
   - Gymnasium integration
   - Torch-backed components
   - later robotics-facing adapters

5. **Artifact/documentation band**
   - serialization
   - schemas
   - reports
   - reproducibility support

The library should not flatten all of this into one namespace of miscellaneous helpers.

## Hidden Graph As A Contract, Not A Generic Graph Object

The package should explicitly adopt the following implementation stance:

- the hidden configuration graph is a contract-defined object
- explored, vista, and quotient graphs are derived overlays or views
- state/action legality is a core contract surface

This should be treated as a serious best-practices decision, not a minor implementation detail.

In particular, the package should not assume that the central hidden graph should be implemented as:

- a `networkx` object
- a giant precomputed adjacency structure
- or a miscellaneous collection of node/edge dictionaries

Those tools can still be useful for diagnostics, exports, or small examples, but they should not define the architecture.

The better professional pattern is:

- define state types
- define primitive action types
- define graph-spec objects or equivalent contracts
- define node-validity and edge-validity predicates
- derive graph views from those contracts

This is the implementation pattern that most naturally supports:

- huge hidden graphs
- partially explored graphs
- online training-time graph growth
- multiple action representations
- quotient overlays carrying coset metadata

This proposal is reinforced by the graph implementation style in the local `rl_counterpoint` project, where graph semantics are defined by typed state/action/spec/predicate modules rather than by a generic graph library object.

## Overlays And Derived Views

The major graph objects in `state_collapser` should not be modeled as unrelated peer graphs.

Instead, they should be modeled as derived layers over one shared graph contract.

Recommended interpretation:

- hidden graph: intensional graph defined by state/action/spec/legality contracts
- explored graph: visited-history restriction of the hidden graph
- vista graph: explored graph plus maintained one-hop forward neighborhoods
- quotient graph: contraction-derived view over a current graph layer, carrying projection and coset data

Best-practices recommendation:

- treat each of these as a distinct class or protocol with explicit provenance
- preserve links back to the source layer they were derived from
- avoid copying graph semantics into each layer independently

This will make it much easier to maintain consistency in:

- reward aggregation
- message passing
- representative lookup
- refinement
- tower-level debugging

## Runtime Update Cycle As A First-Class Design Surface

The mathematical model now suggests a concrete runtime cycle that should be reflected directly in package design.

The library should be organized so that a single training-time step can naturally perform the following sequence:

1. execute a primitive action in the base environment
2. add the resulting state/edge information to the explored graph
3. update the local `1`-hop vista
4. apply the tier-`0` contraction policy to the newly updated local star
5. propagate the induced quotient consequences through the full current tower
6. update the current agent position at every tier
7. compute current step reward and cumulative path reward
8. hand the resulting tower state to training/control logic

This should not be treated as a secondary workflow bolted on after the graph package is designed.

It should be treated as a first-class architectural constraint.

In practice, this means the package should likely expose a runtime object or coordinated service responsible for:

- maintaining current explored/vista/tower state
- applying contraction policy incrementally
- updating tier positions
- computing reward summaries
- returning the current training-facing state after each step

Whether this is called a `TowerRuntime`, `TowerUpdateEngine`, `TowerTracker`, or something similar can be decided later.

The important point is that the package architecture should make this update cycle explicit and central.

## Core Graph Contracts In The Public Design

The package should be explicit, even in its public design documents, that the following are core contracts:

- `State`
- `PrimitiveAction`
- `GraphSpec`
- `is_valid_node(...)`
- `is_valid_edge(...)`

The exact names may still change, but the contract pattern should not.

This matters because downstream components should be written against those contracts rather than silently assuming:

- one fixed action encoding
- one fixed node representation
- one fully materialized adjacency store

The package should support multiple action representations where needed, for example:

- direct next-state action
- delta action
- decoded control action

But the legality and graph-membership semantics should still be routed through a stable graph contract layer.

## Proposed `src/` Layout

A concrete first proposal:

```text
src/state_collapser/
    __init__.py
    _version.py

    core/
        __init__.py
        state.py
        labels.py
        annotations.py
        transitions.py
        similarity.py

    graph/
        __init__.py
        modeled_graph.py
        neighborhoods.py
        stats.py
        views.py

    contract/
        __init__.py
        proposals.py
        selection.py
        equalization.py
        propagation.py
        identity.py
        validation.py

    tower/
        __init__.py
        levels.py
        builders.py
        refinement.py
        maturity.py

    online/
        __init__.py
        notes.py
        message_passing.py
        exploration.py
        local_collapse.py

    train/
        __init__.py
        control.py
        rollout.py
        objectives.py
        policies.py

    adapters/
        __init__.py
        gymnasium.py
        torch.py
        ros2.py

    io/
        __init__.py
        serialization.py
        artifacts.py
        schemas.py
```

The exact filenames can change.

The important thing is that:

- online contraction is not buried inside a generic graph helper
- annotations/notes are treated as first-class
- adapters are visibly adapters
- tower/refinement structure is explicit

## Public API Proposal

The public API should be workflow-oriented, not mechanism-oriented.

Users should be able to approach the package in terms of tasks like:

- build a modeled problem
- analyze it
- construct a tower
- run online tower-building exploration
- train with hierarchical control

So the eventual public API should look more like:

```python
import state_collapser as sc

problem = sc.from_gymnasium(env, projector=...)
stats = sc.analyze(problem)
tower = sc.build_tower(problem, strategy=...)
result = sc.train(problem, tower=tower, controller=...)
```

and less like:

```python
from state_collapser.contract.propagation import internal_equalize_thing
```

The design principle should be:

- public API by user task
- internal modules by engineering mechanism

## Core Domain Objects

The package needs explicit typed records early.

A professional design should avoid making raw dictionaries the main semantic language of the system.

Strong first candidates:

- `ModeledState`
- `StatePayload`
- `StateAnnotationSet`
- `TransitionRecord`
- `LabelValue`
- `ContractionProposal`
- `EqualizationResult`
- `CoarseIdentity`
- `TowerLevel`
- `RefinementPlan`

Recommended practice:

- use `dataclass`-style typed records for stable internal objects
- use protocols for pluggable behaviors
- keep persistent schema design separate from in-memory object design

## State Representation Proposal

The library should treat a state as an agent-usable representational locus in modeled reality.

That means a state may include:

- position or configuration
- scalar values
- tensor values
- categorical values
- string-valued fields
- local notes or marks
- already-induced coarse metadata

Best-practices recommendation:

- distinguish the environment-facing payload from note/annotation overlays
- do not mix every kind of information into one unstructured map
- define named fields and explicit access patterns

A good first decomposition is:

- `payload`: what the modeled state is
- `annotations`: what the agent has written or learned here
- `structural_metadata`: what the contraction/tower machinery has induced here

## Notes, Marks, And Writable Memory

This is one of the most important places where the package must reflect the real system image.

The library should assume that the agent may operate in environments where persistent local marks matter.

Those marks may live:

- in the environment itself
- in the package’s modeled overlay
- or in both

Best-practices proposal:

- treat notes/marks as first-class package concepts
- make their storage and update rules explicit
- do not reduce them to a generic comment field

The package should support:

- writing notes
- reading notes
- propagating notes under contraction
- synchronizing note-relevant knowledge across contracted regions

This is a core reason `state_collapser` is not just a graph package.

## Labels Proposal

The package should preserve the current design conclusion:

- labels are primitive metadata
- labels are local/global agnostic
- labels may be strings or numbers
- nodes and edges may carry multiple labels

Best-practices recommendation:

- make label values immutable
- provide explicit query/predicate helpers
- do not encode ontological meanings like “dimension” directly into the label type system

If a label family induces meaningful large-scale structure, that should be a consequence of the graph and the operation, not of a hard-coded label class hierarchy.

## Contraction Framework Proposal

The package should treat contraction as a structured pipeline, not a one-line merge primitive.

The right internal stages now look something like:

1. identify contraction candidates
2. select a subset according to some strategy
3. form a contraction proposal
4. equalize information across the contracted relation
5. propagate notes/labels/annotations as needed
6. assign or stabilize coarse identity
7. validate the resulting structure

This is the point where the package must reflect the core principle:

**contraction is an information-equalization operation**

That phrase should not live only in conceptual docs.

It should shape the module boundaries.

Best-practices recommendation:

- have an explicit `equalization` subsystem
- have an explicit `identity` subsystem
- separate candidate selection from contraction effects

This is what will let one framework serve both:

- offline full-graph contraction
- online training-time contraction

## Offline And Online Must Share One Abstract Contract

The system now clearly needs two regimes:

- offline contraction over already available graph structure
- online contraction while exploration is still discovering the graph

Best-practices recommendation:

- give them one shared abstract contract
- do not force them into one monolithic implementation

What should be shared:

- state model
- label model
- note/annotation model
- contraction proposal model
- equalization semantics
- coarse identity semantics
- tower level semantics

What can differ:

- candidate discovery
- scheduling
- message-passing mechanisms
- validation cadence

This is probably the most important architectural discipline in the whole package.

## Tower Representation Proposal

The tower should be an explicit object model, not just “a list of graphs.”

At minimum, the tower layer should represent:

- levels
- parent/child tier relationships
- level-local identities
- refinement mappings
- maturity or trust indicators

The maturity indicator matters because the current training-time control principle depends on it:

- collapse unresolved regions
- otherwise act from the lowest trustworthy tier available

So tower objects need to support not just storage, but control decisions.

## Training-Time Control Proposal

The package should encode the current training-time control principle directly:

- if the current region is not yet well collapsed, do local structure-building work
- if a trustworthy coarse tier exists, use the lowest such tier first
- refine upward only as needed to make the move executable

Best-practices recommendation:

- do not model this as a crude mode switch between “exploration” and “training”
- define a controller object that consults local tower maturity
- keep this controller separate from low-level optimization logic

This controller layer should be explicitly modular.

The package should assume from the beginning that the first explore/quotient move-control rule may not be the best one.

So the library should provide a pluggable control-strategy surface, such as a `HierarchicalController` or `ControlPolicy` protocol, whose implementations decide things like:

- when to perform local contraction work
- when to trust an existing coarse tier
- which tier to act from first
- when to refine to a finer tier
- when to continue exploration rather than exploitation

The current proposed rule can be the default controller, but it should not be hard-coded into the tower objects or the contraction primitives.

That way, if a better online control law is discovered later, it should be possible to implement it as a new controller rather than rewriting the rest of the package architecture.

That will make the package’s online behavior feel like one coherent system instead of two competing jobs.

## Gymnasium Adapter Proposal

The Gymnasium adapter should be thin, but not trivial.

It should not assume:

- observations are already modeled states
- actions are already the right edge objects
- note-writing semantics are absent

Instead, the adapter should make the following hooks explicit:

- state projection
- action interpretation
- optional note-write interpretation
- optional state-similarity helpers
- optional persistence hooks for marks/annotations

This is the cleanest way to keep Gymnasium as a shell without letting it dictate the ontology of the package.

## Torch Adapter Proposal

The Torch adapter should gather the learnable pieces without infecting the whole package.

Likely Torch-using components:

- embedders
- learned similarity metrics
- contraction scorers
- message-passing modules
- tier-local policies
- refinement modules

Best-practices recommendation:

- structural tests should run without Torch
- Torch-backed tests should live behind optional dependency markers
- no core object model should require importing Torch tensors just to exist

## RL Terminology Proposal

The RL-facing language of the package should be as familiar as possible to users coming from mainstream Python RL tooling.

The best naming anchor for this purpose is:

- `gymnasium` for environment API terms
- `Stable-Baselines3`-style vocabulary for single-machine RL training concepts

`RLlib` terminology should be borrowed only where the package genuinely introduces distributed runtime components.

`Tianshou` and `CleanRL` can still be useful reference points, but they should not be the primary naming authority for this package.

### Recommended user-facing RL names

Use these names wherever they fit without distortion:

- `environment`
- `observation`
- `action`
- `reward`
- `terminated`
- `truncated`
- `transition`
- `episode`
- `trajectory`
- `rollout`
- `policy`
- `critic`
- `value_function`
- `replay_buffer`
- `rollout_buffer`
- `trainer`
- `evaluation`
- `checkpoint`
- `vector_env` or `vec_env`

These terms are already widely legible to people who know Gymnasium and Stable-Baselines3-style RL codebases.

### Recommended package-specific names

Introduce novel names only where the package is actually doing something novel:

- `modeled_state`
- `annotation`
- `note`
- `contraction`
- `equalization`
- `coarse_identity`
- `tower_level`
- `refinement`
- `hierarchical_controller`

The rule should be:

- standard RL concept -> standard RL name
- genuinely new structural concept -> new package-specific name

### Names to avoid as the default user-facing surface

Avoid making these the primary public vocabulary unless a module genuinely implements the exact concept:

- `collector`
- `batch` as the main semantic name for all RL data
- `learner` as the default name for the whole training object
- `env_runner`
- `rl_module`
- `algorithm_config`

These names are not wrong, but they pull the surface toward the internal terminology of specific frameworks such as Tianshou or RLlib and are more likely to confuse users who expect a Gymnasium plus SB3-style naming surface.

### Reserved terminology

Some names should be reserved for narrower meanings:

- use `learner` only if there is a distinct optimization component separate from the overall trainer
- use `env_runner` only if the package later introduces a genuinely distributed or orchestrated environment-running subsystem
- use `rl_module` only if the package intentionally adopts an RLlib-like model abstraction layer
- use `collector` only if there is a distinct data-collection object whose job is specifically to gather rollouts into storage

This helps keep the public surface stable and easy to parse.

### Terminology consistency rule

The package should not rename common RL pieces unnecessarily.

For example:

- do not rename `policy` to something more exotic unless it is no longer really a policy
- do not rename `trajectory` to something idiosyncratic if it still means a trajectory
- do not rename `replay_buffer` or `rollout_buffer` if those are what they are

Terminology novelty should be spent only on the parts of the package that are actually novel.

## ROS 2 Adapter Proposal

The ROS 2 adapter should be aspirational but separate.

Best-practices recommendation:

- do not place robotics runtime concerns in core modules
- create ROS-facing bridges only when the core state/tower contracts are stable enough
- treat ROS integration as transport/runtime glue around a core model that already exists

That keeps the package focused on what it is actually trying to solve.

## Artifact And Serialization Proposal

This project is structural enough that artifacts need to be first-class early.

The package should be able to serialize:

- modeled states
- annotations/notes
- contraction artifacts
- tower levels
- tower maturity summaries
- graph statistics

Best-practices recommendation:

- define schemas early
- version them explicitly
- separate in-memory Python objects from persisted representations

This will matter for:

- reproducibility
- inspection
- debugging
- comparisons between offline and online tower building

## Testing Proposal

The package should be tested as a professional library, not as an ad hoc research notebook export.

That means:

- keep `src/` layout
- keep package tests in `tests/`
- test installed/editable behavior
- keep invariants central

Important test layers:

1. import and metadata smoke tests
2. domain-object invariant tests
3. label and annotation tests
4. contraction/equalization tests
5. tower/refinement tests
6. Gymnasium adapter tests
7. online note-writing / message-passing tests
8. end-to-end miniature workflow tests

Critical invariants to test:

- contraction equalizes the required information
- labels remain primitive metadata
- notes persist and propagate correctly
- coarse identities remain meaningful after equalization
- every useful coarse transition has a refinement story
- offline and online contraction satisfy the same abstract contract where intended

## Documentation Proposal

The library should be documented in the same layered way it is implemented.

Recommended documentation set:

1. README for package framing
2. quickstart for first install and first example
3. conceptual guide for modeled reality, notes, contraction, and towers
4. API guide by workflow
5. advanced design notes
6. examples for offline and online regimes

The docs should make one thing especially clear:

- Gymnasium provides the env shell
- `state_collapser` provides the modeled-state / contraction / tower structure

That distinction should never again be left implicit.

## Recommended First Concrete Implementation Slice

The first real vertical slice should match the actual system image, not a generic graph library warm-up.

Recommended first slice:

1. define `ModeledState`, labels, annotations, and transitions
2. define a tiny discrete note-writing environment example
3. build the first Gymnasium adapter around that example
4. implement one local contraction plus equalization primitive
5. represent the resulting coarse identity explicitly
6. build one two-level tower from repeated use of that primitive
7. test refinement from coarse move back to fine move

That slice would prove:

- Gymnasium compatibility
- writable-note compatibility
- contraction-as-equalization
- tower emergence
- coarse/fine distinction

all at once, in the smallest honest example.

## Final Proposal

The best-practices package shape for `state_collapser` is:

- a typed core built around modeled states, labels, notes, and transitions
- an explicit contraction/equalization layer
- an explicit tower/refinement layer
- a training-time control layer organized by tower maturity
- thin adapters for Gymnasium, Torch, and later ROS 2
- strong artifacts, tests, and docs from the beginning

That is the first concrete proposal most aligned with the actual system we have now clarified.
