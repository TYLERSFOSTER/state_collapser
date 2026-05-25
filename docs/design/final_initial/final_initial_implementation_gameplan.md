# Final Initial Implementation Gameplan

## Status

This document is the first concrete implementation gameplan for the implementation blueprint in:

- `final_initial_blueprint.md`

It is intentionally operational.

It is not another design discussion.

Its job is to specify the order of implementation, the tests that must exist, and the specific actions required to reach a coherent first implementation.

This plan is organized in **Phase.Stage.Action** form.

Each action should be treated as atomic enough to review and validate.

## Execution Contract For Implementation

1. **Authoritative sources**
- [final_initial_blueprint.md]([state_collapser repository root]/docs/design/final_initial/final_initial_blueprint.md)
- [final_initial_implementation_gameplan.md]([state_collapser repository root]/docs/design/final_initial/final_initial_implementation_gameplan.md)

These are the implementation law.
I should treat older design docs as background only unless the blueprint/gameplan explicitly points back to them.

2. **Execution unit**
- The atomic unit of work is exactly one `Phase.Stage.Action`.
- I do not merge actions, skip actions, reorder actions, or reinterpret actions unless the gameplan itself says to.

3. **Completion loop**
For every `Phase.Stage.Action`, I must do this:
- read the action text again before touching code
- implement only that action
- verify that action against its stated deliverable/tests
- compare the result back to the blueprint/gameplan
- log what changed, blockers, and surprises
- only then move to the next action

4. **No silent simplification**
- I do not build a “minimal slice”
- I do not substitute a weaker version
- I do not “scaffold now, deepen later”
- I do not swap in a more convenient architecture
- I do not infer permission from momentum

If I think an action is too hard, unclear, or would require a simplification, I stop and ask you.

5. **Consultation triggers**
I must stop and consult you if:
- an action is ambiguous
- the blueprint and gameplan seem to conflict
- the codebase reality conflicts with the gameplan
- a required dependency/tooling change was not planned
- a test expectation seems wrong
- I believe the gameplan should be modified
- I am tempted to generalize, simplify, postpone, or substitute

6. **Gameplan modification rule**
- I never modify the gameplan while implementing.
- If I think it needs to change, I tell you:
  - exact `Phase.Stage.Action`
  - why it fails as written
  - proposed amendment
  - consequences if unchanged

Then I wait for your decision.

7. **Status reporting format**
While implementing, I should report in terms of the gameplan, e.g.:
- `Phase 1.Stage 2.Action 3 in progress`
- `Action complete; verified against X/Y/Z`
- `Blocked at Phase ... because ...`

Not vague summaries like “I built the core scaffold.”

8. **Testing rule**
- Tests are part of the action, not optional cleanup after.
- I should run exactly the tests implied by the current action, then broader regression tests when the gameplan says to.

9. **Artifact/log rule**
- Keep the running engineer log updated as implementation proceeds.
- Record pivots, failures, surprises, and any place where I had to stop for your guidance.

10. **Your standing instruction I should carry forward**
- The gameplan is law.
- Follow it to the letter.
- Re-check it after every action.
- Do not modify it without consulting you first.

## Global Implementation Rules

### Rule 1

Tests should be written as close as possible to the introduction of the corresponding contract.

### Rule 2

The implementation should privilege inspectability and correctness over optimization in the first pass.

### Rule 3

Performance-oriented changes such as encoded label arrays, vectorization, or GPU-backed acceleration should only be introduced after the logical runtime model is correct and test-covered.

### Rule 4

All runtime semantics should be validated first in the toy environment before any attempt is made to generalize outward.

## Phase 1 — Establish The Core Contract Surface

### Stage 1.1 — Create Core Type Modules

#### Action 1.1.1

Create:

- `src/state_collapser/core/state.py`
- `src/state_collapser/core/action.py`
- `src/state_collapser/core/edges.py`
- `src/state_collapser/core/labels.py`
- `src/state_collapser/core/annotations.py`
- `src/state_collapser/core/rewards.py`

Define empty or minimal exported symbols for:

- `State`
- `PrimitiveAction`
- `BaseEdge`
- `NodeAnnotationStore`
- `VistaPayload`
- reward summary objects

#### Action 1.1.2

Implement `State` as a frozen dataclass with:

- stable identity or canonical payload
- readable repr
- stable equality
- stable hash

#### Action 1.1.3

Implement `PrimitiveAction` as a frozen dataclass with:

- action identity or canonical payload
- optional labels
- readable repr
- stable equality
- stable hash

