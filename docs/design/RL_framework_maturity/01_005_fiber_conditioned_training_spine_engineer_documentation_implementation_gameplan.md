# Fiber-Conditioned Training Spine Engineer Documentation Implementation Gameplan

## Status

This document is the Phase.Stage.Action implementation gameplan for:

- `docs/design/RL_framework_maturity/01_003_fiber_conditioned_training_spine_engineer_documentation_blueprint.md`

It is paired with:

- `docs/design/RL_framework_maturity/01_004_fiber_conditioned_training_spine_implementation_gameplan.md`

It is downstream of:

- `docs/design/RL_framework_maturity/01_001_rl_framework_maturity_and_tower_training_spine_discussion.md`
- `docs/design/RL_framework_maturity/01_002_fiber_conditioned_training_spine_blueprint.md`

It is governed by:

- `docs/prime_directive/prime_directive.md`
- `docs/prime_directive/git_practices.md`
- `docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md`
- `docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md`

This is a documentation implementation gameplan.

It is not documentation implementation.

No documentation execution should begin until the Project Owner explicitly
approves execution of the paired code and documentation gameplans.

Once approved, this gameplan is law. If documentation reality conflicts with
any Phase.Stage.Action item below, the implementer must stop, identify the exact
item that failed, and ask the Project Owner for guidance. Silent simplification,
silent reordering, and silent reinterpretation are forbidden.

## Paired Reality Contract

This documentation gameplan must remain synchronized with:

```text
docs/design/RL_framework_maturity/01_004_fiber_conditioned_training_spine_implementation_gameplan.md
```

The docs must explain the same architecture the code implements:

```text
PartitionTower
    -> FrozenQuotientBehavior
        -> PathFiber
            -> FiberConditionedStage
                -> existing learner-facing training surfaces
```

The docs must not describe a different package.

In particular, the docs must not imply that:

- `state_collapser` is an RLlib replacement
- `state_collapser` is a Stable-Baselines3 replacement
- `FiberConditionedStage` is Gymnasium-first
- Torch/SB3/RLlib support exists before it does
- users must surrender their training loop to the package
- lift is an externally invented heuristic rather than the path fiber of the
  tower projection

## Fixed Decisions Shared With Code Gameplan

The following decisions are fixed in both paired plans.

1. The canonical frozen behavior name is:

   ```text
   FrozenQuotientBehavior
   ```

2. `PathFiber` may support concrete frozen paths and policy-level frozen
   behavior, but the first runnable docs should use the concrete-step case.

3. `FiberConditionedStage` is package-native first.

   It is not documented as a Gymnasium env.

4. `tower/control` remains proto control infrastructure.

   The docs should not present it as the final fiber-conditioned training spine.

5. Existing `base` / `lower` vocabulary is not swept away immediately.

   New docs should teach corrected vocabulary:

   ```text
   total graph
   fine tier
   coarse tier
   upstairs
   downstairs
   frozen quotient behavior
   path fiber
   fiber-conditioned stage
   ```

6. `CONTRIBUTING.md` receives TODOs for:

   - the future fate of `tower/control`
   - future terminology cleanup

7. The first docs example must not require Torch, SB3, or RLlib.

8. The first docs example must use real import paths that work after the code
   gameplan is implemented.

## Fixed Defaults For This Documentation Gameplan

Unless the Project Owner changes these before execution, documentation must use
the following defaults.

1. Documentation implementation occurs on the same branch as code implementation:

   ```text
   codex/fiber-conditioned-training-spine
   ```

2. Documentation execution writes to the same implementation log:

   ```text
   docs/design/RL_framework_maturity/01_006_fiber_conditioned_training_spine_paired_implementation_log.md
   ```

3. New engineer-facing docs live under:

   ```text
   docs/usage/
   docs/api_notes/
   ```

4. The first usage docs are:

   ```text
   docs/usage/01_001_what_state_collapser_is.md
   docs/usage/01_002_tower_runtime_mental_model.md
   docs/usage/01_003_training_surface_quickstart.md
   docs/usage/01_004_fiber_conditioned_training.md
   docs/usage/01_005_using_your_own_training_loop.md
   docs/usage/01_006_gymnasium_integration.md
   docs/usage/01_007_glossary.md
   docs/usage/01_008_common_misunderstandings.md
   ```

