# Model And Training Surface Implementation Gameplan

## Status

This document is the implementation-law gameplan for the first model and training surface work in `state_collapser`.

It is downstream of:

- [01_001_model_and_training_surface_architecture.md]([state_collapser repository root]/docs/design/model_train_surfaces/01_001_model_and_training_surface_architecture.md)
- [01_002_model_and_training_surface_blueprint.md]([state_collapser repository root]/docs/design/model_train_surfaces/01_002_model_and_training_surface_blueprint.md)

It is written under the authority of:

- [docs/design/training_integration_surface_proposal.md]([state_collapser repository root]/docs/design/training_integration_surface_proposal.md)
- [docs/design/module_design_desiderata.md]([state_collapser repository root]/docs/design/module_design_desiderata.md)
- [docs/prime_directive/git_practices.md]([state_collapser repository root]/docs/prime_directive/git_practices.md)

This document is a `Phase.Stage.Action` implementation gameplan.

It is not:

- a fresh architecture note
- a benchmark protocol
- a PyPI hardening plan
- a backend-specific ML framework plan

Its job is to define exactly how the first reusable `state_collapser.training` surface is to be implemented.

## Execution Contract

This gameplan is governed by the following execution laws.

### 1. Branch discipline is mandatory

Before any implementation work governed by this gameplan begins:

- create or switch to a dedicated implementation branch
- perform the work there
- merge back only after validation is complete

This is fixed by:

- [docs/prime_directive/git_practices.md]([state_collapser repository root]/docs/prime_directive/git_practices.md)

### 2. Surface-role organization is fixed

The new package area must be created under:

- `src/state_collapser/training/`

and must remain organized by:

- surface role

not:

- RL-family label

### 3. The package must not harden into a master trainer

No step in this gameplan may produce:

- one opaque package-owned training engine

The package may provide:

- reusable components
- reusable data objects
- reusable collectors
- reusable learners
- reusable metrics
- reusable reference loops

But the orchestration must remain engineer-authorable.

### 4. Runtime ownership boundaries are fixed

Nothing in this gameplan may collapse or blur the already-fixed ownership split:

- env remains the problem shell
- runtime remains package-owned structural machinery
- training surfaces remain downstream consumers of runtime structure

### 5. First scope is internal-first

The first `state_collapser.training` implementation is:

- real package code
- reusable package code
- immediately usable inside the repo

but it is not yet:

- a finalized public API promise

### 6. First scope requires one real migration

Completion under this gameplan does not mean only:

- creating interfaces and helper objects

It also requires:

- migrating at least one real existing example loop to use the new training surfaces

### 7. First scope includes one concrete reference learner

The new training package must include:

- protocols
- summaries / result objects
- and one explicitly non-canonical concrete reference learner

This learner is:

- reference
- minimal
- temporary

not:

- the official long-term learner design

### 8. First scope includes concrete collectors

The new training package must include immediately:

- `StepCollector`
- `EpisodeCollector`

not just collector protocols.

### 9. Transitional adaptation is allowed, but not structural cheating

Reference loops should be built primarily around the new generic surfaces.

They may temporarily adapt existing runtime patterns where needed.

They may not:

- simply duplicate existing example loops under new names

### 10. Stop conditions are real

If implementation reveals a genuine contradiction between:

- the blueprint
- the architecture note
- the established env/runtime/tower ownership boundaries

then execution must stop for design correction rather than silently improvising a new architecture.

## MORE Execution Contract

### Rule MORE 1 — Gameplan Is Law

When this implementation begins:

- this gameplan is law
- the blueprint is law
- I do not silently simplify
- I do not silently reorder
- I do not silently reinterpret the training-surface architecture into a more rigid or weaker substitute

### Rule MORE 2 — Single Action Discipline

During execution:

- one `Phase.Stage.Action` is the atomic implementation unit
- I re-read the exact action text before touching code
- I verify against that action before advancing

### Rule MORE 3 — Mandatory Full Stop Conditions

I must full-stop and return to the Project Owner if:

- implementing the decision-input / action-decision / transition split requires a new design choice not fixed by the blueprint
- the collector or learner contract cannot support the correction without an ambiguous interface expansion
- the new bookkeeping cannot be added without materially changing another authoritative runtime surface
- tests encode the old example-local training assumptions as if they were still the required architecture
- I discover that the first real migration target cannot use the new surfaces without a new PO decision about scope or target

### Rule MORE 4 — No Fake Compliance

I must not:

- keep old example-local loop structure while only renaming wrappers around it
- claim collector/learner architecture exists when the real logic still lives only inside example training files
- fake generic surfaces by hard-coding them to one example’s local assumptions
- report a successful migration if the new package surfaces are not actually exercised by the migrated example path

### Rule MORE 5 — Running Log Requirement

Maintain a running log at:

- `docs/design/model_train_surfaces/01_004_model_and_training_surface_implementation_log.md`

The log must record:

- completed `Phase.Stage.Action` items
- test results
- surprises
- owner clarifications
- blockers

## Canonical Target Files

The canonical target files for first implementation are:

- `src/state_collapser/training/__init__.py`
- `src/state_collapser/training/inputs.py`
- `src/state_collapser/training/decisions.py`
- `src/state_collapser/training/transitions.py`
- `src/state_collapser/training/collectors.py`
- `src/state_collapser/training/learners.py`
- `src/state_collapser/training/metrics.py`
- `src/state_collapser/training/reference_loops.py`

The canonical first migration targets are:

- one existing example loop under `src/state_collapser/examples/`

The canonical validation targets are:

- new focused tests under `tests/training/`
- updated example-facing tests under `tests/examples/`

The canonical implementation log target is:

- `docs/design/model_train_surfaces/01_004_model_and_training_surface_implementation_log.md`

## First Implementation Decisions Fixed By This Gameplan

The following choices are now bound and must not be reopened during execution unless a true contradiction is found.

### 1. Package locus

The work lives in:

- `src/state_collapser/training/`

### 2. Internal-first status

The first implementation is:

- repo-internal
- structurally reusable
- not yet a hardened public package contract

### 3. Concrete collectors now

First scope includes:

- real `StepCollector`
- real `EpisodeCollector`

### 4. Concrete learner now

First scope includes:

- one concrete reference learner

The recommended first learner is:

- a simple tabular learner

because it matches current repo reality and gives the surfaces a runnable vertical slice.

### 5. One real migration required

At least one existing example must be migrated.

### 6. Generic-first reference loops

The reference loops should primarily compose:

- decision inputs
- action decisions
- transitions
- collectors
- learner surface
- metrics hooks

with runtime adaptation allowed only where needed for first practicality.

## Recommended First Migration Target

The first migration target should be:

- `rl_counterpoint_v3`

rather than:

- `plate_support_env` exploit/explore surfaces

### Why this target is preferred

`rl_counterpoint_v3` is preferred for first migration because it is:

- newer
- flatter
- structurally simpler
- less entangled with exploit/explore-specific control machinery

This gives the new training package a cleaner first reality check.

If implementation shows this target is unexpectedly worse than a different example, that must be recorded explicitly in the implementation log before switching targets.

## Phase 1. Package Foundation

### Stage 1.1. Branch And Logging Setup

#### Action 1.1.1

Create or switch to a dedicated implementation branch before editing code.

#### Action 1.1.2

Create the implementation log:

- `docs/design/model_train_surfaces/01_004_model_and_training_surface_implementation_log.md`

The log must record:

- branch name
- execution start state
- files touched
- validation runs
- architectural deviations if any

### Stage 1.2. Package Skeleton Creation

#### Action 1.2.1

Create the new package directory:

- `src/state_collapser/training/`

#### Action 1.2.2

Create the canonical first-scope files:

- `__init__.py`
- `inputs.py`
- `decisions.py`
- `transitions.py`
- `collectors.py`
- `learners.py`
- `metrics.py`
- `reference_loops.py`

#### Action 1.2.3

Create a first focused test package:

- `tests/training/`

with file layout aligned to the new training package areas.

### Stage 1.3. Import Surface Guardrails

#### Action 1.3.1