#### Action 1.1.4

Implement `BaseEdge` as a frozen dataclass with:

- `source`
- `action`
- `target`
- optional labels

### Stage 1.2 — Core Unit Tests

#### Action 1.2.1

Add tests:

- `tests/core/test_state.py`
- `tests/core/test_action.py`
- `tests/core/test_edges.py`

#### Action 1.2.2

Implement unit tests for `State`:

- equality of identical payloads
- inequality of distinct payloads
- stable hash
- immutability failure on mutation attempt

#### Action 1.2.3

Implement unit tests for `PrimitiveAction`:

- equality
- inequality
- stable hash
- immutability

#### Action 1.2.4

Implement unit tests for `BaseEdge`:

- edge equality
- edge hashing
- correct source/action/target field preservation

## Phase 2 — Hidden Graph Contract

### Stage 2.1 — Graph Spec And Hidden Graph

#### Action 2.1.1

Create:

- `src/state_collapser/graph/spec.py`
- `src/state_collapser/graph/hidden_graph.py`

#### Action 2.1.2

Define `GraphSpec` as an immutable contract object for environment-specific graph rules.

#### Action 2.1.3

Define the `HiddenGraph` protocol with required methods:

- `is_valid_state`
- `is_valid_action`
- `apply_action`
- `is_valid_edge`
- `out_actions`
- `out_neighbors`
- `out_edges`

### Stage 2.2 — Hidden Graph Unit Tests

#### Action 2.2.1

Add:

- `tests/graph/test_hidden_graph_contract.py`

#### Action 2.2.2

Implement contract tests using a tiny stub hidden graph:

- `apply_action` agrees with `is_valid_edge`
- outgoing neighbors derive from outgoing actions
- invalid states/actions are rejected

## Phase 3 — Explored Graph Layer

### Stage 3.1 — Explored Graph Implementation

#### Action 3.1.1

Create:

- `src/state_collapser/graph/explored_graph.py`

#### Action 3.1.2

Implement `ExploredGraph` with:

- visited state store
- visited edge store
- current base state
- ordered current base path

Required methods:

- `has_state`
- `has_edge`
- `add_state`
- `add_edge`
- `visited_states`
- `visited_edges`
- `current_state`
- `current_path`

### Stage 3.2 — Explored Graph Unit Tests

#### Action 3.2.1

Add:

- `tests/graph/test_explored_graph.py`

#### Action 3.2.2

Implement tests for:

- adding a state once
- adding multiple states
- adding edges
- path ordering
- current-state tracking

## Phase 4 — Vista Graph And Annotation Store

### Stage 4.1 — Annotation Store

#### Action 4.1.1

Implement `NodeAnnotationStore` in `core/annotations.py`.

Required capabilities:

- local labels
- local notes
- pushed payload receipt
- pulled payload receipt
- tier-indexed cumulative outgoing-edge knowledge

#### Action 4.1.2

Define cumulative query methods, for example:

- `outgoing_knowledge_exact(tier)`
- `outgoing_knowledge_upto(tier)`

### Stage 4.2 — Vista Payload

#### Action 4.2.1

Implement `VistaPayload` in `core/annotations.py` or nearby.

Required contents:

- outgoing edge set
- reachable target states
- relevant labels
- contraction/coset marks

### Stage 4.3 — Vista Graph

#### Action 4.3.1

Create:

- `src/state_collapser/graph/vista_graph.py`
- `src/state_collapser/graph/local_star.py`

#### Action 4.3.2

Implement `VistaGraph` with:

- explored graph reference or overlay
- local `1`-hop neighborhood cache
- node annotation stores
- push/pull support

Required methods:

- `refresh_local_vista`
- `vista_neighbors`
- `vista_edges`
- `push_message`
- `pull_message`
- `node_payload`

#### Action 4.3.3

Implement `LocalStar` as the tier-`0` selection input object.

### Stage 4.4 — Vista Layer Unit Tests

#### Action 4.4.1

Add:

- `tests/graph/test_annotations.py`
- `tests/graph/test_vista_graph.py`
- `tests/graph/test_local_star.py`

#### Action 4.4.2

Implement tests for `NodeAnnotationStore`:

- storing labels and notes
- receiving push/pull payloads
- exact-tier query
- cumulative `<= k` query

#### Action 4.4.3

Implement tests for `VistaPayload`:

- payload contents preserved
- labels preserved
- outgoing-edge possibility data preserved

#### Action 4.4.4

Implement tests for `VistaGraph`:

- `1`-hop refresh populates vista
- push operation updates target-side annotation state
- pull operation updates source-side annotation state
- cumulative outgoing-edge knowledge grows appropriately

#### Action 4.4.5

Implement tests for `LocalStar`:

- local star reflects current vista data
- local labels and annotations are included

## Phase 5 — Contraction Policy Layer

### Stage 5.1 — Contraction Policy Interface

#### Action 5.1.1

Create:

- `src/state_collapser/contract/policy.py`
- `src/state_collapser/contract/selection.py`

#### Action 5.1.2

Define:

- `ContractionPolicy`
- `EdgeSelection`

### Stage 5.2 — Label-Based Policy

#### Action 5.2.1

Implement a label-based policy that selects edges from a local star by label predicate.

### Stage 5.3 — Seeded-Random Policy

#### Action 5.3.1

Implement a seeded-random policy that samples outgoing edges from a local star.

### Stage 5.4 — Contraction Policy Unit Tests

#### Action 5.4.1

Add:

- `tests/contract/test_label_policy.py`
- `tests/contract/test_random_policy.py`

#### Action 5.4.2

Implement tests for the label-based policy:

- correct edges selected by label
- only requested labels selected
- no tower mutation performed by the policy itself

#### Action 5.4.3

Implement tests for the random policy:

- deterministic output under fixed seed
- output is subset of local star
- no mutation performed by the policy itself

## Phase 6 — Quotient Tier Views

### Stage 6.1 — Projection And Coset Storage

#### Action 6.1.1

Create:

- `src/state_collapser/quotient/projection.py`
- `src/state_collapser/quotient/cosets.py`
- `src/state_collapser/quotient/tier_view.py`

#### Action 6.1.2

Implement explicit:

- state-to-quotient-node projection maps
- edge-to-quotient-edge projection maps
- quotient-node membership maps
- quotient-edge membership maps

#### Action 6.1.3

Implement cumulative tier knowledge on each quotient view so that outgoing-edge query at tier `k` is cumulative.

### Stage 6.2 — Quotient Tier Unit Tests

#### Action 6.2.1

Add:

- `tests/quotient/test_projection.py`
- `tests/quotient/test_cosets.py`
- `tests/quotient/test_tier_view.py`

#### Action 6.2.2

Implement tests for:

- projection correctness
- reverse-membership correctness
- nested cumulative outgoing-edge query semantics
- current tier-position storage

## Phase 7 — Reward Layer

### Stage 7.1 — Reward Objects

#### Action 7.1.1

Implement:

- `StepReward`
- `PathRewardSummary`
- `QuotientRewardSummary`

### Stage 7.2 — Reward Aggregation Logic

#### Action 7.2.1

Implement primitive step reward support.

#### Action 7.2.2

Implement cumulative base-path reward as weighted aggregation over primitive rewards.

#### Action 7.2.3

Implement quotient reward aggregation over boundary-crossing preimage contributors only.

### Stage 7.3 — Reward Unit Tests

#### Action 7.3.1

Add:

- `tests/core/test_rewards.py`
- `tests/quotient/test_reward_aggregation.py`

#### Action 7.3.2

Implement tests for:

- step reward construction
- cumulative weighted path reward
- quotient mean reward computation
- exclusion of internal collapsed edges
- correct use of boundary-crossing contributors

## Phase 8 — Tower Runtime

### Stage 8.1 — Runtime Snapshot

#### Action 8.1.1

Create:

- `src/state_collapser/tower/snapshot.py`

#### Action 8.1.2

Implement `RuntimeSnapshot` with:

- current base state
- explored graph
- vista graph
- ordered quotient tiers
- current position at every tier
- current step reward
- cumulative path reward
- quotient-tier reward summaries

### Stage 8.2 — Tower Runtime Engine

#### Action 8.2.1

Create:

- `src/state_collapser/tower/runtime.py`

#### Action 8.2.2

Implement `TowerRuntime.reset(...)`.

#### Action 8.2.3

Implement `TowerRuntime.step(...)` following the exact update order in the blueprint.

#### Action 8.2.4

Implement full immediate tower propagation after each newly discovered state.

### Stage 8.3 — Trustworthiness Placeholder

#### Action 8.3.1

Create:

- `src/state_collapser/tower/trustworthiness.py`

#### Action 8.3.2

Define `TrustworthinessPolicy` as an extension point only.

Do not make it a first-pass runtime dependency.

### Stage 8.4 — Runtime Unit Tests

#### Action 8.4.1

Add:

- `tests/tower/test_snapshot.py`
- `tests/tower/test_runtime.py`