5. The first API notes are:

   ```text
   docs/api_notes/partition_tower.md
   docs/api_notes/training_inputs_and_transitions.md
   docs/api_notes/frozen_quotient_behavior.md
   docs/api_notes/path_fiber.md
   docs/api_notes/fiber_conditioned_stage.md
   ```

6. README changes remain concise.

7. `CONTRIBUTING.md` remains the location for roadmap/TODO items.

8. User-facing docs should link to design docs but should not require reading
   the entire design discussion.

## Required Branch Discipline

Documentation execution must not start on `main` once paired implementation
execution begins.

Before documentation implementation begins, verify the active branch:

```text
codex/fiber-conditioned-training-spine
```

If the Project Owner requests a different branch name for the paired execution,
use that name.

## Required Running Implementation Log

Documentation execution must record progress in:

```text
docs/design/RL_framework_maturity/01_006_fiber_conditioned_training_spine_paired_implementation_log.md
```

The log must record:

- documentation Phase.Stage.Action items completed
- files created or edited
- import paths checked against code
- snippets checked against code
- validation commands run
- failures or drift from code reality
- Project Owner clarifications
- authorized deviations

## Documentation Stop Conditions

Documentation implementation must stop and ask the Project Owner if any of the
following occur.

- The code gameplan is not approved for execution.
- The code implementation has not yet created the API a usage doc must describe.
- A planned import path does not exist.
- A planned snippet cannot be made true without changing code semantics.
- Docs would need to describe `FiberConditionedStage` as Gymnasium-first.
- Docs would need to claim Torch/SB3/RLlib support exists.
- Docs would need to hide that old `base` / `lower` vocabulary still exists in
  compatibility surfaces.
- A README change would re-clutter the README with design/TODO material.
- A documentation example cannot be validated against code.
- The working tree contains unrelated user changes in files this plan must edit.
- Documentation would need to contradict the paired code gameplan.

## Validation Command Set

Documentation file existence and link sanity can be checked with ordinary shell
inspection.

Python snippet import validation:

```text
uv run python -c "from state_collapser.training import FrozenQuotientBehavior, PathFiber, FiberConditionedStage"
```

Focused tests that should still pass after docs and code:

```text
uv run pytest tests/training tests/tower/partition
```

Full validation:

```text
uv run pytest
```

Static validation:

```text
uv run ruff check .
uv run mypy src
```

If any validation command fails unexpectedly, stop and reconstruct reality before
editing further.

## Phase 0: Documentation Setup And Synchronization

### Stage 0.1: Confirm Execution Authority

#### Action 0.1.1

Confirm that the Project Owner explicitly approved execution of the paired code
and documentation gameplans.

Completion criteria:

- The shared implementation log records approval.
- No user-facing docs are created before approval.

Stop condition:

- If approval is ambiguous, do not implement documentation.

### Stage 0.2: Verify Paired Reality

#### Action 0.2.1

Re-read the paired source and gameplan files from disk.

Required files:

```text
docs/design/RL_framework_maturity/01_002_fiber_conditioned_training_spine_blueprint.md
docs/design/RL_framework_maturity/01_003_fiber_conditioned_training_spine_engineer_documentation_blueprint.md
docs/design/RL_framework_maturity/01_004_fiber_conditioned_training_spine_implementation_gameplan.md
docs/design/RL_framework_maturity/01_005_fiber_conditioned_training_spine_engineer_documentation_implementation_gameplan.md
```

Completion criteria:

- The log records the re-read.
- Shared fixed decisions are unchanged.

#### Action 0.2.2

Check which code surfaces currently exist before writing user-facing docs.

Required checks:

```text
src/state_collapser/training/frozen.py
src/state_collapser/training/fibers.py
src/state_collapser/training/stages.py
src/state_collapser/training/__init__.py
```

Completion criteria:

- The log records whether each file exists.
- Usage docs only claim implemented APIs after those APIs exist.

Stop condition:

- If user-facing docs would need to describe planned APIs as implemented, stop.

## Phase 1: Update Roadmap And Design Indexing

### Stage 1.1: Add `CONTRIBUTING.md` TODOs

#### Action 1.1.1

Add a roadmap TODO for the future fate of `tower/control`.

Required meaning:

```text
After `FiberConditionedStage` is stable, revisit whether the proto
exploit/explore `tower/control` stack should be refactored around it,
preserved as a reference controller, or deprecated.
```

Completion criteria:

- `CONTRIBUTING.md` contains this TODO.
- The TODO does not imply this implementation rewrites `tower/control`.

#### Action 1.1.2

Add a roadmap TODO for old terminology cleanup.

Required meaning:

```text
After new total/fine/coarse/frozen-quotient vocabulary is established, plan a
compatibility/deprecation pass for old `base` and `lower` vocabulary.
```

Completion criteria:

- `CONTRIBUTING.md` contains this TODO.
- The TODO does not authorize sweeping renames in this implementation.

### Stage 1.2: Keep README Concise

#### Action 1.2.1

Review `README.md` after code implementation.

Completion criteria:

- README still explains what `state_collapser` is.
- README still keeps TODO/design sprawl out of the main room.
- README links to usage docs if usage docs exist.

Stop condition:

- If README changes would become a long design essay, stop and ask.

## Phase 2: Create Usage Documentation Skeleton

### Stage 2.1: Create Usage Folder

#### Action 2.1.1

Create:

```text
docs/usage/
```

Completion criteria:

- Folder exists.
- No unrelated docs are moved.

### Stage 2.2: Create Usage Documents

#### Action 2.2.1

Create:

```text
docs/usage/01_001_what_state_collapser_is.md
```

Required content:

- RLlib/SB3/state_collapser comparison
- package positioning as structural layer
- "package builds the stage; engineer brings the learner"
- maturity caveat

Completion criteria:

- A new engineer can understand why the package exists.
- The doc does not describe `state_collapser` as a generic RL learner library.

#### Action 2.2.2

Create:

```text
docs/usage/01_002_tower_runtime_mental_model.md
```

Required content:

- `G_t^0` as total discovered graph
- increasing tier index as coarser/downstairs
- partition tower as state/action partition tables
- compatibility quotient readouts as readouts, not runtime source of truth
- local tower query vocabulary

Completion criteria:

- Direction vocabulary matches the code gameplan.
- No global "base graph" language is introduced.

#### Action 2.2.3

Create:

```text
docs/usage/01_003_training_surface_quickstart.md
```

Required content:

- `ActionSelectionInput`
- `ActionDecision`
- `TrainingTransition`
- learner-owned loop
- current flat/research training surface
- how the new stage/fiber context extends rather than replaces it

Completion criteria:

- Existing training surfaces are explained without overstating maturity.

#### Action 2.2.4

Create:

```text
docs/usage/01_004_fiber_conditioned_training.md
```

Required content:

- `FrozenQuotientBehavior`
- `PathFiber`
- `FiberConditionedStage`
- freeze/fiber/lift explanation
- concrete tiny example
- no Torch/SB3/RLlib requirement

Completion criteria:

- The doc describes implemented APIs only after import paths work.
- The doc distinguishes local `refinement_fiber(...)` queries from path fibers.

#### Action 2.2.5

Create:

```text
docs/usage/01_005_using_your_own_training_loop.md
```

Required content:

- direct stage loop
- where learner/model fits
- what the stage supplies
- what the engineer owns
- what is intentionally not hidden by the package

Completion criteria:

- The example loop is short and runnable against implemented surfaces.

#### Action 2.2.6

Create:

```text
docs/usage/01_006_gymnasium_integration.md
```

Required content:

- current Gymnasium-like wrapper purpose
- distinction between observing external envs and future stage adapter
- explicit statement that `FiberConditionedStage` is not Gymnasium-first
- future adapter direction

Completion criteria:

- No claim that SB3/RLlib adapters currently exist.

