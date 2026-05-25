# Synthetic Blow Review Revision Implementation Gameplan

## Status

Date: 2026-05-24

This document is the Phase.Stage.Action implementation gameplan for:

- `docs/design/synthetic_blow_revisions_01/01_001_synthetic_blow_review_revision_blueprint.md`

It is downstream of:

- `docs/code_review/02_001_synthetic_blow_full_repo_review.md`

It is governed by:

- `docs/prime_directive/prime_directive.md`
- `docs/prime_directive/git_practices.md`
- `docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md`
- `docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md`

This is an implementation gameplan.

It is not an implementation.

No source-code or test implementation should begin until the Project Owner
explicitly approves execution of this gameplan.

Once approved, this gameplan is law. If implementation reality conflicts with
any action below, the implementer must stop, identify the exact
Phase.Stage.Action item that failed, and ask the Project Owner for guidance.
Silent simplification, silent reordering, and silent reinterpretation are
forbidden.

## Executive Implementation Goal

The goal is to make the package honest at its most important runtime and
training boundaries.

The concrete migration is:

```text
old package shape:
    clean Python surfaces, but hidden target semantics, optional masks,
    live mutable "snapshots", eager compatibility readouts, nominal loop
    policies, and a toy Gymnasium adapter

new package shape:
    explicit continuation semantics, first-class masks, live views separated
    from serializable value snapshots, lazy readouts, real internal-loop
    aggregation, strict env boundaries, hook-based Gymnasium bridge, and
    benchmarkable hot-path behavior
```

The implementation must not rewrite the package in another language.

The implementation must not introduce neural model infrastructure.

The implementation must not solve automatic observation-to-state inference.

The implementation must not silently reduce any Phase.Stage.Action item to a
weaker substitute.

## Fixed Defaults For This Gameplan

Unless the Project Owner changes these before execution, implementation must use
the following defaults.

1. The dedicated implementation branch is:

   ```text
   codex/synthetic-blow-revisions-01
   ```

2. The running implementation log is:

   ```text
   docs/design/synthetic_blow_revisions_01/01_003_synthetic_blow_review_revision_implementation_log.md
   ```

3. The first continuation implementation uses flat fields on
   `TrainingTransition`:

   ```python
   bootstrap_allowed: bool
   bootstrap_input: ActionSelectionInput | None = None
   bootstrap_reason: str = "unspecified"
   ```

   Do not introduce a nested `TransitionContinuation` object unless the Project
   Owner explicitly authorizes the extra surface during execution.

4. Default continuation semantics are:

   ```text
   terminated=True  -> bootstrap_allowed=False
   truncated=True and terminated=False -> bootstrap_allowed=True
   otherwise -> bootstrap_allowed=True
   ```

   The fields must still allow future lift-aware overrides through
   `bootstrap_input`.

5. `StepCollector` owns default Gymnasium `info["action_mask"]` extraction.
   A supplied `action_mask_factory` overrides automatic extraction.

6. A source mask with no legal actions is an error for action selection.

7. A target/bootstrap mask with no legal actions yields zero bootstrap.

8. All example Gymnasium envs reject invalid actions before coercion.

9. `bool` actions must be rejected by example envs unless a specific test
   explicitly authorizes bool acceptance. The default is reject.

10. Runtime live objects and serializable value snapshots must be split. The
    implementation should introduce:

    ```text
    LiveRuntimeView
    RuntimeSnapshot
    ```

    where `LiveRuntimeView` replaces the current live-object handoff role and
    `RuntimeSnapshot` becomes a stable value object.

11. If a complete rename from current `RuntimeSnapshot` to `LiveRuntimeView`
    causes excessive unrelated churn, implementation must stop and ask. Do not
    silently choose an alias-only compromise.

12. `PartitionTower` remains the authoritative runtime structure.

13. Compatibility `QuotientTierView` readouts must be lazy. The default
    `TowerRuntime.step(...)` path must not eagerly call
    `PartitionTower.to_quotient_tier_views()`.

14. `PartitionTower.update_with_delta(...)` must accept:

    ```python
    build_morphism: bool = False
    ```

    and must avoid full morphism-domain capture when `False`.

15. `LoopPolicy` decides internal-edge retention/stutter semantics. It must not
    also carry numeric aggregation semantics.

16. Internal/pre-image aggregation is a separate surface named:

    ```text
    InternalEdgeAggregator
    ```

17. `InternalEdgeAggregator` must support at least:

    ```text
    sum
    mean
    max
    ```

    It may delegate implementation to existing reward aggregation utilities
    where appropriate.

18. The new Gymnasium bridge is named:

    ```text
    StateCollapserGymWrapper
    ```

19. The old toy `GymnasiumAdapter` should be renamed or superseded so it no
    longer appears to be the serious Gymnasium bridge.

20. The first Gymnasium bridge uses explicit hooks. It must not infer
    observation-to-state identity automatically.

21. Benchmarks live under:

    ```text
    src/state_collapser/benchmarks/
    ```

22. Benchmark unit tests assert importability, CLI shape, and readout flags.
    They must not assert unstable wall-clock thresholds.

23. Documentation updates come after code behavior is real, not before.

## Global Stop Conditions

Implementation must stop and ask the Project Owner if any of the following
occur.

- A named file or symbol in this gameplan no longer exists.
- A Phase.Stage.Action item cannot be implemented as written.
- An action requires choosing between multiple incompatible public APIs not
  fixed by this gameplan.
- An action would require a lighter substitute implementation.
- A current test encodes behavior that directly contradicts this gameplan.
- A source edit would require rewriting unrelated systems outside the named
  scope of the current phase.
- A rename of `RuntimeSnapshot` causes broad unexpected breakage that would
  force a compatibility compromise.
- A lazy-readout change makes current runtime-position semantics ambiguous.
- A Gymnasium bridge hook signature cannot be typed without deciding an
  unresolved observation/state question.
- A benchmark action would require adding a heavyweight dependency.
- A validation command fails unexpectedly.
- The working tree contains unrelated user changes in a file this gameplan must
  edit.
- The implementation would need to revert user work.

If a stop condition is triggered, do not continue patching. Record the exact
Phase.Stage.Action in the implementation log and return control to the Project
Owner.

## Required Branch Discipline

Execution must not start on `main`.

Before implementation begins, create or switch to:

```text
codex/synthetic-blow-revisions-01
```

If the Project Owner requests a different branch name, use that name.

Before editing implementation files, record the active branch and starting
status in the implementation log.

## Required Running Implementation Log

The implementation log must be created before source-code edits begin:

```text
docs/design/synthetic_blow_revisions_01/01_003_synthetic_blow_review_revision_implementation_log.md
```

The log must record:

- branch name
- starting git status
- current commit hash
- each completed Phase.Stage.Action item
- exact files edited
- exact tests run
- test outcomes
- benchmark outputs when benchmark tooling exists
- surprises and failures
- Project Owner clarifications
- authorized deviations

The log must not hide weakened work behind phrases like "first pass",
"minimal slice", or "good enough" unless the Project Owner explicitly
authorizes that framing.

## Validation Command Set

Focused training validation:

```text
uv run pytest tests/training
```

Focused example boundary validation:

```text
uv run pytest tests/examples/test_env_action_boundaries.py
```

If `test_env_action_boundaries.py` is not yet created, use the per-env validity
tests named in the relevant phase.

Focused tower validation:

```text
uv run pytest tests/tower tests/quotient
```

Focused adapter validation:

```text
uv run pytest tests/adapters
```

Focused benchmark validation:

```text
uv run pytest tests/benchmarks
```

Benchmark smoke command after benchmark module exists:

```text
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only
```

Full validation:

```text
uv run ruff check .
uv run mypy src
uv run pytest
```

If any validation command fails unexpectedly, stop and reconstruct reality
before editing further.

## Phase 0: Execution Setup And Reality Binding

### Stage 0.1: Confirm Execution Authority

#### Action 0.1.1

High-level explanation:

Confirm that the Project Owner has explicitly approved execution. This protects
the design/gameplan boundary required by the prime directive.

Ground-truth files to inspect:

```text
docs/design/synthetic_blow_revisions_01/01_001_synthetic_blow_review_revision_blueprint.md
docs/design/synthetic_blow_revisions_01/01_002_synthetic_blow_review_revision_implementation_gameplan.md
docs/prime_directive/git_practices.md
docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md
docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md
```

Machine action:

Do not edit source. Confirm the owner has explicitly requested execution of
this gameplan.

Associated tests:

No tests.

Completion criteria:

- execution approval is explicit
- implementation has not begun before approval

Failure hypotheses:

- The owner asked only for gameplan creation, not execution.
- The owner wants to revise the gameplan before execution.
- The owner wants a different branch name or implementation order.

#### Action 0.1.2

High-level explanation:

Create or switch to the dedicated implementation branch.

Ground-truth files to inspect:

```text
docs/prime_directive/git_practices.md
```

Machine action:

Create or switch to:

```text
codex/synthetic-blow-revisions-01
```

Associated tests:

No tests.

Completion criteria:

- active branch is `codex/synthetic-blow-revisions-01`
- branch state is recorded in implementation log

Failure hypotheses:

- Branch already exists with unrelated changes.
- Current working tree has untracked or modified files that need owner guidance.
- The owner requests a different branch name.

### Stage 0.2: Create Implementation Log

#### Action 0.2.1

High-level explanation:

Create the running implementation log before any source edits.

Ground-truth files to inspect:

```text
docs/design/synthetic_blow_revisions_01/
```