Ensure the initial import graph does not create circular dependency pressure between:

- `training`
- `tower`
- `examples`

#### Action 1.3.2

Keep the new package downstream of runtime surfaces.

It may import runtime-facing types where appropriate.

Existing runtime packages must not start depending upward on the new training package during the first package-foundation phase.

## Phase 2. Decision And Transition Data Objects

### Stage 2.1. Decision-Input Surface

#### Action 2.1.1

Implement the first reusable decision-input object in:

- `src/state_collapser/training/inputs.py`

using the canonical first name:

- `ActionSelectionInput`

#### Action 2.1.2

Bind its required first fields to support:

- env observation
- current base state
- current runtime snapshot
- current tower-position tuple
- optional action mask

#### Action 2.1.3

Bind optional first-scope extension fields for:

- finite history window
- active-tier state
- frozen lower context
- diagnostics mapping

#### Action 2.1.4

Implement the object as:

- a typed Python data object

not:

- a tensor-backend contract

### Stage 2.2. Action-Decision Surface

#### Action 2.2.1

Implement the first reusable action-decision object in:

- `src/state_collapser/training/decisions.py`

using the canonical first name:

- `ActionDecision`

#### Action 2.2.2

Bind its first-scope fields to allow optional representation of:

- chosen action
- action probabilities
- action logits
- Q-values / action values
- value estimate
- diagnostics mapping

#### Action 2.2.3

Ensure the object is semantically usable by:

- direct policy-style methods
- value-based methods
- actor-critic-shaped methods

without requiring every field to be populated.

### Stage 2.3. Transition Surface

#### Action 2.3.1

Implement the first reusable transition object in:

- `src/state_collapser/training/transitions.py`

using the canonical first name:

- `TrainingTransition`

#### Action 2.3.2

Bind required fields for:

- source decision input
- chosen action
- scalar reward
- target decision input
- terminated flag
- truncated flag
- diagnostics mapping

#### Action 2.3.3

Bind optional structural metadata fields so the object can naturally carry:

- runtime snapshot summary
- tower-position key
- active tier
- frozen-context version

#### Action 2.3.4

Keep these structural fields optional in first scope so flatter learners are not forced into tower-aware complexity they do not need.

## Phase 3. Collector Surfaces

### Stage 3.1. Collector Contract Definition

#### Action 3.1.1

In `src/state_collapser/training/collectors.py`, define the first collector-facing contracts needed for:

- step collection
- episode collection

#### Action 3.1.2

Bind the collector role as owning:

- env/runtime stepping
- packaging transitions
- simple episode-level accumulation

not:

- full experiment management
- checkpoint systems
- replay systems

### Stage 3.2. StepCollector Implementation

#### Action 3.2.1

Implement a real first `StepCollector`.

#### Action 3.2.2

Its first-scope responsibilities must include:

- consuming a runtime-like stepping surface
- consuming learner-produced decisions or chosen actions
- building `ActionSelectionInput`
- building `TrainingTransition`
- returning enough information for engineer-authored loop logic to continue

#### Action 3.2.3

Ensure it can be called directly from custom loops without forcing a package-owned orchestration engine.

### Stage 3.3. EpisodeCollector Implementation

#### Action 3.3.1

Implement a real first `EpisodeCollector`.

#### Action 3.3.2

Its first-scope responsibilities must include:

- repeated step collection
- episode accumulation
- basic episodic summaries

#### Action 3.3.3

Ensure `EpisodeCollector` composes naturally with `StepCollector` rather than duplicating the same logic in a disconnected way.

### Stage 3.4. Collector Testing

#### Action 3.4.1

Create focused tests that prove:

- collectors can build decision-input objects correctly
- collectors can build transition objects correctly
- collectors handle terminated and truncated episodes correctly
- collectors can carry optional tower metadata without making it mandatory

#### Action 3.4.2

Prefer testing against simple runtime/example surfaces already present in the repo rather than inventing fake complexity.

## Phase 4. Learner Surface

### Stage 4.1. General Learner Contract

#### Action 4.1.1

In `src/state_collapser/training/learners.py`, implement the first general learner/update-facing contract.

