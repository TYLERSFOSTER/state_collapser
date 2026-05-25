# `rl_counterpoint_v3` Implementation Gameplan

## Status

This document is the implementation gameplan for:

- [01_002_rl_counterpoint_v3_blueprint.md]([state_collapser repository root]/docs/design/test_design/rl_counterpoint_v3/01_002_rl_counterpoint_v3_blueprint.md)

It is written under the authority of:

- [01_001_rl_counterpoint_v3_transformation_report.md]([state_collapser repository root]/docs/design/test_design/rl_counterpoint_v3/01_001_rl_counterpoint_v3_transformation_report.md)
- [docs/design/test_design/evaluation_strategy.md]([state_collapser repository root]/docs/design/test_design/evaluation_strategy.md)
- [docs/prime_directive/prime_directive.md]([state_collapser repository root]/docs/prime_directive/prime_directive.md)
- [docs/prime_directive/common_failure_mode_001.md]([state_collapser repository root]/docs/prime_directive/common_failure_mode_001.md)
- [docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md]([state_collapser repository root]/docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md)
- [docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md]([state_collapser repository root]/docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md)

It is intentionally operational.

It is not:

- another design sketch
- a music-theory note
- a partial port checklist
- a loose idea bank

Its job is to define:

- the exact implementation order
- the concrete target files
- the validation sequence
- the stop conditions
- the acceptance criteria

This gameplan is organized in `Phase.Stage.Action` form.

## Execution Contract

### Rule 1 - Gameplan Is Law

When implementation begins:

- this gameplan is law
- the three-voice blueprint is law
- the transformation report is law
- the prime-directive stack is law
- I do not silently collapse scope
- I do not silently reintroduce the old explicit `rl_counterpoint` rank tower
- I do not silently weaken the example into a decorative symbolic toy

### Rule 2 - Single-Action Discipline

During execution:

- one `Phase.Stage.Action` is the atomic implementation unit
- I re-read the exact action text before editing code or docs
- I verify the action outcome before advancing
- I do not batch together several action items under the excuse that they are "related"

### Rule 3 - Mandatory Full-Stop Conditions

I must full-stop and return to the Project Owner if:

- the owner later reverses the `v3` normalization and requires a dotted code-package label inside `src/`, because that would reintroduce a Python importability failure
- the first valid three-voice start-set construction is empty, terminal-only, or locally frozen
- the legal outgoing transition structure from curated start states collapses to near-zero and cannot be repaired without a new design decision not fixed by the blueprint
- the edge-legality rules require importing substantial long-history or sequence-model semantics to remain meaningful
- the reward surface cannot be kept narrow without reimporting old `rl_counterpoint` reward bundles
- the implementation begins to require explicit rank-wise scaffold semantics, frozen parent voices, or staged hierarchy to work at all
- the state/action graph becomes too large to inspect under the first-scope spec and needs a new owner decision about bounds
- the runtime surface appears to require new package-level abstractions not already compatible with the existing example/runtime pattern

### Rule 4 - No Smuggled Tower

I must not:

- import the old explicit one-voice/two-voice/three-voice training decomposition
- hide rank semantics inside reset logic, reward logic, or runtime projection helpers
- treat the middle voice as a pre-authored bridge to a staged curriculum
- give the runtime a hand-authored hierarchy over the flat counterpoint problem

The environment must remain:

- flat
- three-voice from the start
- constrained by hidden node and edge legality

### Rule 5 - No Decorative Music-Theory Complexity

I must not:

- import broad music-theory machinery merely because it existed in the old repo
- add cadence micro-taxonomies, transformer-side observation features, or large reward ontologies before the first slice is working
- widen the state/action/reward surface until the example is no longer inspectable

The first implementation must remain:

- sharp
- small
- real
- testable

### Rule 6 - Running Log Requirement

When implementation begins, maintain a running log at:

- `docs/design/test_design/rl_counterpoint_v3/01_004_rl_counterpoint_v3_implementation_log.md`

The log must record:

- completed `Phase.Stage.Action` items
- validation results
- owner clarifications
- surprises
- blockers
- any forced full-stop conditions

## Canonical Target File Set

### Authoritative design artifacts