Machine action:

Create:

```text
docs/design/synthetic_blow_revisions_01/01_003_synthetic_blow_review_revision_implementation_log.md
```

The initial log must include:

- title
- date
- source blueprint
- source gameplan
- active branch
- starting commit
- starting `git status --short --branch`
- statement that no source edits have occurred yet

Associated tests:

No tests.

Completion criteria:

- log file exists
- initial state is recorded

Failure hypotheses:

- The folder contains unexpected files that suggest a previous execution started.
- Git state contains unrelated changes requiring owner guidance.
- The log path conflicts with an existing user-created document.

### Stage 0.3: Bind Current Repository Reality

#### Action 0.3.1

High-level explanation:

Re-read all files that will anchor the first three correctness phases before
editing.

Ground-truth files to inspect:

```text
src/state_collapser/training/transitions.py
src/state_collapser/training/inputs.py
src/state_collapser/training/collectors.py
src/state_collapser/training/learners.py
src/state_collapser/training/reference_loops.py
src/state_collapser/training/__init__.py
tests/training/test_inputs_and_transitions.py
tests/training/test_collectors.py
tests/training/test_learners_and_reference_loops.py
```

Machine action:

Read the files and record in the implementation log whether they still match
the blueprint's current-state claims.

Associated tests:

No tests.

Completion criteria:

- implementation log records observed source/test reality
- any mismatch is documented before editing

Failure hypotheses:

- Files changed after the blueprint was written.
- Existing tests already cover some planned behavior under different names.
- Training interfaces have additional call sites not captured in the blueprint.

#### Action 0.3.2

High-level explanation:

Re-read all files that will anchor runtime, partition, snapshot, adapter, and
example phases.

Ground-truth files to inspect:

```text
src/state_collapser/tower/snapshot.py
src/state_collapser/tower/runtime.py
src/state_collapser/tower/partition/tower.py
src/state_collapser/tower/partition/action_layer.py
src/state_collapser/tower/partition/loop_policy.py
src/state_collapser/tower/partition/reward_aggregation.py
src/state_collapser/tower/partition/update.py
src/state_collapser/adapters/gymnasium.py
src/state_collapser/examples/articulated_loop_env/env.py
src/state_collapser/examples/cable_parallel_env/env.py
src/state_collapser/examples/dual_arm_manipulation_env/env.py
src/state_collapser/examples/parallelogram_singularity_env/env.py
README.md
CONTRIBUTING.md
```

Machine action:

Read the files and record in the implementation log whether they still match
the blueprint's current-state claims.

Associated tests:

No tests.

Completion criteria:

- implementation log records observed runtime/adapter/example reality
- any mismatch is documented before editing

Failure hypotheses:

- Another branch or user edit already changed runtime snapshots.
- The adapter surface was already renamed.
- Example env validation has already been fixed in some files.

## Phase 1: Strict Example Environment Action Boundaries

### Stage 1.1: Add Shared Boundary Tests

#### Action 1.1.1

High-level explanation:

Create one shared test file that verifies invalid action behavior across the
Gymnasium example envs named in the review.

Ground-truth files to inspect:

```text
tests/examples/test_articulated_loop_env_validity.py
tests/examples/test_cable_parallel_env_validity.py
tests/examples/test_dual_arm_manipulation_env_validity.py
tests/examples/test_parallelogram_singularity_env_validity.py
tests/examples/test_plate_support_env_gymnasium.py
tests/examples/test_rl_counterpoint_v3_gymnasium.py
```

Machine action:

Add:

```text
tests/examples/test_env_action_boundaries.py
```

The test file must parameterize over:

- `ArticulatedLoopEnv`, `ACTION_COUNT`
- `CableParallelEnv`, `ACTION_COUNT`
- `DualArmManipulationEnv`, `ACTION_COUNT`
- `ParallelogramSingularityEnv`, `ACTION_COUNT`
- `PlateSupportEnv`, `ACTION_COUNT`
- `RlCounterpointEnv`, `ACTION_COUNT`

It must assert that:

- `env.step(-1)` raises `ValueError`
- `env.step(ACTION_COUNT)` raises `ValueError`
- `env.step(1.9)` raises `ValueError`
- `env.step(True)` raises `ValueError`

Associated tests:

```text
uv run pytest tests/examples/test_env_action_boundaries.py
```

Expected test state after this action:

- tests may fail until Stage 1.2 fixes envs

Completion criteria:

- shared boundary test file exists
- tests express the desired behavior for all six envs

Failure hypotheses:

- Some envs intentionally accept NumPy integer scalar types and the test needs
  to avoid rejecting those.
- `RlCounterpointEnv` already has different invalid-action exception wording.
- Gymnasium `Discrete.contains(True)` behavior requires explicit bool guard in
  env code.

### Stage 1.2: Fix Environment Action Validation

#### Action 1.2.1

High-level explanation:

Update `ArticulatedLoopEnv.step(...)` to validate actions before conversion.

Ground-truth files to inspect:

```text
src/state_collapser/examples/articulated_loop_env/env.py
```

Machine action:

Modify `ArticulatedLoopEnv.step(...)` so it:

- rejects bool actions
- checks `self.action_space.contains(action)` before `int(action)`
- raises `ValueError` for unsupported actions
- only calls `primitive_transition(self.state, action_index)` after validation

Associated tests:

```text
uv run pytest tests/examples/test_env_action_boundaries.py tests/examples/test_articulated_loop_env_validity.py
```

Completion criteria:

- articulated-loop invalid actions fail before coercion
- existing articulated-loop validity tests still pass

Failure hypotheses:

- Existing tests assumed implicit int coercion.
- Gymnasium accepts bool under `Discrete.contains`, requiring explicit bool
  rejection before the contains check.
- NumPy integer scalar handling must remain accepted if Gymnasium accepts it.

#### Action 1.2.2

High-level explanation:

Update `CableParallelEnv.step(...)` to validate actions before conversion.

Ground-truth files to inspect:

```text
src/state_collapser/examples/cable_parallel_env/env.py
```

Machine action:

Apply the same validation pattern used in Action 1.2.1.

Associated tests:

```text
uv run pytest tests/examples/test_env_action_boundaries.py tests/examples/test_cable_parallel_env_validity.py
```

Completion criteria:

- cable-parallel invalid actions fail before coercion
- existing cable-parallel validity tests still pass

Failure hypotheses:

- Existing transition tests use a type accepted only by coercion.
- Error message expectations need update.
- Bool requires explicit rejection before `action_space.contains`.

#### Action 1.2.3

High-level explanation:

Update `DualArmManipulationEnv.step(...)` to validate actions before conversion.

Ground-truth files to inspect:

```text
src/state_collapser/examples/dual_arm_manipulation_env/env.py
```

Machine action:

Apply the same validation pattern used in Action 1.2.1.

Associated tests:

```text
uv run pytest tests/examples/test_env_action_boundaries.py tests/examples/test_dual_arm_manipulation_env_validity.py
```

Completion criteria:

- dual-arm invalid actions fail before coercion
- existing dual-arm validity tests still pass

Failure hypotheses:

- Existing tests use a raw NumPy scalar that remains valid and should not be
  rejected.
- Bool rejection needs an explicit `isinstance(action, bool)` check.
- Transition helper may raise its own exception if validation order is wrong.

#### Action 1.2.4

High-level explanation:

Update `ParallelogramSingularityEnv.step(...)` to validate actions before
conversion.

Ground-truth files to inspect:

```text
src/state_collapser/examples/parallelogram_singularity_env/env.py
```

Machine action:

Apply the same validation pattern used in Action 1.2.1.

Associated tests:

```text
uv run pytest tests/examples/test_env_action_boundaries.py tests/examples/test_parallelogram_singularity_env_validity.py
```

Completion criteria:

- parallelogram invalid actions fail before coercion
- existing parallelogram validity tests still pass

Failure hypotheses:

- Existing tests used float-like action values.
- Error type differs from other envs.
- Gymnasium contains check still accepts bool without explicit rejection.

### Stage 1.3: Validate Phase 1

#### Action 1.3.1

High-level explanation:

Run the complete example action-boundary and validity surface.

Ground-truth files to inspect:

```text
tests/examples/test_env_action_boundaries.py
tests/examples/test_*_validity.py
tests/examples/test_*_gymnasium.py
```

Machine action:

Run:

```text
uv run pytest tests/examples/test_env_action_boundaries.py tests/examples/test_articulated_loop_env_validity.py tests/examples/test_cable_parallel_env_validity.py tests/examples/test_dual_arm_manipulation_env_validity.py tests/examples/test_parallelogram_singularity_env_validity.py tests/examples/test_plate_support_env_gymnasium.py tests/examples/test_rl_counterpoint_v3_gymnasium.py
```

Associated tests:

Same as machine action.

Completion criteria:

- focused env-boundary tests pass
- implementation log records test command and outcome

Failure hypotheses:

- Existing envs return different invalid-action exception types.
- `RlCounterpointEnv` or `PlateSupportEnv` needs bool-specific adjustment.
- Shared parameterization imports wrong `ACTION_COUNT` symbol.

## Phase 2: First-Class Action Masks

### Stage 2.1: Add Mask Utility Surface

#### Action 2.1.1

High-level explanation:

Add reusable action-mask helpers so collectors and learners do not duplicate
mask interpretation.

Ground-truth files to inspect:

```text
src/state_collapser/training/inputs.py
src/state_collapser/training/__init__.py
```

Machine action:

Add:

```text
src/state_collapser/training/masks.py
```

The file must implement:

```python
def mask_from_info(info: Mapping[str, object]) -> tuple[bool, ...] | None
def legal_actions(mask: tuple[bool, ...] | None, action_count: int) -> tuple[int, ...]
def action_is_legal(action: int, mask: tuple[bool, ...] | None) -> bool
```

Behavior:

- missing `action_mask` returns `None`
- list, tuple, and NumPy-like iterable masks normalize to tuple of bools
- `None` mask means all actions legal
- empty tuple means no actions legal
- out-of-range action is illegal
- non-int action is illegal for `action_is_legal`

Associated tests:

Add:

```text
tests/training/test_masks.py
```

Run:

```text
uv run pytest tests/training/test_masks.py
```

Completion criteria:

- mask helper tests pass
- helpers are exported from `state_collapser.training` if consistent with
  existing package style

Failure hypotheses:

- NumPy arrays need special handling for truth-value ambiguity.
- Current pyproject optional dependencies affect whether tests can import NumPy
  directly.
- Existing typing style prefers `Sequence[bool]` over generic iterables.

### Stage 2.2: Wire Masks Into Collector

#### Action 2.2.1

High-level explanation:

Make `StepCollector.reset_episode(...)` extract action masks from runtime info
when no factory override is supplied.

Ground-truth files to inspect:

```text
src/state_collapser/training/collectors.py
tests/training/test_collectors.py
```

Machine action:

Modify `StepCollector._build_action_mask(...)` or its call sites so that:

- if `action_mask_factory` is not `None`, it remains authoritative
- otherwise `mask_from_info(action_input.diagnostics)` is used
- reset input receives normalized `action_mask`

Associated tests:

Add tests to `tests/training/test_collectors.py`:

- reset extracts `info["action_mask"]`
- factory overrides `info["action_mask"]`

Run:

```text
uv run pytest tests/training/test_collectors.py tests/training/test_masks.py
```

Completion criteria:

- reset mask extraction works without custom factory
- factory override remains working

Failure hypotheses:

- Current diagnostics field does not preserve reset info exactly.
- Existing collector tests assume `action_mask is None`.
- Runtime protocol tests use minimal fake reset objects without `info`.

#### Action 2.2.2

High-level explanation:

Make `StepCollector.collect_step(...)` reject masked-off selected actions before
stepping the runtime.

Ground-truth files to inspect:

```text
src/state_collapser/training/collectors.py
tests/training/test_collectors.py
```

Machine action:

Modify `collect_step(...)` so that:

- non-int chosen actions still raise as before
- if source input has a mask and chosen action is illegal, raise `ValueError`
- runtime step is not called after masked-off action

Associated tests:

Add tests:

- masked-off decision raises
- fake runtime step call count remains zero after masked-off decision

Run:

```text
uv run pytest tests/training/test_collectors.py
```

Completion criteria:

- masked action rejection occurs before runtime mutation
- existing collector behavior remains intact

Failure hypotheses:

- Current fake runtime does not expose a call-count hook.
- Existing action decisions use object actions in tests.
- Mask length shorter than action count needs explicit behavior.

#### Action 2.2.3

High-level explanation:

Make `StepCollector.collect_step(...)` attach target masks from step info.

Ground-truth files to inspect:

```text
src/state_collapser/training/collectors.py
tests/training/test_collectors.py
```

Machine action:

Modify target-input construction so step-result `info["action_mask"]` becomes
`next_input.action_mask` when no factory override is supplied.

Associated tests:

Add tests:

- target input extracts `info["action_mask"]`
- target factory override works

Run:

```text
uv run pytest tests/training/test_collectors.py
```

Completion criteria:

- next input carries normalized action mask
- no duplicate mask construction logic is introduced

Failure hypotheses:

- Current `build_action_selection_input(...)` rebuild path drops diagnostics.
- Existing tests assert exact input equality without masks.
- Runtime fake result `info` shape needs extension.

### Stage 2.3: Validate Phase 2

#### Action 2.3.1

High-level explanation:

Run full training tests after mask utility and collector integration.

Ground-truth files to inspect:

```text
tests/training/
```

Machine action:

Run:

```text
uv run pytest tests/training
```

Associated tests:

Same as machine action.

Completion criteria:

- training tests pass
- implementation log records command and outcome

Failure hypotheses:

- Learner tests now expose target-mask bootstrap bug planned for Phase 3.
- Collector tests need updates for new default extraction behavior.
- `ActionSelectionInput` construction helpers need clearer mask handling.

## Phase 3: Continuation-Aware And Masked Learner Semantics

### Stage 3.1: Extend TrainingTransition

#### Action 3.1.1

High-level explanation:

Add explicit continuation/bootstrap fields to `TrainingTransition`.

Ground-truth files to inspect:

```text
src/state_collapser/training/transitions.py
tests/training/test_inputs_and_transitions.py
```

Machine action:

Modify `TrainingTransition` to include:

```python
bootstrap_allowed: bool
bootstrap_input: ActionSelectionInput | None = None
bootstrap_reason: str = "unspecified"
```

The field order should preserve required fields before optional defaults.

Associated tests:

Update or add tests asserting:

- transition can be constructed with explicit `bootstrap_allowed`
- default `bootstrap_input` is `None`
- default `bootstrap_reason` is `"unspecified"`

Run:

```text
uv run pytest tests/training/test_inputs_and_transitions.py
```

Completion criteria:

- transition dataclass exposes fields
- transition tests pass

Failure hypotheses:

- Existing tests instantiate `TrainingTransition` without new required field.
- Mypy requires adjusting `__all__` or imports.
- Field ordering conflicts with dataclass default rules.

#### Action 3.1.2

High-level explanation:

Add a small continuation helper so collectors use one semantics path.

Ground-truth files to inspect:

```text
src/state_collapser/training/transitions.py
src/state_collapser/training/collectors.py
```

Machine action:

Add either to `transitions.py` or a new `continuation.py`:

```python
@dataclass(frozen=True, slots=True)
class BootstrapSemantics:
    bootstrap_on_truncation: bool = True

def default_bootstrap_allowed(
    *,
    terminated: bool,
    truncated: bool,
    semantics: BootstrapSemantics,
) -> bool:
    ...
```

Behavior:

- terminal means no bootstrap
- truncation means bootstrap if configured
- otherwise bootstrap

Associated tests:

Add:

```text
tests/training/test_continuation.py
```

Run:

```text
uv run pytest tests/training/test_continuation.py
```

Completion criteria:

- helper has tests for terminal, truncation default, truncation disabled, and
  ordinary transition

Failure hypotheses:

- Keeping helper in `transitions.py` creates import cycles.
- Existing package style prefers smaller modules.
- The name `BootstrapSemantics` conflicts with another symbol.

### Stage 3.2: Collector Computes Continuation

#### Action 3.2.1

High-level explanation:

Make `StepCollector` compute and populate transition bootstrap fields.

Ground-truth files to inspect:

```text
src/state_collapser/training/collectors.py
src/state_collapser/training/transitions.py
tests/training/test_collectors.py
```

Machine action:

Modify `StepCollector` so it:

- accepts a bootstrap/continuation config with default
  `bootstrap_on_truncation=True`
- computes `bootstrap_allowed`
- sets `bootstrap_input=next_input`
- sets `bootstrap_reason` to one of:
  - `"terminated"`
  - `"truncated_bootstrap"`
  - `"truncated_no_bootstrap"`
  - `"continuing"`

Associated tests:

Add collector tests:

- terminal transition has `bootstrap_allowed=False`
- truncation default has `bootstrap_allowed=True`
- truncation disabled has `bootstrap_allowed=False`
- continuing transition has `bootstrap_allowed=True`
- bootstrap input is target input

Run:

```text
uv run pytest tests/training/test_collectors.py tests/training/test_continuation.py
```

Completion criteria:

- collector owns continuation semantics
- transition objects are populated consistently

Failure hypotheses:

- Adding config to `StepCollector` changes existing constructor call sites.
- Existing reference loops instantiate collector without updated args.
- Fake step results need terminal/truncation variants.

#### Action 3.2.2

High-level explanation:

Add one synthetic lift-aware override test using manual `bootstrap_input`.

Ground-truth files to inspect:

```text
tests/training/test_learners_and_reference_loops.py
src/state_collapser/training/learners.py
```

Machine action:

Add a test that constructs a `TrainingTransition` where:

- `target_input` has one key
- `bootstrap_input` has a different key
- `bootstrap_allowed=True`
- learner update uses the `bootstrap_input` key

Associated tests:

```text
uv run pytest tests/training/test_learners_and_reference_loops.py
```

Expected test state after this action:

- may fail until Stage 3.3 updates learner

Completion criteria:

- test encodes lift-aware future behavior
- no implementation shortcut is used

Failure hypotheses:

- Current learner key function cannot distinguish target and bootstrap inputs in
  the test setup.
- Existing helper constructors make it awkward to create different tower keys.
- Test must avoid depending on live runtime snapshots.

### Stage 3.3: Learner Uses Continuation And Masks

#### Action 3.3.1

High-level explanation:

Update `TabularQLearner.act(...)` so all-false source masks are explicit errors.

Ground-truth files to inspect:

```text
src/state_collapser/training/learners.py
tests/training/test_learners_and_reference_loops.py
```

Machine action:

Modify action selection so:

- `None` mask means all actions legal
- non-empty mask selects only true entries within `action_count`
- mask with no legal actions raises `ValueError`
- learner never silently falls back to all actions when mask exists