#### Action 4.1.2

Bind the contract to preserve the three-part separation:

- action-decision production
- transition ingestion
- parameter update

#### Action 4.1.3

The canonical surface should support methods equivalent to:

- `act(...)`
- `observe(...)`
- `update(...)`

The exact spelling may vary slightly if needed, but the separation must remain explicit.

### Stage 4.2. Reference Learner Implementation

#### Action 4.2.1

Implement one concrete reference learner in `learners.py`.

#### Action 4.2.2

The first recommended learner is:

- a simple tabular learner

grounded in the repo’s current training reality.

#### Action 4.2.3

Ensure the code and documentation frame this learner as:

- reference
- minimal
- non-canonical

#### Action 4.2.4

Do not let this learner silently redefine the architecture around tabular assumptions.

It must implement the broader surface without claiming that the broader surface is only for tabular methods.

### Stage 4.3. Relationship To Existing TierLearner

#### Action 4.3.1

Do not force an immediate unification with `TierLearner`.

#### Action 4.3.2

Record clearly in code comments or implementation log whether:

- `TierLearner` is merely analogous
- or whether any light adapter path was introduced

#### Action 4.3.3

Do not rewrite exploit/explore learner machinery as part of first scope unless it becomes the chosen migration target.

### Stage 4.4. Learner Testing

#### Action 4.4.1

Add focused tests proving:

- a learner can produce `ActionDecision`
- a learner can ingest `TrainingTransition`
- a learner can update internal learning state

#### Action 4.4.2

Add a focused smoke test proving the reference learner works end to end with the collector and reference loop surfaces.

## Phase 5. Metrics And Reporting

### Stage 5.1. Metrics Surface Definition

#### Action 5.1.1

Implement a minimal metrics/reporting surface in:

- `src/state_collapser/training/metrics.py`

#### Action 5.1.2

Bind first-scope reporting capability for:

- episodic return
- success/failure
- step counts
- optional tower depth
- optional control/tier diagnostics

### Stage 5.2. Hook Semantics

#### Action 5.2.1

Design the first metrics surface as:

- hook
- callback
- summary object
- or a small combination of these

not:

- a full experiment manager

#### Action 5.2.2

Ensure loops and collectors can report into the metrics surface without becoming tightly coupled to one single reporting backend.

### Stage 5.3. Metrics Testing

#### Action 5.3.1

Add focused tests proving:

- metrics hooks can observe episode summaries
- optional tower-specific metadata can be reported
- flatter runs can still use the same metrics surface without tower-specific burden

## Phase 6. Reference Loops

### Stage 6.1. Online Reference Loop

#### Action 6.1.1

Implement:

- `run_reference_online_loop(...)`

in:

- `src/state_collapser/training/reference_loops.py`

#### Action 6.1.2

This loop must demonstrate composition of:

- decision-input construction
- learner action-decision production
- step collection
- transition ingestion
- learner update
- metrics reporting

#### Action 6.1.3

The loop must remain:

- short
- readable
- obviously engineer-authorable

It must not become a disguised central trainer.

### Stage 6.2. Episode Reference Loop

#### Action 6.2.1

Implement:

- `run_reference_episode_loop(...)`

in the same file.

#### Action 6.2.2

This loop must demonstrate composition of:

- episode collection
- learner integration
- episodic metrics

#### Action 6.2.3

If current runtime patterns require light transitional adaptation, that is allowed, but the loops must still read as consumers of the new generic surfaces rather than copies of old example code.

### Stage 6.3. Reference Loop Testing

#### Action 6.3.1

Add focused tests proving both reference loops run end to end with:

- the reference learner
- the concrete collectors
- the new data objects

#### Action 6.3.2

Ensure tests are small and deterministic enough to remain stable in the repo’s validation suite.

## Phase 7. Real Example Migration

### Stage 7.1. Migration Target Confirmation

#### Action 7.1.1

Begin with `rl_counterpoint_v3` as the first migration target.

#### Action 7.1.2

Record in the implementation log why this target was chosen.

#### Action 7.1.3