- `docs/design/test_design/rl_counterpoint_v3/01_001_rl_counterpoint_v3_transformation_report.md`
- `docs/design/test_design/rl_counterpoint_v3/01_002_rl_counterpoint_v3_blueprint.md`
- `docs/design/test_design/rl_counterpoint_v3/01_003_rl_counterpoint_v3_implementation_gameplan.md`
- `docs/design/test_design/rl_counterpoint_v3/01_004_rl_counterpoint_v3_implementation_log.md`

### Code package targets

The design label is:

- `rl_counterpoint_v3`

The import-safe code package target should be:

- `src/state_collapser/examples/rl_counterpoint_v3/`

If the owner explicitly requires the literal dotted directory to remain the executable package target, implementation must full-stop before code work proceeds.

The code package should eventually include:

- `src/state_collapser/examples/rl_counterpoint_v3/__init__.py`
- `src/state_collapser/examples/rl_counterpoint_v3/env.py`
- `src/state_collapser/examples/rl_counterpoint_v3/runtime.py`
- `src/state_collapser/examples/rl_counterpoint_v3/training.py`

### Test targets

The first-scope test suite should eventually include:

- `tests/examples/test_rl_counterpoint_v3_validity.py`
- `tests/examples/test_rl_counterpoint_v3_transitions.py`
- `tests/examples/test_rl_counterpoint_v3_rewards.py`
- `tests/examples/test_rl_counterpoint_v3_gymnasium.py`
- `tests/examples/test_rl_counterpoint_v3_runtime_integration.py`
- `tests/examples/test_rl_counterpoint_v3_tower_training.py`

If helper-level tests are needed, they may be added, but not at the expense of these behavior-facing tests.

### Optional evaluation-surface targets

If the example reaches full runtime readiness without extra design drift, the implementation may also bind it into:

- `src/state_collapser/examples/tower_depth_probe.py`
- `tests/examples/test_tower_depth_probe.py`

This is not allowed to come before core env/runtime/training validity.

## Global Implementation Rules

### Rule A

The first implementation is a:

- three-voice flat RL problem

not:

- a curriculum
- a rank tower
- a staged port of old training artifacts

### Rule B

The explicit graph state must remain:

- concrete
- small
- inspectable

The first canonical state remains:

- `(bass_pitch, inner_pitch, upper_pitch, beat_index)`

with episode-history machinery held outside explicit graph state unless the blueprint is revised.

### Rule C

The action surface remains the bounded simultaneous per-voice delta lattice.

It must not be replaced by:

- hand-authored chord templates
- pre-baked contrapuntal maneuvers
- hierarchical sub-actions

### Rule D

The first reward surface remains:

- narrow
- structured
- diagnostically inspectable

It must not collapse to either:

- a pure sparse terminal-only reward
- or an overgrown imported reward ontology

### Rule E

The runtime must expose a flat hidden graph to the package.

It must not:

- encode the old rank decomposition
- own a hand-authored tower
- treat lower voices as frozen parent scaffolds

### Rule F

The first implementation must be evaluation-oriented.

That means it must support, at minimum:

- validity inspection
- legal transition inspection
- runtime integration
- tower-aware training smoke runs

## Phase 1 - Establish The Implementation Artifact Surface

### Stage 1.1 - Create The Running Log

#### Action 1.1.1

Create:

- `docs/design/test_design/rl_counterpoint_v3/01_004_rl_counterpoint_v3_implementation_log.md`

The log must include:

- status
- authoritative sources
- action-completion entries
- validation-result entries
- owner-clarification entries
- blocker entries

### Stage 1.2 - Bind The Authoritative Source Set

#### Action 1.2.1

Record in the running log that the implementation is governed by:

- the transformation report
- the three-voice blueprint
- the general evaluation strategy
- the prime-directive stack

#### Action 1.2.2

Record in the running log that the central non-negotiable design claim is:

- the first `rl_counterpoint_v3` example is a three-voice flat constrained RL problem

#### Action 1.2.3

Record in the running log the explicit banned regressions:

- no imported rank hierarchy
- no transformer stack
- no artifact lineage system
- no checkpoint-driven package surface
- no staged parent-child scaffold semantics

## Phase 2 - Resolve The Package Naming And File-Surface Binding