Associated tests:

Add tests:

- all-false source mask raises
- partial mask never chooses masked-off action over repeated calls

Run:

```text
uv run pytest tests/training/test_learners_and_reference_loops.py
```

Completion criteria:

- action selection mask behavior is explicit
- existing epsilon-greedy tests still pass

Failure hypotheses:

- Existing tests expected fallback-to-all behavior.
- Randomness makes repeated-call mask test flaky if not seeded.
- Mask shorter than action count needs clear helper behavior.

#### Action 3.3.2

High-level explanation:

Update `TabularQLearner.update(...)` to use explicit continuation and target
masks.

Ground-truth files to inspect:

```text
src/state_collapser/training/learners.py
src/state_collapser/training/masks.py
tests/training/test_learners_and_reference_loops.py
```

Machine action:

Modify update semantics so:

- bootstrap is zero if `transition.bootstrap_allowed` is false
- bootstrap input is `transition.bootstrap_input` if not `None`
- otherwise bootstrap input is `transition.target_input`
- bootstrap candidate actions are legal actions from bootstrap input mask
- no legal bootstrap actions means bootstrap `0.0`
- diagnostics include `bootstrap_allowed`, `bootstrap_key`,
  `legal_target_action_count`, and `bootstrap_reason`

Associated tests:

Add tests:

- terminal transition target equals reward
- truncation default bootstraps
- truncation disabled does not bootstrap
- bootstrap uses `bootstrap_input` key when present
- bootstrap ignores masked-off target actions
- all-false target mask yields zero bootstrap

Run:

```text
uv run pytest tests/training/test_learners_and_reference_loops.py tests/training/test_masks.py tests/training/test_continuation.py
```

Completion criteria:

- learner no longer infers bootstrap from raw `terminated/truncated`
- learner uses masks in target calculation
- focused learner tests pass

Failure hypotheses:

- Existing `TrainingTransition` construction tests need all new fields.
- Diagnostics assertions need flexible matching.
- Q-table setup for masked bootstrap tests must initialize values carefully.

### Stage 3.4: Validate Phase 3

#### Action 3.4.1

High-level explanation:

Run full training validation after masks and continuation semantics are wired.

Ground-truth files to inspect:

```text
src/state_collapser/training/
tests/training/
```

Machine action:

Run:

```text
uv run pytest tests/training
uv run mypy src/state_collapser/training
```

Associated tests:

Same as machine action.

Completion criteria:

- training tests pass
- training package type-checks
- implementation log records outcomes

Failure hypotheses:

- Mypy command may need full `uv run mypy src` because package-level mypy config
  expects root source path.
- Reference loops need constructor changes for new collector config.
- Example tests may still fail later until example loops are consolidated.

## Phase 4: Reference Training Loop Consolidation

### Stage 4.1: Add Shared Example Training Helper

#### Action 4.1.1

High-level explanation:

Add a shared example helper so mechanical examples do not duplicate tabular
target semantics.

Ground-truth files to inspect:

```text
src/state_collapser/training/reference_loops.py
src/state_collapser/training/learners.py
src/state_collapser/examples/articulated_loop_env/training.py
src/state_collapser/examples/cable_parallel_env/training.py
src/state_collapser/examples/dual_arm_manipulation_env/training.py
src/state_collapser/examples/parallelogram_singularity_env/training.py
src/state_collapser/examples/plate_support_env/training.py
```

Machine action:

Add:

```text
src/state_collapser/examples/_shared_training.py
```

The helper should provide a reusable function for simple tower-aware tabular
training around:

- runtime factory
- action count
- config dataclass or config-like protocol
- result/episode summary builders
- `TabularQLearner`
- `run_reference_online_loop` or direct `StepCollector` use

Associated tests:

Add:

```text
tests/examples/test_training_semantics_shared.py
```

Run:

```text
uv run pytest tests/examples/test_training_semantics_shared.py tests/training
```

Completion criteria:

- shared helper exists
- test proves helper uses `TabularQLearner` continuation semantics

Failure hypotheses:

- Existing example result dataclasses differ too much for one generic helper.
- A simpler migration through `run_reference_online_loop` is cleaner.
- Plate support exploit/explore path must be excluded from shared helper.

### Stage 4.2: Migrate Mechanical Example Training Paths

#### Action 4.2.1

High-level explanation:

Migrate `ArticulatedLoopEnv` tower training to shared target semantics.

Ground-truth files to inspect:

```text
src/state_collapser/examples/articulated_loop_env/training.py
tests/examples/test_articulated_loop_env_tower_training.py
```

Machine action:

Refactor `run_tower_training(...)` to use the shared helper or generic
reference loop without changing the public result shape unless unavoidable.

Associated tests:

```text
uv run pytest tests/examples/test_articulated_loop_env_tower_training.py
```

Completion criteria:

- public training smoke path still passes
- no local Q-target formula remains in the file

Failure hypotheses:

- Tests assert exact q-table shape tied to old loop.
- Result dataclass needs adapter code.
- Runtime reset/step result differs from generic protocol.

#### Action 4.2.2

High-level explanation:

Migrate `CableParallelEnv` tower training to shared target semantics.

Ground-truth files to inspect:

```text
src/state_collapser/examples/cable_parallel_env/training.py
tests/examples/test_cable_parallel_env_tower_training.py
```

Machine action:

Apply the same pattern as Action 4.2.1.

Associated tests:

```text
uv run pytest tests/examples/test_cable_parallel_env_tower_training.py
```

Completion criteria:

- cable-parallel training smoke path still passes
- no local Q-target formula remains

Failure hypotheses:

- Existing runtime protocol differs subtly from shared helper expectation.
- Config/result dataclasses need compatibility adapter.
- Tests depend on old q-table mutation details.

#### Action 4.2.3

High-level explanation:

Migrate `DualArmManipulationEnv` tower training to shared target semantics.

Ground-truth files to inspect:

```text
src/state_collapser/examples/dual_arm_manipulation_env/training.py
tests/examples/test_dual_arm_manipulation_env_tower_training.py
```

Machine action:

Apply the same pattern as Action 4.2.1.

Associated tests:

```text
uv run pytest tests/examples/test_dual_arm_manipulation_env_tower_training.py
```

Completion criteria:

- dual-arm training smoke path still passes
- no local Q-target formula remains

Failure hypotheses:

- Action count import differs from helper assumptions.
- Runtime factory requires schema/policy parameters not shared across examples.
- Tests need update to assert semantic invariants instead of exact internals.

#### Action 4.2.4

High-level explanation:

Migrate `ParallelogramSingularityEnv` tower training to shared target
semantics.

Ground-truth files to inspect:

```text
src/state_collapser/examples/parallelogram_singularity_env/training.py
tests/examples/test_parallelogram_singularity_env_tower_training.py
```

Machine action:

Apply the same pattern as Action 4.2.1.

Associated tests:

```text
uv run pytest tests/examples/test_parallelogram_singularity_env_tower_training.py
```

Completion criteria:

- parallelogram training smoke path still passes
- no local Q-target formula remains

Failure hypotheses:

- Existing tests rely on old episode summary fields.
- Runtime constructor signature differs from helper assumptions.
- Local training path contains behavior not covered by shared helper.

#### Action 4.2.5

High-level explanation:

Migrate the ordinary `PlateSupportEnv` tower training path while preserving the
experimental exploit/explore path.

Ground-truth files to inspect:

```text
src/state_collapser/examples/plate_support_env/training.py
tests/examples/test_plate_support_env_tower_training.py
tests/examples/test_plate_support_env_exploit_explore_training.py
```

Machine action:

Refactor only the ordinary `run_tower_training(...)` path to shared/generic
target semantics.

Do not refactor `PlateSupportTierLearner` or
`run_exploit_explore_training(...)` in this action.

Associated tests:

```text
uv run pytest tests/examples/test_plate_support_env_tower_training.py tests/examples/test_plate_support_env_exploit_explore_training.py
```

Completion criteria:

- ordinary plate-support training path shares target semantics
- exploit/explore tests still pass
- experimental exploit/explore path remains isolated

Failure hypotheses:

- Ordinary and exploit/explore training code share helper functions that cannot
  be split trivially.
- Existing tests import private helpers removed by refactor.
- Exploit/explore path exposes separate target-semantics issues requiring a
  later authorized phase.

### Stage 4.3: Validate Phase 4

#### Action 4.3.1

High-level explanation:

Run all example training tests after consolidation.

Ground-truth files to inspect:

```text
tests/examples/*tower_training*.py
tests/examples/*exploit_explore_training*.py
```

Machine action:

Run:

```text
uv run pytest tests/examples/test_articulated_loop_env_tower_training.py tests/examples/test_cable_parallel_env_tower_training.py tests/examples/test_dual_arm_manipulation_env_tower_training.py tests/examples/test_parallelogram_singularity_env_tower_training.py tests/examples/test_plate_support_env_tower_training.py tests/examples/test_plate_support_env_exploit_explore_training.py tests/examples/test_rl_counterpoint_v3_tower_training.py tests/examples/test_training_semantics_shared.py
```

Associated tests:

Same as machine action.

Completion criteria:

- all example training tests pass
- implementation log records any intentionally unmigrated experimental path

Failure hypotheses:

- `rl_counterpoint_v3` now fails because mask enforcement exposes invalid
  policy choices.
- Shared helper changed q-table keys.
- Some examples still require local training wrappers for public API stability.

## Phase 5: Runtime View And Serializable Snapshot Split

