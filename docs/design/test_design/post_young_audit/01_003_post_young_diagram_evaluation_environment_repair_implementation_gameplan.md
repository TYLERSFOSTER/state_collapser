# Post-Young-Diagram Evaluation Environment Repair Implementation Gameplan

## Status

Date: 2026-05-24

This document is the Phase.Stage.Action implementation gameplan for:

- `docs/design/test_design/post_young_audit/01_002_post_young_diagram_evaluation_environment_repair_blueprint.md`

It is downstream of:

- `docs/design/test_design/post_young_audit/01_001_post_young_diagram_evaluation_environment_audit.md`
- `docs/design/Young_tableaux_refactor/01_001_young_tableaux_runtime_refactor_blueprint.md`
- `docs/design/Young_tableaux_refactor/01_002_young_tableaux_runtime_refactor_implementation_gameplan.md`

It is governed by:

- `docs/prime_directive/prime_directive.md`
- `docs/prime_directive/git_practices.md`
- `docs/prime_directive/common_failure_mode_001.md`
- `docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md`
- `docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md`
- `docs/prime_directive/consultant_tricks.md`

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

The goal is to repair the post-Young-diagram evaluation environment surface so
that the example environments again exercise meaningful partition-tower behavior.

The concrete migration is:

```text
old assumption:
    contraction_policy controls example tower coarsening

new runtime reality:
    contraction_schema controls partition-tower coarsening

required repair:
    environment edge labels + environment default schemas + schema-aware probes
    + tests that fail if quotient behavior silently goes flat
```

The repair must not undo the Young diagram refactor.

The repair must not reintroduce the old explicit counterpoint rank tower.

The repair must make schema-driven hierarchy observable, configurable, and tested
across the evaluation environments.

## Fixed Defaults For This Gameplan

Unless the Project Owner changes these before execution, implementation must use
the following defaults.

1. The dedicated implementation branch is:

   ```text
   codex/post-young-eval-env-schema-repair
   ```

2. The running implementation log is:

   ```text
   docs/design/test_design/post_young_audit/01_004_post_young_diagram_evaluation_environment_repair_implementation_log.md
   ```

3. Every migrated evaluation runtime accepts:

   ```python
   contraction_schema: ContractionSchema | None = None
   ```

4. `contraction_schema=None` means "use the environment default schema" for
   every schema-enabled evaluation environment.

5. `NoContractionSchema()` is the explicit flat-baseline mode.

6. Default schemas are smoke/default compatibility schemas:

   ```python
   DimensionwiseSchema(("<env-transition-label>",))
   ```

7. Semantic schema helpers are implemented where the blueprint names semantic
   labels. They are not the default unless the Project Owner later changes that
   decision.

8. Edge labels live on `BaseEdge.labels`, not by mutating hidden env state.

9. The old `contraction_policy` constructor parameter remains accepted for
   compatibility, but docs, probe names, and tests must not describe it as the
   partition-tower contraction schedule.

10. Tests must assert nontrivial behavior through schema facts:

    ```python
    len(snapshot.current_position_at_every_tier) >= 2
    ```

    and:

    ```python
    any(assignment.block_id is not None for assignment in schema_assignments)
    ```

11. Tests must avoid exact tower-depth expectations except in tiny controlled
    synthetic tests.

12. The counterpoint post-refactor reality check requires nontrivial depth, not
    the historical legacy value `max_depth = 15`.

## Global Stop Conditions

Implementation must stop and ask the Project Owner if any of the following
occur.

- A named file or symbol in this gameplan no longer exists.
- A Phase.Stage.Action item cannot be implemented as written.
- An action requires a schema choice not fixed by the blueprint or this
  gameplan.
- An action would need a lighter substitute implementation.
- A test encodes current depth-1 behavior as an intended invariant.
- A migrated environment cannot reach nontrivial depth under the default schema
  without adding labels outside the blueprint.
- A runtime constructor change would break existing public example imports.
- A probe change requires changing exit-code semantics beyond the no-env parser
  bug.
- A command fails unexpectedly.
- The implementation would require reverting or rewriting unrelated user changes.

If a stop condition is triggered, do not continue patching. Record the exact
Phase.Stage.Action in the implementation log and return control to the Project
Owner.

## Required Branch Discipline

Execution must not start on `main`.

Before implementation begins, create or switch to:

```text
codex/post-young-eval-env-schema-repair
```

If the Project Owner requests a different branch name, use that name.

If the current branch already contains unmerged Young diagram refactor work, bind
the base branch explicitly in the implementation log before touching source
files.

## Required Running Implementation Log

The implementation log must be created before source-code edits begin:

```text
docs/design/test_design/post_young_audit/01_004_post_young_diagram_evaluation_environment_repair_implementation_log.md
```

The log must record:

- the branch name;
- the starting git status;
- each completed Phase.Stage.Action item;
- exact files edited;
- exact tests run;
- test outcomes;
- probe outputs;
- surprises and failures;
- Project Owner clarifications;
- any authorized deviation.

The log must not hide weakened work behind language such as "first pass,"
"minimal slice," or "good enough" unless the Project Owner explicitly authorizes
that framing.

## Validation Command Set

Focused validation commands:

```text
uv run pytest tests/examples/test_tower_depth_probe.py
```

```text
uv run pytest tests/examples/test_plate_support_env_runtime_integration.py
```

```text
uv run pytest tests/examples/test_parallelogram_singularity_env_runtime_integration.py
```

```text
uv run pytest tests/examples/test_articulated_loop_env_runtime_integration.py
```

```text
uv run pytest tests/examples/test_cable_parallel_env_runtime_integration.py
```

```text
uv run pytest tests/examples/test_dual_arm_manipulation_env_runtime_integration.py
```

```text
uv run pytest tests/examples/test_rl_counterpoint_v3_runtime_integration.py
```

Example-suite validation:

```text
uv run pytest tests/examples
```

Probe validation:

```text
uv run python -m state_collapser.examples.tower_depth_probe --steps 20 --seed 7 --summary-only
```

```text
uv run python -m state_collapser.examples.tower_depth_probe --steps 20 --seed 7 --schema-mode none --summary-only
```

Full validation:

```text
uv run pytest
```

If any validation command fails unexpectedly, stop and reconstruct reality before
editing further.

## Phase 0: Execution Setup And Reality Binding

### Stage 0.1: Confirm Authority

#### Action 0.1.1

High-level purpose:

Confirm that the Project Owner has explicitly approved execution of this
gameplan.

Ground truth:

- `docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md`
- this gameplan

Implementation:

- Do not edit source or tests.
- Confirm that the Project Owner has issued an execution request for this exact
  gameplan.

Tests:

- None.

Completion condition:

- Execution approval is present in the conversation.

Failure hypotheses:

- The Project Owner may want edits to the gameplan before execution.
- The Project Owner may approve only a subset, which is not enough to execute the
  whole gameplan as law.
- The Project Owner may want a different branch name.

#### Action 0.1.2

High-level purpose:

Create or switch to the dedicated implementation branch before code changes.

Ground truth:

- `docs/prime_directive/git_practices.md`
- `git status --short`
- `git branch --show-current`

Implementation:

- Run a status check.
- Create or switch to `codex/post-young-eval-env-schema-repair`.
- If unexpected dirty files exist outside the design docs for this work, stop and
  ask the Project Owner whether to proceed.

Tests:

- None.

Completion condition:

- Current branch is `codex/post-young-eval-env-schema-repair` or another
  Project-Owner-approved branch.

Failure hypotheses:

- The repo may already be on a work branch that should be used as the base.
- The branch may already exist with older work.
- The working tree may include unrelated user edits.

### Stage 0.2: Establish Implementation Log

#### Action 0.2.1

High-level purpose:

Create the running implementation log before touching source files.

Ground truth:

- `docs/design/test_design/post_young_audit/`
- `docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md`

Implementation:

- Create:

  ```text
  docs/design/test_design/post_young_audit/01_004_post_young_diagram_evaluation_environment_repair_implementation_log.md
  ```

- Include the gameplan path, branch, starting status, and validation command set.

Tests:

- None.

Completion condition:

- The implementation log exists and records the starting context.

Failure hypotheses:

- The folder may contain a newer numbering convention.
- The Project Owner may prefer a different log filename.
- The current branch may not yet be settled.

### Stage 0.3: Reconstruct Current Runtime Reality

#### Action 0.3.1

High-level purpose:

Re-bind repository reality before implementation starts.

Ground truth:

- `git status --short`
- `src/state_collapser/tower/runtime.py`
- `src/state_collapser/tower/partition/schema.py`
- `src/state_collapser/core/edges.py`
- `src/state_collapser/core/action.py`

Implementation:

- Inspect the named files and confirm that:

  ```text
  TowerRuntime accepts contraction_schema
  BaseEdge accepts labels
  PrimitiveAction accepts labels
  DimensionwiseSchema exists
  NoContractionSchema exists
  ```

- Record findings in the implementation log.

Tests:

- None.

Completion condition:

- The implementation log contains a short reality-binding note.

Failure hypotheses:

- The code may have changed since the audit.
- Schema classes may have moved.
- Runtime constructor behavior may have changed.

#### Action 0.3.2

High-level purpose:

Capture the pre-repair baseline.

Ground truth:

- `tests/examples`
- `src/state_collapser/examples/tower_depth_probe.py`

Implementation:

- Run:

  ```text
  uv run pytest tests/examples
  ```

- Run:

  ```text
  uv run python -m state_collapser.examples.tower_depth_probe plate_support_env articulated_loop_env dual_arm_manipulation_env cable_parallel_env parallelogram_singularity_env rl_counterpoint_v3 --steps 20 --seed 7 --summary-only
  ```

- Record outputs in the implementation log.

Tests:

- The commands above are the tests for this action.

Completion condition:

- The implementation log records baseline example-test health and baseline depth
  results.

Failure hypotheses:

- Existing tests may already fail for reasons unrelated to this repair.
- Probe behavior may have changed since the audit.
- The no-env probe bug may still prevent all-env shorthand but explicit envs
  should work.

## Phase 1: Shared Diagnostics And Probe Surface

### Stage 1.1: Add Test Helpers For Schema-Depth Assertions

#### Action 1.1.1

High-level purpose:

Create a small shared test helper surface so every environment test checks schema
behavior consistently.

Ground truth:

- `tests/examples/`
- `tests/examples/test_robot_constraint_toy.py`
- `src/state_collapser/tower/partition/update.py`

Implementation:

- Add a helper module under `tests/examples/`, for example:

  ```text
  tests/examples/schema_assertions.py
  ```

- Provide helper functions for:

  ```python
  scheduled_assignment_count(runtime: object) -> int
  latest_schema_assignment_count(runtime: object) -> int
  snapshot_has_nontrivial_tower(snapshot: RuntimeSnapshot) -> bool
  assert_runtime_scheduled_schema_assignments(runtime: object) -> None
  assert_snapshot_has_nontrivial_tower(snapshot: RuntimeSnapshot) -> None
  ```

- Helpers must inspect `runtime.tower_runtime.last_tower_update_result` and treat
  missing update results as zero scheduled assignments.

Tests:

- Add or update a tiny helper test only if needed.
- Otherwise consume the helper in later environment tests.

Completion condition:

- Helper module exists and imports without requiring environment-specific code.

Failure hypotheses:

- Test helpers may require typing looseness because runtime classes are not
  protocol-unified.
- Some update results may be reset-time only, step-time only, or no-op.
- Counting only the latest update may miss earlier scheduled edges, requiring an
  accumulated probe count later.

#### Action 1.1.2

High-level purpose:

Define a deterministic short-action-sequence convention for runtime integration
tests.

Ground truth:

- existing `tests/examples/test_*_runtime_integration.py`
- each environment `ACTION_COUNT`

Implementation:

- In each test file as it is migrated, use explicit action sequences local to
  the environment.
- Do not create a single shared global action sequence because action semantics
  differ by environment.

Tests:

- No standalone tests.

Completion condition:

- The implementation log records that deterministic environment-local sequences
  are the test convention.

Failure hypotheses:

- Some action sequences may produce only self-transitions.
- Some action sequences may terminate early.
- Some default schemas may schedule at reset from vista edges rather than only
  after step.

### Stage 1.2: Repair `tower_depth_probe` CLI Defaults

#### Action 1.2.1

High-level purpose:

Fix the no-env default bug without changing probe semantics yet.

Ground truth:

- `src/state_collapser/examples/tower_depth_probe.py`
- `tests/examples/test_tower_depth_probe.py`

Implementation:

- Remove `choices=tuple(SUPPORTED_ENVIRONMENTS)` from the variadic positional
  parser argument.
- Validate env names manually after parsing.
- Preserve the existing default-to-all behavior in `main(...)`.
- Unsupported env names should still fail clearly.

Tests:

- Add a test that `parse_args([])` is accepted.
- Add a test that `main([...])` or a lower-level validation path rejects an
  unsupported env name cleanly.

Completion condition:

- The no-env command can run without argparse rejecting `[]`.

Failure hypotheses:

- Existing tests may import `parse_args` only indirectly.
- Testing `main(...)` may require capturing stdout.
- Manual parser errors may raise `SystemExit`.

#### Action 1.2.2

High-level purpose:

Add schema-mode plumbing to the probe while preserving legacy policy controls.

Ground truth:

- `src/state_collapser/examples/tower_depth_probe.py`
- `src/state_collapser/tower/partition/schema.py`
- environment runtime constructors

Implementation:

- Extend `ProbeEnvironment.runtime_factory` so it accepts:

  ```python
  ContractionPolicy | None
  ContractionSchema | None
  ```

- Add schema mode support:

  ```text
  --schema-mode default
  --schema-mode none
  ```

- `default` must pass `contraction_schema=None`.
- `none` must pass `NoContractionSchema()`.
- Keep `--no-contraction-policy`, but update help text so it says this controls
  only the seeded random legacy/annotation policy, not schema scheduling.

Tests:

- Update `tests/examples/test_tower_depth_probe.py`.
- Add a test that `continuous_probe(..., schema_mode="none")` can run.
- Add a test that `continuous_probe(..., schema_mode="default")` can run.

Completion condition:

- Probe still runs for `plate_support_env` in default and none modes.

Failure hypotheses:

- `continuous_probe(...)` may need a new parameter, requiring tests and callers
  to update.
- Runtime factories for non-migrated envs do not yet accept schemas; this may
  require temporary adaptation or staged changes.
- If temporary adaptation is impossible without a weaker design, stop and ask.

#### Action 1.2.3

High-level purpose:

Extend probe results with schema diagnostics.

Ground truth:

- `DepthProbeResult` in `src/state_collapser/examples/tower_depth_probe.py`
- `TowerRuntime.last_tower_update_result`

Implementation:

- Extend `DepthProbeResult` with:

  ```python
  schema_mode: str
  scheduled_assignment_count: int
  unscheduled_assignment_count: int
  ```

- During `continuous_probe(...)`, accumulate assignment counts across reset and
  step updates.
- In summary output, include at least `max_depth` and scheduled assignment count.

Tests:

- Assert `DepthProbeResult.scheduled_assignment_count >= 0`.
- Assert `DepthProbeResult.schema_mode` matches the requested mode.
- For `plate_support_env` default mode, assert scheduled assignments are
  positive after a short probe.

Completion condition:

- Probe output is schema-aware but still backwards-readable.

Failure hypotheses:

- The same update result may be counted more than once if not carefully sampled
  after each runtime operation.
- Reset-time schema assignments may matter for environments with visible vista
  edges at reset.
- No-op updates may have zero assignments even after earlier scheduled updates.

## Phase 2: Plate Support Reference Hardening

### Stage 2.1: Normalize Plate Support Schema Helper

#### Action 2.1.1

High-level purpose:

Make `plate_support_env` the explicit reference pattern for schema-enabled
evaluation runtimes.

Ground truth:

- `src/state_collapser/examples/plate_support_env/runtime.py`
- `src/state_collapser/examples/plate_support_env/__init__.py`

Implementation:

- Add:

  ```python
  def default_plate_support_schema() -> ContractionSchema:
      return DimensionwiseSchema(("plate-support-transition",))
  ```

- Replace inline `DimensionwiseSchema(("plate-support-transition",))` construction
  in `PlateSupportEnvRuntime` with the helper.
- Export the helper from the runtime module and package `__init__.py`.

Tests:

- Update plate-support runtime tests to import and call
  `default_plate_support_schema()`.

Completion condition:

- Plate support still reaches nontrivial depth by default.

Failure hypotheses:

- Export changes may reveal existing `__all__` ordering assumptions.
- Type imports may need `ContractionSchema`.
- Exploit/explore runtime construction may indirectly rely on the old inline
  behavior.

### Stage 2.2: Add Plate Support Flat Baseline Tests

#### Action 2.2.1

High-level purpose:

Make the already-migrated environment prove both schema and flat modes.

Ground truth:

- `tests/examples/test_plate_support_env_runtime_integration.py`
- `src/state_collapser/tower/partition/schema.py`

Implementation:

- Add a test that default `PlateSupportEnvRuntime(env=PlateSupportEnv())` reaches
  at least two tier positions after reset or a short deterministic step.
- Add a test that `PlateSupportEnvRuntime(..., contraction_schema=NoContractionSchema())`
  stays flat under the same deterministic check.
- Add a test that the default runtime has positive scheduled schema assignment
  count.

Tests:

- Run:

  ```text
  uv run pytest tests/examples/test_plate_support_env_runtime_integration.py
  ```

Completion condition:

- Plate support becomes the template proof for default schema and flat baseline.

Failure hypotheses:

- The default schema may schedule at reset, not after step.
- The flat baseline may still show seed quotient tiers if a test constructs them.
- Existing tests may assume `runtime.quotient_tiers == ()` before reset only.

## Phase 3: Parallelogram Singularity Migration

### Stage 3.1: Add Parallelogram Edge Labels And Schema Helpers

#### Action 3.1.1

High-level purpose:

Add auditable edge labels for the parallelogram environment.

Ground truth:

- `src/state_collapser/examples/parallelogram_singularity_env/env.py`
- `src/state_collapser/examples/parallelogram_singularity_env/runtime.py`

Implementation:

- Import or use:

  ```python
  is_singular_state
  ```

- Add a helper:

  ```python
  def parallelogram_edge_labels(
      source: ParallelogramState,
      action_index: int,
      target: ParallelogramState,
  ) -> tuple[Hashable, ...]:
      ...
  ```

- Labels must include `"parallelogram-transition"` on every valid edge.
- Labels must include action-family labels:

  ```text
  "parallelogram-left-angle"
  "parallelogram-right-angle"
  "parallelogram-span"
  "parallelogram-alignment-mode"
  ```

- Labels must include singularity-status labels where applicable:

  ```text
  "parallelogram-singular-source"
  "parallelogram-singular-target"
  "parallelogram-enters-singular-regime"
  "parallelogram-leaves-singular-regime"
  ```

- Use labels in `ParallelogramHiddenGraph.out_edges(...)`.

Tests:

- Add or update tests to inspect at least one edge label from the hidden graph.

Completion condition:

- Parallelogram hidden graph emits nonempty labels on valid edges.

Failure hypotheses:

- Some actions may produce self-transitions and still be valid.
- Some edge labels may require inspecting the target payload after transition.
- Singular-boundary labels may not appear from the start state and may require a
  targeted valid source state.

#### Action 3.1.2

High-level purpose:

Add parallelogram default and semantic schemas.

Ground truth:

- `src/state_collapser/examples/parallelogram_singularity_env/runtime.py`
- `src/state_collapser/examples/parallelogram_singularity_env/__init__.py`

Implementation:

- Add:

  ```python
  def default_parallelogram_schema() -> ContractionSchema:
      return DimensionwiseSchema(("parallelogram-transition",))
  ```

- Add:

  ```python
  def semantic_parallelogram_schema() -> ContractionSchema:
      return DimensionwiseSchema(
          (
              "parallelogram-enters-singular-regime",
              "parallelogram-leaves-singular-regime",
              "parallelogram-span",
              "parallelogram-alignment-mode",
              "parallelogram-left-angle",
              "parallelogram-right-angle",
          )
      )
  ```

- Export both helpers from runtime and package `__init__.py`.

Tests:

- Add import tests only if existing package import tests are present.
- Otherwise use helpers in runtime integration tests.

Completion condition:

- Schema helpers are importable from the package.

Failure hypotheses:

- `ContractionSchema` may need to be imported under type-checking constraints.
- The semantic schema may not schedule every edge, which is allowed.
- `__all__` omissions may hide helpers from package-level imports.

### Stage 3.2: Wire Parallelogram Runtime Schema

#### Action 3.2.1

High-level purpose:

Make parallelogram runtime schema-enabled by default.

Ground truth:

- `src/state_collapser/examples/parallelogram_singularity_env/runtime.py`

Implementation:

- Add `contraction_schema: ContractionSchema | None = None` to
  `ParallelogramSingularityEnvRuntime.__init__`.
- Pass `default_parallelogram_schema()` when `contraction_schema is None`.
- Preserve `contraction_policy`.

Tests:

- Update `tests/examples/test_parallelogram_singularity_env_runtime_integration.py`.
- Add default nontrivial-depth and scheduled-assignment assertions.
- Add explicit `NoContractionSchema()` flat-baseline assertion.

Completion condition:

- Parallelogram default runtime reaches nontrivial depth under deterministic test.

Failure hypotheses:

- The broad default schema may produce a point tier too quickly but should still
  be nontrivial.
- The test may need a deterministic action sequence with at least one discovered
  edge.
- The runtime may schedule labels at reset before any step.

#### Action 3.2.2

High-level purpose:

Validate parallelogram migration before moving to the next environment.

Ground truth:

- `tests/examples/test_parallelogram_singularity_env_runtime_integration.py`
- `tests/examples/test_tower_depth_probe.py`