### Stage 2.1 - Inspect The Existing Example Folder Situation

#### Action 2.1.1

Inspect the current example folder state under:

- `src/state_collapser/examples/`

and record whether:

- `rl_counterpoint_v3/` exists
- an import-safe package directory already exists
- any accidental duplicate surfaces are present

This action is diagnostic only.

### Stage 2.2 - Bind The Code-Package Naming Law

#### Action 2.2.1

Record that:

- `rl_counterpoint_v3` is both the design/document label and the import-safe code package name

#### Action 2.2.2

If the owner has not explicitly authorized a different code-package name, do not invent alternatives beyond:

- `rl_counterpoint_v3`

#### Action 2.2.3

If the owner insists that the dotted directory itself must be the importable code package, full-stop.

This is a Python importability reality condition, not a stylistic preference.

### Stage 2.3 - Create Or Normalize The Example Package Surface

#### Action 2.3.1

Create or normalize the code package directory so the executable package target is:

- `src/state_collapser/examples/rl_counterpoint_v3/`

Do not yet populate it with speculative code beyond what the next phases authorize.

#### Action 2.3.2

Record in the running log any filesystem normalization performed from the originally created dotted folder surface.

## Phase 3 - Define The `env.py` Structural Skeleton

### Stage 3.1 - Establish The Canonical Data Types

#### Action 3.1.1

Create the first `env.py` skeleton with canonical dataclass and type aliases for:

- `RlCounterpointState`
- `RlCounterpointGraphSpec`
- `StepDelta`
- any first-pass reward context/result records authorized by the blueprint

This step is type-surface construction only.

#### Action 3.1.2

Bind the explicit state to:

- `bass_pitch`
- `inner_pitch`
- `upper_pitch`
- `beat_index`

Do not add extra graph-state coordinates unless the blueprint is revised.

#### Action 3.1.3

Bind the graph spec to the first-scale fields authorized by the blueprint, including:

- tonic pitch class
- pitch bounds
- measure size
- max steps
- max step size
- allowed adjacent interval classes
- allowed outer interval classes
- forbidden parallel interval classes
- max outer span
- strict-order requirement

If additional fields seem needed, full-stop unless they are clearly representable as narrow derived helpers rather than new authority-bearing spec fields.

### Stage 3.2 - Establish Constant And Alias Surfaces

#### Action 3.2.1

Define the small first-scope exported constants needed for the example package, such as:

- default graph spec
- action-count derivation
- max-steps exposure

These constants must reflect the actual spec rather than duplicating disconnected values.

#### Action 3.2.2

Do not define public constants that imply a hidden hierarchy, such as:

- rank counts
- parent/child role labels
- stage-local curriculum maxima

## Phase 4 - Implement Ambient Action Enumeration And Basic Transition Proposal

### Stage 4.1 - Build The Ambient Delta Lattice

#### Action 4.1.1

Implement the ambient primitive action family:

- `{ -d, ..., +d }^3 \\ {(0, 0, 0)}`

for the configured `max_step_size`.

This step must produce a stable indexable action ordering suitable for:

- discrete action IDs
- repeatable tests
- runtime translation

#### Action 4.1.2

Expose helpers for:

- action index to `StepDelta`
- `StepDelta` to action index if the reverse map is useful and total

These helpers must remain flat and literal.

### Stage 4.2 - Implement Candidate Next-State Proposal

#### Action 4.2.1

Implement the pure candidate-next-state transform:

- apply three signed pitch deltas
- advance `beat_index` modulo `measure_size`

This step must not yet decide legality.

#### Action 4.2.2

Implement a small structured transition-proposal result if needed for tests and inspection.

Do not overgrow it into a tower or training artifact object.

## Phase 5 - Implement Node Legality

### Stage 5.1 - Range And Ordering Rules

#### Action 5.1.1

Implement the first node-validity helpers for:

- pitch-range checks
- strict voice ordering
- beat-index range

These are the lowest-level hidden-node-membership conditions.

#### Action 5.1.2

Ensure the ordering law is strict:

- `bass_pitch < inner_pitch < upper_pitch`

Do not weaken to non-strict order.

### Stage 5.2 - Vertical Interval And Span Rules