### Stage 5.1: Define View And Snapshot Types

#### Action 5.1.1

High-level explanation:

Split the current live-object snapshot role from the value-snapshot role.

Ground-truth files to inspect:

```text
src/state_collapser/tower/snapshot.py
tests/tower/test_snapshot.py
```

Machine action:

Modify `src/state_collapser/tower/snapshot.py` to define:

```text
LiveRuntimeView
RuntimeSnapshot
```

`LiveRuntimeView` must carry the fields currently needed by runtime/training
surfaces, including live graph/tower references.

`RuntimeSnapshot` must be a value object with no live graph/tower fields.

Associated tests:

Update `tests/tower/test_snapshot.py` and add if needed:

```text
tests/tower/test_runtime_snapshot_values.py
```

Run:

```text
uv run pytest tests/tower/test_snapshot.py tests/tower/test_runtime_snapshot_values.py
```

Completion criteria:

- live and value concepts are separate
- docstrings do not call live view serializable
- value snapshot tests exist

Failure hypotheses:

- Existing imports expect `RuntimeSnapshot` to be the live object.
- A compatibility alias may be needed but is not authorized if it hides
  semantics.
- Value snapshot cannot serialize arbitrary user states without serializer
  policy.

#### Action 5.1.2

High-level explanation:

Implement value snapshot serialization for JSON-safe payloads.

Ground-truth files to inspect:

```text
src/state_collapser/tower/snapshot.py
tests/tower/test_runtime_snapshot_values.py
```

Machine action:

Add `to_dict()` to `RuntimeSnapshot`.

Rules:

- include current base state as-is only if JSON-safe or represent it through
  `repr(...)` with a documented field name
- include tier positions, counts, reward totals, active control tier, last
  control action, update flags, and diagnostics
- do not include live graph objects
- do not include `PartitionTower`
- do not include `QuotientTierView`

Associated tests:

Add tests:

- `json.dumps(snapshot.to_dict())` succeeds for JSON-safe state
- no live graph/tower fields appear in dict

Run:

```text
uv run pytest tests/tower/test_runtime_snapshot_values.py
```

Completion criteria:

- value snapshot can be serialized in controlled JSON-safe cases
- non-goal of universal arbitrary object JSON is documented in code comments or
  tests

Failure hypotheses:

- Current state ids are custom objects not JSON-safe.
- Diagnostics contain non-JSON-safe objects.
- Mypy dislikes broad dict value type.

### Stage 5.2: Update Runtime To Return Live Views

#### Action 5.2.1

High-level explanation:

Update `TowerRuntime.reset(...)` and `TowerRuntime.step(...)` to return
`LiveRuntimeView`.

Ground-truth files to inspect:

```text
src/state_collapser/tower/runtime.py
src/state_collapser/tower/snapshot.py
tests/tower/test_runtime.py
```

Machine action:

Modify runtime return construction to use `LiveRuntimeView`.

Add a method or property on the live view to produce a value snapshot:

```python
def to_snapshot(self) -> RuntimeSnapshot:
    ...
```

Associated tests:

Update runtime tests to assert:

- reset returns `LiveRuntimeView`
- step returns `LiveRuntimeView`
- `to_snapshot()` returns `RuntimeSnapshot`

Run:

```text
uv run pytest tests/tower/test_runtime.py tests/tower/test_snapshot.py tests/tower/test_runtime_snapshot_values.py
```

Completion criteria:

- runtime live handoff is honestly named
- value snapshot production exists

Failure hypotheses:

- Many tests import `RuntimeSnapshot` directly as the live type.
- Example runtime protocols annotate the old class.
- `to_snapshot()` needs runtime diagnostics not stored on live view.

#### Action 5.2.2

High-level explanation:

Update training protocols and summaries to depend on live view shape rather than
serializable snapshot naming.

Ground-truth files to inspect:

```text
src/state_collapser/training/inputs.py
src/state_collapser/training/transitions.py
src/state_collapser/training/collectors.py
tests/training/
```

Machine action:

Update imports and type annotations from old `RuntimeSnapshot` live role to
`LiveRuntimeView` or a protocol.

Ensure `RuntimeSnapshotSummary` stores only value summary data.

Associated tests:

```text
uv run pytest tests/training tests/tower/test_snapshot.py
```

Completion criteria:

- training package no longer treats live view as serializable snapshot
- transition summary remains small and stable

Failure hypotheses:

- Protocol typing is easier than concrete class import.
- Tests constructing action inputs need helper updates.
- Existing `tower_position_key(...)` function expects old class name.

### Stage 5.3: Validate Snapshot Immutability

#### Action 5.3.1

High-level explanation:

Prove old value snapshots do not mutate after runtime advances.

Ground-truth files to inspect:

```text
tests/tower/test_runtime_snapshot_values.py
src/state_collapser/tower/runtime.py
```

Machine action:

Add test:

- reset runtime
- take value snapshot
- step runtime
- assert old value snapshot dict is unchanged

Associated tests:

```text
uv run pytest tests/tower/test_runtime_snapshot_values.py
```

Completion criteria:

- immutability test passes
- old live view mutability is not confused with value snapshot stability

Failure hypotheses:

- Value snapshot still stores tuple containing mutable diagnostics.
- Runtime step changes object referenced inside snapshot.
- Test uses a state object whose repr changes.

### Stage 5.4: Validate Phase 5

#### Action 5.4.1

High-level explanation:

Run tower, training, and example runtime integration tests after snapshot split.

Ground-truth files to inspect:

```text
tests/tower/
tests/training/
tests/examples/*runtime_integration*.py
```

Machine action:

Run:

```text
uv run pytest tests/tower tests/training tests/examples/test_articulated_loop_env_runtime_integration.py tests/examples/test_cable_parallel_env_runtime_integration.py tests/examples/test_dual_arm_manipulation_env_runtime_integration.py tests/examples/test_parallelogram_singularity_env_runtime_integration.py tests/examples/test_plate_support_env_runtime_integration.py tests/examples/test_rl_counterpoint_v3_runtime_integration.py
```

Associated tests:

Same as machine action.

Completion criteria:

- snapshot/view split does not break runtime/training integration
- implementation log records any compatibility shim used

Failure hypotheses:

- Example runtimes annotate old snapshot names.
- Tests assert `isinstance(..., RuntimeSnapshot)` for live views.
- Compatibility readouts still coupled to snapshot construction.

## Phase 6: Lazy Compatibility Readouts And Optional Morphisms

### Stage 6.1: Add Optional Morphism Capture

#### Action 6.1.1

High-level explanation:

Make morphism construction optional in partition updates.

Ground-truth files to inspect:

```text
src/state_collapser/tower/partition/tower.py
src/state_collapser/tower/partition/update.py
tests/tower/partition/test_incremental_update.py
```

Machine action:

Modify `PartitionTower.update_with_delta(...)` to accept:

```python
build_morphism: bool = False
```

Behavior:

- if `False`, do not call `_capture_morphism_domain()`
- returned `TowerUpdateResult.morphism` should encode no explicit maps or a
  documented empty/default morphism
- if `True`, preserve current morphism behavior

Associated tests:

Add tests:

- default update avoids morphism capture
- explicit `build_morphism=True` preserves non-empty morphism behavior where
  applicable

Run:

```text
uv run pytest tests/tower/partition/test_incremental_update.py
```

Completion criteria:

- optional morphism parameter exists
- default path avoids full morphism-domain capture

Failure hypotheses:

- Existing tests require morphism maps by default.
- `TowerMorphism` cannot represent "not built" cleanly.
- Monkeypatching `_capture_morphism_domain` is needed to prove it is not called.

### Stage 6.2: Make Quotient Readouts Lazy

#### Action 6.2.1

High-level explanation:

Stop rebuilding compatibility quotient tiers in the default runtime update path.

Ground-truth files to inspect:

```text
src/state_collapser/tower/runtime.py
tests/tower/test_runtime.py
tests/tower/partition/test_readout.py
```

Machine action:

Modify `TowerRuntime._apply_partition_update_result(...)` so it:

- stores `TowerUpdateResult`
- updates selected base edges and stopping reason
- invalidates a compatibility-readout cache
- does not call `to_quotient_tier_views()` by default

Associated tests:

Add tests:

- monkeypatch or spy proves `to_quotient_tier_views()` is not called during
  default step
- current position remains available from partition cell ids

Run:

```text
uv run pytest tests/tower/test_runtime.py tests/tower/partition/test_readout.py
```

Completion criteria:

- default runtime step avoids eager readout
- runtime still exposes depth/position through partition state

Failure hypotheses:

- Existing `quotient_tiers` property expects eager data.
- Runtime snapshots currently require ordered quotient tiers.
- Depth probe depends on `tower_runtime.quotient_tiers`.

#### Action 6.2.2

High-level explanation:

Add explicit compatibility readout API.

Ground-truth files to inspect:

```text
src/state_collapser/tower/runtime.py
tests/tower/test_runtime.py
tests/tower/partition/test_readout.py
```

Machine action:

Add:

```python
def compatibility_quotient_tiers(self) -> tuple[QuotientTierView, ...]:
    ...
```

Behavior:

- for partition backend, lazily builds and caches readout
- for legacy backend, returns current quotient tiers
- cache invalidates on partition update
- `quotient_tiers` property should be documented as compatibility-facing or
  delegated to `compatibility_quotient_tiers()` only if existing public tests
  require it

Associated tests:

Add tests:

- explicit compatibility call returns tier views
- repeated call uses cache if cache is implemented
- update invalidates cache