#### Action 2.2.7

Create:

```text
docs/usage/01_007_glossary.md
```

Required content:

- glossary entries listed in the documentation blueprint
- plain English sentence
- package/code reference where possible
- "do not confuse with" notes for ambiguous terms

Completion criteria:

- Terms match code gameplan vocabulary.

#### Action 2.2.8

Create:

```text
docs/usage/01_008_common_misunderstandings.md
```

Required content:

- `G_t^0` is not globally "the base graph"
- lift is not an external heuristic
- `state_collapser` is not RLlib/SB3
- the package should not hide the training loop
- local refinement fiber is not the whole path fiber

Completion criteria:

- The doc directly prevents the known conceptual failures from the discussion.

## Phase 3: Create API Notes

### Stage 3.1: Create API Notes Folder

#### Action 3.1.1

Create:

```text
docs/api_notes/
```

Completion criteria:

- Folder exists.

### Stage 3.2: Create Existing Runtime API Notes

#### Action 3.2.1

Create:

```text
docs/api_notes/partition_tower.md
```

Required content:

- what `PartitionTower` owns
- why it is the runtime model
- query methods used by `PathFiber`
- compatibility readouts

Completion criteria:

- It references implemented methods accurately.

#### Action 3.2.2

Create:

```text
docs/api_notes/training_inputs_and_transitions.md
```

Required content:

- `ActionSelectionInput`
- `ActionDecision`
- `TrainingTransition`
- stage/fiber context fields
- compatibility notes for existing fields

Completion criteria:

- It matches actual dataclass fields.

### Stage 3.3: Create New Surface API Notes

#### Action 3.3.1

Create:

```text
docs/api_notes/frozen_quotient_behavior.md
```

Required content:

- what is frozen
- concrete step behavior
- policy-surface future
- immutability
- metadata/version

Completion criteria:

- It matches actual `FrozenQuotientBehavior` fields.

#### Action 3.3.2

Create:

```text
docs/api_notes/path_fiber.md
```

Required content:

- tower projection relationship
- use of `PartitionTower` queries
- admissible action cells
- action masks
- lift candidates
- departure diagnostics

Completion criteria:

- It distinguishes `PathFiber` from `PartitionTower.refinement_fiber(...)`.

#### Action 3.3.3

Create:

```text
docs/api_notes/fiber_conditioned_stage.md
```

Required content:

- direct stage API
- reset/current input/step
- stage context
- transition output
- non-goals
- future Gymnasium adapter boundary

Completion criteria:

- It matches actual `FiberConditionedStage` behavior.

## Phase 4: Write Runnable Examples

### Stage 4.1: Tiny Graph Example

#### Action 4.1.1

Add a tiny graph walkthrough to:

```text
docs/usage/01_004_fiber_conditioned_training.md
```

Required sequence:

```text
1. Build or discover a small graph.
2. Build a partition tower.
3. Choose a coarser tier action/path.
4. Freeze it as FrozenQuotientBehavior.
5. Construct PathFiber at the finer tier.
6. Ask for admissible actions or masks.
7. Step through FiberConditionedStage.
8. Show TrainingTransition carrying stage/fiber context.
```

Completion criteria:

- The example uses real imports.
- The example does not require Torch.
- The example does not require Gymnasium.

#### Action 4.1.2

Validate the example's imports.

Command:

```text
uv run python -c "from state_collapser.training import FrozenQuotientBehavior, PathFiber, FiberConditionedStage"
```

Completion criteria:

- The command passes.
- The log records the result.

### Stage 4.2: Existing Environment Example

#### Action 4.2.1

Add a `plate_support_env` walkthrough to:

```text
docs/usage/01_004_fiber_conditioned_training.md
```

or create a separate file only if the section becomes too large.

Required content:

- normal flat tower-aware training exists
- fiber-conditioned stage adds frozen behavior and path-fiber context
- inputs/transitions gain stage/fiber metadata
- learner loop remains engineer-owned

Completion criteria:

- The example does not overclaim benchmark or neural-training maturity.