#### Action 5.2.1

Implement helpers for:

- adjacent interval classes modulo 12
- outer interval class modulo 12
- total outer span

#### Action 5.2.2

Implement node-validity checks enforcing:

- allowed adjacent interval classes
- allowed outer interval classes
- max outer span

These must be explicit and inspectable rather than embedded opaquely in one large predicate body.

### Stage 5.3 - Harmonic Root-Class Admissibility

#### Action 5.3.1

Implement the narrow first-pass root-class admissibility rule over the bass pitch class.

This should descend directly from the blueprint’s "allowed harmonic root-class family" requirement.

#### Action 5.3.2

Keep this first slice narrow.

Do not import broad harmonic-state machines or old repo progression logic.

### Stage 5.4 - Compose The Canonical Node Predicate

#### Action 5.4.1

Compose the canonical public node predicate, e.g.:

- `is_valid_state(...)`

from the previously implemented rule helpers.

#### Action 5.4.2

Add small enumeration helpers for valid-state inspection only if they remain tractable under the first-scope graph spec.

If exact full-state enumeration is not tractable enough for example-level tests, full-stop before inventing a weaker substitute.

## Phase 6 - Implement Edge Legality

### Stage 6.1 - Per-Voice Motion Bound Rules

#### Action 6.1.1

Implement helpers that verify each voice motion lies within the configured step bound.

This must remain derived from the same `max_step_size` that defines the action lattice.

### Stage 6.2 - Outer-Voice Parallel-Perfect Rule

#### Action 6.2.1

Implement the first-pass parallel-perfect rejection rule for the outer voices:

- if bass and upper move in the same direction
- and the outer interval class remains in the configured perfect-set family
- reject the transition

#### Action 6.2.2

Keep the rule explicit and local.

Do not import a broad motion-class taxonomy from the old repo.

### Stage 6.3 - Adjacency-Collapse And Optional Middle-Voice Guard

#### Action 6.3.1

Implement the exact unison-adjacency collapse rejection via the target-state legality surface.

#### Action 6.3.2

If an inner-voice leap guard is required to keep the graph musically and structurally sane, implement it as:

- a narrow additional edge predicate

not:

- a new major subsystem

If a useful middle-voice guard cannot be chosen from the blueprint without a new musical design decision, full-stop.

### Stage 6.4 - Compose The Canonical Edge Predicate

#### Action 6.4.1

Compose the canonical transition-validity predicate from:

- target-state node validity
- per-voice step bounds
- first-pass motion rules

#### Action 6.4.2

Expose the inspection helpers needed for:

- valid outgoing transitions from a state
- legal action set from a state
- primitive transition results

These helpers should support testability and runtime integration directly.

## Phase 7 - Implement Reward And Terminal Semantics

### Stage 7.1 - Reward Context And Reward Result Surfaces

#### Action 7.1.1

Implement the structured reward context carrying at least:

- current step index
- max steps
- measure size
- source state
- target state
- action
- finite episode history
- final-step or terminal-step indicator

#### Action 7.1.2

Implement the structured reward result carrying at least:

- scalar reward
- terminal-success flag
- optional hard-violation flag
- diagnostics mapping

These surfaces must remain lightweight example surfaces, not analytics frameworks.

### Stage 7.2 - First-Pass Reward Terms

#### Action 7.2.1

Implement the small per-step cost.

#### Action 7.2.2

Implement the terminal cadence success reward.

#### Action 7.2.3

Implement the simple consonance preference.

#### Action 7.2.4

Implement the downbeat stability preference.

#### Action 7.2.5

Only if needed, implement the mild melodic smoothness preference.

If legality already captures enough of the intended behavior, do not add this term merely for richness.

### Stage 7.3 - Terminal And Truncation Conditions

#### Action 7.3.1

Implement the three-voice terminal-success check directly on the 3-voice state using the blueprint’s first-pass cadence semantics:

- terminal beat regime
- bass resolves to tonic pitch class
- outer voice forms desired terminal consonance
- inner voice lies in configured admissible terminal relation

#### Action 7.3.2

Implement truncation when:

- `step_index >= max_steps`

Do not introduce rank-local or curriculum-local deadline logic.