#### Action 8.4.2

Implement tests for:

- reset snapshot shape
- step update order
- immediate full tower update
- cross-tier position update
- runtime snapshot completeness

## Phase 9 — First Toy Environment

### Stage 9.1 — Environment Design

#### Action 9.1.1

Create:

- `src/state_collapser/examples/robot_constraint_toy.py`

#### Action 9.1.2

Design a small discretized robot-arm-style constraint environment with:

- opaque global parameterization
- inspectable local states
- meaningful primitive transitions
- region-specific labels where applicable

### Stage 9.2 — Hidden Graph Binding

#### Action 9.2.1

Bind the toy environment to a `GraphSpec` and `HiddenGraph` implementation.

### Stage 9.3 — Environment Tests

#### Action 9.3.1

Add:

- `tests/examples/test_robot_constraint_toy.py`

#### Action 9.3.2

Implement tests for:

- valid state generation
- valid action generation
- edge legality
- local label availability in some regions
- absence of label support in other regions where intended

## Phase 10 — End-To-End Vertical Slice

### Stage 10.1 — Runtime Through Toy Environment

#### Action 10.1.1

Write an end-to-end integration path that:

- initializes the toy environment
- creates a `TowerRuntime`
- steps through several primitive actions
- updates the full tower
- computes rewards
- returns snapshots

### Stage 10.2 — End-To-End Tests

#### Action 10.2.1

Add:

- `tests/integration/test_vertical_slice.py`

#### Action 10.2.2

Implement tests verifying:

- discovered graph grows over time
- vista graph grows over time
- push/pull changes annotation state
- both contraction policies work in the same runtime pipeline
- quotient-tier views update cumulatively
- reward aggregation works
- runtime snapshots remain coherent

## Phase 11 — Gymnasium Adapter

### Stage 11.1 — Adapter Surface

#### Action 11.1.1

Create:

- `src/state_collapser/adapters/gymnasium.py`

#### Action 11.1.2

Implement a thin adapter layer that:

- wraps the toy environment/runtime
- exposes Gymnasium-style `reset` and `step`
- preserves the richer runtime snapshot internally or in `info`

### Stage 11.2 — Adapter Tests

#### Action 11.2.1

Add:

- `tests/adapters/test_gymnasium_adapter.py`

#### Action 11.2.2

Implement tests for:

- Gymnasium-style reset output
- Gymnasium-style step output
- preservation of runtime metadata in adapter-visible structures

## Phase 12 — Documentation And Validation Pass

### Stage 12.1 — Sync Public Docs

#### Action 12.1.1

Update public/package docs so they match the implemented blueprint.

Minimum targets:

- README
- `package_usage.md`
- `public_api.md`

### Stage 12.2 — Sync Design Docs

#### Action 12.2.1

Update design docs that were superseded or sharpened by implementation reality.

Minimum targets:

- `module_design_desiderata.md`
- `package_best_practices_proposal.md`
- `reward_locality_for_quotient_training.md`

### Stage 12.3 — Validation Checklist

#### Action 12.3.1

Run the full unit/integration suite and verify:

- all core contracts are instantiated in code
- all tests described above exist
- the toy environment exercises both contraction styles
- the tower updates immediately at every discovered-state step
- cumulative tier query semantics are correct
- internal collapsed edges are excluded from outgoing quotient reward aggregation

## Summary Of Critical Test Files

The implementation should include, at minimum:

- `tests/core/test_state.py`
- `tests/core/test_action.py`
- `tests/core/test_edges.py`
- `tests/core/test_rewards.py`
- `tests/graph/test_hidden_graph_contract.py`
- `tests/graph/test_explored_graph.py`
- `tests/graph/test_annotations.py`
- `tests/graph/test_vista_graph.py`
- `tests/graph/test_local_star.py`
- `tests/contract/test_label_policy.py`
- `tests/contract/test_random_policy.py`
- `tests/quotient/test_projection.py`
- `tests/quotient/test_cosets.py`
- `tests/quotient/test_tier_view.py`
- `tests/quotient/test_reward_aggregation.py`
- `tests/tower/test_snapshot.py`
- `tests/tower/test_runtime.py`
- `tests/examples/test_robot_constraint_toy.py`
- `tests/integration/test_vertical_slice.py`
- `tests/adapters/test_gymnasium_adapter.py`

## Final Gameplan Statement

If this Phase.Stage.Action plan is followed in order, the project should reach a first honest implementation of the current blueprint without requiring major design reinterpretation during coding.