Implementation:

- Run:

  ```text
  uv run pytest tests/examples/test_parallelogram_singularity_env_runtime_integration.py tests/examples/test_tower_depth_probe.py
  ```

- Run a focused probe:

  ```text
  uv run python -m state_collapser.examples.tower_depth_probe parallelogram_singularity_env --steps 20 --seed 7 --summary-only
  ```

- Record results in the implementation log.

Tests:

- Commands above.

Completion condition:

- Parallelogram migration is green and nontrivial by probe.

Failure hypotheses:

- Probe schema-mode output may need updates after runtime migration.
- Deterministic random probe may not discover a scheduled edge quickly enough.
- If probe remains flat while tests are nontrivial, the probe action stream may
  need explicit seed/step adjustment approved by the Project Owner.

## Phase 4: Articulated Loop Migration

### Stage 4.1: Add Articulated Loop Edge Labels And Schema Helpers

#### Action 4.1.1

High-level purpose:

Add auditable action-family labels to `articulated_loop_env`.

Ground truth:

- `src/state_collapser/examples/articulated_loop_env/env.py`
- `src/state_collapser/examples/articulated_loop_env/runtime.py`

Implementation:

- Add:

  ```python
  def articulated_loop_edge_labels(action_index: int) -> tuple[Hashable, ...]:
      ...
  ```

- Every valid edge must include:

  ```text
  "articulated-loop-transition"
  ```

- Action-family labels:

  ```text
  actions 0,1 -> "articulated-loop-link-1"
  actions 2,3 -> "articulated-loop-link-2"
  actions 4,5 -> "articulated-loop-link-3"
  action 6 -> "articulated-loop-brace-mode"
  actions 7,8 -> "articulated-loop-coupler-slack"
  ```

- Use labels in `ArticulatedLoopHiddenGraph.out_edges(...)`.

Tests:

- Add hidden-graph label assertions in
  `tests/examples/test_articulated_loop_env_runtime_integration.py`.

Completion condition:

- Outgoing hidden graph edges expose the expected labels.

Failure hypotheses:

- Some action families may not be valid from the start state.
- Tests may need to inspect all valid states to find a representative edge for a
  label.
- Self-transitions may still carry labels and be registered as edges.

#### Action 4.1.2

High-level purpose:

Add articulated-loop schema helpers.

Ground truth:

- `src/state_collapser/examples/articulated_loop_env/runtime.py`
- `src/state_collapser/examples/articulated_loop_env/__init__.py`

Implementation:

- Add:

  ```python
  def default_articulated_loop_schema() -> ContractionSchema:
      return DimensionwiseSchema(("articulated-loop-transition",))
  ```

- Add:

  ```python
  def semantic_articulated_loop_schema() -> ContractionSchema:
      return DimensionwiseSchema(
          (
              "articulated-loop-coupler-slack",
              "articulated-loop-brace-mode",
              "articulated-loop-link-1",
              "articulated-loop-link-2",
              "articulated-loop-link-3",
          )
      )
  ```

- Export helpers from runtime and package `__init__.py`.

Tests:

- Helpers must be importable through package imports.

Completion condition:

- Helpers are available and used by later runtime tests.

Failure hypotheses:

- Package-level `TowerTrainingConfig` names may collide across examples only in
  wildcard contexts, which is existing behavior.
- Helper exports may require updating import order.
- Type imports may need to avoid circular references.

### Stage 4.2: Wire Articulated Loop Runtime Schema

#### Action 4.2.1

High-level purpose:

Make articulated-loop runtime schema-enabled by default.

Ground truth:

- `src/state_collapser/examples/articulated_loop_env/runtime.py`

Implementation:

- Add `contraction_schema: ContractionSchema | None = None` to
  `ArticulatedLoopEnvRuntime.__init__`.
- Pass `default_articulated_loop_schema()` when no schema is supplied.
- Preserve `contraction_policy`.

Tests:

- Update `tests/examples/test_articulated_loop_env_runtime_integration.py`.
- Add default nontrivial-depth test.
- Add scheduled-assignment test.
- Add explicit flat-baseline test using `NoContractionSchema()`.

Completion condition:

- Articulated loop no longer probes as tower-flat by default.

Failure hypotheses:

- Broad transition labels may over-collapse too much but should still create a
  nontrivial tier.
- Start-state vista may not expose all action labels.
- Existing runtime tests may need to stop asserting only truthiness of tier
  positions.

#### Action 4.2.2

High-level purpose:

Validate articulated-loop migration before moving on.

Ground truth:

- `tests/examples/test_articulated_loop_env_runtime_integration.py`
- `src/state_collapser/examples/tower_depth_probe.py`

Implementation:

- Run:

  ```text
  uv run pytest tests/examples/test_articulated_loop_env_runtime_integration.py tests/examples/test_tower_depth_probe.py
  ```

- Run:

  ```text
  uv run python -m state_collapser.examples.tower_depth_probe articulated_loop_env --steps 20 --seed 7 --summary-only
  ```

- Record results in the implementation log.

Tests:

- Commands above.

Completion condition:

- Articulated-loop tests and focused probe pass.

Failure hypotheses:

- Probe random actions may need more steps to discover a scheduled edge.
- Some invalid/self transitions may produce less graph growth than expected.
- If nontrivial depth appears only with semantic schema, stop and ask before
  changing the default.

## Phase 5: Cable Parallel Migration

### Stage 5.1: Add Cable Parallel Edge Labels And Schema Helpers

#### Action 5.1.1

High-level purpose:

Add pose/tension edge labels to `cable_parallel_env`.

Ground truth:

- `src/state_collapser/examples/cable_parallel_env/env.py`
- `src/state_collapser/examples/cable_parallel_env/runtime.py`

Implementation:

- Add:

  ```python
  def cable_parallel_edge_labels(action_index: int) -> tuple[Hashable, ...]:
      ...
  ```

- Every valid edge must include:

  ```text
  "cable-parallel-transition"
  ```

- Action-family labels:

  ```text
  actions 0,1 -> "cable-parallel-x-motion", "cable-parallel-platform-motion"
  actions 2,3 -> "cable-parallel-y-motion", "cable-parallel-platform-motion"
  action 4 -> "cable-parallel-orientation-motion", "cable-parallel-platform-motion"
  actions 5,6 -> "cable-parallel-cable-1-tension", "cable-parallel-tension-motion"
  actions 7,8 -> "cable-parallel-cable-2-tension", "cable-parallel-tension-motion"
  actions 9,10 -> "cable-parallel-cable-3-tension", "cable-parallel-tension-motion"
  ```

- Use labels in `CableParallelHiddenGraph.out_edges(...)`.

Tests:

- Add hidden-graph label assertions in
  `tests/examples/test_cable_parallel_env_runtime_integration.py`.

Completion condition:

- Cable parallel hidden graph emits pose and tension labels.

Failure hypotheses:

- Some pose actions may be invalid from the start state.
- Some tension labels may require searching a valid state with that outgoing
  transition.
- The current `is_valid_state` implementation in runtime is broader than
  `all_valid_states`, so tests should rely on hidden-graph behavior.

#### Action 5.1.2

High-level purpose:

Add cable-parallel schema helpers.

Ground truth:

- `src/state_collapser/examples/cable_parallel_env/runtime.py`
- `src/state_collapser/examples/cable_parallel_env/__init__.py`

Implementation:

- Add:

  ```python
  def default_cable_parallel_schema() -> ContractionSchema:
      return DimensionwiseSchema(("cable-parallel-transition",))
  ```

- Add:

  ```python
  def semantic_cable_parallel_schema() -> ContractionSchema:
      return DimensionwiseSchema(
          (
              "cable-parallel-tension-motion",
              "cable-parallel-platform-motion",
              "cable-parallel-orientation-motion",
              "cable-parallel-cable-1-tension",
              "cable-parallel-cable-2-tension",
              "cable-parallel-cable-3-tension",
          )
      )
  ```

- Export helpers from runtime and package `__init__.py`.

Tests:

- Use helpers in runtime tests.

Completion condition:

- Default and semantic schemas are importable.

Failure hypotheses:

- Semantic schema duplicate coverage may be order-sensitive.
- `DimensionwiseSchema` assigns an edge to the first matching label only.
- The order must intentionally place coarse tension/platform labels before
  cable-specific labels.

### Stage 5.2: Wire Cable Runtime Schema

#### Action 5.2.1

High-level purpose:

Make cable-parallel runtime schema-enabled by default.

Ground truth:

- `src/state_collapser/examples/cable_parallel_env/runtime.py`

Implementation:

- Add `contraction_schema: ContractionSchema | None = None` to
  `CableParallelEnvRuntime.__init__`.
- Pass `default_cable_parallel_schema()` when no schema is supplied.
- Preserve `contraction_policy`.

Tests:

- Update `tests/examples/test_cable_parallel_env_runtime_integration.py`.
- Add default nontrivial-depth test.
- Add scheduled-assignment test.
- Add explicit flat-baseline test.

Completion condition:

- Cable parallel no longer probes as tower-flat by default.

Failure hypotheses:

- Broad schema may collapse a large visible local component quickly.
- The default random probe may not visit enough non-self edges.
- Runtime tests may need deterministic action selection based on valid outgoing
  transitions rather than hard-coded action indices.

#### Action 5.2.2

High-level purpose:

Validate cable migration before moving on.

Ground truth:

- `tests/examples/test_cable_parallel_env_runtime_integration.py`
- `src/state_collapser/examples/tower_depth_probe.py`

Implementation:

- Run:

  ```text
  uv run pytest tests/examples/test_cable_parallel_env_runtime_integration.py tests/examples/test_tower_depth_probe.py
  ```

- Run:

  ```text
  uv run python -m state_collapser.examples.tower_depth_probe cable_parallel_env --steps 20 --seed 7 --summary-only
  ```

- Record results in the implementation log.

Tests:

- Commands above.

Completion condition:

- Cable tests and focused probe pass.

Failure hypotheses:

- If only tests pass but probe is flat, probe step count may be insufficient.
- If flat baseline is not flat, a default schema may be leaking into explicit
  `NoContractionSchema()` mode.
- If scheduled assignments are positive but depth remains one, inspect whether
  all scheduled edges were loops or internal edges.

## Phase 6: Dual Arm Migration

### Stage 6.1: Add Dual Arm Edge Labels And Schema Helpers

#### Action 6.1.1

High-level purpose:

Add object/arm/coordination labels to `dual_arm_manipulation_env`.

Ground truth:

- `src/state_collapser/examples/dual_arm_manipulation_env/env.py`
- `src/state_collapser/examples/dual_arm_manipulation_env/runtime.py`

Implementation:

- Add:

  ```python
  def dual_arm_edge_labels(action_index: int) -> tuple[Hashable, ...]:
      ...
  ```

- Every valid edge must include:

  ```text
  "dual-arm-transition"
  ```

- Action-family labels:

  ```text
  actions 0,1 -> "dual-arm-object-x-motion", "dual-arm-object-motion"
  actions 2,3 -> "dual-arm-object-y-motion", "dual-arm-object-motion"
  action 4 -> "dual-arm-object-orientation-motion", "dual-arm-object-motion"
  action 5 -> "dual-arm-left-mode-motion", "dual-arm-left-arm-motion", "dual-arm-coordination-motion"
  action 6 -> "dual-arm-right-mode-motion", "dual-arm-right-arm-motion", "dual-arm-coordination-motion"
  actions 7,8 -> "dual-arm-left-reach-motion", "dual-arm-left-arm-motion", "dual-arm-coordination-motion"
  actions 9,10 -> "dual-arm-right-reach-motion", "dual-arm-right-arm-motion", "dual-arm-coordination-motion"
  ```

- Use labels in `DualArmManipulationHiddenGraph.out_edges(...)`.

Tests:

- Add hidden-graph label assertions in
  `tests/examples/test_dual_arm_manipulation_env_runtime_integration.py`.

Completion condition:

- Dual-arm hidden graph emits object, left-arm, right-arm, and coordination
  labels.

Failure hypotheses:

- Some arm actions may be invalid from the start state.
- Coordination labels may appear only on arm-mode/reach changes.
- Tests may need to search over valid states for representative labels.

#### Action 6.1.2

High-level purpose:

Add dual-arm schema helpers.

Ground truth:

- `src/state_collapser/examples/dual_arm_manipulation_env/runtime.py`
- `src/state_collapser/examples/dual_arm_manipulation_env/__init__.py`

Implementation:

- Add:

  ```python
  def default_dual_arm_schema() -> ContractionSchema:
      return DimensionwiseSchema(("dual-arm-transition",))
  ```

- Add:

  ```python
  def semantic_dual_arm_schema() -> ContractionSchema:
      return DimensionwiseSchema(
          (
              "dual-arm-coordination-motion",
              "dual-arm-object-motion",
              "dual-arm-left-arm-motion",
              "dual-arm-right-arm-motion",
          )
      )
  ```

- Export helpers from runtime and package `__init__.py`.

Tests:

- Use helpers in runtime tests.

Completion condition:

- Default and semantic schemas are importable.

Failure hypotheses:

- The semantic order intentionally coarsens coordination before object motion.
- Some object edges also require arm support, but labels remain action-family
  facts.
- Helper names must not collide with env functions.

### Stage 6.2: Wire Dual Arm Runtime Schema

#### Action 6.2.1

High-level purpose:

Make dual-arm runtime schema-enabled by default.

Ground truth:

- `src/state_collapser/examples/dual_arm_manipulation_env/runtime.py`

Implementation:

- Add `contraction_schema: ContractionSchema | None = None` to
  `DualArmManipulationEnvRuntime.__init__`.
- Pass `default_dual_arm_schema()` when no schema is supplied.
- Preserve `contraction_policy`.

Tests:

- Update `tests/examples/test_dual_arm_manipulation_env_runtime_integration.py`.
- Add default nontrivial-depth test.
- Add scheduled-assignment test.
- Add explicit flat-baseline test.

Completion condition:

- Dual-arm no longer probes as tower-flat by default.

Failure hypotheses:

- Random probe may under-sample valid object/arm transitions.
- Runtime tests may need to drive deterministic valid actions.
- If scheduled assignments are all loops, depth may not increase.

#### Action 6.2.2

High-level purpose:

Validate dual-arm migration before moving on.

Ground truth:

- `tests/examples/test_dual_arm_manipulation_env_runtime_integration.py`
- `src/state_collapser/examples/tower_depth_probe.py`

Implementation:

- Run:

  ```text
  uv run pytest tests/examples/test_dual_arm_manipulation_env_runtime_integration.py tests/examples/test_tower_depth_probe.py
  ```