### Stage 7.4 - Bind The Public Reward/Termination Helpers

#### Action 7.4.1

Expose the public helpers needed for:

- `transition_reward(...)`
- `transition_terminated(...)`
- `transition_truncated(...)`

Keep their semantics faithful to the narrower first-scope design.

## Phase 8 - Implement Reset Semantics And The Concrete Example Environment

### Stage 8.1 - Curate The Start-State Surface

#### Action 8.1.1

Implement construction of a curated subset of valid start states that are:

- non-terminal
- node-valid
- not trivially degenerate

#### Action 8.1.2

Require that each curated start state has at least one legal outgoing action.

If the first attempted curated start family fails this property broadly, full-stop.

### Stage 8.2 - Implement `RlCounterpointEnv`

#### Action 8.2.1

Implement the concrete env class in the repo’s example idiom, including:

- observation encoding surface
- reset
- step
- reward emission
- termination/truncation behavior

This step should remain a compact example env, not a general counterpoint engine.

#### Action 8.2.2

Ensure the env internally tracks:

- step index
- episode history
- current state

without pushing that entire temporal structure into the explicit graph-state surface.

### Stage 8.3 - Implement Public Inspection Helpers

#### Action 8.3.1

Expose the small public helper surface needed for example usability and testing, such as:

- encode/decode observation
- `valid_outgoing_transitions(...)`
- `primitive_transition(...)`
- `is_goal_state(...)` if a terminal-success helper is useful

Do not export helpers that expose old-rank semantics.

## Phase 9 - Implement Runtime Integration

### Stage 9.1 - Implement State And Action Translation

#### Action 9.1.1

Implement translation from `RlCounterpointState` to package core `State`.

#### Action 9.1.2

Implement translation from discrete action index to package `PrimitiveAction`.

These translations must stay flat and literal.

### Stage 9.2 - Implement The Hidden-Graph Binding

#### Action 9.2.1

Implement the hidden-graph surface exposing the example to `TowerRuntime`.

This binding must derive its legality from the flat env helpers rather than inventing a separate graph law.

#### Action 9.2.2

Verify that the hidden-graph surface does not own:

- explicit rank projections
- parent/child role semantics
- hand-authored tower tiers

### Stage 9.3 - Implement The Example Runtime

#### Action 9.3.1

Implement `runtime.py` following the normal example pattern:

- runtime reset result
- runtime step result
- runtime wrapper around the env

#### Action 9.3.2

Ensure the runtime delegates tower construction to package surfaces rather than defining a counterpoint-specific explicit hierarchy.

### Stage 9.4 - Bind Public Runtime Exports

#### Action 9.4.1

Expose the runtime-facing helpers and classes through the package `__init__.py` only after the env/runtime surfaces are stable enough to export.

Do not prematurely export speculative internals.

## Phase 10 - Implement The First Training Surface

### Stage 10.1 - Define The Minimal Training Config And Result Types

#### Action 10.1.1

Implement the first minimal tower-training config, episode summary, and result dataclasses in:

- `training.py`

These should mirror the repo’s example shape while remaining specific to this env.

### Stage 10.2 - Implement `run_tower_training(...)`

#### Action 10.2.1

Implement one minimal but real `run_tower_training(...)` entrypoint over the example runtime.

This is the required first training surface.

#### Action 10.2.2

Do not implement at this stage:

- exploit/explore control
- curriculum staging
- transformer policy integration
- artifact-backed musical output

Those are explicitly out of first-scope.

## Phase 11 - Write The First-Scope Test Suite

### Stage 11.1 - Validity Tests

#### Action 11.1.1

Create:

- `tests/examples/test_rl_counterpoint_v3_validity.py`

and cover at least:

- strict order validity
- pitch-range validity
- interval-class validity
- span validity
- root-class admissibility

### Stage 11.2 - Transition Tests

#### Action 11.2.1

Create:

- `tests/examples/test_rl_counterpoint_v3_transitions.py`

and cover at least:

- candidate-next-state proposal
- step-bound enforcement
- parallel-perfect rejection
- legal outgoing transition construction
- nonzero action exclusion

### Stage 11.3 - Reward Tests

#### Action 11.3.1

Create:

- `tests/examples/test_rl_counterpoint_v3_rewards.py`