Run:

```text
uv run pytest tests/tower/test_runtime.py tests/tower/partition/test_readout.py
```

Completion criteria:

- compatibility readout is explicit
- old consumers can be migrated

Failure hypotheses:

- Keeping `quotient_tiers` property lazy may hide readout cost from benchmarks.
- Cache invalidation is easy to miss.
- Legacy backend semantics differ.

### Stage 6.3: Update Depth Probe And Runtime Consumers

#### Action 6.3.1

High-level explanation:

Update tower-depth probe to avoid forcing compatibility readouts in the default
measurement path.

Ground-truth files to inspect:

```text
src/state_collapser/examples/tower_depth_probe.py
tests/examples/test_tower_depth_probe.py
```

Machine action:

Modify probe runtime handle so default depth calculation can use partition tower
depth or live-view position length without requiring `quotient_tiers`.

If a compatibility-readout mode is needed, expose it explicitly.

Associated tests:

```text
uv run pytest tests/examples/test_tower_depth_probe.py tests/tower/test_runtime.py
```

Completion criteria:

- depth probe still works
- default probe does not force quotient readout
- explicit readout path remains testable

Failure hypotheses:

- Some runtimes use legacy backend and only expose quotient tiers.
- Protocol changes ripple through example runtimes.
- Existing tests assert `quotient_tiers` access.

### Stage 6.4: Validate Phase 6

#### Action 6.4.1

High-level explanation:

Run full tower and probe validation after lazy readout changes.

Ground-truth files to inspect:

```text
tests/tower/
tests/tower/partition/
tests/examples/test_tower_depth_probe.py
```

Machine action:

Run:

```text
uv run pytest tests/tower tests/quotient tests/examples/test_tower_depth_probe.py
```

Associated tests:

Same as machine action.

Completion criteria:

- tower/partition/readout tests pass
- probe tests pass
- implementation log records any compatibility readout migration decisions

Failure hypotheses:

- Lazy readout changes break snapshot/view tests.
- Legacy builder tests assume eager quotient tiers.
- Morphism tests need explicit `build_morphism=True`.

## Phase 7: Loop Policy Carry-Forward And Internal Aggregation

### Stage 7.1: Fix LoopPolicy Carry-Forward

#### Action 7.1.1

High-level explanation:

Stop hard-coding `LoopPolicy.drop_internal()` during action-layer carry-forward.

Ground-truth files to inspect:

```text
src/state_collapser/tower/partition/action_layer.py
src/state_collapser/tower/partition/tower.py
tests/tower/partition/test_loop_policy.py
```

Machine action:

Modify `ActionPartitionLayer.carry_forward_from(...)` to accept
`loop_policy: LoopPolicy`.

Update all call sites in `PartitionTower.initialize(...)`,
`PartitionTower._ensure_tier_exists(...)`, and any other carry-forward paths.

Associated tests:

Add tests:

- aggregate policy survives carry-forward records
- formal stutter policy survives carry-forward records

Run:

```text
uv run pytest tests/tower/partition/test_loop_policy.py tests/tower/partition/test_action_layer.py tests/tower/partition/test_incremental_update.py
```

Completion criteria:

- no hard-coded `LoopPolicy.drop_internal()` remains in carry-forward paths
- loop policy tests pass

Failure hypotheses:

- There are multiple carry-forward paths.
- Existing tests assume default drop policy implicitly.
- Internal edge records are not created in the path used by the new tests.

### Stage 7.2: Add InternalEdgeAggregator

#### Action 7.2.1

High-level explanation:

Create explicit internal/pre-image loop aggregation surface.

Ground-truth files to inspect:

```text
src/state_collapser/tower/partition/reward_aggregation.py
src/state_collapser/tower/partition/loop_policy.py
src/state_collapser/tower/partition/__init__.py
```

Machine action:

Add:

```text
src/state_collapser/tower/partition/internal_aggregation.py
```

It must define:

- `InternalAggregationName`
- `InternalAggregationResult`
- `InternalEdgeAggregator`
- `aggregate_internal_values(...)`

Required aggregation modes:

- `sum`
- `mean`
- `max`

Optional modes if cheap:

- `softmax`
- `p_mean`
- `p_norm`
- `custom`

Associated tests:

Add:

```text
tests/tower/partition/test_internal_aggregation.py
```

Run:

```text
uv run pytest tests/tower/partition/test_internal_aggregation.py
```

Completion criteria:

- internal aggregation surface exists
- sum/mean/max tests pass
- module exports are updated

Failure hypotheses:

- Reusing `RewardAggregator` directly creates confusing result names.
- Empty value behavior must be explicitly defined.
- Custom callable typing may complicate mypy.

#### Action 7.2.2

High-level explanation:

Wire internal aggregation configuration into `PartitionTower` diagnostics or
records without over-claiming full policy semantics.

Ground-truth files to inspect:

```text
src/state_collapser/tower/partition/tower.py
src/state_collapser/tower/partition/diagnostics.py
src/state_collapser/tower/partition/update.py
tests/tower/partition/test_internal_aggregation.py
```

Machine action:

Add `internal_edge_aggregator` configuration to `PartitionTower`.

At minimum:

- store the configured aggregator
- expose aggregator name in diagnostics or update result metadata
- do not invent unapproved reward semantics if no internal values exist

Associated tests:

Add tests:

- configured `InternalEdgeAggregator.max()` is retained by tower
- aggregator name appears in diagnostics or update result metadata

Run:

```text
uv run pytest tests/tower/partition/test_internal_aggregation.py tests/tower/partition/test_tower_initialization.py
```

Completion criteria:

- tower owns internal aggregation config
- diagnostics make choice visible

Failure hypotheses:

- Existing diagnostics dataclass needs schema change.
- There are no internal reward values yet, so value aggregation should remain
  standalone.
- Wiring too deeply would require unresolved reward semantics.

### Stage 7.3: Validate Phase 7

#### Action 7.3.1

High-level explanation:

Run partition tests after loop policy and aggregation changes.

Ground-truth files to inspect:

```text
tests/tower/partition/
```

Machine action:

Run:

```text
uv run pytest tests/tower/partition
```

Associated tests:

Same as machine action.

Completion criteria:

- partition tests pass
- loop-policy choices survive carry-forward
- internal aggregation tests pass

Failure hypotheses:

- Full incremental equivalence tests assume exact diagnostics counts.
- New diagnostics fields require expected-value updates.
- Existing reward aggregation tests need import-path updates.

## Phase 8: Real Gymnasium Bridge With Explicit Hooks

### Stage 8.1: Rename Or Supersede Toy Adapter

#### Action 8.1.1

High-level explanation:

Stop presenting the toy robot adapter as the serious Gymnasium bridge.

Ground-truth files to inspect:

```text
src/state_collapser/adapters/gymnasium.py
tests/adapters/test_gymnasium_adapter.py
README.md
```

Machine action:

Rename the current `GymnasiumAdapter` class to:

```text
RobotConstraintRuntimeAdapter
```

Keep a compatibility import only if required, but it must be documented as
legacy/toy and not as the primary bridge.

Associated tests:

Update:

```text
tests/adapters/test_gymnasium_adapter.py
```

Run:

```text
uv run pytest tests/adapters/test_gymnasium_adapter.py
```

Completion criteria:

- toy adapter no longer overclaims
- adapter tests pass under new naming

Failure hypotheses:

- Public exports or README examples import `GymnasiumAdapter`.
- Tests need to be renamed but file rename may be larger than necessary.
- Compatibility alias risks preserving confusing public API.

### Stage 8.2: Define Hook Config

#### Action 8.2.1

High-level explanation:

Define explicit hooks for interpreting a Gymnasium env as a
`state_collapser` graph/tower problem.

Ground-truth files to inspect:

```text
src/state_collapser/adapters/gymnasium.py
src/state_collapser/core/edges.py
src/state_collapser/core/action.py
src/state_collapser/core/state.py
```

Machine action:

Add hook dataclasses/protocols, either in `gymnasium.py` or:

```text
src/state_collapser/adapters/gymnasium_hooks.py
```

Required hooks:

- `state_key(observation, info) -> object`
- `action_key(action, observation, info) -> object`
- `action_mask(info, env) -> tuple[bool, ...] | None`
- `edge_labeler(source_key, action_key, target_key, info) -> tuple[object, ...]`
- optional `vista_provider`

Associated tests:

Add:

```text
tests/adapters/test_state_collapser_gym_wrapper.py
```

Initial tests should assert hook config construction and default optional hook
behavior.

Run:

```text
uv run pytest tests/adapters/test_state_collapser_gym_wrapper.py
```

Completion criteria:

- hooks are typed and importable
- no automatic observation-to-state inference is introduced

Failure hypotheses:

- Importing `gymnasium.Env` in type signatures complicates optional dependency
  behavior.
- `BaseEdge` construction expects `State` and `PrimitiveAction` wrappers rather
  than raw objects.
- Hook signatures need previous observation in `action_key`.

### Stage 8.3: Implement StateCollapserGymWrapper

#### Action 8.3.1

High-level explanation:

Implement a real wrapper around an arbitrary Gymnasium env in empirical opaque
mode.

Ground-truth files to inspect:

```text
src/state_collapser/adapters/gymnasium.py
tests/adapters/test_state_collapser_gym_wrapper.py
```

Machine action:

Implement `StateCollapserGymWrapper`.

Required behavior:

- wraps a provided env
- exposes `action_space`
- exposes `observation_space`
- `reset(seed=None, options=None)` delegates to wrapped env
- `step(action)` delegates to wrapped env
- uses hooks to compute source/target state identities and action identity
- records realized transition into `state_collapser` structural runtime or
  discovered graph layer
- attaches tower/runtime metadata to `info`
- does not infer unseen outgoing edges in opaque mode

Associated tests:

Add tests:

- wrapper exposes spaces
- reset delegates seed/options
- step returns five-tuple
- info contains state-collapser metadata
- source/action/target hooks are called
- opaque mode records only realized transition

Run:

```text
uv run pytest tests/adapters/test_state_collapser_gym_wrapper.py
```

Completion criteria:

- bridge exists and works for a small fake Gymnasium env
- empirical mode is honest about only observed transitions

Failure hypotheses:

- Building `TowerRuntime` requires a `HiddenGraph`, not just observed
  transitions.
- A lighter discovered-graph bridge is needed before full tower runtime
  integration.
- This action exposes an unresolved design decision about arbitrary Gymnasium
  env integration and must stop for PO guidance.

#### Action 8.3.2

High-level explanation:

Implement action-mask and edge-label propagation in the wrapper.

Ground-truth files to inspect:

```text
src/state_collapser/adapters/gymnasium.py
src/state_collapser/training/masks.py
tests/adapters/test_state_collapser_gym_wrapper.py
```

Machine action:

Extend wrapper so:

- `action_mask` hook result appears in returned `info`
- `edge_labeler` result is attached to recorded transition metadata
- no hook means no mask or empty label tuple, as configured

Associated tests:

Add tests:

- action mask hook result appears in info
- edge labels from hook are recorded
- missing optional mask hook is accepted

Run:

```text
uv run pytest tests/adapters/test_state_collapser_gym_wrapper.py
```

Completion criteria:

- bridge can provide masks and labels to downstream training/tower layers

Failure hypotheses:

- Existing `BaseEdge.labels` expects a specific label type.
- Info mutation needs to avoid overwriting env-provided keys.
- Hook exceptions need clear propagation.

### Stage 8.4: Document Observation-Vs-State Future Work

#### Action 8.4.1

High-level explanation:

Update README TODOs to document the explicit-hook bridge and the harder
observation-vs-state problem.

Ground-truth files to inspect:

```text
README.md
```

Machine action:

Update README TODO section to include:

- hook-based Gymnasium bridge
- observation-vs-state inference as future contribution area
- note that automatic inference is not required for core package usefulness

Associated tests:

No tests.

Completion criteria:

- README does not claim automatic observation-to-state inference is solved
- README names the future work clearly

Failure hypotheses:

- README TODO section has shifted since blueprint.
- Existing wording already covers this and should be amended not duplicated.
- The bridge implementation differs from planned name.

#### Action 8.4.2

High-level explanation:

Update CONTRIBUTING guidance for Gymnasium integrations.

Ground-truth files to inspect:

```text
CONTRIBUTING.md
```

Machine action:

Add guidance explaining:

- Gymnasium envs provide interaction shell
- `state_key` may be needed when observation is not state
- action masks should be exposed through info or hook
- transition labels drive contraction schemas
- automatic observation-to-state inference is future work

Associated tests:

No tests.

Completion criteria:

- contributor guidance matches actual bridge behavior

Failure hypotheses:

- CONTRIBUTING already has a section that should be extended rather than
  duplicated.
- New bridge naming changes during implementation.
- Docs overclaim current state of wrapper.

### Stage 8.5: Validate Phase 8

#### Action 8.5.1

High-level explanation:

Run adapter and docs-adjacent package tests.

Ground-truth files to inspect:

```text
tests/adapters/
tests/test_package.py
README.md
CONTRIBUTING.md
```

Machine action:

Run:

```text
uv run pytest tests/adapters tests/test_package.py
```

Associated tests:

Same as machine action.

Completion criteria:

- adapter tests pass
- package metadata tests still pass

Failure hypotheses:

- Optional dependency declarations need update if wrapper imports Gymnasium at
  module import time.
- Test package expects old adapter export.
- README links or badges are unaffected but package tests may inspect docs.

## Phase 9: Benchmark And Performance Regression Surface

### Stage 9.1: Add Benchmark Package

#### Action 9.1.1

High-level explanation:

Create a lightweight benchmark namespace without adding heavyweight benchmark
dependencies.

Ground-truth files to inspect:

```text
src/state_collapser/examples/tower_depth_probe.py
src/state_collapser/tower/runtime.py
src/state_collapser/tower/partition/tower.py
```

Machine action:

Add:

```text
src/state_collapser/benchmarks/__init__.py
src/state_collapser/benchmarks/tower_runtime_bench.py
```

The benchmark module must define a structured result dataclass with:

- benchmark name
- steps
- elapsed seconds
- operations per second
- discovered state count
- discovered edge count
- tower depth
- readout requested
- morphism requested

Associated tests:

Add:

```text
tests/benchmarks/test_tower_runtime_bench.py
```

Run:

```text
uv run pytest tests/benchmarks/test_tower_runtime_bench.py
```

Completion criteria:

- benchmark module imports
- structured result can be constructed

Failure hypotheses:

- `tests/benchmarks` package needs `__init__.py`.
- Benchmark imports examples that are slow or optional.
- Mypy requires exact numeric types for timing.

### Stage 9.2: Implement Benchmark Modes

#### Action 9.2.1

High-level explanation:

Implement no-schema and default-schema benchmark modes.

Ground-truth files to inspect:

```text
src/state_collapser/benchmarks/tower_runtime_bench.py
src/state_collapser/examples/tower_depth_probe.py
```

Machine action:

Benchmark should support:

- no-schema flat probe
- default schema probe
- configurable step count
- seed
- summary-only output

Associated tests:

Add tests:

- tiny no-schema run returns result
- tiny default-schema run returns result

Run:

```text
uv run pytest tests/benchmarks/test_tower_runtime_bench.py
```

Completion criteria:

- benchmark runs fast with tiny step count
- benchmark does not enforce timing thresholds

Failure hypotheses:

- Default schema requires env-specific schema setup.
- Reusing tower-depth probe makes readout behavior ambiguous.
- Benchmark output needs stable formatting for tests.

#### Action 9.2.2

High-level explanation:

Implement readout-disabled and readout-enabled partition update benchmark modes.

Ground-truth files to inspect:

```text
src/state_collapser/benchmarks/tower_runtime_bench.py
src/state_collapser/tower/runtime.py
src/state_collapser/tower/partition/tower.py
```

Machine action:

Add modes that separately measure:

- partition update without compatibility readout
- partition update with compatibility readout

Associated tests:

Add tests:

- readout-disabled mode records `readout_requested=False`
- readout-enabled mode records `readout_requested=True`
- readout-enabled mode actually calls compatibility readout

Run:

```text
uv run pytest tests/benchmarks/test_tower_runtime_bench.py
```

Completion criteria:

- benchmark can distinguish hot path from compatibility path

Failure hypotheses:

- Runtime API does not expose enough hooks to isolate update from env stepping.
- Readout-enabled path still uses cached readout and hides cost.
- Tests need a spy instead of timing assertions.

### Stage 9.3: Benchmark CLI

#### Action 9.3.1

High-level explanation:

Expose benchmark as a `python -m` CLI.

Ground-truth files to inspect:

```text
src/state_collapser/benchmarks/tower_runtime_bench.py
```

Machine action:

Add CLI arguments:

- `--steps`
- `--seed`
- `--mode`
- `--summary-only`
- `--readout`
- `--morphism`

Associated tests:

Add tests:

- main function with tiny args exits successfully
- summary-only output is concise

Run:

```text
uv run pytest tests/benchmarks/test_tower_runtime_bench.py
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only
```

Completion criteria:

- CLI works through `python -m`
- output is human-readable and testable

Failure hypotheses:

- CLI imports optional Gymnasium dependency outside `rl` extra.
- `argparse` output is awkward to test.
- Benchmark defaults choose an env too slow for CI.

### Stage 9.4: Validate Phase 9

#### Action 9.4.1

High-level explanation:

Run benchmark tests and smoke command.

Ground-truth files to inspect:

```text
src/state_collapser/benchmarks/
tests/benchmarks/
```

Machine action:

Run:

```text
uv run pytest tests/benchmarks
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only
```

Associated tests:

Same as machine action.

Completion criteria:

- benchmark tests pass
- benchmark smoke command succeeds
- implementation log records output

Failure hypotheses:

- Environment import path is wrong.
- Benchmark is slower than expected even for tiny steps.
- CLI summary-only option still emits too much output for tests.

## Phase 10: Documentation And Public Surface Cleanup

### Stage 10.1: README Updates

#### Action 10.1.1

High-level explanation:

Update README TODOs to match implemented revisions.

Ground-truth files to inspect:

```text
README.md
docs/design/synthetic_blow_revisions_01/01_001_synthetic_blow_review_revision_blueprint.md
```

Machine action:

Update README TODOs to accurately mention:

- training transition semantics and masks
- live view vs value snapshot hardening
- lazy compatibility readout and benchmark work
- hook-based Gymnasium bridge
- observation-vs-state inference as future work

Associated tests:

No tests.

Completion criteria:

- README does not overclaim incomplete features
- README names future observation/state problem clearly

Failure hypotheses:

- README TODO section has changed during implementation.
- Some planned features were blocked and cannot be documented as complete.
- README wording conflicts with PyPI readiness docs.

#### Action 10.1.2

High-level explanation:

Update README package map if public module names changed.

Ground-truth files to inspect:

```text
README.md
src/state_collapser/training/__init__.py
src/state_collapser/tower/snapshot.py
src/state_collapser/adapters/gymnasium.py
src/state_collapser/benchmarks/
```

Machine action:

Update README package map for:

- `state_collapser.training.masks`
- `LiveRuntimeView` and `RuntimeSnapshot`
- `StateCollapserGymWrapper`
- `state_collapser.benchmarks`

Associated tests:

No tests.

Completion criteria:

- package map matches actual implemented modules

Failure hypotheses:

- Some modules remain private and should not be advertised.
- Compatibility alias names require careful wording.
- README already has too much detail and needs concise update.

### Stage 10.2: CONTRIBUTING Updates

#### Action 10.2.1

High-level explanation:

Document Gymnasium integration expectations for contributors.

Ground-truth files to inspect:

```text
CONTRIBUTING.md
src/state_collapser/adapters/gymnasium.py
```

Machine action:

Add or update a section explaining:

- Gymnasium is the environment shell
- `state_collapser` owns graph/tower structure
- hooks are required when observation is not state
- action masks should be exposed explicitly
- edge labels/contraction features should be explicit
- automatic observation-to-state inference is future work

Associated tests:

No tests.

Completion criteria:

- contribution guidance matches actual wrapper behavior

Failure hypotheses:

- Existing contributor docs already include similar guidance.
- Wording overstates current wrapper maturity.
- Contributor docs need references to design documents.

#### Action 10.2.2

High-level explanation:

Document benchmark and hot-path discipline for contributors.

Ground-truth files to inspect:

```text
CONTRIBUTING.md
src/state_collapser/benchmarks/
```

Machine action:

Add guidance explaining:

- correctness tests are not enough for runtime claims
- compatibility readouts must not hide in hot paths
- benchmark tests should avoid strict timing thresholds
- benchmark smoke command to run after runtime changes

Associated tests:

No tests.

Completion criteria:

- contributor docs tell future implementers how not to regress the review fixes

Failure hypotheses:

- Benchmark module is not complete enough to document as stable.
- Docs become too prescriptive for research mode.
- Commands differ from actual implemented CLI.

### Stage 10.3: Design Log Closure

#### Action 10.3.1

High-level explanation:

Update implementation log with final documentation changes and any deferred
items.

Ground-truth files to inspect:

```text
docs/design/synthetic_blow_revisions_01/01_003_synthetic_blow_review_revision_implementation_log.md
```

Machine action:

Record:

- completed phases
- deferred compiled-core/language issue
- deferred automatic observation-to-state inference
- any authorized deviations
- final validation commands

Associated tests:

No tests.

Completion criteria:

- implementation log is complete enough for continuity

Failure hypotheses:

- A phase was partially completed and needs explicit status.
- An authorized deviation needs PO wording.
- Final validation has not yet run.

## Phase 11: Full Validation And Final Consistency Pass

### Stage 11.1: Focused Validation Sweep

#### Action 11.1.1

High-level explanation:

Run all focused validation groups after implementation.

Ground-truth files to inspect:

```text
tests/training/
tests/tower/
tests/quotient/
tests/adapters/
tests/benchmarks/
tests/examples/
```

Machine action:

Run:

```text
uv run pytest tests/training
uv run pytest tests/tower tests/quotient
uv run pytest tests/adapters
uv run pytest tests/benchmarks
uv run pytest tests/examples
```

Associated tests:

Same as machine action.

Completion criteria:

- all focused suites pass
- failures are resolved or trigger stop condition

Failure hypotheses:

- Example tests expose mismatched snapshot/view assumptions.
- Adapter tests require optional dependency handling.
- Benchmark tests are too slow or brittle.

### Stage 11.2: Full Validation Sweep

#### Action 11.2.1

High-level explanation:

Run the full package validation set.

Ground-truth files to inspect:

```text
pyproject.toml
src/
tests/
```

Machine action:

Run:

```text
uv run ruff check .
uv run mypy src
uv run pytest
```

Associated tests:

Same as machine action.

Completion criteria:

- ruff passes
- mypy passes
- full pytest passes
- implementation log records exact output summary

Failure hypotheses:

- Mypy catches type fallout from snapshot rename.
- Ruff catches unused compatibility imports.
- Full pytest exposes a slow interaction not seen in focused suites.

### Stage 11.3: Benchmark Smoke Validation

#### Action 11.3.1

High-level explanation:

Run the benchmark smoke command and record output.

Ground-truth files to inspect:

```text
src/state_collapser/benchmarks/tower_runtime_bench.py
```

Machine action:

Run:

```text
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only
```

Associated tests:

No pytest. This is a CLI smoke validation.

Completion criteria:

- command exits successfully
- output includes benchmark mode, steps, elapsed time, and readout flag
- implementation log records output

Failure hypotheses:

- CLI module path is wrong.
- Benchmark depends on environment state not initialized in CLI.
- Summary-only output is missing required fields.

### Stage 11.4: Public Surface Consistency Check

#### Action 11.4.1

High-level explanation:

Search for stale names and review-derived contradictions before final report.

Ground-truth files to inspect:

```text
src/
tests/
README.md
CONTRIBUTING.md
docs/design/synthetic_blow_revisions_01/
```

Machine action:

Search for stale or suspicious terms:

```text
GymnasiumAdapter
Serializable runtime handoff
terminated or truncated
to_quotient_tier_views()
LoopPolicy.drop_internal()
```

Interpretation:

- `GymnasiumAdapter` may appear only as documented legacy compatibility if
  authorized
- `Serializable runtime handoff` should not describe live objects
- `terminated or truncated` should not drive learner bootstrap
- `to_quotient_tier_views()` should not appear in default hot path
- `LoopPolicy.drop_internal()` should not be hard-coded in carry-forward

Associated tests:

No tests.

Completion criteria:

- stale names are eliminated or documented as intentional
- implementation log records final consistency check

Failure hypotheses:

- Compatibility aliases retain old names in ways that need docs.
- Some test names still include old adapter name.
- Legitimate `to_quotient_tier_views()` calls exist in explicit readout tests.

## Phase 12: Completion Report And Merge Readiness

### Stage 12.1: Implementation Log Finalization

#### Action 12.1.1

High-level explanation:

Finalize the implementation log with completion status for every phase.

Ground-truth files to inspect:

```text
docs/design/synthetic_blow_revisions_01/01_003_synthetic_blow_review_revision_implementation_log.md
```

Machine action:

Ensure the implementation log includes:

- branch name
- starting commit
- final commit candidate status
- all completed Phase.Stage.Action items
- all tests run
- all benchmark smoke outputs
- all owner-approved deviations
- all deferred items
- final validation state

Associated tests:

No tests.

Completion criteria:

- log is complete and accurate

Failure hypotheses:

- Some tests were run but not recorded.
- A deviation occurred and needs PO confirmation before merge.
- Final status has untracked files not mentioned in log.

### Stage 12.2: Final Git Status Review

#### Action 12.2.1

High-level explanation:

Review final working tree state before asking the Project Owner about commit or
merge.

Ground-truth files to inspect:

```text
git status --short --branch
git diff --stat
```

Machine action:

Run status and diff-stat commands. Do not commit unless the Project Owner
explicitly asks.

Associated tests:

No tests.

Completion criteria:

- final changed-file set is known
- no unrelated files are mixed in

Failure hypotheses:

- Existing untracked review/design docs need owner decision before commit.
- Generated cache files appear and should not be committed.
- A file outside the implementation scope changed unexpectedly.

### Stage 12.3: Final Report To Project Owner

#### Action 12.3.1

High-level explanation:

Report completion concisely and accurately.

Ground-truth files to inspect:

```text
docs/design/synthetic_blow_revisions_01/01_003_synthetic_blow_review_revision_implementation_log.md
git status --short --branch
```

Machine action:

Return a final implementation summary with:

- completed high-level outcomes
- validation commands and outcomes
- benchmark smoke outcome
- remaining known risks
- files/documents created
- branch status

Associated tests:

No tests.

Completion criteria:

- Project Owner has enough information to decide commit/merge/release next
  steps

Failure hypotheses:

- There are unresolved stop-condition items.
- Validation did not pass and must be reported as blocked.
- The implementation log and final report disagree.

## Cross-Phase Traceability Matrix

| Blueprint requirement | Gameplan coverage |
|---|---|
| strict env action boundaries | Phase 1 |
| first-class action masks | Phase 2 |
| continuation/bootstrap semantics | Phase 3 |
| example training loop consolidation | Phase 4 |
| live view vs serializable snapshot split | Phase 5 |
| lazy quotient readouts | Phase 6 |
| optional morphism capture | Phase 6 |
| loop policy carry-forward | Phase 7 |
| internal/pre-image aggregation | Phase 7 |
| real hook-based Gymnasium bridge | Phase 8 |
| README and CONTRIBUTING updates | Phase 8 and Phase 10 |
| benchmark surface | Phase 9 |
| full validation | Phase 11 |
| implementation log | Phase 0 through Phase 12 |

## Final Gameplan Verdict

This gameplan is ready for Project Owner review.

It is intentionally strict. The review identified correctness and runtime
honesty problems, not cosmetic cleanup. The implementation therefore has to
proceed in small verifiable units, with tests attached to each semantic change.

If approved for execution, the next operational step is:

```text
create/switch to codex/synthetic-blow-revisions-01 and create the implementation log
```

No implementation should begin until that approval is explicit.