If implementation reveals this target is materially worse than another example for first migration, stop and record the reason before switching targets.

### Stage 7.2. Surface Integration Strategy

#### Action 7.2.1

Inspect the current example-local training loop and identify exactly which concerns move to the new package:

- decision-input creation
- collection
- learner surface
- reference loop usage
- metrics handling

#### Action 7.2.2

Do not migrate code merely to shift imports around.

The migration must make the example materially more aligned with the new training surface architecture.

### Stage 7.3. Migration Implementation

#### Action 7.3.1

Refactor the chosen example training path to use the new package surfaces where appropriate.

#### Action 7.3.2

Preserve the example’s actual RL problem semantics.

#### Action 7.3.3

Do not let the migration rewrite env/runtime ownership boundaries.

#### Action 7.3.4

Keep the migrated example runnable and testable.

### Stage 7.4. Migration Validation

#### Action 7.4.1

Add or update example-facing tests proving:

- the migrated training path still runs
- the new training surfaces are actually being exercised
- the example’s behavior has not been accidentally invalidated

#### Action 7.4.2

If the example previously had smoke training coverage, preserve or improve it.

## Phase 8. Package Surface Cleanup

### Stage 8.1. `__init__.py` Curation

#### Action 8.1.1

Curate `src/state_collapser/training/__init__.py` so it exposes the intended first internal surface cleanly.

#### Action 8.1.2

Do not over-export internal helpers.

### Stage 8.2. Naming And Comment Pass

#### Action 8.2.1

Review all new names for consistency with the architecture and blueprint.

#### Action 8.2.2

Add succinct comments only where the control/data boundary would otherwise be easy to misread.

### Stage 8.3. Documentation Alignment

#### Action 8.3.1

Update the implementation log with:

- final file set
- migration target used
- any transitional compromises taken
- any explicitly deferred cleanup

#### Action 8.3.2

Do not rewrite the architecture note or blueprint during implementation except for clearly marked errata if a genuine contradiction is discovered.

## Phase 9. Validation

### Stage 9.1. Focused Validation

#### Action 9.1.1

Run focused tests for:

- `tests/training/`
- migrated example tests

#### Action 9.1.2

Run linting for touched files.

#### Action 9.1.3

Run typing checks for touched source or the repo-standard typecheck target if practical.

### Stage 9.2. Broader Validation

#### Action 9.2.1

Run the relevant broader example/runtime test slice needed to ensure the new training package did not create architectural regressions.

#### Action 9.2.2

If there is a failure, classify it honestly as one of:

- local implementation bug
- migration bug
- design contradiction

and respond accordingly.

### Stage 9.3. Completion Check

#### Action 9.3.1

Confirm all blueprint acceptance conditions are satisfied.

#### Action 9.3.2

Confirm the additional gameplan-specific conditions are also satisfied:

- concrete collectors exist
- one concrete reference learner exists
- one real example migration exists
- the package did not harden into a master trainer

## Phase 10. Closeout

### Stage 10.1. Final Log

#### Action 10.1.1

Finish:

- `docs/design/model_train_surfaces/01_004_model_and_training_surface_implementation_log.md`

with:

- branch used
- validation performed
- migration performed
- unresolved deferred hardening items

### Stage 10.2. Merge Readiness

#### Action 10.2.1

Only after validation passes and the log is complete should the work be considered ready for merge back from the implementation branch.

#### Action 10.2.2

If merge happens, it must preserve the git-practice rule:

- dedicated implementation branch first
- merge back after validated execution

## Completion Standard

This gameplan counts as successfully executed only if the repo now contains:

- a real `state_collapser.training` package
- the first reusable training-facing data objects
- concrete collectors
- a general learner surface
- one concrete reference learner
- minimal metrics/reporting support
- reference loops
- at least one migrated real example
- focused tests proving the surfaces compose

and if the implementation still preserves:

- env/runtime/tower ownership boundaries
- engineer-authored loop freedom
- the non-policy-only model surface philosophy

If instead the implementation yields:

- another abstract package with no reality check
- another example-local ad hoc loop with no reusable surfaces
- or a disguised central trainer framework

then execution has failed.