## Phase 5: Add Cross-Links And Navigation

### Stage 5.1: README Link

#### Action 5.1.1

Add a concise README pointer to `docs/usage`.

Completion criteria:

- README remains concise.
- README does not regain the old construction/TODO sprawl.

### Stage 5.2: CONTRIBUTING Link

#### Action 5.2.1

Add or update `CONTRIBUTING.md` design-authority links so contributors can find:

```text
docs/design/RL_framework_maturity/
docs/usage/
docs/api_notes/
```

Completion criteria:

- Links are accurate.
- TODOs from Phase 1 remain present.

### Stage 5.3: Internal Cross-Links

#### Action 5.3.1

Add cross-links between usage docs and API notes.

Completion criteria:

- Usage docs point to API notes for details.
- API notes point back to usage docs for examples.
- Design docs are linked as deeper context, not required prerequisites.

## Phase 6: Documentation Consistency Review

### Stage 6.1: Terminology Review

#### Action 6.1.1

Search new docs for ambiguous direction vocabulary.

Required search terms:

```text
base graph
base state
lower context
lower tier
upstairs/coarser
downstairs/finer
```

Completion criteria:

- Any occurrence is either quoted as a misunderstanding, described as legacy
  compatibility, or replaced.

### Stage 6.2: Framework Boundary Review

#### Action 6.2.1

Search new docs for RLlib/SB3/Torch claims.

Completion criteria:

- Any mention is either positioning, non-goal, future adapter, or explicit
  optional dependency context.
- No docs claim implemented external adapters.

### Stage 6.3: Import Path Review

#### Action 6.3.1

Validate all public imports shown in usage docs.

Required import baseline:

```python
from state_collapser.training import FrozenQuotientBehavior
from state_collapser.training import PathFiber
from state_collapser.training import FiberConditionedStage
```

Completion criteria:

- Imports work.
- Any non-working future API is marked as future or removed.

## Phase 7: Test And Static Validation

### Stage 7.1: Focused Validation

#### Action 7.1.1

Run focused validation after docs are updated.

Command:

```text
uv run pytest tests/training tests/tower/partition
```

Completion criteria:

- The command passes.
- The log records the result.

### Stage 7.2: Full Validation

#### Action 7.2.1

Run full validation.

Command:

```text
uv run pytest
```

Completion criteria:

- The command passes.
- The log records the result.

#### Action 7.2.2

Run static validation.

Commands:

```text
uv run ruff check .
uv run mypy src
```

Completion criteria:

- Both commands pass.
- The log records the result.

## Phase 8: Final Documentation Readiness Review

### Stage 8.1: Acceptance Criteria Review

#### Action 8.1.1

Verify that a competent engineer can answer:

- What is `state_collapser` for?
- Why is it not RLlib or Stable-Baselines3?
- What does the package own?
- What does the learner own?
- What is the total graph?
- Which direction is down the tower?
- What does it mean to freeze coarser behavior?
- What is the path fiber over that behavior?
- What is a fiber-conditioned stage?
- How do action masks arise from fiber admissibility?
- Where do I plug in my model or learner?
- What should I not expect this package to do yet?

Completion criteria:

- The shared implementation log records a checklist result.

### Stage 8.2: Paired Reality Review

#### Action 8.2.1

Compare docs against implemented code surfaces.

Completion criteria:

- No usage doc describes a non-existent implemented API.
- No API note omits a required public field.
- No doc contradicts the code gameplan's deferred-work register.

### Stage 8.3: Final Summary

#### Action 8.3.1

Add final documentation summary to the shared implementation log.

Required content:

- docs created
- docs updated
- snippets/imports validated
- known documentation gaps
- deferred documentation topics
- whether docs are ready for Project Owner review

Completion criteria:

- The Project Owner can review documentation without reconstructing context from
  chat.

## Final Non-Negotiable

The docs are successful only if they make the implemented surface usable.

They must teach:

```text
The package builds the stage.
You bring the learner.
The fiber is the lift.
The tower direction is downward with increasing tier index.
```

They are not successful if they merely restate the design discussion in a
friendlier voice.