- Run:

  ```text
  uv run python -m state_collapser.examples.tower_depth_probe dual_arm_manipulation_env --steps 20 --seed 7 --summary-only
  ```

- Record results in the implementation log.

Tests:

- Commands above.

Completion condition:

- Dual-arm tests and focused probe pass.

Failure hypotheses:

- The default action stream may terminate or truncate quickly.
- Some valid transitions may produce no new state discovery.
- If probe is unstable, the test should assert deterministic helper behavior
  rather than exact random-trajectory depth.

## Phase 7: RL Counterpoint V3 Migration

### Stage 7.1: Add Counterpoint Edge Labels

#### Action 7.1.1

High-level purpose:

Add neutral motion-family labels to `rl_counterpoint_v3` without restoring the
old explicit rank tower.

Ground truth:

- `src/state_collapser/examples/rl_counterpoint_v3/env.py`
- `src/state_collapser/examples/rl_counterpoint_v3/runtime.py`

Implementation:

- Import:

  ```python
  action_index_to_step_delta
  ```

- Add:

  ```python
  def rl_counterpoint_edge_labels(
      source: RlCounterpointState,
      action_index: int,
      target: RlCounterpointState,
      spec: RlCounterpointGraphSpec,
  ) -> tuple[Hashable, ...]:
      ...
  ```

- Every valid edge must include:

  ```text
  "rl-counterpoint-v3-transition"
  "rl-counterpoint-v3-beat-advance"
  ```

- Voice labels:

  ```text
  bass_delta != 0 -> "rl-counterpoint-v3-bass-motion"
  inner_delta != 0 -> "rl-counterpoint-v3-inner-motion"
  upper_delta != 0 -> "rl-counterpoint-v3-upper-motion"
  any nonzero delta -> "rl-counterpoint-v3-any-voice-motion"
  ```

- Motion-size labels:

  ```text
  all nonzero absolute deltas <= 1 -> "rl-counterpoint-v3-stepwise-motion"
  any absolute delta > 1 -> "rl-counterpoint-v3-leap-motion"
  ```

- Direction-family labels:

  ```text
  exactly one moving voice -> "rl-counterpoint-v3-oblique-motion"
  all moving voices have the same sign -> "rl-counterpoint-v3-parallel-direction-motion"
  moving voices contain both positive and negative signs -> "rl-counterpoint-v3-contrary-direction-motion"
  ```

- Use labels in `RlCounterpointHiddenGraph.out_edges(...)`.

Tests:

- Add label tests in `tests/examples/test_rl_counterpoint_v3_runtime_integration.py`.
- Decode a known action delta and assert corresponding labels.

Completion condition:

- Counterpoint hidden graph labels are derived from action facts, not old rank
  tier names.

Failure hypotheses:

- Some action indices may be invalid from the start state.
- Test actions should use `step_delta_to_action_index(...)` or search valid
  outgoing transitions instead of assuming fixed indices.
- Oblique/parallel/contrary definitions need to ignore zero deltas carefully.

### Stage 7.2: Add Counterpoint Schemas

#### Action 7.2.1

High-level purpose:

Add default and semantic counterpoint schemas.

Ground truth:

- `src/state_collapser/examples/rl_counterpoint_v3/runtime.py`
- `src/state_collapser/examples/rl_counterpoint_v3/__init__.py`

Implementation:

- Add:

  ```python
  def default_rl_counterpoint_v3_schema() -> ContractionSchema:
      return DimensionwiseSchema(("rl-counterpoint-v3-transition",))
  ```

- Add:

  ```python
  def semantic_rl_counterpoint_v3_schema() -> ContractionSchema:
      return DimensionwiseSchema(
          (
              "rl-counterpoint-v3-bass-motion",
              "rl-counterpoint-v3-inner-motion",
              "rl-counterpoint-v3-upper-motion",
              "rl-counterpoint-v3-contrary-direction-motion",
              "rl-counterpoint-v3-oblique-motion",
              "rl-counterpoint-v3-parallel-direction-motion",
          )
      )
  ```

- Export helpers from runtime and package `__init__.py`.

Tests:

- Use helpers in runtime tests.

Completion condition:

- Counterpoint schema helpers are importable.

Failure hypotheses:

- The semantic schema assigns to first matching label, so voice labels precede
  direction labels by design.
- If direction labels should be primary, that is a design change requiring PO
  approval.
- The smoke schema may over-collapse but is the fixed default for this gameplan.

### Stage 7.3: Wire Counterpoint Runtime Schema

#### Action 7.3.1

High-level purpose:

Make counterpoint runtime schema-enabled by default.

Ground truth:

- `src/state_collapser/examples/rl_counterpoint_v3/runtime.py`

Implementation:

- Add `contraction_schema: ContractionSchema | None = None` to
  `RlCounterpointEnvRuntime.__init__`.
- Pass `default_rl_counterpoint_v3_schema()` when no schema is supplied.
- Preserve `contraction_policy`.

Tests:

- Update `tests/examples/test_rl_counterpoint_v3_runtime_integration.py`.
- Add default nontrivial-depth test.
- Add scheduled-assignment test.
- Add explicit flat-baseline test.

Completion condition:

- Counterpoint no longer probes as tower-flat by default.

Failure hypotheses:

- Counterpoint validity constraints may make deterministic action selection
  trickier than mechanical toy environments.
- The runtime may need a short sequence from a curated start state.
- If the smoke schema causes too much collapse, that is acceptable unless tests
  or runtime break.

#### Action 7.3.2

High-level purpose:

Restore the post-refactor counterpoint tower-depth reality check.

Ground truth:

- `tests/examples/test_rl_counterpoint_v3_runtime_integration.py`
- `src/state_collapser/examples/tower_depth_probe.py`
- `docs/design/test_design/rl_counterpoint_v3/01_004_rl_counterpoint_v3_implementation_log.md`

Implementation:

- Add a test or probe assertion that default `rl_counterpoint_v3` reaches:

  ```text
  max_depth >= 2
  scheduled_assignment_count > 0
  ```

- Do not assert `max_depth == 15`.
- Add a comment explaining that `15` was historical legacy dynamic-builder
  behavior and the partition schema has different semantics.

Tests:

- Run:

  ```text
  uv run pytest tests/examples/test_rl_counterpoint_v3_runtime_integration.py tests/examples/test_tower_depth_probe.py
  ```

- Run:

  ```text
  uv run python -m state_collapser.examples.tower_depth_probe rl_counterpoint_v3 --steps 40 --seed 0 --summary-only
  ```

Completion condition:

- Counterpoint has a nontrivial post-refactor depth check.

Failure hypotheses:

- Random probing may need enough steps to expose valid counterpoint edges.
- If deterministic probe depth is flaky, use a deterministic action sequence in
  tests and keep CLI probe as diagnostic output.
- If no schema can produce nontrivial depth without old rank semantics, stop and
  ask.

## Phase 8: Training Pass-Through Migration

### Stage 8.1: Add Schema Pass-Through To Mechanical Environment Training

#### Action 8.1.1

High-level purpose:

Make mechanical example training loops use the same schema surface as runtimes.

Ground truth:

- `src/state_collapser/examples/articulated_loop_env/training.py`
- `src/state_collapser/examples/cable_parallel_env/training.py`
- `src/state_collapser/examples/dual_arm_manipulation_env/training.py`
- `src/state_collapser/examples/parallelogram_singularity_env/training.py`