and cover at least:

- per-step cost
- terminal success reward
- downbeat stability preference behavior
- reward diagnostics presence

### Stage 11.4 - Env Tests

#### Action 11.4.1

Create:

- `tests/examples/test_rl_counterpoint_v3_gymnasium.py`

and cover at least:

- reset returns valid start states
- step advances beat index correctly
- termination and truncation behavior
- no curated start state is frozen

### Stage 11.5 - Runtime Integration Tests

#### Action 11.5.1

Create:

- `tests/examples/test_rl_counterpoint_v3_runtime_integration.py`

and cover at least:

- runtime reset
- runtime step
- hidden-graph binding
- tower-runtime compatibility

### Stage 11.6 - Tower-Training Tests

#### Action 11.6.1

Create:

- `tests/examples/test_rl_counterpoint_v3_tower_training.py`

and cover at least:

- `run_tower_training(...)` returns structured results
- episode summaries are populated
- the training path remains runnable under default config

### Stage 11.7 - Optional Probe Registration Tests

#### Action 11.7.1

Only if the example is bound into `tower_depth_probe.py`, update:

- `tests/examples/test_tower_depth_probe.py`

to cover the new registry entry.

## Phase 12 - Validate The Example End To End

### Stage 12.1 - Focused Example Validation

#### Action 12.1.1

Run the focused `rl_counterpoint_v3` test slice first.

No broader test pass is allowed to substitute for a focused example-surface pass.

### Stage 12.2 - Broader Example Validation

#### Action 12.2.1

Run the broader examples slice to ensure the new package does not break neighboring example conventions.

### Stage 12.3 - Repo-Wide Validation

#### Action 12.3.1

Run the full repository test suite.

#### Action 12.3.2

Run:

- `ruff check .`
- `mypy src`

Record all results in the running log.

### Stage 12.4 - Reality Checks Specific To This Example

#### Action 12.4.1

Perform a grounded reality check that curated valid start states are genuinely usable:

- non-terminal
- legal
- not frozen
- not immediately forced into trivial failure

#### Action 12.4.2

Perform a grounded reality check that the runtime is operating over a flat hidden graph rather than a smuggled explicit hierarchy.

#### Action 12.4.3

If tower-aware runtime smoke runs show no meaningful discovered structure at all, do not silently wave this away.

Record the result and full-stop if the failure appears structural rather than merely stochastic.

## Phase 13 - Bind The Public Package Surface

### Stage 13.1 - Finalize `__init__.py`

#### Action 13.1.1

Populate the example package `__init__.py` with the stable first-scope public exports from:

- `env.py`
- `runtime.py`
- `training.py`

#### Action 13.1.2

Do not export every internal helper by default.

Expose:

- the main env class
- the main state/spec types
- the action-count and transition helpers that are genuinely useful
- the runtime
- the training entrypoint and result/config types

### Stage 13.2 - Keep The Public Surface Honest

#### Action 13.2.1

Ensure the public export surface does not imply support for:

- exploit/explore training
- rank staging
- artifact generation
- advanced symbolic music tooling

unless those surfaces were actually implemented and validated.

## Phase 14 - Record Completion And Residual Limits

### Stage 14.1 - Write The Implementation Log Close-Out

#### Action 14.1.1

Record in the running log:

- completed actions
- exact validation commands and results
- any owner clarifications
- any residual limitations
- whether optional probe integration was included

### Stage 14.2 - Completion Criteria

#### Action 14.2.1

This implementation counts as faithful to the blueprint only if all of the following are true:

1. the example is three-voice from the start
2. the problem is flat rather than explicitly hierarchical
3. ordered pitch tuples and bounded per-voice deltas remain the ambient state/action surfaces
4. node legality is real and inspectable
5. edge legality is real and inspectable
6. the reward surface is narrow, structured, and real
7. curated start states are valid and not frozen
8. the runtime exposes a flat hidden graph to package-owned tower construction
9. `run_tower_training(...)` is implemented and runnable
10. the old explicit `rl_counterpoint` rank tower has not been smuggled back in through env, runtime, or training design

#### Action 14.2.2

If any one of those conditions is false, the implementation is not complete, even if code exists and tests partially pass.