Implementation:

- Import `ContractionSchema`.
- Add `contraction_schema: ContractionSchema | None = None` to each
  `run_tower_training(...)`.
- Pass `contraction_schema` through to each runtime.

Tests:

- Existing training tests must still pass.
- Add schema-specific training assertions where runtime integration tests do not
  already cover pass-through.

Completion condition:

- Mechanical training entrypoints accept and forward schema overrides.

Failure hypotheses:

- Some training modules have minimal docstrings and may need imports only.
- Type check or lint may flag unused imports if annotations are postponed.
- Existing tests may not call schema pass-through, requiring new tests.

#### Action 8.1.2

High-level purpose:

Add training flat-baseline pass-through tests.

Ground truth:

- `tests/examples/test_*_tower_training.py` if present
- runtime integration tests if no training-specific test exists

Implementation:

- For each migrated mechanical environment, add or update a training test that
  passes `contraction_schema=NoContractionSchema()`.
- Assert the training run completes and returns a nonempty Q-table.
- For at least one representative mechanical environment, assert default training
  produces at least one Q-table key with length greater than `1`.

Tests:

- Run:

  ```text
  uv run pytest tests/examples
  ```

Completion condition:

- Training schema pass-through is covered.

Failure hypotheses:

- Some environments may not have dedicated tower-training tests.
- It may be cleaner to add one shared schema pass-through test file.
- If adding broad training tests makes runtime slow, keep episode counts small.

### Stage 8.2: Add Schema Pass-Through To Counterpoint Training

#### Action 8.2.1

High-level purpose:

Make `rl_counterpoint_v3` training schema-aware.

Ground truth:

- `src/state_collapser/examples/rl_counterpoint_v3/training.py`
- `src/state_collapser/examples/rl_counterpoint_v3/runtime.py`

Implementation:

- Import `ContractionSchema`.
- Add `contraction_schema: ContractionSchema | None = None` to
  `run_tower_training(...)`.
- Pass it through to `RlCounterpointEnvRuntime`.

Tests:

- Add or update counterpoint training tests.
- Assert default training Q-table keys can include more than one tier position.
- Assert flat-baseline training completes with `NoContractionSchema()`.

Completion condition:

- Counterpoint training can sweep schema/default/flat modes.

Failure hypotheses:

- Existing counterpoint training uses generic `state_collapser.training`
  surfaces and may need different assertions than hand-written loops.
- Short training may not encounter a nontrivial tower key unless deterministic
  seed/episode count is adjusted.
- Do not increase test runtime substantially without PO approval.

### Stage 8.3: Verify Training Migration

#### Action 8.3.1

High-level purpose:

Validate training pass-through across examples.

Ground truth:

- `tests/examples`

Implementation:

- Run:

  ```text
  uv run pytest tests/examples
  ```

- Record results in the implementation log.

Tests:

- Command above.

Completion condition:

- Example suite passes after training pass-through.

Failure hypotheses:

- Runtime migrations may expose old flat assumptions in training tests.
- Q-table key length expectations may be too strict for short stochastic tests.
- If test runtime grows too much, optimize deterministic action selection rather
  than weakening assertions silently.

## Phase 9: Cross-Environment Probe Finalization

### Stage 9.1: Update Probe Registry For Schema-Enabled Runtimes

#### Action 9.1.1

High-level purpose:

Make the probe registry instantiate every environment with policy and schema
parameters.

Ground truth:

- `src/state_collapser/examples/tower_depth_probe.py`
- all migrated runtime constructors

Implementation:

- Ensure every `SUPPORTED_ENVIRONMENTS` entry passes:

  ```python
  contraction_policy=policy
  contraction_schema=schema
  ```

- Keep `schema=None` in default mode.
- Pass `NoContractionSchema()` in none mode.

Tests:

- Update `tests/examples/test_tower_depth_probe.py`.

Completion condition:

- Probe can run every supported environment in `default` and `none` modes.

Failure hypotheses:

- `plate_support_env` exploit/explore runtime is unrelated and should not be
  touched by the probe.
- Non-migrated toy environments may need explicit handling if they enter the
  probe registry later.
- Runtime factory typing may need a protocol import.

### Stage 9.2: Add Cross-Environment Depth Expectations

#### Action 9.2.1

High-level purpose:

Make the probe test fail if migrated evaluation environments silently go flat.

Ground truth:

- `tests/examples/test_tower_depth_probe.py`

Implementation:

- Add a test over schema-enabled env names:

  ```text
  plate_support_env
  parallelogram_singularity_env
  articulated_loop_env
  cable_parallel_env
  dual_arm_manipulation_env
  rl_counterpoint_v3
  ```

- In default mode, assert:

  ```python
  result.max_depth >= 2
  result.scheduled_assignment_count > 0
  ```

- In none mode, assert:

  ```python
  result.scheduled_assignment_count == 0
  ```

- Only assert flat `max_depth == 1` in none mode if current runtime reality
  verifies it is stable for all envs.

Tests:

- Run:

  ```text
  uv run pytest tests/examples/test_tower_depth_probe.py
  ```

Completion condition:

- Probe tests encode the schema-vs-flat distinction.

Failure hypotheses:

- Some envs may require more than `20` probe steps under random action selection.
- If exact flat depth is not stable in none mode, scheduled count is the safer
  invariant.
- If default depth is stochastic, tests should use deterministic seeds and enough
  steps, not exact depth.

### Stage 9.3: Validate CLI Probe Output

#### Action 9.3.1

High-level purpose:

Confirm the CLI probe is usable as a human diagnostic.

Ground truth:

- `src/state_collapser/examples/tower_depth_probe.py`

Implementation:

- Run:

  ```text
  uv run python -m state_collapser.examples.tower_depth_probe --steps 20 --seed 7 --summary-only
  ```

- Run:

  ```text
  uv run python -m state_collapser.examples.tower_depth_probe --steps 20 --seed 7 --schema-mode none --summary-only
  ```

- Record output in the implementation log.

Tests:

- Commands above.

Completion condition:

- Default mode visibly reports nontrivial depth and positive scheduled counts for
  schema-enabled envs.
- None mode visibly reports no scheduled assignments.

Failure hypotheses:

- Output formatting changes may require test fixture updates.
- Summary-only output may need to include scheduled counts.
- CLI output may become too noisy; keep it compact.

## Phase 10: Documentation Updates

### Stage 10.1: Update README Environment/Tower Language

#### Action 10.1.1

High-level purpose:

Clarify that schema controls partition-tower contraction in the current runtime.

Ground truth:

- `README.md`
- `docs/design/test_design/post_young_audit/01_002_post_young_diagram_evaluation_environment_repair_blueprint.md`

Implementation:

- Update README only where it currently describes example evaluation
  environments, tower depth, contraction policy, or probe usage.
- State that:

  ```text
  ContractionSchema is the partition-tower contraction schedule.
  ContractionPolicy remains a legacy/local-star/vista policy surface.
  Evaluation envs provide default schemas and flat baselines via NoContractionSchema.
  ```

Tests:

- No code tests.

Completion condition:

- README no longer implies `contraction_policy` controls partition coarsening.

Failure hypotheses:

- README may not currently discuss the probe in detail.
- Avoid over-documenting smoke schemas as final benchmark schemas.
- If README has release-facing language, keep the change concise.

### Stage 10.2: Update Post-Audit Design Docs

#### Action 10.2.1

High-level purpose:

Record the implementation outcome in the post-young audit folder.

Ground truth:

- `docs/design/test_design/post_young_audit/01_004_post_young_diagram_evaluation_environment_repair_implementation_log.md`

Implementation:

- Keep the implementation log current.
- At the end of execution, add a final summary with:

  ```text
  files changed
  tests run
  final depth probe table
  known residual risks
  ```

Tests:

- No code tests.

Completion condition:

- Future readers can reconstruct what changed and why.

Failure hypotheses:

- If execution stops early, the log should say blocked rather than pretending
  completion.
- Probe results may be too large; include the summary table.
- Residual risks should be named, not hidden.

### Stage 10.3: Update Probe Help Text

#### Action 10.3.1

High-level purpose:

Make CLI help text semantically current.

Ground truth:

- `src/state_collapser/examples/tower_depth_probe.py`

Implementation:

- Ensure help text for `--schema-mode`, `--no-contraction-policy`, and
  `--sample-size` accurately describes partition-backend behavior.
- Do not remove legacy flags unless the Project Owner explicitly approves
  deprecation/removal.

Tests:

- Add or update a parser test if practical.
- Run:

  ```text
  uv run pytest tests/examples/test_tower_depth_probe.py
  ```

Completion condition:

- Help text no longer misleads users about policy-driven coarsening.

Failure hypotheses:

- Existing CLI tests may not inspect help output.
- Keeping legacy flags may still be confusing; docs should compensate.
- Removing flags would be a breaking change and is out of scope.

## Phase 11: Full Validation And Release-Quality Handoff

### Stage 11.1: Run Full Example Validation

#### Action 11.1.1

High-level purpose:

Verify the whole examples suite after all migrations.

Ground truth:

- `tests/examples`

Implementation:

- Run:

  ```text
  uv run pytest tests/examples
  ```

- Record result in the implementation log.

Tests:

- Command above.

Completion condition:

- All example tests pass.

Failure hypotheses:

- Tests may be order-dependent if runtime/schema state is accidentally shared.
- Stochastic probe tests may need deterministic seeds.
- If failures appear unrelated, stop and reconstruct before touching code.

### Stage 11.2: Run Full Validation

#### Action 11.2.1

High-level purpose:

Verify the whole repository after the repair.

Ground truth:

- full repo test suite

Implementation:

- Run:

  ```text
  uv run pytest
  ```

- Record result in the implementation log.

Tests:

- Command above.

Completion condition:

- Full test suite passes, or any failure is understood and recorded with Project
  Owner guidance.

Failure hypotheses:

- Non-example tests may rely on old probe output formatting.
- Full suite may include slow or environment-sensitive tests.
- If failures are unrelated, do not repair them under this gameplan without
  Project Owner approval.

### Stage 11.3: Run Final Probe Table

#### Action 11.3.1

High-level purpose:

Produce the final semantic evidence that the post-Young evaluation surface is no
longer mostly flat.

Ground truth:

- `src/state_collapser/examples/tower_depth_probe.py`

Implementation:

- Run:

  ```text
  uv run python -m state_collapser.examples.tower_depth_probe --steps 20 --seed 7 --summary-only
  ```

- Run:

  ```text
  uv run python -m state_collapser.examples.tower_depth_probe --steps 20 --seed 7 --schema-mode none --summary-only
  ```

- Add both outputs to the implementation log.

Tests:

- Commands above.

Completion condition:

- Default schema mode shows nontrivial depth and scheduled assignments for the
  schema-enabled evaluation environments.
- None mode shows zero scheduled assignments.

Failure hypotheses:

- The CLI probe may be less stable than deterministic unit tests.
- If one environment remains flat in the probe but not in deterministic tests,
  document and ask whether to adjust probe trajectory or schema.
- If scheduled counts are positive but depth is flat, inspect loops/internal-edge
  policy before changing schemas.

### Stage 11.4: Final Diff Review

#### Action 11.4.1

High-level purpose:

Verify that the implementation followed this gameplan and did not drift.

Ground truth:

- `git diff`
- this gameplan
- implementation log

Implementation:

- Review the diff by file.
- Check every Phase.Stage.Action has a corresponding log entry.
- Confirm no unrelated source files were modified.
- Confirm no hidden design decisions were encoded without Project Owner approval.

Tests:

- No new tests.

Completion condition:

- The implementation can be honestly reported as executing this gameplan.

Failure hypotheses:

- A needed export may have been added but not logged.
- Some test helper may have changed more than intended.
- A shortcut may have crept in; if so, stop and report it.

## Phase 12: Completion Report

### Stage 12.1: Prepare Final Implementation Report

#### Action 12.1.1

High-level purpose:

Produce the final concise report to the Project Owner.

Ground truth:

- implementation log
- final test outputs
- final probe outputs
- `git status --short`

Implementation:

- Report:

  ```text
  what changed
  what tests passed
  final probe result summary
  known residual risks
  whether the worktree has only intended changes
  ```

Tests:

- No new tests.

Completion condition:

- Project Owner can decide whether to review, commit, or request changes.

Failure hypotheses:

- Tests may not all pass and the report must say so.
- Some residual risk may remain around smoke-vs-semantic schema quality.
- The Project Owner may request an engineer continuity report before merge.

## Required Final Acceptance Criteria

This gameplan is complete only when all of the following are true.

- `plate_support_env` still has nontrivial default schema behavior.
- `parallelogram_singularity_env` has labeled edges, schema helpers, schema
  runtime support, tests, and nontrivial default behavior.
- `articulated_loop_env` has labeled edges, schema helpers, schema runtime
  support, tests, and nontrivial default behavior.
- `cable_parallel_env` has labeled edges, schema helpers, schema runtime support,
  tests, and nontrivial default behavior.
- `dual_arm_manipulation_env` has labeled edges, schema helpers, schema runtime
  support, tests, and nontrivial default behavior.
- `rl_counterpoint_v3` has neutral motion-family labels, schema helpers, schema
  runtime support, tests, and nontrivial post-refactor depth behavior.
- Every migrated training loop accepts `contraction_schema`.
- `tower_depth_probe` supports `--schema-mode default` and `--schema-mode none`.
- The no-env probe command works.
- Tests distinguish default schema behavior from explicit flat-baseline behavior.
- The implementation log records the execution interval.
- `uv run pytest tests/examples` passes.
- `uv run pytest` passes, or any failure is explicitly understood and approved by
  the Project Owner as out of scope.

## Explicit Non-Completion Conditions

The work is not complete if any of the following remain true.

- Any migrated environment has unlabeled `BaseEdge(...)` construction in its
  main hidden graph path.
- Any migrated runtime lacks `contraction_schema`.
- Any migrated training loop cannot pass a schema to the runtime.
- `tower_depth_probe` still implies `contraction_policy` controls partition
  coarsening.
- `rl_counterpoint_v3` remains depth `1` under default schema probing.
- Tests only assert that `current_position_at_every_tier` is nonempty.
- The explicit flat baseline cannot be tested.
- The implementation skipped semantic labels entirely where this gameplan
  required them.

## Final Note On Authority

This gameplan intentionally fixes defaults that the blueprint left as
recommendations. That is necessary so execution does not smuggle design choices
into source files.

If the Project Owner disagrees with any fixed default, the correct next step is
to revise this gameplan before implementation begins.

Once approved, the gameplan is law.
